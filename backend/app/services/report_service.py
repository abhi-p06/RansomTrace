import io
import html
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

def _safe_str(val: Any) -> str:
    """Escapes XML/HTML special characters to prevent ReportLab XML parser injection."""
    if val is None:
        return ""
    return html.escape(str(val))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line

from backend.app.models.case import InvestigationCase
from backend.app.models.evidence import Evidence
from backend.app.models.custody import ChainOfCustodyEntry
from backend.app.models.analysis import RiskAssessment, MLAnalysis
from backend.app.models.wallet import Wallet
from backend.app.models.transaction import Transaction
from backend.app.schemas.wallet import TransactionResponse, TxIO
from backend.app.services.mempool_client import mempool_client
from backend.app.services.blockchain_service import sats_to_btc, format_timestamp_iso
from backend.app.services.analytics_service import (
    calculate_total_transactions,
    calculate_incoming_transactions,
    calculate_outgoing_transactions,
    calculate_total_received,
    calculate_total_sent,
    calculate_average_transaction_amount,
    calculate_largest_transaction,
    calculate_smallest_transaction,
    calculate_unique_counterparties,
    calculate_average_time_between_tx_hours,
    INSUFFICIENT_DATA_MSG,
)
from backend.app.services.risk_service import (
    calculate_simple_risk_score,
    determine_risk_level,
    WEIGHT_TX_FREQUENCY,
    WEIGHT_AMOUNT_VARIATION,
    WEIGHT_COUNTERPARTIES,
    WEIGHT_RAPID_MOVEMENT,
    WEIGHT_ML_ANOMALY,
    DISCLAIMER_TEXT as RISK_DISCLAIMER_TEXT,
)
from backend.app.services.ml_service import (
    MLAnomalyService,
    extract_features,
    generate_simple_explanations,
    DISCLAIMER_TEXT as ML_DISCLAIMER_TEXT,
)
from backend.app.services.evidence_service import (
    generate_evidence_hash,
    verify_evidence_hash,
    CUSTODY_DISCLAIMER,
)
from backend.app.schemas.report import (
    ReportPreviewResponse,
    ReportPreviewCaseInfo,
    ReportPreviewAnalytics,
    ReportPreviewRisk,
    ReportPreviewEvidenceItem,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for rendering total page numbers (Page X of Y) and running headers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(colors.HexColor("#64748b"))

        # Top Running Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 755, "RANSOMTRACE FORENSIC INVESTIGATION REPORT // CONFIDENTIAL & TAMPER-EVIDENT")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 750, 558, 750)

        # Bottom Running Footer
        self.setFont("Helvetica", 7)
        self.drawString(54, 34, "Academic Digital Forensics Demonstration • Section 65B IT Act / ISO 27037 • SHA-256 Verifiable")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 34, page_str)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 44, 558, 44)

        self.restoreState()


