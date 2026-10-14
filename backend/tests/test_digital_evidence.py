"""
Comprehensive Unit & Forensic Verification Tests for Digital Evidence System
Validates strictly the 5 requested steps:
1. Preserve evidence (evidence_id, case_id, transaction_id, wallet_address, amount, timestamp, source, collected_at, sha256_hash).
2. Generate hash using Python hashlib on canonical representation (deterministic/reproducible).
3. Verify hash ("INTEGRITY VERIFIED").
4. Modify test data.
5. Verify that the system detects the change ("INTEGRITY CHECK FAILED").
"""

import sys
import os
import unittest
import hashlib
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import SessionLocal
from backend.app.models.evidence import Evidence
from backend.app.models.case import InvestigationCase
from backend.app.schemas.evidence import EvidenceCreate, PreserveTransactionRequest
from backend.app.services.evidence_service import (
    create_canonical_representation,
    generate_evidence_hash,
    preserve_evidence_record,
    verify_evidence_hash,
    evidence_service,
    STATUS_VERIFIED,
    STATUS_FAILED,
)


class TestDigitalEvidenceSystem(unittest.TestCase):

    def setUp(self):
        self.db = SessionLocal()
        # Find or create a demo case
        case = self.db.query(InvestigationCase).first()
        if not case:
            case = InvestigationCase(
                id="CASE-TEST-EV-001",
                case_id="RT-2026-TEST-EV",
                title="Academic Forensic Evidence Test Case",
                description="Test docket for digital evidence integrity validation",
                status="OPEN"
            )
            self.db.add(case)
            self.db.commit()
            self.db.refresh(case)
        self.test_case_id = case.id

    def tearDown(self):
        self.db.close()

    def test_step_1_and_2_preserve_evidence_and_deterministic_hash(self):
        """
        Step 1: Preserve evidence with all 9 required fields.
        Step 2: Generate hash using Python hashlib & verify canonical determinism.
        """
        case_id = self.test_case_id
        tx_id = "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
        wallet_addr = "1DemoTestRansomWallet999"
        amount = 2.45
        timestamp = "2026-10-06T14:30:00Z"
        source = "Public Bitcoin Blockchain / Mempool API"

        # Step 1: Preserve evidence record
        evidence = preserve_evidence_record(
            case_id=case_id,
            transaction_id=tx_id,
            wallet_address=wallet_addr,
            amount=amount,
            timestamp=timestamp,
            source=source,
            collector="Inspector Vance",
            db=self.db
        )

        # Verify all 9 required fields exist
        required_fields = [
            "evidence_id",
            "case_id",
            "transaction_id",
            "wallet_address",
            "amount",
            "timestamp",
            "source",
            "collected_at",
            "sha256_hash",
        ]
        for field in required_fields:
            self.assertIn(field, evidence, f"Field '{field}' missing from evidence record.")
            self.assertIsNotNone(evidence[field], f"Field '{field}' cannot be None.")

        # Step 2: Validate deterministic canonical representation and hashlib SHA-256
        canonical_bytes_1 = create_canonical_representation(
            case_id=case_id,
            transaction_id=tx_id,
            wallet_address=wallet_addr,
            amount=amount,
            timestamp=timestamp,
            source=source
        )
        canonical_bytes_2 = create_canonical_representation(
            case_id=case_id,
            transaction_id=tx_id,
            wallet_address=wallet_addr,
            amount=amount,
            timestamp=timestamp,
            source=source
        )
        self.assertEqual(canonical_bytes_1, canonical_bytes_2)

        # Hash independently using hashlib
        expected_hash = hashlib.sha256(canonical_bytes_1).hexdigest()
        self.assertEqual(evidence["sha256_hash"], expected_hash)
        self.assertEqual(len(evidence["sha256_hash"]), 64)

        print("\n[Step 1 & 2 Passed]: Evidence Preserved with SHA-256 Fingerprint:")
        print(f"  Evidence ID: {evidence['evidence_id']}")
        print(f"  SHA-256 Hash: {evidence['sha256_hash']}")

    def test_step_3_verify_hash_integrity_verified(self):
        """
        Step 3: Verify hash when evidence is intact.
        Must return 'INTEGRITY VERIFIED'.
        """
        case_id = self.test_case_id
        tx_id = "b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890a1"
        wallet_addr = "1DemoIntactEvidenceWallet"
        amount = 0.75
        timestamp = "2026-10-06T15:00:00Z"
        source = "Public Bitcoin Blockchain / Mempool API"

        # Preserve evidence via service
        evidence = preserve_evidence_record(
            case_id=case_id,
            transaction_id=tx_id,
            wallet_address=wallet_addr,
            amount=amount,
            timestamp=timestamp,
            source=source,
            db=self.db
        )

        evidence_id = evidence["evidence_id"]

        # Run integrity verification
        result = evidence_service.verify_evidence_integrity(
            db=self.db,
            evidence_id=evidence_id,
            actor_name="Integrity Verification Agent"
        )

        self.assertTrue(result.verified)
        self.assertFalse(result.tampered)
        self.assertEqual(result.status, STATUS_VERIFIED)
        self.assertEqual(result.stored_hash, evidence["sha256_hash"])
        self.assertEqual(result.computed_hash, evidence["sha256_hash"])

        print(f"\n[Step 3 Passed]: Integrity Check: {result.status}")

    def test_step_4_and_5_modify_data_and_verify_failure_detected(self):
        """
        Step 4: Modify test data (tamper with amount or transaction).
        Step 5: Verify that the system detects the change -> 'INTEGRITY CHECK FAILED'.
        """
        case_id = self.test_case_id
        tx_id = "c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890a1b2"
        wallet_addr = "1DemoTamperDetectionWallet"
        amount = 1.00
        timestamp = "2026-10-06T16:00:00Z"
        source = "Public Bitcoin Blockchain / Mempool API"

        # Preserve evidence
        evidence = preserve_evidence_record(
            case_id=case_id,
            transaction_id=tx_id,
            wallet_address=wallet_addr,
            amount=amount,
            timestamp=timestamp,
            source=source,
            db=self.db
        )
        evidence_id = evidence["evidence_id"]
        original_hash = evidence["sha256_hash"]

        # Step 4: Deliberately modify / tamper with the stored test data
        db_record = self.db.query(Evidence).filter(Evidence.id == evidence_id).first()
        self.assertIsNotNone(db_record)

        # Alter the evidence amount from 1.00 BTC to 999.00 BTC
        db_record.amount_btc = 999.00
        self.db.commit()

        # Step 5: Verify that the system detects the tampering
        tampered_result = evidence_service.verify_evidence_integrity(
            db=self.db,
            evidence_id=evidence_id,
            actor_name="Forensic Integrity Auditor"
        )

        self.assertFalse(tampered_result.verified)
        self.assertTrue(tampered_result.tampered)
        self.assertEqual(tampered_result.status, STATUS_FAILED)
        self.assertNotEqual(tampered_result.computed_hash, original_hash)
        self.assertEqual(tampered_result.stored_hash, original_hash)

        print("\n[Step 4 & 5 Passed]: Tampering Successfully Detected!")
        print(f"  Status: {tampered_result.status}")
        print(f"  Stored Hash:   {tampered_result.stored_hash}")
        print(f"  Computed Hash: {tampered_result.computed_hash}")
        print(f"  Message:       {tampered_result.message}")


if __name__ == "__main__":
    unittest.main()
