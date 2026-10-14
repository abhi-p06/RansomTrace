"""
Simplified Forensic AI Anomaly Detection Engine
Designed for undergraduate cybersecurity students.

Technology:
- scikit-learn IsolationForest (Unsupervised outlier detection)

Core Pipeline:
Transaction Data
      ↓
Feature Extraction (7 Features Only)
      ↓
Isolation Forest
      ↓
Anomaly Score (Raw & 0-100 Normalized)
      ↓
Anomaly Level (NORMAL, LOW ANOMALY, MEDIUM ANOMALY, HIGH ANOMALY)

Ethical & Academic Integrity:
- The model does NOT prove or claim criminal guilt or ransomware affiliation.
- It identifies statistical outliers in observable transaction patterns.
- Zero fabricated precision, recall, or accuracy scores.
- Clear message when data is insufficient:
  'Insufficient transaction data for anomaly analysis.'
"""

import uuid
from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from backend.app.schemas.wallet import TransactionResponse
from backend.app.schemas.ml import (
    FeatureItem,
    ModelInfo,
    MLAnalysisResponse,
    MLAnalysisHistoryItem,
)
from backend.app.models.analysis import MLAnalysis
from backend.app.models.wallet import Wallet

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "The model does NOT determine whether a wallet belongs to a ransomware attacker. "
    "It only identifies unusual transaction behaviour based on publicly observable blockchain patterns."
)

INSUFFICIENT_DATA_MSG = "Insufficient transaction data for anomaly analysis."

# Feature labels and baseline reference values (for student explanation)
FEATURE_CONFIG = [
    {
        "name": "transaction_count",
        "label": "Transaction Count",
        "baseline_median": 5.0,
        "description": "Total observed transactions for this wallet",
    },
    {
        "name": "average_transaction_amount",
        "label": "Average Transaction Amount (BTC)",
        "baseline_median": 0.05,
        "description": "Mean value transferred per transaction in BTC",
    },
    {
        "name": "incoming_count",
        "label": "Incoming Transactions",
        "baseline_median": 3.0,
        "description": "Number of deposit transfers received",
    },
    {
        "name": "outgoing_count",
        "label": "Outgoing Transactions",
        "baseline_median": 2.0,
        "description": "Number of withdrawal / disbursement transfers",
    },
    {
        "name": "unique_counterparties",
        "label": "Unique Counterparties",
        "baseline_median": 4.0,
        "description": "Count of distinct external input/output addresses",
    },
    {
        "name": "transaction_frequency",
        "label": "Transaction Frequency (tx/day)",
        "baseline_median": 0.5,
        "description": "Average transaction rate per active operational day",
    },
    {
        "name": "amount_variance",
        "label": "Amount Variance (BTC)",
        "baseline_median": 0.02,
        "description": "Statistical variance of transfer magnitudes",
    },
]

FEATURE_KEYS: List[str] = [f["name"] for f in FEATURE_CONFIG]

# Baseline representative corpus for Isolation Forest training
BASELINE_CORPUS = np.array([
    [1.0,  0.02, 1.0, 0.0, 1.0, 0.1,  0.000],
    [2.0,  0.04, 2.0, 0.0, 2.0, 0.15, 0.001],
    [3.0,  0.05, 2.0, 1.0, 3.0, 0.2,  0.002],
    [4.0,  0.08, 3.0, 1.0, 4.0, 0.3,  0.004],
    [5.0,  0.06, 3.0, 2.0, 4.0, 0.35, 0.003],
    [6.0,  0.10, 4.0, 2.0, 5.0, 0.4,  0.008],
    [8.0,  0.07, 5.0, 3.0, 6.0, 0.5,  0.005],
    [10.0, 0.09, 7.0, 3.0, 8.0, 0.6,  0.006],
    [12.0, 0.12, 8.0, 4.0, 9.0, 0.7,  0.010],
    [15.0, 0.15, 10.0, 5.0, 11.0, 0.8, 0.015],
])


