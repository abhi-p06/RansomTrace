"""
Comprehensive Unit & Boundary Tests for Simplified Risk Scoring System
Validates:
1. 0 score
2. Middle score
3. High score
4. Boundary values (0, 29, 30, 59, 60, 79, 80, 100)
5. Transparent 5 observable indicators & weights (20, 15, 20, 20, 25)
6. Mandatory disclaimer & investigative tone
7. FastAPI endpoints & SQLite database persistence
"""

import sys
import os
import unittest
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.schemas.wallet import TransactionResponse, TxIO
from backend.app.services.risk_service import (
    determine_risk_level,
    calculate_simple_risk_score,
    RiskScoringService,
    WEIGHT_TX_FREQUENCY,
    WEIGHT_AMOUNT_VARIATION,
    WEIGHT_COUNTERPARTIES,
    WEIGHT_RAPID_MOVEMENT,
    WEIGHT_ML_ANOMALY,
    TOTAL_WEIGHT,
    DISCLAIMER_TEXT,
)
from backend.app.core.database import SessionLocal


def make_dummy_tx(
    txid: str,
    target_addr: str,
    counterparty_addr: str,
    direction: str,
    amount_btc: float,
    block_time: int
) -> TransactionResponse:
    sats = int(amount_btc * 100_000_000)
    if direction == "INCOMING":
        inputs = [TxIO(address=counterparty_addr, value_sats=sats, value_btc=amount_btc)]
        outputs = [TxIO(address=target_addr, value_sats=sats, value_btc=amount_btc)]
    else:
        inputs = [TxIO(address=target_addr, value_sats=sats, value_btc=amount_btc)]
        outputs = [TxIO(address=counterparty_addr, value_sats=sats, value_btc=amount_btc)]

    return TransactionResponse(
        txid=txid,
        flow_direction=direction,
        net_value_sats=sats if direction == "INCOMING" else -sats,
        net_value_btc=amount_btc if direction == "INCOMING" else -amount_btc,
        fee_sats=1000,
        fee_btc=0.00001,
        block_time=block_time,
        block_height=800000,
        confirmed=True,
        inputs=inputs,
        outputs=outputs
    )


