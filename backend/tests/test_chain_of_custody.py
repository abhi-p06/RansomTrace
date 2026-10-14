"""
Comprehensive Unit & Lifecycle Tests for Chain of Custody System
Validates:
1. Complete forensic evidence lifecycle:
   - COLLECTED
   - HASHED
   - STORED
   - REVIEWED
   - VERIFIED
   - EXPORTED
2. Each entry contains:
   - evidence_id
   - action
   - timestamp
   - actor
   - notes
3. Chronological timeline ordering.
4. Prevention of editing past entries (immutability / append-only).
5. Mandatory academic disclaimer:
   'This is an academic demonstration of chain-of-custody principles and does not replace formal legal evidence procedures.'
6. FastAPI endpoints & SQLite database persistence.
"""

import sys
import os
import unittest
import httpx
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import SessionLocal
from backend.app.models.evidence import Evidence
from backend.app.models.custody import ChainOfCustodyEntry
from backend.app.models.case import InvestigationCase
from backend.app.services.evidence_service import (
    preserve_evidence_record,
    evidence_service,
    CUSTODY_DISCLAIMER,
)
from backend.app.schemas.evidence import VALID_CUSTODY_ACTIONS


class TestChainOfCustodySystem(unittest.TestCase):

    def setUp(self):
        self.db = SessionLocal()
        case = self.db.query(InvestigationCase).first()
        if not case:
            case = InvestigationCase(
                id="CASE-COC-TEST-001",
                case_id="RT-2026-COC-TEST",
                title="Chain of Custody Test Case",
                description="Test case for CoC lifecycle verification",
                status="OPEN"
            )
            self.db.add(case)
            self.db.commit()
            self.db.refresh(case)
        self.case_id = case.id
        self.client = httpx.Client(base_url="http://localhost:8000")

    def tearDown(self):
        self.db.close()
        self.client.close()

    def test_complete_evidence_lifecycle(self):
        """
        Tests the entire forensic lifecycle:
        1. COLLECTED (seized from blockchain)
        2. HASHED (cryptographic SHA-256 fingerprint generated)
        3. STORED (preserved in digital evidence vault)
        4. REVIEWED (examined by digital forensics examiner)
        5. VERIFIED (integrity checked against stored SHA-256 hash)
        6. EXPORTED (exported for judicial court filing)
        """
        # Step 1-3: Preserve evidence (automatically triggers COLLECTED, HASHED, STORED)
        ev_record = preserve_evidence_record(
            case_id=self.case_id,
            transaction_id="coc_tx_lifecycle_001_002_003_004_005_006_007_008_009_010_011_012",
            wallet_address="1DemoRansomCollectionWallet002",
            amount=3.50,
            timestamp="2026-10-06T10:00:00Z",
            source="Public Bitcoin Blockchain / Mempool API",
            collector="Detective Vance",
            description="Lifecycle digital artifact",
            db=self.db,
        )
        evidence_id = ev_record["evidence_id"]

        # Step 4: Examiner reviews the evidence
        review_entry = evidence_service.append_custody_action(
            db=self.db,
            evidence_id=evidence_id,
            action="REVIEWED",
            actor="Senior Forensic Examiner Davis",
            notes="Analyzed peel-chain pattern and corroborated incoming ransom addresses."
        )
        self.assertEqual(review_entry.action, "REVIEWED")
        self.assertEqual(review_entry.actor, "Senior Forensic Examiner Davis")
        self.assertEqual(review_entry.evidence_id, evidence_id)
        self.assertEqual(review_entry.disclaimer, CUSTODY_DISCLAIMER)

        # Step 5: Examiner cryptographically verifies the evidence
        verify_result = evidence_service.verify_evidence_integrity(
            db=self.db,
            evidence_id=evidence_id,
            actor_name="Automated Forensics Auditor"
        )
        self.assertEqual(verify_result.status, "INTEGRITY VERIFIED")

        # Step 6: Investigator exports evidence for prosecution
        export_entry = evidence_service.append_custody_action(
            db=self.db,
            evidence_id=evidence_id,
            action="EXPORTED",
            actor="Prosecutor Reynolds",
            notes="Sealed PDF report and JSON dossier generated for judicial filing."
        )
        self.assertEqual(export_entry.action, "EXPORTED")
        self.assertEqual(export_entry.actor, "Prosecutor Reynolds")

        # Query full chronological timeline
        timeline = evidence_service.get_custody_timeline(db=self.db, evidence_id=evidence_id)

        # Verify all 6 canonical actions exist in the timeline
        actions_present = [e.action for e in timeline]
        expected_actions = ["COLLECTED", "HASHED", "STORED", "REVIEWED", "VERIFIED", "EXPORTED"]

        for expected in expected_actions:
            self.assertIn(expected, actions_present, f"Action '{expected}' missing from custody lifecycle!")

        # Verify entry content: evidence_id, action, timestamp, actor, notes, disclaimer
        for entry in timeline:
            self.assertEqual(entry.evidence_id, evidence_id)
            self.assertIn(entry.action, VALID_CUSTODY_ACTIONS)
            self.assertIsNotNone(entry.timestamp)
            self.assertTrue(len(entry.actor) > 0)
            self.assertIsNotNone(entry.notes)
            self.assertEqual(entry.disclaimer, CUSTODY_DISCLAIMER)

        # Verify chronological ordering (each timestamp >= previous timestamp)
        timestamps = [e.timestamp for e in timeline]
        for i in range(len(timestamps) - 1):
            self.assertLessEqual(timestamps[i], timestamps[i + 1], "Custody entries must be in chronological order!")

        print("\n[Lifecycle Test Passed]: All 6 actions recorded in chronological sequence:")
        for idx, e in enumerate(timeline, 1):
            print(f"  #{idx} [{e.action}] by {e.actor} at {e.timestamp.isoformat()} — {e.notes}")

    def test_immutability_enforcement_prevents_edits(self):
        """
        Verifies that normal users cannot edit previous entries.
        Any attempt to PUT or PATCH an existing custody entry is blocked with HTTP 403 Forbidden.
        """
        # Create an evidence item
        ev_record = preserve_evidence_record(
            case_id=self.case_id,
            transaction_id="coc_tx_immutable_test_txid_00112233445566778899aabbccddeeff00",
            wallet_address="1DemoRansomCollectionWallet002",
            amount=0.50,
            db=self.db,
        )
        ev_id = ev_record["evidence_id"]

        # Get initial custody entry
        timeline = evidence_service.get_custody_timeline(db=self.db, evidence_id=ev_id)
        entry_id = timeline[0].id

        # Attempt to edit previous entry via PUT (must fail with 403 Forbidden)
        put_res = self.client.put(
            f"/api/v1/evidence/{ev_id}/custody/{entry_id}",
            json={"notes": "Tampered notes attempt"}
        )
        self.assertEqual(put_res.status_code, 403)
        self.assertIn("immutable", put_res.json()["detail"].lower())

        # Attempt to edit previous entry via PATCH (must fail with 403 Forbidden)
        patch_res = self.client.patch(
            f"/api/v1/evidence/{ev_id}/custody/{entry_id}",
            json={"notes": "Tampered notes attempt"}
        )
        self.assertEqual(patch_res.status_code, 403)
        self.assertIn("immutable", patch_res.json()["detail"].lower())

        print("\n[Immutability Test Passed]: PUT and PATCH correctly rejected with HTTP 403 Forbidden.")

    def test_custody_disclaimer_mandatory_presence(self):
        """
        Verifies mandatory presence of the exact required disclaimer:
        'This is an academic demonstration of chain-of-custody principles and does not replace formal legal evidence procedures.'
        """
        expected_text = (
            "This is an academic demonstration of chain-of-custody principles "
            "and does not replace formal legal evidence procedures."
        )
        self.assertEqual(CUSTODY_DISCLAIMER, expected_text)

        # Verify disclaimer in API response
        ev_record = preserve_evidence_record(
            case_id=self.case_id,
            transaction_id="coc_tx_disclaimer_test_txid_11223344556677889900aabbccddeeff",
            wallet_address="1DemoRansomCollectionWallet002",
            amount=1.00,
            db=self.db,
        )
        api_res = self.client.get(f"/api/v1/evidence/{ev_record['evidence_id']}/custody")
        self.assertEqual(api_res.status_code, 200)
        items = api_res.json()
        self.assertTrue(len(items) > 0)
        for item in items:
            self.assertEqual(item["disclaimer"], expected_text)

        print(f"\n[Disclaimer Test Passed]: Verified on all entries: '{expected_text}'")


if __name__ == "__main__":
    unittest.main()