def extract_features(txs: List[TransactionResponse], target_address: str) -> Dict[str, float]:
    """
    Extracts strictly the 7 required features from observed transactions:
    1. transaction_count
    2. average_transaction_amount
    3. incoming_count
    4. outgoing_count
    5. unique_counterparties
    6. transaction_frequency
    7. amount_variance
    """
    clean_target = target_address.strip()
    total_tx = len(txs)
    if total_tx == 0:
        return {
            "transaction_count": 0.0,
            "average_transaction_amount": 0.0,
            "incoming_count": 0.0,
            "outgoing_count": 0.0,
            "unique_counterparties": 0.0,
            "transaction_frequency": 0.0,
            "amount_variance": 0.0,
        }

    # 1. Transaction count
    tx_count = float(total_tx)

    # 2. Amounts and average amount
    amounts = [abs(tx.net_value_btc) for tx in txs if abs(tx.net_value_btc) > 0]
    avg_amount = round(sum(amounts) / len(amounts), 4) if amounts else 0.0

    # 3. Incoming count
    in_count = float(sum(1 for tx in txs if tx.flow_direction == "INCOMING"))

    # 4. Outgoing count
    out_count = float(sum(1 for tx in txs if tx.flow_direction == "OUTGOING"))

    # 5. Unique counterparties
    counterparties = set()
    for tx in txs:
        for inp in tx.inputs:
            if inp.address and inp.address != clean_target:
                counterparties.add(inp.address)
        for out in tx.outputs:
            if out.address and out.address != clean_target:
                counterparties.add(out.address)
    unique_cp = float(len(counterparties))

    # 6. Transaction frequency (tx per day)
    timestamps = [tx.block_time for tx in txs if tx.block_time]
    if timestamps and len(timestamps) >= 2:
        span_seconds = max(timestamps) - min(timestamps)
        active_days = max(1.0, span_seconds / 86400.0)
    else:
        active_days = 1.0
    tx_freq = round(total_tx / active_days, 2)

    # 7. Amount variance
    if len(amounts) >= 2:
        mean_amt = sum(amounts) / len(amounts)
        amt_var = round(sum((x - mean_amt) ** 2 for x in amounts) / len(amounts), 4)
    else:
        amt_var = 0.0

    return {
        "transaction_count": tx_count,
        "average_transaction_amount": avg_amount,
        "incoming_count": in_count,
        "outgoing_count": out_count,
        "unique_counterparties": unique_cp,
        "transaction_frequency": tx_freq,
        "amount_variance": amt_var,
    }


def generate_simple_explanations(features: Dict[str, float]) -> str:
    """
    Generates a simple, human-readable forensic explanation
    based on observed behavioral deviations.
    """
    reasons: List[str] = []

    if features["transaction_frequency"] > 1.0:
        reasons.append("Unusually high transaction frequency was observed.")

    if features["amount_variance"] > 0.1:
        reasons.append("Transaction amounts show higher-than-normal variation.")

    if features["unique_counterparties"] >= 4:
        reasons.append("Multiple distinct counterparties were observed.")

    if features["average_transaction_amount"] > 1.0:
        reasons.append("High average transaction amounts detected compared to baseline transfers.")

    if features["incoming_count"] > 0 and features["outgoing_count"] > 0 and abs(features["incoming_count"] - features["outgoing_count"]) <= 1:
        reasons.append("Direct deposit-to-withdrawal pass-through behavior was observed.")

    if not reasons:
        return "Transaction patterns show standard, consistent activity within expected baseline parameters."

    return " ".join(reasons)


