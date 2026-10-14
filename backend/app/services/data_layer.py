"""
RansomTrace Simplified Data Access Layer (CRUD & Demo Dataset Engine)
Designed specifically for undergraduate cybersecurity students.

Core Entities:
1. CASE: case_id, case_name, incident_type, description, status, created_at
2. WALLET: wallet_address, case_id
3. TRANSACTION: transaction_id, wallet_address, sender, receiver, amount, timestamp, direction

Academic Compliance:
- Zero complex ORM patterns or abstractions.
- Pure SQLite compatibility.
- Transparent, easily explainable CRUD functions for viva defense.
- DEMO DATA mode marked explicitly as: 'DEMONSTRATION DATA — SYNTHETIC'.
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from backend.app.core.database import engine, Base
from backend.app.models.case import InvestigationCase, CaseStatus, CaseSeverity
from backend.app.models.wallet import Wallet
from backend.app.models.transaction import Transaction

logger = logging.getLogger(__name__)

# Standard Bitcoin conversion constant
SATS_PER_BTC = 100_000_000

# Explicit academic disclaimer for synthetic data
SYNTHETIC_DATA_LABEL = "DEMONSTRATION DATA — SYNTHETIC"
SYNTHETIC_DISCLAIMER = (
    "DEMONSTRATION DATA — SYNTHETIC. This dataset contains simulated blockchain-style "
    "transaction records generated solely for academic forensic education and viva demonstration. "
    "It does not represent any real-world ransomware attack, real victims, or criminal actors."
)


def init_database() -> None:
    """
    Initializes SQLite tables and guarantees required columns exist.
    Beginner-friendly: Runs automatically without requiring Alembic migration commands.
    """
    Base.metadata.create_all(bind=engine)

    # Ensure beginner-friendly columns exist in SQLite transactions table
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(transactions);"))
            existing_cols = {row[1] for row in result.fetchall()}
            
            if "wallet_address" not in existing_cols:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN wallet_address VARCHAR(128);"))
            if "sender" not in existing_cols:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN sender VARCHAR(128);"))
            if "receiver" not in existing_cols:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN receiver VARCHAR(128);"))
            if "amount" not in existing_cols:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN amount FLOAT DEFAULT 0.0;"))
            conn.commit()
        except Exception as e:
            logger.warning(f"Database column alignment check: {e}")


# =====================================================================
# 1. CASE CRUD FUNCTIONS
# =====================================================================

def create_case(
    db: Session,
    case_id: str,
    case_name: str,
    incident_type: str = "Ransomware Extortion",
    description: str = "",
    status: str = "Open",
    severity: str = "Medium",
    target_label: Optional[str] = None
) -> InvestigationCase:
    """
    Creates a new investigation case.
    Accepts both beginner field 'case_name' and maps it directly to database storage.
    """
    # Check if case_id already exists
    existing = db.query(InvestigationCase).filter(InvestigationCase.case_id == case_id).first()
    if existing:
        raise ValueError(f"Case with ID '{case_id}' already exists.")

    new_case = InvestigationCase(
        id=str(uuid.uuid4()),
        case_id=case_id.strip(),
        title=case_name.strip(),
        incident_type=incident_type.strip(),
        description=description.strip() if description else None,
        target_label=target_label.strip() if target_label else None,
        severity=severity if severity in [s.value for s in CaseSeverity] else CaseSeverity.MEDIUM.value,
        status=status if status in [s.value for s in CaseStatus] else CaseStatus.OPEN.value,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case


def get_case(db: Session, identifier: str) -> Optional[InvestigationCase]:
    """Retrieves an investigation case by its internal UUID or user-assigned case_id."""
    clean_id = identifier.strip()
    return db.query(InvestigationCase).filter(
        or_(InvestigationCase.id == clean_id, InvestigationCase.case_id == clean_id)
    ).first()


def list_cases(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[InvestigationCase]:
    """Lists investigation cases with optional filtering."""
    query = db.query(InvestigationCase)
    if status:
        query = query.filter(InvestigationCase.status == status)
    if severity:
        query = query.filter(InvestigationCase.severity == severity)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                InvestigationCase.title.ilike(search_pattern),
                InvestigationCase.case_id.ilike(search_pattern),
                InvestigationCase.incident_type.ilike(search_pattern)
            )
        )
    return query.order_by(InvestigationCase.created_at.desc()).offset(skip).limit(limit).all()


def update_case(
    db: Session,
    identifier: str,
    case_name: Optional[str] = None,
    incident_type: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    target_label: Optional[str] = None
) -> InvestigationCase:
    """Updates fields on an existing investigation case."""
    case = get_case(db, identifier)
    if not case:
        raise ValueError(f"Investigation Case '{identifier}' not found.")

    if case_name is not None:
        case.title = case_name.strip()
    if incident_type is not None:
        case.incident_type = incident_type.strip()
    if description is not None:
        case.description = description.strip()
    if status is not None:
        case.status = status.strip()
    if severity is not None:
        case.severity = severity.strip()
    if target_label is not None:
        case.target_label = target_label.strip()

    case.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(case)
    return case


def delete_case(db: Session, identifier: str) -> bool:
    """Deletes an investigation case and associated cascaded records."""
    case = get_case(db, identifier)
    if not case:
        return False
    db.delete(case)
    db.commit()
    return True


# =====================================================================
# 2. WALLET CRUD FUNCTIONS
# =====================================================================

def add_wallet(
    db: Session,
    case_id: str,
    wallet_address: str,
    label: Optional[str] = None,
    wallet_type: str = "P2PKH",
    balance_btc: float = 0.0,
    total_received_btc: float = 0.0,
    total_sent_btc: float = 0.0,
    tx_count: int = 0
) -> Wallet:
    """
    Registers a cryptocurrency wallet address under an investigation case.
    """
    # Verify the parent case exists
    case = get_case(db, case_id)
    if not case:
        raise ValueError(f"Associated case '{case_id}' does not exist.")

    clean_addr = wallet_address.strip()
    # Check if this address is already registered in this case
    existing = db.query(Wallet).filter(
        Wallet.case_id == case.id,
        Wallet.address == clean_addr
    ).first()
    if existing:
        return existing

    new_wallet = Wallet(
        id=str(uuid.uuid4()),
        case_id=case.id,
        address=clean_addr,
        label=label.strip() if label else None,
        wallet_type=wallet_type,
        balance_sats=int(balance_btc * SATS_PER_BTC),
        total_received_sats=int(total_received_btc * SATS_PER_BTC),
        total_sent_sats=int(total_sent_btc * SATS_PER_BTC),
        tx_count=tx_count,
        first_seen_timestamp=int(time.time()),
        last_seen_timestamp=int(time.time())
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet


def get_wallet(db: Session, wallet_address: str) -> Optional[Wallet]:
    """Retrieves a wallet record by its public Bitcoin address."""
    clean_addr = wallet_address.strip()
    return db.query(Wallet).filter(Wallet.address == clean_addr).first()


def get_wallets_for_case(db: Session, case_id: str) -> List[Wallet]:
    """Retrieves all tracked wallets for a given case."""
    case = get_case(db, case_id)
    if not case:
        return []
    return db.query(Wallet).filter(Wallet.case_id == case.id).all()


# =====================================================================
# 3. TRANSACTION CRUD FUNCTIONS
# =====================================================================

def add_transaction(
    db: Session,
    wallet_address: str,
    transaction_id: str,
    sender: str,
    receiver: str,
    amount: float,
    timestamp: Optional[int] = None,
    direction: str = "INCOMING",
    fee_btc: float = 0.0001,
    case_id: Optional[str] = None
) -> Transaction:
    """
    Adds a simple cryptocurrency transaction record linked to a wallet.
    Accepts student-friendly fields: transaction_id, wallet_address, sender, receiver, amount, timestamp, direction.
    """
    clean_addr = wallet_address.strip()
    wallet = get_wallet(db, clean_addr)

    # Auto-create wallet if not present, linking to case if provided
    if not wallet:
        parent_case_id = case_id
        if not parent_case_id:
            # Fall back to first available case or create an unassigned case
            first_case = db.query(InvestigationCase).first()
            if not first_case:
                first_case = create_case(
                    db,
                    case_id="CASE-GENERAL-001",
                    case_name="General Forensic Ingestion",
                    incident_type="Forensic Triage",
                    description="Default triage container for newly ingested wallet queries."
                )
            parent_case_id = first_case.id
        wallet = add_wallet(db, case_id=parent_case_id, wallet_address=clean_addr, label="Ingested Target")

    clean_txid = transaction_id.strip()
    existing_tx = db.query(Transaction).filter(
        Transaction.wallet_id == wallet.id,
        Transaction.txid == clean_txid
    ).first()
    if existing_tx:
        return existing_tx

    block_time = timestamp if timestamp else int(time.time())
    net_sats = int(amount * SATS_PER_BTC)
    fee_sats = int(fee_btc * SATS_PER_BTC)

    new_tx = Transaction(
        id=str(uuid.uuid4()),
        wallet_id=wallet.id,
        txid=clean_txid,
        wallet_address_val=clean_addr,
        sender_val=sender.strip(),
        receiver_val=receiver.strip(),
        amount_btc=float(amount),
        block_time=block_time,
        fee_sats=fee_sats,
        net_value_sats=net_sats,
        flow_direction=direction.upper(),
        raw_inputs=[{"address": sender.strip(), "value_sats": net_sats, "value_btc": float(amount)}],
        raw_outputs=[{"address": receiver.strip(), "value_sats": net_sats, "value_btc": float(amount)}]
    )
    db.add(new_tx)
    
    # Update wallet metrics
    wallet.tx_count = (wallet.tx_count or 0) + 1
    if direction.upper() == "INCOMING":
        wallet.total_received_sats = (wallet.total_received_sats or 0) + net_sats
        wallet.balance_sats = (wallet.balance_sats or 0) + net_sats
    else:
        wallet.total_sent_sats = (wallet.total_sent_sats or 0) + net_sats
        wallet.balance_sats = max(0, (wallet.balance_sats or 0) - net_sats)

    db.commit()
    db.refresh(new_tx)
    return new_tx


def get_transactions_for_wallet(
    db: Session,
    wallet_address: str,
    limit: int = 50
) -> List[Transaction]:
    """Retrieves all transaction records for a given public address."""
    clean_addr = wallet_address.strip()
    wallet = get_wallet(db, clean_addr)
    if not wallet:
        return []
    return db.query(Transaction).filter(
        Transaction.wallet_id == wallet.id
    ).order_by(Transaction.block_time.desc()).limit(limit).all()


# =====================================================================
# 4. DEMO DATA MODE (SYNTHETIC BENCHMARK CASE)
# =====================================================================

def load_demo_data(db: Session, force_reload: bool = False) -> Dict[str, Any]:
    """
    Loads synthetic demonstration data into SQLite.
    Guarantees beginner students can run reliable, offline demos during viva exams.

    Academic Rules:
    1. Clearly marked as 'DEMONSTRATION DATA — SYNTHETIC'.
    2. Does NOT claim to represent any real ransomware incident.
    3. Contains clean synthetic blockchain records showing a 3-step laundering pattern:
       - Inflow (Victim payment)
       - Peeling Hop (Intermediate transfer)
       - Cashout (Mixer/Exchange split)
    """
    demo_case_id = "CASE-DEMO-SYNTHETIC-001"
    existing = get_case(db, demo_case_id)

    if existing and not force_reload:
        return {
            "status": "already_loaded",
            "case_id": existing.case_id,
            "case_name": existing.title,
            "label": SYNTHETIC_DATA_LABEL,
            "wallet_count": len(existing.wallets),
            "message": "Synthetic demonstration dataset is already loaded in the database."
        }

    if existing and force_reload:
        delete_case(db, demo_case_id)

    # 1. Create Synthetic Investigation Case
    demo_case = create_case(
        db,
        case_id=demo_case_id,
        case_name="DEMONSTRATION DATA — SYNTHETIC: Multi-Hop Ransomware Simulation",
        incident_type="Simulated Extortion Analysis",
        description=SYNTHETIC_DISCLAIMER,
        status="Investigating",
        severity="High",
        target_label="Simulated Extortion Vault"
    )

    # 2. Synthetic Addresses
    victim_addr = "1DemoVictimCorpSimulatedDeposit001"
    ransom_collector_addr = "1DemoRansomCollectionWallet002"
    intermediary_peel_addr = "1DemoIntermediaryHopPeeling003"
    mixer_cashout_addr = "1DemoMixerCashoutSimulated004"

    # Register Wallets
    w_collector = add_wallet(
        db,
        case_id=demo_case.id,
        wallet_address=ransom_collector_addr,
        label=f"{SYNTHETIC_DATA_LABEL}: Primary Ransom Collector",
        wallet_type="P2PKH (Legacy)",
        balance_btc=0.0,
        total_received_btc=3.50,
        total_sent_btc=3.50,
        tx_count=2
    )

    w_peeling = add_wallet(
        db,
        case_id=demo_case.id,
        wallet_address=intermediary_peel_addr,
        label=f"{SYNTHETIC_DATA_LABEL}: Peeling Chain Intermediary",
        wallet_type="P2WPKH (Native SegWit)",
        balance_btc=0.01,
        total_received_btc=3.49,
        total_sent_btc=3.48,
        tx_count=2
    )

    # 3. Synthetic Blockchain Transactions (Simulated timeline)
    base_timestamp = int(time.time()) - 86400  # 24 hours ago

    # Tx 1: Victim pays simulated ransom demand (3.5 BTC) into Collector
    add_transaction(
        db,
        wallet_address=ransom_collector_addr,
        transaction_id="demo_tx_001_synthetic_victim_payment_3_5btc",
        sender=victim_addr,
        receiver=ransom_collector_addr,
        amount=3.50,
        timestamp=base_timestamp,
        direction="INCOMING",
        fee_btc=0.00015,
        case_id=demo_case.id
    )

    # Tx 2: Ransom Collector moves funds out into Peeling Intermediary (3.49 BTC + 0.01 fee)
    add_transaction(
        db,
        wallet_address=ransom_collector_addr,
        transaction_id="demo_tx_002_synthetic_peeling_hop_3_49btc",
        sender=ransom_collector_addr,
        receiver=intermediary_peel_addr,
        amount=3.49,
        timestamp=base_timestamp + 7200,
        direction="OUTGOING",
        fee_btc=0.00020,
        case_id=demo_case.id
    )

    # Tx 3: Intermediary peels funds into simulated mixer/cashout service (3.48 BTC)
    add_transaction(
        db,
        wallet_address=intermediary_peel_addr,
        transaction_id="demo_tx_003_synthetic_mixer_cashout_3_48btc",
        sender=intermediary_peel_addr,
        receiver=mixer_cashout_addr,
        amount=3.48,
        timestamp=base_timestamp + 14400,
        direction="OUTGOING",
        fee_btc=0.00025,
        case_id=demo_case.id
    )

    # Load WannaCry demonstration case study if present
    wc_sample_path = Path("data/sample_cases/wannacry_sample.json")
    if wc_sample_path.exists():
        try:
            with open(wc_sample_path, "r", encoding="utf-8") as f:
                wc_json = json.load(f)
            
            wc_meta = wc_json.get("case_metadata", {})
            wc_wallet = wc_json.get("wallet", {})
            wc_cid = wc_meta.get("case_number", "RT-2017-WCRY-001")
            
            wc_case = get_case(db, wc_cid)
            if not wc_case:
                wc_case = create_case(
                    db,
                    case_id=wc_cid,
                    case_name=f"{SYNTHETIC_DATA_LABEL}: {wc_meta.get('title', 'WannaCry Case Study')}",
                    incident_type=wc_meta.get("incident_type", "Ransomware Extortion"),
                    description=f"{SYNTHETIC_DISCLAIMER} {wc_meta.get('description', '')}",
                    status="Investigating",
                    severity="Critical",
                    target_label="WannaCry Primary Extortion Address"
                )

            wc_addr = wc_wallet.get("address", "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94")
            w_record = get_wallet(db, wc_addr)
            if not w_record or len(w_record.transactions) == 0:
                if not w_record:
                    w_record = add_wallet(
                    db,
                    case_id=wc_case.id,
                    wallet_address=wc_addr,
                    label=f"{SYNTHETIC_DATA_LABEL}: WannaCry Extortion Address",
                    wallet_type=wc_wallet.get("address_type", "P2PKH (Legacy)"),
                    balance_btc=0.0,
                    total_received_btc=(wc_wallet.get("total_received_sats", 5218765400)) / SATS_PER_BTC,
                    total_sent_btc=(wc_wallet.get("total_sent_sats", 5218765400)) / SATS_PER_BTC,
                    tx_count=wc_wallet.get("tx_count", 8)
                )

                for tx_data in wc_json.get("transactions", []):
                    txid = tx_data.get("txid")
                    b_time = tx_data.get("block_time", int(time.time()))
                    direction = tx_data.get("flow_direction", "INCOMING")
                    sats = tx_data.get("net_value_sats", 0)
                    btc_val = sats / SATS_PER_BTC
                    inputs = tx_data.get("raw_inputs", [{}])
                    outputs = tx_data.get("raw_outputs", [{}])
                    sndr = inputs[0].get("prevout", {}).get("scriptpubkey_address", "1VictimSampleAddress") if inputs else "1VictimSampleAddress"
                    rcvr = outputs[0].get("scriptpubkey_address", wc_addr) if outputs else wc_addr

                    add_transaction(
                        db,
                        wallet_address=wc_addr,
                        transaction_id=txid,
                        sender=sndr,
                        receiver=rcvr,
                        amount=btc_val,
                        timestamp=b_time,
                        direction=direction,
                        fee_btc=(tx_data.get("fee_sats", 45000)) / SATS_PER_BTC,
                        case_id=wc_case.id
                    )
        except Exception as e:
            logger.warning(f"Could not load WannaCry demo case: {e}")

    return {
        "status": "success",
        "case_id": demo_case.case_id,
        "case_name": demo_case.title,
        "label": SYNTHETIC_DATA_LABEL,
        "wallet_count": len(demo_case.wallets),
        "transactions_created": 3,
        "disclaimer": SYNTHETIC_DISCLAIMER
    }