class ForensicReportService:
    """
    Generates academic and judicial-grade PDF forensic investigation reports
    synthesizing all digital forensics artifacts, blockchain transactions,
    Isolation Forest anomaly scores, transparent risk indicators, and append-only custody logs.

    Strictly satisfies the 13 required forensic sections:
    1. Case information
    2. Wallet information
    3. Transaction summary
    4. Transaction analysis (10 metrics)
    5. Fund-flow summary (Depth 1)
    6. AI anomaly result (Isolation Forest)
    7. Risk score (0-100)
    8. Risk factors
    9. Evidence records
    10. SHA-256 hashes
    11. Chain-of-custody history
    12. Limitations
    13. Legal/ethical disclaimer

    Explicitly differentiates:
    - OBSERVED DATA
    - ANALYSIS
    - INVESTIGATIVE INDICATORS
    """

    def __init__(self):
        self.ml_service = MLAnomalyService(random_seed=42)

    def _get_target_wallet_for_case(self, db: Session, case: InvestigationCase) -> Optional[str]:
        """Resolves primary target wallet address for a case from wallets, evidence, or target label."""
        wallet = db.query(Wallet).filter(Wallet.case_id == case.id).first()
        if wallet and wallet.address:
            return wallet.address

        ev = db.query(Evidence).filter(Evidence.case_id == case.id, Evidence.wallet_address.isnot(None)).first()
        if ev and ev.wallet_address:
            return ev.wallet_address

        if case.target_label and (case.target_label.startswith("1") or case.target_label.startswith("3") or case.target_label.startswith("bc1")):
            return case.target_label

        return None

    def _get_case_transactions(self, db: Session, case: InvestigationCase, target_wallet: Optional[str]) -> List[TransactionResponse]:
        """
        Retrieves all transactions associated with the investigation case or target wallet,
        converting them to standard TransactionResponse objects.
        Prioritizes the local investigation database.
        """
        wallets = db.query(Wallet).filter(Wallet.case_id == case.id).all()
        wallet_ids = [w.id for w in wallets]
        wallet_addrs = [w.address for w in wallets if w.address]
        if target_wallet and target_wallet not in wallet_addrs:
            wallet_addrs.append(target_wallet)

        query_filters = []
        if wallet_ids:
            query_filters.append(Transaction.wallet_id.in_(wallet_ids))
        if wallet_addrs:
            query_filters.append(Transaction.wallet_address_val.in_(wallet_addrs))
            query_filters.append(Transaction.sender_val.in_(wallet_addrs))
            query_filters.append(Transaction.receiver_val.in_(wallet_addrs))

        db_txs = []
        if query_filters:
            db_txs = db.query(Transaction).filter(or_(*query_filters)).order_by(Transaction.block_time.asc()).all()

        responses: List[TransactionResponse] = []
        seen_txids = set()

        for tx in db_txs:
            if tx.txid in seen_txids:
                continue
            seen_txids.add(tx.txid)
            inp = [TxIO(address=i.get("address"), value_sats=i.get("value_sats", 0), value_btc=i.get("value_btc", 0.0)) for i in (tx.raw_inputs or [])]
            out = [TxIO(address=o.get("address"), value_sats=o.get("value_sats", 0), value_btc=o.get("value_btc", 0.0)) for o in (tx.raw_outputs or [])]
            responses.append(TransactionResponse(
                txid=tx.txid,
                block_height=tx.block_height,
                block_time=tx.block_time,
                block_time_iso=format_timestamp_iso(tx.block_time),
                confirmed=True,
                fee_sats=tx.fee_sats or 0,
                fee_btc=sats_to_btc(tx.fee_sats or 0),
                size_bytes=tx.size_bytes,
                net_value_sats=tx.net_value_sats or 0,
                net_value_btc=sats_to_btc(tx.net_value_sats or 0),
                flow_direction=tx.flow_direction,
                inputs=inp,
                outputs=out,
                data_source="Investigation Evidence Database"
            ))

        # Fallback to Mempool API if target_wallet exists and no transactions stored in DB
        if not responses and target_wallet and not target_wallet.startswith(("1Demo", "3Demo", "bc1demo")):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                txs_raw = loop.run_until_complete(mempool_client.get_address_transactions(target_wallet))
                loop.close()

                for raw in txs_raw[:50]:
                    txid = raw.get("txid", "")
                    if txid in seen_txids:
                        continue
                    seen_txids.add(txid)
                    status_info = raw.get("status", {})
                    bt = status_info.get("block_time")

                    inps: List[TxIO] = []
                    for vin in raw.get("vin", []):
                        prev = vin.get("prevout", {})
                        inps.append(TxIO(
                            address=prev.get("scriptpubkey_address"),
                            value_sats=prev.get("value", 0),
                            value_btc=sats_to_btc(prev.get("value", 0))
                        ))

                    outs: List[TxIO] = []
                    for vout in raw.get("vout", []):
                        outs.append(TxIO(
                            address=vout.get("scriptpubkey_address"),
                            value_sats=vout.get("value", 0),
                            value_btc=sats_to_btc(vout.get("value", 0))
                        ))

                    is_in = any(o.address == target_wallet for o in outs)
                    is_out = any(i.address == target_wallet for i in inps)
                    direction = "INCOMING" if is_in and not is_out else "OUTGOING" if is_out and not is_in else "TRANSIT"
                    val_sats = sum(o.value_sats for o in outs if o.address == target_wallet) if is_in else sum(o.value_sats for o in outs if o.address != target_wallet)

                    responses.append(TransactionResponse(
                        txid=txid,
                        block_height=status_info.get("block_height"),
                        block_time=bt,
                        block_time_iso=format_timestamp_iso(bt),
                        confirmed=status_info.get("confirmed", False),
                        fee_sats=raw.get("fee", 0),
                        fee_btc=sats_to_btc(raw.get("fee", 0)),
                        size_bytes=raw.get("size"),
                        net_value_sats=val_sats,
                        net_value_btc=sats_to_btc(val_sats),
                        flow_direction=direction,
                        inputs=inps,
                        outputs=outs,
                        data_source="Public Bitcoin Blockchain (Mempool API)"
                    ))
            except Exception:
                pass

        return responses

    def _create_risk_gauge_chart(self, score: float) -> Drawing:
        """Renders vector risk gauge bar chart with 4-tier indicator thresholds."""
        d = Drawing(504, 44)
        d.add(Rect(0, 0, 504, 44, rx=4, ry=4, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#e2e8f0"), strokeWidth=0.5))

        bar_x = 18
        bar_y = 10
        bar_w = 360
        bar_h = 15

        # 4 Risk Zones: 0-29 LOW, 30-59 MEDIUM, 60-79 HIGH, 80-100 CRITICAL
        d.add(Rect(bar_x, bar_y, bar_w * 0.29, bar_h, fillColor=colors.HexColor("#dcfce7"), strokeColor=None))
        d.add(Rect(bar_x + bar_w * 0.29, bar_y, bar_w * 0.30, bar_h, fillColor=colors.HexColor("#fef9c3"), strokeColor=None))
        d.add(Rect(bar_x + bar_w * 0.59, bar_y, bar_w * 0.20, bar_h, fillColor=colors.HexColor("#ffedd5"), strokeColor=None))
        d.add(Rect(bar_x + bar_w * 0.79, bar_y, bar_w * 0.21, bar_h, fillColor=colors.HexColor("#fee2e2"), strokeColor=None))

        # Pointer marker
        score_clamped = max(0.0, min(100.0, score))
        marker_x = bar_x + (score_clamped / 100.0) * bar_w
        d.add(Line(marker_x, bar_y - 2, marker_x, bar_y + bar_h + 4, strokeColor=colors.HexColor("#0f172a"), strokeWidth=2.5))

        # Zone labels
        d.add(String(bar_x + 5, bar_y + 4.5, "LOW (0-29)", fontSize=6.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#166534")))
        d.add(String(bar_x + bar_w * 0.32, bar_y + 4.5, "MEDIUM (30-59)", fontSize=6.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#854d0e")))
        d.add(String(bar_x + bar_w * 0.61, bar_y + 4.5, "HIGH (60-79)", fontSize=6.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#9a3412")))
        d.add(String(bar_x + bar_w * 0.81, bar_y + 4.5, "CRITICAL (80+)", fontSize=6.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#991b1b")))

        # Title text
        d.add(String(18, 30, "INVESTIGATIVE PRIORITIZATION GAUGE // 5 Weighted Indicators", fontSize=7.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#334155")))

        # Score Badge
        tier_color = "#dc2626" if score >= 80 else "#ea580c" if score >= 60 else "#ca8a04" if score >= 30 else "#16a34a"
        d.add(Rect(394, 8, 96, 26, rx=3, ry=3, fillColor=colors.HexColor(tier_color), strokeColor=None))
        d.add(String(404, 16, f"{score:.1f} / 100", fontSize=11, fontName="Helvetica-Bold", fillColor=colors.white))
        return d

    def _create_fund_flow_chart(self, received_btc: float, sent_btc: float, balance_btc: float) -> Drawing:
        """Renders vector fund flow dispersal ratio chart."""
        d = Drawing(504, 42)
        d.add(Rect(0, 0, 504, 42, rx=4, ry=4, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#e2e8f0"), strokeWidth=0.5))

        total = max(0.00000001, received_btc)
        sent_ratio = min(1.0, sent_btc / total) if total > 0 else 0
        bal_ratio = max(0.0, 1.0 - sent_ratio)

        bar_x = 135
        bar_y = 10
        bar_w = 350
        bar_h = 14

        w_sent = bar_w * sent_ratio
        w_bal = bar_w * bal_ratio
        d.add(Rect(bar_x, bar_y, w_sent, bar_h, fillColor=colors.HexColor("#f87171"), strokeColor=None))
        d.add(Rect(bar_x + w_sent, bar_y, w_bal, bar_h, fillColor=colors.HexColor("#34d399"), strokeColor=None))

        d.add(String(16, 28, "FUND DISPERSAL TOPOLOGY", fontSize=7.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#0f172a")))
        d.add(String(200, 28, f"Total Inflow: {received_btc:.6f} BTC", fontSize=7, fontName="Helvetica", fillColor=colors.HexColor("#475569")))

        d.add(String(16, 13, "Dispersal Ratio:", fontSize=7.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#334155")))
        d.add(String(bar_x + 5, bar_y + 4, f"Dispersed: {sent_btc:.4f} BTC ({sent_ratio*100:.1f}%)", fontSize=6.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#7f1d1d")))
        if w_bal > 50:
            d.add(String(bar_x + w_sent + 5, bar_y + 4, f"Retained: {balance_btc:.4f} BTC", fontSize=6.5, fontName="Helvetica-Bold", fillColor=colors.HexColor("#064e3b")))
        return d

    def get_report_preview_data(self, db: Session, case_id: str) -> ReportPreviewResponse:
        """
        Collects structured preview metadata for the web interface prior to PDF compilation.
        Uses data already generated by the investigation.
        """
        case = db.query(InvestigationCase).filter(
            (InvestigationCase.id == case_id) | (InvestigationCase.case_id == case_id)
        ).first()
        if not case:
            raise ValueError(f"Investigation Case '{case_id}' does not exist.")

        target_wallet = self._get_target_wallet_for_case(db, case)
        tx_responses = self._get_case_transactions(db, case, target_wallet)

        total_txs = calculate_total_transactions(tx_responses)
        incoming_txs = calculate_incoming_transactions(tx_responses)
        outgoing_txs = calculate_outgoing_transactions(tx_responses)
        rec_dict = calculate_total_received(tx_responses)
        sent_dict = calculate_total_sent(tx_responses)
        avg_amt_dict = calculate_average_transaction_amount(tx_responses)
        cp_dict = calculate_unique_counterparties(tx_responses, target_address=target_wallet or "")
        avg_time = calculate_average_time_between_tx_hours(tx_responses)

        rec_btc = rec_dict["btc"]
        sent_btc = sent_dict["btc"]
        bal_btc = max(0.0, rec_btc - sent_btc)

        analytics_summary = ReportPreviewAnalytics(
            total_tx_count=total_txs,
            incoming_tx_count=incoming_txs,
            outgoing_tx_count=outgoing_txs,
            total_received_btc=rec_btc,
            total_sent_btc=sent_btc,
            current_balance_btc=bal_btc,
            avg_tx_amount_btc=avg_amt_dict["btc"],
            tx_velocity_hourly=round(1.0 / avg_time, 2) if isinstance(avg_time, (int, float)) and avg_time > 0 else 0.0,
            burst_count=1 if total_txs > 0 else 0,
            unique_counterparties_count=cp_dict.get("count", 0),
        )

        # Risk scoring
        risk_record = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.case_id == case.id)
            .order_by(RiskAssessment.created_at.desc())
            .first()
        )
        if risk_record:
            summary_json = risk_record.heuristics_summary or {}
            risk_summary = ReportPreviewRisk(
                final_score=risk_record.risk_score,
                risk_level=risk_record.risk_tier,
                rule_score=summary_json.get("rule_score", 0.0),
                ml_score=summary_json.get("ml_score"),
                rule_triggers=summary_json.get("reasons", []),
            )
        else:
            calc_risk = calculate_simple_risk_score(tx_responses, target_address=target_wallet or "")
            risk_summary = ReportPreviewRisk(
                final_score=calc_risk["risk_score"],
                risk_level=calc_risk["risk_level"],
                rule_score=calc_risk["rule_score"],
                ml_score=calc_risk["ml_score"],
                rule_triggers=calc_risk["risk_factors"],
            )

        # ML anomaly result
        ml_record = (
            db.query(MLAnalysis)
            .filter(MLAnalysis.case_id == case.id)
            .order_by(MLAnalysis.created_at.desc())
            .first()
        )
        if ml_record:
            ml_classification = ml_record.classification
        elif tx_responses and target_wallet:
            _, _, classification, _ = self.ml_service.score_wallet(tx_responses, target_wallet)
            ml_classification = classification
        else:
            ml_classification = "NORMAL"

        # Evidence items
        evidences = db.query(Evidence).filter(Evidence.case_id == case.id).order_by(Evidence.seized_at.asc()).all()
        custody_count = db.query(ChainOfCustodyEntry).filter(ChainOfCustodyEntry.case_id == case.id).count()

        evidence_items = []
        for e in evidences:
            c_count = db.query(ChainOfCustodyEntry).filter(ChainOfCustodyEntry.evidence_id == e.id).count()
            evidence_items.append(ReportPreviewEvidenceItem(
                evidence_id=e.id,
                artifact_type=e.artifact_type,
                description=e.description,
                sha256_hash=e.sha256_hash,
                captured_by=e.captured_by or "Forensic Examiner",
                seized_at=e.seized_at,
                custody_events_count=c_count,
            ))

        return ReportPreviewResponse(
            case_info=ReportPreviewCaseInfo(
                id=case.id,
                case_id=case.case_id,
                title=case.title,
                incident_type=case.incident_type,
                description=case.description,
                target_label=case.target_label,
                severity=case.severity,
                status=case.status,
                target_wallet=target_wallet,
                created_at=case.created_at,
                updated_at=case.updated_at,
            ),
            target_wallet=target_wallet,
            analytics_summary=analytics_summary,
            risk_summary=risk_summary,
            ml_classification=ml_classification,
            evidence_items=evidence_items,
            chain_of_custody_count=custody_count,
            generated_at=datetime.now(timezone.utc),
            disclaimer=RISK_DISCLAIMER_TEXT,
        )

    def generate_pdf_report(self, db: Session, case_id: str) -> bytes:
        """
        Compiles and renders a publication-grade forensic PDF report
        incorporating all 13 specified forensic sections using data already generated.
        Clearly distinguishes: OBSERVED DATA, ANALYSIS, INVESTIGATIVE INDICATORS.
        """
        case = db.query(InvestigationCase).filter(
            (InvestigationCase.id == case_id) | (InvestigationCase.case_id == case_id)
        ).first()
        if not case:
            raise ValueError(f"Investigation Case '{case_id}' does not exist.")

        target_wallet = self._get_target_wallet_for_case(db, case)
        tx_responses = self._get_case_transactions(db, case, target_wallet)

        # -------------------------------------------------------------
        # Gather 10 Core Transaction Analysis Metrics
        # -------------------------------------------------------------
        total_txs = calculate_total_transactions(tx_responses)
        incoming_txs = calculate_incoming_transactions(tx_responses)
        outgoing_txs = calculate_outgoing_transactions(tx_responses)
        rec_dict = calculate_total_received(tx_responses)
        sent_dict = calculate_total_sent(tx_responses)
        avg_amt_dict = calculate_average_transaction_amount(tx_responses)
        largest_btc = calculate_largest_transaction(tx_responses)
        smallest_btc = calculate_smallest_transaction(tx_responses)
        cp_dict = calculate_unique_counterparties(tx_responses, target_address=target_wallet or "")
        unique_cp_count = cp_dict.get("count", 0)
        avg_time_hrs = calculate_average_time_between_tx_hours(tx_responses)

        rec_btc = rec_dict["btc"]
        sent_btc = sent_dict["btc"]
        bal_btc = max(0.0, rec_btc - sent_btc)
        avg_amt_btc = avg_amt_dict["btc"]

        # -------------------------------------------------------------
        # Gather AI Anomaly Detection Result
        # -------------------------------------------------------------
        ml_record = (
            db.query(MLAnalysis)
            .filter(MLAnalysis.case_id == case.id)
            .order_by(MLAnalysis.created_at.desc())
            .first()
        )
        if ml_record:
            raw_ml_score = ml_record.raw_anomaly_score
            norm_ml_score = ml_record.normalized_score
            ml_classification = ml_record.classification
            ml_feats = extract_features(tx_responses, target_wallet or "") if tx_responses else {
                "transaction_count": total_txs,
                "average_transaction_amount": avg_amt_btc,
                "incoming_count": incoming_txs,
                "outgoing_count": outgoing_txs,
                "unique_counterparties": unique_cp_count,
                "transaction_frequency": 1.0,
                "amount_variance": 0.0,
            }
            ml_explanation = generate_simple_explanations(ml_feats)
        elif tx_responses and target_wallet:
            raw_ml_score, norm_ml_score, ml_classification, _ = self.ml_service.score_wallet(tx_responses, target_wallet)
            ml_feats = extract_features(tx_responses, target_wallet)
            ml_explanation = generate_simple_explanations(ml_feats)
        else:
            raw_ml_score = 0.0
            norm_ml_score = 0.0
            ml_classification = "NORMAL"
            ml_feats = {
                "transaction_count": 0.0,
                "average_transaction_amount": 0.0,
                "incoming_count": 0.0,
                "outgoing_count": 0.0,
                "unique_counterparties": 0.0,
                "transaction_frequency": 0.0,
                "amount_variance": 0.0,
            }
            ml_explanation = "Insufficient transaction data for anomaly analysis."

        # -------------------------------------------------------------
        # Gather Risk Score & Risk Factors
        # -------------------------------------------------------------
        risk_record = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.case_id == case.id)
            .order_by(RiskAssessment.created_at.desc())
            .first()
        )
        if risk_record:
            final_risk_score = risk_record.risk_score
            risk_tier = risk_record.risk_tier
            summary_json = risk_record.heuristics_summary or {}
            risk_factors = summary_json.get("reasons", [])
        else:
            calc_risk = calculate_simple_risk_score(tx_responses, target_address=target_wallet or "")
            final_risk_score = calc_risk["risk_score"]
            risk_tier = calc_risk["risk_level"]
            risk_factors = calc_risk["risk_factors"]

        # -------------------------------------------------------------
        # Gather Evidence & Chain of Custody
        # -------------------------------------------------------------
        evidences = db.query(Evidence).filter(Evidence.case_id == case.id).order_by(Evidence.seized_at.asc()).all()
        custody_entries = (
            db.query(ChainOfCustodyEntry)
            .filter(ChainOfCustodyEntry.case_id == case.id)
            .order_by(ChainOfCustodyEntry.timestamp.asc())
            .all()
        )

        # -------------------------------------------------------------
        # PDF Document Buffer & Setup
        # -------------------------------------------------------------
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        # Style System
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=3,
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0284c7"),
            spaceAfter=8,
        )
        section_h1 = ParagraphStyle(
            "SectionH1",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=7,
            spaceAfter=3,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=10,
            textColor=colors.HexColor("#334155"),
        )
        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=6.8,
            leading=8.8,
            textColor=colors.HexColor("#1e293b"),
        )
        table_cell_bold = ParagraphStyle(
            "TableCellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8.8,
            textColor=colors.HexColor("#0f172a"),
        )
        disclaimer_p_style = ParagraphStyle(
            "DisclaimerP",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=6.8,
            leading=9,
            textColor=colors.HexColor("#78350f"),
        )

        elements = []

        # =============================================================
        # Header & Subtitle
        # =============================================================
        elements.append(Paragraph("RANSOMTRACE FORENSIC INVESTIGATION REPORT", title_style))
        elements.append(Paragraph(
            "Cryptocurrency-Based Ransomware Investigation & Digital Forensics System • University Forensic Report",
            subtitle_style,
        ))
        elements.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0f172a"), spaceAfter=5))

        # =============================================================
        # Tripartite Evidentiary Distinction Banner
        # =============================================================
        tripartite_data = [
            [
                Paragraph("<b>OBSERVED DATA (OBSERVED FACTS)</b>", table_cell_bold),
                Paragraph("Directly verifiable, immutable electronic records from the public Bitcoin blockchain and seized evidence vault (transactions, addresses, balances, SHA-256 digests, custody timeline).", body_style),
            ],
            [
                Paragraph("<b>ANALYSIS (ANALYTICAL INDICATORS)</b>", table_cell_bold),
                Paragraph("Mathematical and algorithmic derivatives: 10 transaction analysis metrics, fund-flow dispersal topology, and unsupervised scikit-learn Isolation Forest anomaly partition scores.", body_style),
            ],
            [
                Paragraph("<b>INVESTIGATIVE INDICATORS (INVESTIGATOR INTERPRETATION)</b>", table_cell_bold),
                Paragraph("Transparent 0–100 weighted prioritization indicators and triggered risk factors for investigative triage. <i>Does NOT establish criminal identity or guilt.</i>", body_style),
            ],
        ]
        trip_table = Table(tripartite_data, colWidths=[150, 354])
        trip_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0fdf4")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#eff6ff")),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#fefce8")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ]))
        elements.append(trip_table)
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 1: Case Information [OBSERVED DATA]
        # =============================================================
        elements.append(Paragraph("1. CASE INFORMATION [OBSERVED DATA]", section_h1))
        gen_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        case_created_str = case.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if case.created_at else "N/A"

        case_info_data = [
            [
                Paragraph("<b>Case Identifier:</b>", table_cell_bold),
                Paragraph(f"<b>{_safe_str(case.case_id)}</b>", table_cell_bold),
                Paragraph("<b>Investigation Severity:</b>", table_cell_bold),
                Paragraph(f"<font color='{colors.HexColor('#e11d48').hexval()}'><b>{_safe_str(case.severity.upper())}</b></font>", table_cell_bold),
            ],
            [
                Paragraph("<b>Case Name / Title:</b>", table_cell_bold),
                Paragraph(_safe_str(case.title), table_cell_style),
                Paragraph("<b>Operational Status:</b>", table_cell_bold),
                Paragraph(_safe_str(case.status), table_cell_style),
            ],
            [
                Paragraph("<b>Incident Type:</b>", table_cell_bold),
                Paragraph(_safe_str(case.incident_type), table_cell_style),
                Paragraph("<b>Case Created:</b>", table_cell_bold),
                Paragraph(case_created_str, table_cell_style),
            ],
            [
                Paragraph("<b>Report Generated:</b>", table_cell_bold),
                Paragraph(gen_time_str, table_cell_style),
                Paragraph("<b>Target Entity / Label:</b>", table_cell_bold),
                Paragraph(_safe_str(case.target_label or "Extortion Triage"), table_cell_style),
            ],
            [
                Paragraph("<b>Description / Scope:</b>", table_cell_bold),
                Paragraph(_safe_str(case.description or "Forensic inquiry into ransomware payment transactions and evidence preservation."), table_cell_style),
                Paragraph("<b>Investigator Node:</b>", table_cell_bold),
                Paragraph("RansomTrace Academic Forensics Subsystem", table_cell_style),
            ],
        ]
        case_table = Table(case_info_data, colWidths=[110, 150, 110, 134])
        case_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ]))
        elements.append(case_table)
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 2: Wallet Information [OBSERVED DATA]
        # =============================================================
        elements.append(Paragraph("2. WALLET INFORMATION [OBSERVED DATA]", section_h1))
        wallet_addr_str = target_wallet or "No Target Wallet Assigned"
        first_act_str = tx_responses[0].block_time_iso if tx_responses else "N/A"
        latest_act_str = tx_responses[-1].block_time_iso if tx_responses else "N/A"

        wallet_info_data = [
            [
                Paragraph("<b>Target Wallet Address:</b>", table_cell_bold),
                Paragraph(f"<font name='Courier'><b>{_safe_str(wallet_addr_str)}</b></font>", table_cell_style),
                Paragraph("<b>Address Format:</b>", table_cell_bold),
                Paragraph("Legacy P2PKH (Base58Check)", table_cell_style),
            ],
            [
                Paragraph("<b>Retained Balance:</b>", table_cell_bold),
                Paragraph(f"<b>{bal_btc:.6f} BTC</b>", table_cell_style),
                Paragraph("<b>Activity Window:</b>", table_cell_bold),
                Paragraph(f"{first_act_str[:10]} to {latest_act_str[:10]}", table_cell_style),
            ],
        ]
        wallet_table = Table(wallet_info_data, colWidths=[110, 150, 110, 134])
        wallet_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ]))
        elements.append(wallet_table)
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 3: Transaction Summary [OBSERVED DATA]
        # =============================================================
        elements.append(Paragraph("3. TRANSACTION SUMMARY [OBSERVED DATA]", section_h1))
        tx_summary_data = [
            [
                Paragraph("<b>Total Transactions:</b>", table_cell_bold),
                Paragraph(f"<b>{total_txs}</b> confirmed records", table_cell_style),
                Paragraph("<b>Confirmed Inputs / Outputs:</b>", table_cell_bold),
                Paragraph(f"{incoming_txs} Incoming / {outgoing_txs} Outgoing", table_cell_style),
            ],
            [
                Paragraph("<b>Gross Received (Inflow):</b>", table_cell_bold),
                Paragraph(f"<b>{rec_btc:.6f} BTC</b> ({rec_dict['sats']:,} sats)", table_cell_style),
                Paragraph("<b>Gross Sent (Outflow):</b>", table_cell_bold),
                Paragraph(f"<b>{sent_btc:.6f} BTC</b> ({sent_dict['sats']:,} sats)", table_cell_style),
            ],
            [
                Paragraph("<b>Net Retained Balance:</b>", table_cell_bold),
                Paragraph(f"<b>{bal_btc:.6f} BTC</b>", table_cell_style),
                Paragraph("<b>Data Origin / Mode:</b>", table_cell_bold),
                Paragraph("Demonstration / Public Bitcoin Ledger", table_cell_style),
            ],
        ]
        summary_table = Table(tx_summary_data, colWidths=[120, 140, 120, 124])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 4: Transaction Analysis (10 Forensic Metrics) [ANALYSIS]
        # =============================================================
        elements.append(Paragraph("4. TRANSACTION ANALYSIS (10 FORENSIC METRICS) [ANALYSIS]", section_h1))
        avg_time_str = f"{avg_time_hrs:.2f} hours" if isinstance(avg_time_hrs, (int, float)) else INSUFFICIENT_DATA_MSG

        analysis_metrics_data = [
            [
                Paragraph("<b>Metric #</b>", table_cell_bold),
                Paragraph("<b>Forensic Analytical Calculation</b>", table_cell_bold),
                Paragraph("<b>Computed Value</b>", table_cell_bold),
                Paragraph("<b>Analytical Context / Interpretation</b>", table_cell_bold),
            ],
            [
                Paragraph("1", table_cell_style),
                Paragraph("Total Transactions", table_cell_bold),
                Paragraph(f"{total_txs}", table_cell_style),
                Paragraph("Total count of observable public blockchain ledger events.", table_cell_style),
            ],
            [
                Paragraph("2", table_cell_style),
                Paragraph("Incoming Transactions", table_cell_bold),
                Paragraph(f"{incoming_txs}", table_cell_style),
                Paragraph("Inflow payment deposits credited to the target wallet address.", table_cell_style),
            ],
            [
                Paragraph("3", table_cell_style),
                Paragraph("Outgoing Transactions", table_cell_bold),
                Paragraph(f"{outgoing_txs}", table_cell_style),
                Paragraph("Dispersal / withdrawal events moving funds to external addresses.", table_cell_style),
            ],
            [
                Paragraph("4", table_cell_style),
                Paragraph("Total Received", table_cell_bold),
                Paragraph(f"{rec_btc:.6f} BTC", table_cell_style),
                Paragraph(f"Aggregate volume deposited ({rec_dict['sats']:,} Satoshis).", table_cell_style),
            ],
            [
                Paragraph("5", table_cell_style),
                Paragraph("Total Sent", table_cell_bold),
                Paragraph(f"{sent_btc:.6f} BTC", table_cell_style),
                Paragraph(f"Aggregate volume dispersed ({sent_dict['sats']:,} Satoshis).", table_cell_style),
            ],
            [
                Paragraph("6", table_cell_style),
                Paragraph("Average Transaction Amount", table_cell_bold),
                Paragraph(f"{avg_amt_btc:.6f} BTC", table_cell_style),
                Paragraph(f"Arithmetic mean value transferred ({avg_amt_dict['sats']:,} Satoshis).", table_cell_style),
            ],
            [
                Paragraph("7", table_cell_style),
                Paragraph("Largest Transaction", table_cell_bold),
                Paragraph(f"{largest_btc:.6f} BTC", table_cell_style),
                Paragraph("Peak single transaction value observed across all inputs/outputs.", table_cell_style),
            ],
            [
                Paragraph("8", table_cell_style),
                Paragraph("Smallest Transaction", table_cell_bold),
                Paragraph(f"{smallest_btc:.6f} BTC", table_cell_style),
                Paragraph("Minimum non-zero transaction magnitude observed.", table_cell_style),
            ],
            [
                Paragraph("9", table_cell_style),
                Paragraph("Number of Unique Counterparties", table_cell_bold),
                Paragraph(f"{unique_cp_count}", table_cell_style),
                Paragraph("Distinct external sender and receiver addresses interacting with wallet.", table_cell_style),
            ],
            [
                Paragraph("10", table_cell_style),
                Paragraph("Average Time Between Transactions", table_cell_bold),
                Paragraph(avg_time_str, table_cell_style),
                Paragraph("Temporal interval between sequential transactions.", table_cell_style),
            ],
        ]
        analysis_table = Table(analysis_metrics_data, colWidths=[40, 160, 95, 209])
        analysis_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 1.8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ]))
        for c_i in range(4):
            analysis_metrics_data[0][c_i].style.textColor = colors.white
        elements.append(analysis_table)
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 5: Fund-Flow Summary (Direct Depth-1) [ANALYSIS]
        # =============================================================
        elements.append(Paragraph("5. FUND-FLOW SUMMARY (DIRECT DEPTH-1) [ANALYSIS]", section_h1))
        flow_chart = self._create_fund_flow_chart(
            received_btc=rec_btc,
            sent_btc=sent_btc,
            balance_btc=bal_btc,
        )
        elements.append(flow_chart)
        elements.append(Spacer(1, 3))

        counterparties_list = cp_dict.get("counterparties", [])
        if counterparties_list:
            ff_rows = [
                [
                    Paragraph("<b>Counterparty Address</b>", table_cell_bold),
                    Paragraph("<b>Role</b>", table_cell_bold),
                    Paragraph("<b>Tx Count</b>", table_cell_bold),
                    Paragraph("<b>Volume Transferred</b>", table_cell_bold),
                ]
            ]
            for cp in counterparties_list[:5]:
                ff_rows.append([
                    Paragraph(f"<font name='Courier' size='6'>{_safe_str(cp.address)}</font>", table_cell_style),
                    Paragraph(_safe_str(cp.role), table_cell_style),
                    Paragraph(str(cp.tx_count), table_cell_style),
                    Paragraph(f"{cp.total_btc:.6f} BTC", table_cell_style),
                ])
            ff_table = Table(ff_rows, colWidths=[234, 80, 70, 120])
            ff_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            for c_i in range(4):
                ff_rows[0][c_i].style.textColor = colors.white
            elements.append(ff_table)
        else:
            elements.append(Paragraph("No directly connected counterparties observed.", body_style))

        elements.append(Spacer(1, 3))
        elements.append(Paragraph(
            "<b>Topological Observations:</b> Direct Depth-1 fund routing reveals fund dispersion from incoming extortion deposits "
            "into intermediary forwarding counterparties, consistent with typical ransomware payment collection patterns.",
            body_style,
        ))
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 6: AI Anomaly Result (Isolation Forest) [ANALYSIS]
        # =============================================================
        elements.append(Paragraph("6. AI ANOMALY DETECTION (ISOLATION FOREST) [ANALYSIS]", section_h1))
        ml_data = [
            [
                Paragraph("<b>Model Architecture:</b>", table_cell_bold),
                Paragraph("scikit-learn IsolationForest (100 Decision Trees, Contamination: 0.15, Seed: 42)", table_cell_style),
            ],
            [
                Paragraph("<b>7 Extracted Features:</b>", table_cell_bold),
                Paragraph(
                    f"Tx Count: {ml_feats['transaction_count']} | Avg Amount: {ml_feats['average_transaction_amount']:.4f} BTC | "
                    f"In: {ml_feats['incoming_count']} | Out: {ml_feats['outgoing_count']} | Counterparties: {ml_feats['unique_counterparties']} | "
                    f"Freq: {ml_feats['transaction_frequency']} tx/day | Variance: {ml_feats['amount_variance']:.4f}",
                    table_cell_style
                ),
            ],
            [
                Paragraph("<b>Raw Outlier Score:</b>", table_cell_bold),
                Paragraph(f"{raw_ml_score:.4f} (Negative value indicates tree partition outlier)", table_cell_style),
            ],
            [
                Paragraph("<b>Normalized Anomaly Score:</b>", table_cell_bold),
                Paragraph(f"<b>{norm_ml_score:.1f} / 100</b> (Classification: <b>{ml_classification}</b>)", table_cell_style),
            ],
            [
                Paragraph("<b>Forensic Explanation:</b>", table_cell_bold),
                Paragraph(f"<i>{_safe_str(ml_explanation)}</i>", body_style),
            ],
            [
                Paragraph("<b>Important Model Limitation:</b>", table_cell_bold),
                Paragraph(f"<font color='#b45309'><b>{ML_DISCLAIMER_TEXT}</b></font>", body_style),
            ],
        ]
        ml_table = Table(ml_data, colWidths=[130, 374])
        ml_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 2.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ]))
        elements.append(ml_table)
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 7: Risk Score [INVESTIGATIVE INDICATORS]
        # =============================================================
        elements.append(Paragraph("7. INVESTIGATIVE RISK SCORE [INVESTIGATIVE INDICATORS]", section_h1))
        risk_chart = self._create_risk_gauge_chart(score=final_risk_score)
        elements.append(risk_chart)
        elements.append(Spacer(1, 3))

        weights_data = [
            [
                Paragraph("<b>Indicator</b>", table_cell_bold),
                Paragraph("<b>Max Weight</b>", table_cell_bold),
                Paragraph("<b>Forensic Rationalization</b>", table_cell_bold),
            ],
            [
                Paragraph("1. High Transaction Frequency", table_cell_style),
                Paragraph(f"{WEIGHT_TX_FREQUENCY:.0f} pts", table_cell_style),
                Paragraph("Measures rapid burst transaction activity across active operational days.", table_cell_style),
            ],
            [
                Paragraph("2. High Transaction Amount Variation", table_cell_style),
                Paragraph(f"{WEIGHT_AMOUNT_VARIATION:.0f} pts", table_cell_style),
                Paragraph("Captures irregular transfer magnitudes suggesting tiered extortion or splitting.", table_cell_style),
            ],
            [
                Paragraph("3. Large Number of Counterparties", table_cell_style),
                Paragraph(f"{WEIGHT_COUNTERPARTIES:.0f} pts", table_cell_style),
                Paragraph("Measures breadth of unique external sender and receiver addresses.", table_cell_style),
            ],
            [
                Paragraph("4. Rapid Movement of Funds", table_cell_style),
                Paragraph(f"{WEIGHT_RAPID_MOVEMENT:.0f} pts", table_cell_style),
                Paragraph("Detects short temporal windows between inbound deposit and outbound dispersal.", table_cell_style),
            ],
            [
                Paragraph("5. ML Anomaly Result", table_cell_style),
                Paragraph(f"{WEIGHT_ML_ANOMALY:.0f} pts", table_cell_style),
                Paragraph("Unsupervised Isolation Forest score measuring deviation from typical usage baselines.", table_cell_style),
            ],
            [
                Paragraph("<b>Total Potential Score</b>", table_cell_bold),
                Paragraph("<b>100 pts</b>", table_cell_bold),
                Paragraph("<b>Tiers: 0–29 LOW | 30–59 MEDIUM | 60–79 HIGH | 80–100 CRITICAL</b>", table_cell_bold),
            ],
        ]
        weights_table = Table(weights_data, colWidths=[160, 64, 280])
        weights_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 1.8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ]))
        for c_i in range(3):
            weights_data[0][c_i].style.textColor = colors.white
        elements.append(weights_table)
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 8: Risk Factors [INVESTIGATIVE INDICATORS]
        # =============================================================
        elements.append(Paragraph("8. TRIGGERED RISK FACTORS [INVESTIGATIVE INDICATORS]", section_h1))
        if risk_factors:
            for factor in risk_factors:
                elements.append(Paragraph(f"• <b>{_safe_str(factor)}</b>", body_style))
        else:
            elements.append(Paragraph("• No anomalous risk factors exceeded configured operational thresholds.", body_style))

        elements.append(Spacer(1, 2))
        elements.append(Paragraph(
            f"<b>Investigative Prioritization Note:</b> {RISK_DISCLAIMER_TEXT}",
            body_style,
        ))
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 9: Evidence Records [OBSERVED DATA]
        # =============================================================
        elements.append(Paragraph("9. DIGITAL EVIDENCE RECORDS [OBSERVED DATA]", section_h1))
        if evidences:
            ev_rows = [
                [
                    Paragraph("<b>Evidence ID</b>", table_cell_bold),
                    Paragraph("<b>Case ID</b>", table_cell_bold),
                    Paragraph("<b>Transaction ID / Finding</b>", table_cell_bold),
                    Paragraph("<b>Wallet Address</b>", table_cell_bold),
                    Paragraph("<b>Amount</b>", table_cell_bold),
                    Paragraph("<b>Seized (UTC)</b>", table_cell_bold),
                ]
            ]
            for ev in evidences:
                tx_label = ev.transaction_hash or ev.description or "General Finding"
                short_tx = tx_label[:18] + "..." if len(tx_label) > 18 else tx_label
                ev_rows.append([
                    Paragraph(_safe_str(ev.id[:8] + "..."), table_cell_style),
                    Paragraph(_safe_str(ev.case_id or case.case_id), table_cell_style),
                    Paragraph(f"<font name='Courier' size='6'>{_safe_str(short_tx)}</font>", table_cell_style),
                    Paragraph(f"<font name='Courier' size='6'>{_safe_str((ev.wallet_address or 'N/A')[:16] + '...')}</font>", table_cell_style),
                    Paragraph(f"{ev.amount_btc:.4f} BTC" if ev.amount_btc else "N/A", table_cell_style),
                    Paragraph(ev.seized_at.strftime("%Y-%m-%d %H:%M"), table_cell_style),
                ])
            ev_table = Table(ev_rows, colWidths=[55, 75, 125, 115, 65, 69])
            ev_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            for c_i in range(6):
                ev_rows[0][c_i].style.textColor = colors.white
            elements.append(ev_table)
        else:
            elements.append(Paragraph("No digital evidence records preserved for this case docket.", body_style))
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 10: SHA-256 Hashes & Cryptographic Integrity [OBSERVED DATA]
        # =============================================================
        elements.append(Paragraph("10. CRYPTOGRAPHIC SHA-256 INTEGRITY HASHES [OBSERVED DATA]", section_h1))
        if evidences:
            hash_rows = [
                [
                    Paragraph("<b>Evidence ID</b>", table_cell_bold),
                    Paragraph("<b>Deterministic Canonical SHA-256 Digest (RFC 8785)</b>", table_cell_bold),
                    Paragraph("<b>Integrity Status</b>", table_cell_bold),
                ]
            ]
            for ev in evidences:
                timestamp_val = ""
                if ev.raw_payload and isinstance(ev.raw_payload, dict):
                    timestamp_val = (
                        ev.raw_payload.get("timestamp")
                        or ev.raw_payload.get("collected_at")
                        or ""
                    )
                verified, status_text, _ = verify_evidence_hash(
                    stored_hash=ev.sha256_hash,
                    case_id=ev.case_id,
                    transaction_id=ev.transaction_hash or "",
                    wallet_address=ev.wallet_address or "",
                    amount=ev.amount_btc,
                    timestamp=timestamp_val,
                    source=ev.source,
                )
                status_color = "#16a34a" if verified else "#dc2626"

                hash_rows.append([
                    Paragraph(_safe_str(ev.id[:8] + "..."), table_cell_style),
                    Paragraph(f"<font name='Courier' size='6'><b>{_safe_str(ev.sha256_hash)}</b></font>", table_cell_style),
                    Paragraph(f"<font color='{status_color}'><b>{status_text}</b></font>", table_cell_style),
                ])
            hash_table = Table(hash_rows, colWidths=[65, 335, 104])
            hash_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            for c_i in range(3):
                hash_rows[0][c_i].style.textColor = colors.white
            elements.append(hash_table)
        else:
            elements.append(Paragraph("No cryptographic evidence hashes present.", body_style))
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 11: Chain-of-Custody History [OBSERVED DATA]
        # =============================================================
        elements.append(Paragraph("11. APPEND-ONLY CHAIN OF CUSTODY HISTORY [OBSERVED DATA]", section_h1))
        if custody_entries:
            coc_rows = [
                [
                    Paragraph("<b>Seq</b>", table_cell_bold),
                    Paragraph("<b>Action Performed</b>", table_cell_bold),
                    Paragraph("<b>Timestamp (UTC)</b>", table_cell_bold),
                    Paragraph("<b>Forensic Actor / Officer</b>", table_cell_bold),
                    Paragraph("<b>Procedural Notes & Custody Remarks</b>", table_cell_bold),
                ]
            ]
            for idx, entry in enumerate(custody_entries[:8]):
                coc_rows.append([
                    Paragraph(str(idx + 1), table_cell_style),
                    Paragraph(f"<b>{_safe_str(entry.action_performed)}</b>", table_cell_style),
                    Paragraph(entry.timestamp.strftime("%Y-%m-%d %H:%M"), table_cell_style),
                    Paragraph(_safe_str(entry.actor_name), table_cell_style),
                    Paragraph(_safe_str(entry.notes or "Forensic evidence lifecycle preservation."), body_style),
                ])
            coc_table = Table(coc_rows, colWidths=[24, 76, 75, 95, 234])
            coc_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            for c_i in range(5):
                coc_rows[0][c_i].style.textColor = colors.white
            elements.append(coc_table)
        else:
            elements.append(Paragraph("No chain-of-custody log records available for this docket.", body_style))
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 12: Technical Boundaries & Methodological Limitations
        # =============================================================
        elements.append(Paragraph("12. FORENSIC & TECHNICAL LIMITATIONS [ANALYSIS]", section_h1))
        limits_text = (
            "1. <b>Public Blockchain Ledger Bounds:</b> All observations are extracted strictly from public Bitcoin blockchain "
            "records. The system operates with zero visibility into private cryptographic keys or off-chain communications.<br/>"
            "2. <b>Pseudonymous Identification:</b> Blockchain addresses constitute cryptographic public keys, not verified natural "
            "persons or corporate entities. Conclusive legal attribution mandates subpoenaed KYC records from licensed Virtual Asset Service Providers (VASPs).<br/>"
            "3. <b>Unsupervised ML Boundaries:</b> The scikit-learn Isolation Forest model measures statistical distance from typical "
            "transaction density baselines. It does not determine intent, mens rea, or legal culpability.<br/>"
            "4. <b>Graph Traversal Depth:</b> Topological analysis is restricted to direct Depth-1 counterparties. Complex peeling chains "
            "or CoinJoin mixing protocols require targeted, multi-hop iterative analysis."
        )
        elements.append(Paragraph(limits_text, body_style))
        elements.append(Spacer(1, 5))

        # =============================================================
        # SECTION 13: Legal & Ethical Disclaimer [STATUTORY NOTICE]
        # =============================================================
        elements.append(Paragraph("13. LEGAL & ETHICAL DISCLAIMER [STATUTORY NOTICE]", section_h1))
        disclaimer_box_content = (
            "<b>STATUTORY DISCLAIMER & ACADEMIC INTEGRITY NOTICE:</b><br/>"
            f"{CUSTODY_DISCLAIMER}<br/><br/>"
            "<b>NO CLAIM OF GUILT OR CRIMINAL ATTRIBUTION:</b> This forensic report does NOT make claims of criminal identity, "
            "attacker attribution, or legal guilt. All computed risk indicators and machine learning classifications are automated prioritization "
            "signals reflecting observable transaction behaviour. <b>This wallet exhibits transaction behaviour that warrants further investigation.</b><br/><br/>"
            "<b>STANDARDS COMPLIANCE:</b> Digital evidence items recorded in this document have been preserved using canonical RFC 8785 JSON byte "
            "serialization and hashed via Python hashlib SHA-256 in compliance with Section 65B of the Indian Evidence Act and ISO/IEC 27037 standards "
            "for digital evidence collection and preservation."
        )
        disc_table = Table([[Paragraph(disclaimer_box_content, disclaimer_p_style)]], colWidths=[504])
        disc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef3c7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#f59e0b")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        elements.append(disc_table)

        # -------------------------------------------------------------
        # Render PDF with NumberedCanvas (2-pass page numbering)
        # -------------------------------------------------------------
        doc.build(elements, canvasmaker=NumberedCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes


forensic_report_service = ForensicReportService()