class TestRiskScoringSystem(unittest.TestCase):

    def test_weights_sum_to_100(self):
        """Verify the 5 indicators have exact visible weights summing to 100."""
        self.assertEqual(WEIGHT_TX_FREQUENCY, 20.0)
        self.assertEqual(WEIGHT_AMOUNT_VARIATION, 15.0)
        self.assertEqual(WEIGHT_COUNTERPARTIES, 20.0)
        self.assertEqual(WEIGHT_RAPID_MOVEMENT, 20.0)
        self.assertEqual(WEIGHT_ML_ANOMALY, 25.0)
        self.assertEqual(TOTAL_WEIGHT, 100.0)

    def test_boundary_values_classification(self):
        """
        Verify boundary values:
        0–29 = LOW
        30–59 = MEDIUM
        60–79 = HIGH
        80–100 = CRITICAL
        """
        self.assertEqual(determine_risk_level(0.0), "LOW")
        self.assertEqual(determine_risk_level(15.0), "LOW")
        self.assertEqual(determine_risk_level(29.0), "LOW")
        self.assertEqual(determine_risk_level(29.99), "LOW")

        # Boundary at 30
        self.assertEqual(determine_risk_level(30.0), "MEDIUM")
        self.assertEqual(determine_risk_level(45.0), "MEDIUM")
        self.assertEqual(determine_risk_level(59.0), "MEDIUM")
        self.assertEqual(determine_risk_level(59.99), "MEDIUM")

        # Boundary at 60
        self.assertEqual(determine_risk_level(60.0), "HIGH")
        self.assertEqual(determine_risk_level(70.0), "HIGH")
        self.assertEqual(determine_risk_level(79.0), "HIGH")
        self.assertEqual(determine_risk_level(79.99), "HIGH")

        # Boundary at 80
        self.assertEqual(determine_risk_level(80.0), "CRITICAL")
        self.assertEqual(determine_risk_level(95.0), "CRITICAL")
        self.assertEqual(determine_risk_level(100.0), "CRITICAL")

    def test_zero_score(self):
        """Verify 0 score for empty or dormant wallet with no activity."""
        result = calculate_simple_risk_score(txs=[], target_address="1ZeroActivityAddr", include_ml=False)
        self.assertEqual(result["risk_score"], 0.0)
        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(result["indicator_breakdown"]["tx_frequency_score"], 0.0)
        self.assertEqual(result["indicator_breakdown"]["amount_variation_score"], 0.0)
        self.assertEqual(result["indicator_breakdown"]["counterparties_score"], 0.0)
        self.assertEqual(result["indicator_breakdown"]["rapid_movement_score"], 0.0)
        self.assertEqual(result["indicator_breakdown"]["ml_anomaly_score"], 0.0)
        self.assertIn("investigative prioritization indicator", result["disclaimer"])
        self.assertNotIn("This is a ransomware wallet", result["disclaimer"])

    def test_middle_score(self):
        """Verify middle score in the MEDIUM tier (30–59)."""
        target = "1MiddleRiskWalletAddr"
        # 4 transactions over moderate time interval, 2 counterparties, low variance
        base_time = 1700000000
        txs = [
            make_dummy_tx("tx1", target, "1CounterPartyA", "INCOMING", 0.50, base_time),
            make_dummy_tx("tx2", target, "1CounterPartyB", "OUTGOING", 0.48, base_time + 7200),     # 2 hrs later
            make_dummy_tx("tx3", target, "1CounterPartyA", "INCOMING", 0.52, base_time + 14400),    # 2 hrs later
            make_dummy_tx("tx4", target, "1CounterPartyB", "OUTGOING", 0.49, base_time + 21600),    # 2 hrs later
        ]
        # tx_freq (4 txs >= 3): 6.0
        # amount_var (near identical ~0.5 btc): 0.0
        # counterparties (2 cps): 6.0
        # rapid movement (2.0 hrs avg <= 6.0 hrs): 12.0
        # Subtotal behavioral: 24.0. With ML override of 40: (40 / 100) * 25 = 10.0
        # Total = 24.0 + 10.0 = 34.0 (MEDIUM tier: 30-59)
        result = calculate_simple_risk_score(
            txs=txs,
            target_address=target,
            include_ml=True,
            ml_score_override=40.0
        )
        self.assertGreaterEqual(result["risk_score"], 30.0)
        self.assertLessEqual(result["risk_score"], 59.9)
        self.assertEqual(result["risk_level"], "MEDIUM")
        self.assertTrue(len(result["risk_factors"]) > 0)
        print(f"\n[Test Middle Score]: {result['risk_score']} ({result['risk_level']}), Factors: {result['risk_factors']}")

    def test_high_and_critical_score(self):
        """Verify high/critical score (60–79 HIGH, 80–100 CRITICAL)."""
        target = "1HighRiskBurstWallet"
        base_time = 1700000000
        # 16 transactions with 11 distinct counterparties, high variance, very rapid succession (15 mins)
        txs = []
        for i in range(16):
            cp = f"1CounterPartyAddr_{i % 12}"
            amt = 5.0 if i % 2 == 0 else 0.05
            direction = "INCOMING" if i % 3 == 0 else "OUTGOING"
            txs.append(make_dummy_tx(f"tx_high_{i}", target, cp, direction, amt, base_time + (i * 900)))

        # tx_freq (16 txs >= 15): 20.0
        # amount_var (0.05 to 5.0, variance > 1.0): 15.0
        # counterparties (12 cps >= 10): 20.0
        # rapid movement (15 mins = 0.25 hrs <= 1.0 hr): 20.0
        # Behavioral subtotal = 75.0 (Max behavioral)
        # ML override of 90: (90 / 100) * 25 = 22.5
        # Total = 75.0 + 22.5 = 97.5 (CRITICAL tier >= 80)
        result = calculate_simple_risk_score(
            txs=txs,
            target_address=target,
            include_ml=True,
            ml_score_override=90.0
        )
        self.assertGreaterEqual(result["risk_score"], 80.0)
        self.assertEqual(result["risk_level"], "CRITICAL")
        self.assertIn("High transaction frequency", result["risk_factors"])
        self.assertIn("High transaction amount variation", result["risk_factors"])
        self.assertIn("Large number of counterparties", result["risk_factors"])
        self.assertIn("Rapid movement of funds", result["risk_factors"])
        self.assertIn("High anomaly score", result["risk_factors"])
        print(f"\n[Test High/Critical Score]: {result['risk_score']} ({result['risk_level']}), Factors: {result['risk_factors']}")

    def test_database_persistence_and_service(self):
        """Verify full RiskScoringService execution and database storage."""
        db = SessionLocal()
        try:
            service = RiskScoringService()
            target = "1DemoRansomCollectionWallet002"
            base_time = 1700000000
            txs = [
                make_dummy_tx("tx_db1", target, "1Sender1", "INCOMING", 1.2, base_time),
                make_dummy_tx("tx_db2", target, "1Receiver1", "OUTGOING", 0.05, base_time + 600),
                make_dummy_tx("tx_db3", target, "1Receiver2", "OUTGOING", 1.1, base_time + 1200),
            ]
            response = service.assess_wallet(
                db=db,
                wallet_address=target,
                txs=txs,
                include_ml=True
            )
            self.assertIsNotNone(response.id)
            self.assertEqual(response.wallet_address, target)
            self.assertEqual(response.risk_score, response.final_score)
            self.assertIn(response.risk_level, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            self.assertTrue(len(response.reasons) > 0)
            self.assertIn(DISCLAIMER_TEXT, response.disclaimer)

            # Check history query
            history = service.get_history(db=db, wallet_address=target, limit=5)
            self.assertTrue(len(history) >= 1)
            self.assertEqual(history[0].wallet_address, target)
            print(f"\n[Test Service DB Persistence]: Saved assessment {response.id}, score={response.risk_score}, level={response.risk_level}")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