class MLAnomalyService:
    """
    Isolation Forest anomaly detection service for cryptocurrency forensics.
    Beginner-friendly and easy to explain in a university viva.
    """

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.model_info = ModelInfo(
            model_name="IsolationForest",
            model_version="1.0.0",
            algorithm_type="Unsupervised Anomaly Detection",
            n_estimators=100,
            contamination=0.15,
            random_state=self.random_seed,
            framework="scikit-learn",
            evaluation_methodology=(
                "Unsupervised tree isolation path length. Evaluates how easily a data point "
                "is separated from the baseline without supervised training labels."
            )
        )

    def score_wallet(self, txs: List[TransactionResponse], wallet_address: str) -> Tuple[float, float, str, bool]:
        """
        Runs IsolationForest outlier scoring on the 7 extracted features.
        Returns:
            (raw_score, normalized_score, classification, is_anomaly)
        """
        clean_addr = wallet_address.strip()
        if not txs or len(txs) == 0:
            return 0.0, 0.0, "NORMAL", False

        feats = extract_features(txs, clean_addr)
        feature_vector = np.array([[
            feats["transaction_count"],
            feats["average_transaction_amount"],
            feats["incoming_count"],
            feats["outgoing_count"],
            feats["unique_counterparties"],
            feats["transaction_frequency"],
            feats["amount_variance"],
        ]])

        training_data = np.vstack([BASELINE_CORPUS, feature_vector])
        clf = IsolationForest(
            n_estimators=self.model_info.n_estimators,
            contamination=self.model_info.contamination,
            random_state=self.random_seed
        )
        clf.fit(training_data)

        raw_score = float(clf.decision_function(feature_vector)[0])
        normalized_score = round(float(np.clip(50.0 - (raw_score * 125.0), 5.0, 95.0)), 1)

        if normalized_score < 35.0:
            classification = "NORMAL"
        elif normalized_score < 55.0:
            classification = "LOW ANOMALY"
        elif normalized_score < 75.0:
            classification = "MEDIUM ANOMALY"
        else:
            classification = "HIGH ANOMALY"

        is_anomaly = classification != "NORMAL"
        return raw_score, normalized_score, classification, is_anomaly

    def analyze_wallet(
        self,
        db: Session,
        wallet_address: str,
        txs: List[TransactionResponse],
        case_id: Optional[str] = None
    ) -> MLAnalysisResponse:
        """
        Executes the 5-step ML pipeline:
        1. Check data sufficiency
        2. Extract 7 features
        3. Run IsolationForest scoring
        4. Classify anomaly level (NORMAL, LOW, MEDIUM, HIGH)
        5. Generate human-readable explanation and persist to DB
        """
        clean_addr = wallet_address.strip()
        now_dt = datetime.now(timezone.utc)

        # -----------------------------------------------------------------
        # STEP 1: Check Data Sufficiency
        # -----------------------------------------------------------------
        if not txs or len(txs) == 0:
            return MLAnalysisResponse(
                id=str(uuid.uuid4()),
                wallet_address=clean_addr,
                case_id=case_id,
                raw_anomaly_score=0.0,
                normalized_score=0.0,
                classification="NORMAL",
                is_anomaly=False,
                features_used={cfg["name"]: 0.0 for cfg in FEATURE_CONFIG},
                feature_breakdown=[
                    FeatureItem(
                        name=cfg["name"],
                        label=cfg["label"],
                        value=0.0,
                        baseline_median=cfg["baseline_median"],
                        deviation_ratio=0.0,
                        description=cfg["description"]
                    )
                    for cfg in FEATURE_CONFIG
                ],
                explanation=INSUFFICIENT_DATA_MSG,
                model_info=self.model_info,
                evaluation_notes="Insufficient transaction data for anomaly analysis. At least 1 transaction is required.",
                disclaimer=DISCLAIMER_TEXT,
                analysis_timestamp=now_dt,
                data_source="Public Bitcoin Blockchain (Zero History)"
            )

        # -----------------------------------------------------------------
        # STEP 2: Feature Extraction (7 Features)
        # -----------------------------------------------------------------
        feats = extract_features(txs, clean_addr)
        feature_vector = np.array([[
            feats["transaction_count"],
            feats["average_transaction_amount"],
            feats["incoming_count"],
            feats["outgoing_count"],
            feats["unique_counterparties"],
            feats["transaction_frequency"],
            feats["amount_variance"],
        ]])

        # -----------------------------------------------------------------
        # STEP 3: Isolation Forest Scoring
        # -----------------------------------------------------------------
        # Train IsolationForest on baseline corpus combined with observed sample
        training_data = np.vstack([BASELINE_CORPUS, feature_vector])
        clf = IsolationForest(
            n_estimators=self.model_info.n_estimators,
            contamination=self.model_info.contamination,
            random_state=self.random_seed
        )
        clf.fit(training_data)

        # Decision function: negative values indicate outliers
        raw_score = float(clf.decision_function(feature_vector)[0])

        # Map raw score to 0.0 - 100.0 scale:
        # High raw score (+0.2) -> Low anomaly (~25.0)
        # Low/negative raw score (-0.2) -> High anomaly (~75.0)
        normalized_score = round(float(np.clip(50.0 - (raw_score * 125.0), 5.0, 95.0)), 1)

        # -----------------------------------------------------------------
        # STEP 4: Classify Anomaly Level
        # -----------------------------------------------------------------
        if normalized_score < 35.0:
            classification = "NORMAL"
        elif normalized_score < 55.0:
            classification = "LOW ANOMALY"
        elif normalized_score < 75.0:
            classification = "MEDIUM ANOMALY"
        else:
            classification = "HIGH ANOMALY"

        is_anomaly = classification != "NORMAL"

        # -----------------------------------------------------------------
        # STEP 5: Explanations and Breakdown
        # -----------------------------------------------------------------
        explanation_text = generate_simple_explanations(feats)

        feature_breakdown: List[FeatureItem] = []
        for cfg in FEATURE_CONFIG:
            val = feats[cfg["name"]]
            base_med = cfg["baseline_median"]
            dev_ratio = round(val / base_med, 2) if base_med > 0 else 1.0
            feature_breakdown.append(FeatureItem(
                name=cfg["name"],
                label=cfg["label"],
                value=val,
                baseline_median=base_med,
                deviation_ratio=dev_ratio,
                description=cfg["description"]
            ))

        # Persist to database
        scan_id = str(uuid.uuid4())
        try:
            # Look up wallet ID if exists
            wallet_record = db.query(Wallet).filter(Wallet.address == clean_addr).first()
            wallet_id = wallet_record.id if wallet_record else None

            db_analysis = MLAnalysis(
                id=scan_id,
                case_id=case_id,
                wallet_id=wallet_id,
                wallet_address=clean_addr,
                model_name=self.model_info.model_name,
                model_version=self.model_info.model_version,
                raw_anomaly_score=raw_score,
                normalized_score=normalized_score,
                classification=classification,
                is_anomaly=is_anomaly,
                features_used=feats,
                feature_contributions={item.name: item.deviation_ratio for item in feature_breakdown},
                explanation=explanation_text
            )
            db.add(db_analysis)
            db.commit()
        except Exception as e:
            logger.warning(f"Could not persist ML analysis to DB: {e}")
            db.rollback()

        is_synthetic = any("synthetic" in (t.data_source or "").lower() or "demo" in (t.txid or "").lower() for t in txs)
        src_label = "DEMONSTRATION DATA — SYNTHETIC" if is_synthetic else "Public Bitcoin Blockchain Ledger"

        return MLAnalysisResponse(
            id=scan_id,
            wallet_address=clean_addr,
            case_id=case_id,
            raw_anomaly_score=round(raw_score, 4),
            normalized_score=normalized_score,
            classification=classification,
            is_anomaly=is_anomaly,
            features_used=feats,
            feature_breakdown=feature_breakdown,
            explanation=explanation_text,
            model_info=self.model_info,
            evaluation_notes=f"Anomaly evaluation completed across {len(txs)} transactions.",
            disclaimer=DISCLAIMER_TEXT,
            analysis_timestamp=now_dt,
            data_source=src_label
        )

    def get_analysis_history(
        self,
        db: Session,
        wallet_address: str,
        limit: int = 10
    ) -> List[MLAnalysisHistoryItem]:
        """Retrieves past ML anomaly scans for a wallet from SQLite."""
        clean_addr = wallet_address.strip()
        records = db.query(MLAnalysis).filter(
            MLAnalysis.wallet_address == clean_addr
        ).order_by(MLAnalysis.created_at.desc()).limit(limit).all()
        return [MLAnalysisHistoryItem.model_validate(r) for r in records]

    def get_model_info(self) -> ModelInfo:
        """Returns the public specifications of the Isolation Forest model."""
        return self.model_info


ml_anomaly_service = MLAnomalyService(random_seed=42)
