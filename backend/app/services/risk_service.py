"""
Simplified Transparent Risk Scoring Engine
Designed for undergraduate cybersecurity investigations.

Implements a transparent 0-100 investigative risk score using ONLY 5 observable indicators:
1. High transaction frequency (0-20 pts)
2. High transaction amount variation (0-15 pts)
3. Large number of counterparties (0-20 pts)
4. Rapid movement of funds (0-20 pts)
5. ML anomaly result (0-25 pts)

Total Score = Sum of 5 indicators (0-100 pts).

Risk Levels:
  0–29   = LOW
  30–59  = MEDIUM
  60–79  = HIGH
  80–100 = CRITICAL

IMPORTANT FORENSIC NOTICE:
The risk score is NOT proof of ransomware activity.
It is an investigative prioritization indicator.
"This wallet exhibits transaction behaviour that warrants further investigation."
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.schemas.wallet import TransactionResponse
from backend.app.schemas.risk import (
    RuleContribution,
    MLContribution,
    RiskWeights,
    RiskAssessmentResponse,
    RiskAssessmentHistoryItem,
)
from backend.app.models.analysis import RiskAssessment
from backend.app.services.analytics_service import (
    calculate_unique_counterparties,
    calculate_average_time_between_tx_hours,
)
from backend.app.services.ml_service import MLAnomalyService

logger = logging.getLogger(__name__)

# =============================================================================
# TRANSPARENT RISK SCORING WEIGHTS (SUM = 100.0 POINTS)
# =============================================================================
WEIGHT_TX_FREQUENCY: float = 20.0       # Indicator 1: High transaction frequency
WEIGHT_AMOUNT_VARIATION: float = 15.0   # Indicator 2: High transaction amount variation
WEIGHT_COUNTERPARTIES: float = 20.0     # Indicator 3: Large number of counterparties
WEIGHT_RAPID_MOVEMENT: float = 20.0     # Indicator 4: Rapid movement of funds
WEIGHT_ML_ANOMALY: float = 25.0         # Indicator 5: ML anomaly result (Isolation Forest)

TOTAL_WEIGHT: float = (
    WEIGHT_TX_FREQUENCY
    + WEIGHT_AMOUNT_VARIATION
    + WEIGHT_COUNTERPARTIES
    + WEIGHT_RAPID_MOVEMENT
    + WEIGHT_ML_ANOMALY
)

DISCLAIMER_TEXT: str = (
    "The risk score is an investigative prioritization indicator, NOT proof of ransomware activity. "
    "This wallet exhibits transaction behaviour that warrants further investigation."
)


# =============================================================================
# RISK LEVEL CLASSIFICATION (0-29 LOW, 30-59 MEDIUM, 60-79 HIGH, 80-100 CRITICAL)
# =============================================================================
def determine_risk_level(score: float) -> str:
    """
    Classifies a 0-100 risk score into transparent operational tiers:
      0–29   = LOW
      30–59  = MEDIUM
      60–79  = HIGH
      80–100 = CRITICAL
    """
    if score <= 29.99:
        return "LOW"
    elif score <= 59.99:
        return "MEDIUM"
    elif score <= 79.99:
        return "HIGH"
    else:
        return "CRITICAL"


# =============================================================================
# STANDALONE SIMPLIFIED RISK SCORE CALCULATION
# =============================================================================
def calculate_simple_risk_score(
    txs: List[TransactionResponse],
    target_address: str = "",
    include_ml: bool = True,
    ml_score_override: Optional[float] = None,
    ml_service: Optional[MLAnomalyService] = None,
) -> Dict[str, Any]:
    """
    Calculates the 0-100 investigative risk score using the 5 observable indicators.

    Returns:
        {
            "risk_score": float,
            "risk_level": str,
            "risk_factors": List[str],
            "indicator_breakdown": Dict[str, float],
            "rule_contributions": List[RuleContribution],
            "ml_contribution": MLContribution,
            "disclaimer": str,
        }
    """
    risk_factors: List[str] = []
    rule_contributions: List[RuleContribution] = []

    tx_count = len(txs)

    # -------------------------------------------------------------------------
    # Indicator 1: High transaction frequency (Max 20 pts)
    # -------------------------------------------------------------------------
    tx_freq_score = 0.0
    tx_freq_triggered = False

    if tx_count >= 15:
        tx_freq_score = 20.0
        tx_freq_triggered = True
        risk_factors.append("High transaction frequency")
    elif tx_count >= 8:
        tx_freq_score = 12.0
        tx_freq_triggered = True
        risk_factors.append("High transaction frequency")
    elif tx_count >= 3:
        tx_freq_score = 6.0
        tx_freq_triggered = True
        risk_factors.append("High transaction frequency")

    rule_contributions.append(RuleContribution(
        rule_id="RULE_TX_FREQUENCY",
        rule_name="High Transaction Frequency",
        category="Frequency",
        score_contribution=tx_freq_score,
        max_score=WEIGHT_TX_FREQUENCY,
        triggered=tx_freq_triggered,
        observed_value=f"{tx_count} transactions",
        threshold=">= 3 transactions",
        description="Wallet exhibits elevated transaction volume compared to normal dormant personal addresses."
    ))

    # -------------------------------------------------------------------------
    # Indicator 2: High transaction amount variation (Max 15 pts)
    # -------------------------------------------------------------------------
    amounts_btc = [abs(tx.net_value_btc) for tx in txs if abs(tx.net_value_btc) > 0]
    amount_var_score = 0.0
    amount_var_triggered = False
    variance_btc = 0.0

    if len(amounts_btc) >= 2:
        mean_btc = sum(amounts_btc) / len(amounts_btc)
        variance_btc = sum((x - mean_btc) ** 2 for x in amounts_btc) / len(amounts_btc)

        if variance_btc >= 1.0:
            amount_var_score = 15.0
            amount_var_triggered = True
            risk_factors.append("High transaction amount variation")
        elif variance_btc >= 0.1:
            amount_var_score = 8.0
            amount_var_triggered = True
            risk_factors.append("High transaction amount variation")

    rule_contributions.append(RuleContribution(
        rule_id="RULE_AMOUNT_VARIATION",
        rule_name="High Transaction Amount Variation",
        category="Variance",
        score_contribution=amount_var_score,
        max_score=WEIGHT_AMOUNT_VARIATION,
        triggered=amount_var_triggered,
        observed_value=f"Variance: {variance_btc:.3f} BTC²" if len(amounts_btc) >= 2 else "0.000 BTC² (N/A)",
        threshold="Variance >= 0.100 BTC²",
        description="Significant dispersion in transaction amounts suggests irregular payment dispersion."
    ))

    # -------------------------------------------------------------------------
    # Indicator 3: Large number of counterparties (Max 20 pts)
    # -------------------------------------------------------------------------
    cp_data = calculate_unique_counterparties(txs, target_address) if tx_count > 0 else {"count": 0}
    cp_count = cp_data["count"]
    cp_score = 0.0
    cp_triggered = False

    if cp_count >= 10:
        cp_score = 20.0
        cp_triggered = True
        risk_factors.append("Large number of counterparties")
    elif cp_count >= 5:
        cp_score = 12.0
        cp_triggered = True
        risk_factors.append("Large number of counterparties")
    elif cp_count >= 2:
        cp_score = 6.0
        cp_triggered = True
        risk_factors.append("Large number of counterparties")

    rule_contributions.append(RuleContribution(
        rule_id="RULE_COUNTERPARTIES",
        rule_name="Large Number of Counterparties",
        category="Network",
        score_contribution=cp_score,
        max_score=WEIGHT_COUNTERPARTIES,
        triggered=cp_triggered,
        observed_value=f"{cp_count} counterparties",
        threshold=">= 2 unique counterparties",
        description="Interactions across numerous external counterparties indicate fund dispersal or collection."
    ))

    # -------------------------------------------------------------------------
    # Indicator 4: Rapid movement of funds (Max 20 pts)
    # -------------------------------------------------------------------------
    avg_interval_hours = calculate_average_time_between_tx_hours(txs) if tx_count >= 2 else 0.0
    rapid_score = 0.0
    rapid_triggered = False

    if tx_count >= 2 and avg_interval_hours > 0:
        if avg_interval_hours <= 1.0:
            rapid_score = 20.0
            rapid_triggered = True
            risk_factors.append("Rapid movement of funds")
        elif avg_interval_hours <= 6.0:
            rapid_score = 12.0
            rapid_triggered = True
            risk_factors.append("Rapid movement of funds")
        elif avg_interval_hours <= 24.0:
            rapid_score = 6.0
            rapid_triggered = True
            risk_factors.append("Rapid movement of funds")

    rule_contributions.append(RuleContribution(
        rule_id="RULE_RAPID_MOVEMENT",
        rule_name="Rapid Movement of Funds",
        category="Velocity",
        score_contribution=rapid_score,
        max_score=WEIGHT_RAPID_MOVEMENT,
        triggered=rapid_triggered,
        observed_value=f"{avg_interval_hours:.1f} hrs between txs" if tx_count >= 2 else "N/A (<2 txs)",
        threshold="<= 24.0 hrs between transactions",
        description="Transactions occurring in rapid succession within short time windows indicate fast fund routing."
    ))

    behavioral_points = tx_freq_score + amount_var_score + cp_score + rapid_score

    # -------------------------------------------------------------------------
    # Indicator 5: ML anomaly result (Max 25 pts)
    # -------------------------------------------------------------------------
    ml_available = False
    ml_anomaly_score = 0.0
    ml_normalized = 0.0
    ml_class = "NORMAL"
    ml_is_anomaly = False
    raw_anomaly = None

    if ml_score_override is not None:
        # Override for testing or mocking
        ml_available = True
        ml_normalized = float(min(100.0, max(0.0, ml_score_override)))
        raw_anomaly = round(0.16 - (ml_normalized / 100.0 * 0.40), 4)
        ml_class = (
            "HIGH ANOMALY" if ml_normalized > 75
            else ("MEDIUM ANOMALY" if ml_normalized > 55
            else ("LOW ANOMALY" if ml_normalized > 30 else "NORMAL"))
        )
        ml_is_anomaly = ml_normalized > 55.0
        ml_anomaly_score = round((ml_normalized / 100.0) * WEIGHT_ML_ANOMALY, 1)
        if ml_normalized >= 50.0:
            risk_factors.append("High anomaly score")
    elif include_ml and tx_count > 0:
        if ml_service is None:
            ml_service = MLAnomalyService(random_seed=42)
        try:
            raw_s, norm_s, classification, is_anom = ml_service.score_wallet(txs=txs, wallet_address=target_address)
            ml_available = True
            raw_anomaly = round(raw_s, 4)
            ml_normalized = norm_s
            ml_class = classification
            ml_is_anomaly = is_anom
            ml_anomaly_score = round((norm_s / 100.0) * WEIGHT_ML_ANOMALY, 1)

            if norm_s >= 50.0 or is_anom:
                risk_factors.append("High anomaly score")
        except Exception as e:
            logger.warning(f"ML anomaly evaluation bypassed gracefully: {e}")
            ml_available = False

    # -------------------------------------------------------------------------
    # Final Score Calculation
    # -------------------------------------------------------------------------
    if include_ml and ml_available:
        final_score = round(behavioral_points + ml_anomaly_score, 1)
        rule_score_normalized = round((behavioral_points / 75.0) * 100.0, 1)
        rule_weight = 0.75
        ml_weight = 0.25
    else:
        # When ML is disabled or unavailable, normalize behavioral rules to 100
        final_score = round((behavioral_points / 75.0) * 100.0, 1) if behavioral_points > 0 else 0.0
        rule_score_normalized = final_score
        rule_weight = 1.0
        ml_weight = 0.0

    final_score = float(min(100.0, max(0.0, final_score)))
    risk_level = determine_risk_level(final_score)

    ml_contribution = MLContribution(
        available=ml_available,
        raw_anomaly_score=raw_anomaly,
        normalized_score=ml_normalized if ml_available else None,
        classification=ml_class if ml_available else None,
        is_anomaly=ml_is_anomaly if ml_available else None,
        weight=ml_weight,
    )

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "rule_score": rule_score_normalized,
        "ml_score": ml_normalized if ml_available else None,
        "rule_weight": rule_weight,
        "ml_weight": ml_weight,
        "indicator_breakdown": {
            "tx_frequency_score": tx_freq_score,
            "amount_variation_score": amount_var_score,
            "counterparties_score": cp_score,
            "rapid_movement_score": rapid_score,
            "ml_anomaly_score": ml_anomaly_score,
        },
        "rule_contributions": rule_contributions,
        "ml_contribution": ml_contribution,
        "disclaimer": DISCLAIMER_TEXT,
    }


# =============================================================================
# RISK SCORING SERVICE CLASS (FOR API ROUTER AND DB PERSISTENCE)
# =============================================================================
class RiskScoringService:
    """
    Transparent, beginner-friendly forensic risk scoring service.
    Connects simple 0-100 investigative risk scoring to SQLite and existing UI.
    """

    def __init__(self, rule_weight: float = 0.75, ml_weight: float = 0.25):
        self.ml_service = MLAnomalyService(random_seed=42)
        self.rule_weight = rule_weight
        self.ml_weight = ml_weight

    @staticmethod
    def determine_risk_level(score: float) -> str:
        return determine_risk_level(score)

    def assess_wallet(
        self,
        db: Session,
        wallet_address: str,
        txs: List[TransactionResponse],
        case_id: Optional[str] = None,
        wallet_id: Optional[str] = None,
        include_ml: bool = True,
        ml_score_override: Optional[float] = None,
    ) -> RiskAssessmentResponse:
        """
        Executes transparent 0-100 investigative risk assessment.
        Saves result to SQLite/PostgreSQL database for forensic audit history.
        """
        clean_addr = wallet_address.strip()

        calc = calculate_simple_risk_score(
            txs=txs,
            target_address=clean_addr,
            include_ml=include_ml,
            ml_score_override=ml_score_override,
            ml_service=self.ml_service,
        )

        final_score = calc["risk_score"]
        risk_level = calc["risk_level"]
        risk_factors = calc["risk_factors"]
        rule_score = calc["rule_score"]
        ml_score = calc["ml_score"]
        rule_contributions = calc["rule_contributions"]
        ml_contribution = calc["ml_contribution"]

        # User-facing reasons: use risk_factors or explain normal behavior
        if risk_factors:
            reasons = list(risk_factors)
        else:
            reasons = ["Transaction behaviour is within normal observable boundaries."]

        weights = RiskWeights(
            rule_weight=calc["rule_weight"],
            ml_weight=calc["ml_weight"]
        )

        assessment_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Persist record in database
        db_record = RiskAssessment(
            id=assessment_id,
            case_id=case_id,
            wallet_id=wallet_id,
            wallet_address=clean_addr,
            risk_score=final_score,
            risk_tier=risk_level,
            heuristics_summary={
                "rule_score": rule_score,
                "ml_score": ml_score,
                "weights": weights.model_dump(),
                "rule_contributions": [r.model_dump() for r in rule_contributions],
                "ml_contribution": ml_contribution.model_dump(),
                "reasons": reasons,
                "risk_factors": risk_factors,
                "indicator_breakdown": calc["indicator_breakdown"],
            },
            disclaimer=DISCLAIMER_TEXT,
            assessed_by="Transparent 5-Indicator Risk Engine",
            created_at=now,
            updated_at=now,
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        return RiskAssessmentResponse(
            id=db_record.id,
            wallet_address=clean_addr,
            case_id=case_id,
            final_score=final_score,
            risk_score=final_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            rule_score=rule_score,
            ml_score=ml_score,
            weights=weights,
            rule_contributions=rule_contributions,
            ml_contribution=ml_contribution,
            reasons=reasons,
            disclaimer=DISCLAIMER_TEXT,
            assessed_by=db_record.assessed_by,
            assessed_at=now,
            data_source="Public Bitcoin Blockchain & Transparent Forensics",
        )

    def get_history(
        self,
        db: Session,
        wallet_address: str,
        limit: int = 10,
    ) -> List[RiskAssessmentHistoryItem]:
        """
        Retrieves historical risk assessments recorded for this wallet address.
        """
        records = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.wallet_address == wallet_address)
            .order_by(RiskAssessment.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            RiskAssessmentHistoryItem(
                id=r.id,
                wallet_address=r.wallet_address or wallet_address,
                case_id=r.case_id,
                risk_score=round(r.risk_score, 1),
                risk_tier=r.risk_tier,
                heuristics_summary=r.heuristics_summary,
                disclaimer=r.disclaimer,
                assessed_by=r.assessed_by,
                created_at=r.created_at,
            )
            for r in records
        ]
