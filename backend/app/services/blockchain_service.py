"""
Simplified Blockchain Service for RansomTrace
Designed for beginner undergraduate students.

Features:
1. Validates Bitcoin address format.
2. Mode 1: Demonstration Dataset (Offline, synthetic, deterministic).
3. Mode 2: Optional live public Bitcoin blockchain lookup (via Mempool API).
4. Calculates:
   - Total Received (BTC & Satoshis)
   - Total Sent (BTC & Satoshis)
   - Current Balance (BTC & Satoshis)
   - Transaction Count
   - First Transaction Date (Unix & ISO)
   - Latest Transaction Date (Unix & ISO)
5. Robust fallback: If public API fails, informative error is shown and Demo Mode continues working.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.services.mempool_client import mempool_client, validate_bitcoin_address
from backend.app.models.wallet import Wallet
from backend.app.models.transaction import Transaction
from backend.app.models.case import InvestigationCase
from backend.app.schemas.wallet import WalletStatsResponse, TransactionResponse, TxIO

logger = logging.getLogger(__name__)

SATS_PER_BTC = 100_000_000

DEMO_DATA_LABEL = "DEMONSTRATION DATA — SYNTHETIC"


def sats_to_btc(sats: int) -> float:
    """Converts Satoshis to Bitcoins rounded to 8 decimal places."""
    return round(sats / SATS_PER_BTC, 8)


def format_timestamp_iso(ts: Optional[int]) -> Optional[str]:
    """Formats a Unix epoch timestamp into ISO UTC string."""
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return None


def normalize_tx_data(raw_tx: Dict[str, Any], target_address: Optional[str] = None) -> Dict[str, Any]:
    """Normalizes raw Bitcoin transaction JSON from Mempool into structured forensic model."""
    txid = raw_tx.get("txid", "")
    status_info = raw_tx.get("status", {})
    confirmed = status_info.get("confirmed", False)
    block_height = status_info.get("block_height")
    block_time = status_info.get("block_time")
    fee_sats = raw_tx.get("fee", 0)
    size_bytes = raw_tx.get("size")

    # Inputs decomposition
    inputs: List[TxIO] = []
    incoming_from_target = False
    target_spent_sats = 0

    for vin in raw_tx.get("vin", []):
        prevout = vin.get("prevout") or {}
        in_addr = prevout.get("scriptpubkey_address")
        in_val = prevout.get("value", 0)
        inputs.append(TxIO(
            address=in_addr,
            value_sats=in_val,
            value_btc=sats_to_btc(in_val)
        ))
        if target_address and in_addr == target_address:
            incoming_from_target = True
            target_spent_sats += in_val

    # Outputs decomposition
    outputs: List[TxIO] = []
    received_by_target = False
    target_received_sats = 0

    for vout in raw_tx.get("vout", []):
        out_addr = vout.get("scriptpubkey_address")
        out_val = vout.get("value", 0)
        outputs.append(TxIO(
            address=out_addr,
            value_sats=out_val,
            value_btc=sats_to_btc(out_val)
        ))
        if target_address and out_addr == target_address:
            received_by_target = True
            target_received_sats += out_val

    # Determine flow direction relative to investigated address
    if target_address:
        if incoming_from_target and not received_by_target:
            flow_direction = "OUTGOING"
            net_value_sats = -target_spent_sats
        elif received_by_target and not incoming_from_target:
            flow_direction = "INCOMING"
            net_value_sats = target_received_sats
        elif incoming_from_target and received_by_target:
            flow_direction = "INTERNAL"
            net_value_sats = target_received_sats - target_spent_sats
        else:
            flow_direction = "TRANSIT"
            net_value_sats = 0
    else:
        flow_direction = "TRANSIT"
        net_value_sats = 0

    return {
        "txid": txid,
        "block_height": block_height,
        "block_time": block_time,
        "block_time_iso": format_timestamp_iso(block_time),
        "confirmed": confirmed,
        "fee_sats": fee_sats,
        "fee_btc": sats_to_btc(fee_sats),
        "size_bytes": size_bytes,
        "net_value_sats": net_value_sats,
        "net_value_btc": sats_to_btc(net_value_sats),
        "flow_direction": flow_direction,
        "inputs": inputs,
        "outputs": outputs,
        "raw_inputs": [i.model_dump() for i in inputs],
        "raw_outputs": [o.model_dump() for o in outputs]
    }


class BlockchainService:
    """Service layer coordinating Bitcoin blockchain retrieval, caching, and forensic normalization."""

    async def get_wallet_overview(
        self,
        address: str,
        db: Session,
        case_id: Optional[str] = None
    ) -> WalletStatsResponse:
        """
        Retrieves public address statistics from:
        - MODE 1: Demonstration Dataset (if simulated or preloaded)
        - MODE 2: Optional Live Public Bitcoin API (Mempool)
        """
        clean_addr = address.strip()
        val = validate_bitcoin_address(clean_addr)
        if not val["valid"]:
            raise ValueError(val["reason"])

        # -----------------------------------------------------------------
        # MODE 1: Check Local Demonstration Dataset
        # -----------------------------------------------------------------
        db_wallet = db.query(Wallet).filter(Wallet.address == clean_addr).first()
        is_demo_addr = clean_addr.startswith(("1Demo", "3Demo", "bc1demo")) or (
            db_wallet is not None and (
                "SYNTHETIC" in (db_wallet.label or "") or
                (db_wallet.case and "Simulated" in (db_wallet.case.incident_type or "")) or
                (db_wallet.case and "WannaCry" in (db_wallet.case.title or ""))
            )
        )

        if is_demo_addr:
            if not db_wallet:
                # Demonstration address with zero transaction history
                return WalletStatsResponse(
                    address=clean_addr,
                    address_type=val["type"],
                    total_received_sats=0,
                    total_received_btc=0.0,
                    total_sent_sats=0,
                    total_sent_btc=0.0,
                    balance_sats=0,
                    balance_btc=0.0,
                    tx_count=0,
                    first_activity_time=None,
                    first_activity_iso=None,
                    latest_activity_time=None,
                    latest_activity_iso=None,
                    incoming_tx_count=0,
                    outgoing_tx_count=0,
                    data_source=DEMO_DATA_LABEL,
                    cached=True
                )

            txs = db.query(Transaction).filter(
                Transaction.wallet_id == db_wallet.id
            ).order_by(Transaction.block_time.asc()).all()

            first_time = txs[0].block_time if txs else db_wallet.first_seen_timestamp
            last_time = txs[-1].block_time if txs else db_wallet.last_seen_timestamp
            incoming_count = sum(1 for t in txs if t.flow_direction == "INCOMING")
            outgoing_count = sum(1 for t in txs if t.flow_direction == "OUTGOING")

            tot_recv = db_wallet.total_received_sats or sum(t.net_value_sats for t in txs if t.flow_direction == "INCOMING")
            tot_sent = db_wallet.total_sent_sats or sum(t.net_value_sats for t in txs if t.flow_direction == "OUTGOING")
            bal = max(0, tot_recv - tot_sent)

            return WalletStatsResponse(
                address=clean_addr,
                address_type=val["type"],
                total_received_sats=tot_recv,
                total_received_btc=sats_to_btc(tot_recv),
                total_sent_sats=tot_sent,
                total_sent_btc=sats_to_btc(tot_sent),
                balance_sats=bal,
                balance_btc=sats_to_btc(bal),
                tx_count=len(txs) or db_wallet.tx_count,
                first_activity_time=first_time,
                first_activity_iso=format_timestamp_iso(first_time),
                latest_activity_time=last_time,
                latest_activity_iso=format_timestamp_iso(last_time),
                incoming_tx_count=incoming_count,
                outgoing_tx_count=outgoing_count,
                data_source=DEMO_DATA_LABEL,
                cached=True
            )

        # -----------------------------------------------------------------
        # MODE 2: Optional Live Public Bitcoin Blockchain Lookup
        # -----------------------------------------------------------------
        try:
            summary = await mempool_client.get_address_summary(clean_addr)
            chain_stats = summary.get("chain_stats", {})
            mempool_stats = summary.get("mempool_stats", {})

            total_received = chain_stats.get("funded_txo_sum", 0) + mempool_stats.get("funded_txo_sum", 0)
            total_sent = chain_stats.get("spent_txo_sum", 0) + mempool_stats.get("spent_txo_sum", 0)
            balance = max(0, total_received - total_sent)
            tx_count = chain_stats.get("tx_count", 0) + mempool_stats.get("tx_count", 0)

            txs_raw = await mempool_client.get_address_transactions(clean_addr)

            first_seen: Optional[int] = None
            last_seen: Optional[int] = None
            incoming_count = 0
            outgoing_count = 0

            for tx in txs_raw:
                bt = tx.get("status", {}).get("block_time")
                if bt:
                    if last_seen is None or bt > last_seen:
                        last_seen = bt
                    if first_seen is None or bt < first_seen:
                        first_seen = bt

                is_in = any(vout.get("scriptpubkey_address") == clean_addr for vout in tx.get("vout", []))
                is_out = any(vin.get("prevout", {}).get("scriptpubkey_address") == clean_addr for vin in tx.get("vin", []))
                if is_in:
                    incoming_count += 1
                if is_out:
                    outgoing_count += 1

            # Cache in SQLite for offline availability
            if not db_wallet:
                first_case = db.query(InvestigationCase).first()
                parent_case_id = case_id if case_id else (first_case.id if first_case else None)
                db_wallet = Wallet(
                    case_id=parent_case_id,
                    address=clean_addr,
                    wallet_type=val["type"],
                    balance_sats=balance,
                    total_received_sats=total_received,
                    total_sent_sats=total_sent,
                    tx_count=tx_count,
                    first_seen_timestamp=first_seen,
                    last_seen_timestamp=last_seen
                )
                if parent_case_id:
                    db.add(db_wallet)
                    db.commit()
            else:
                db_wallet.balance_sats = balance
                db_wallet.total_received_sats = total_received
                db_wallet.total_sent_sats = total_sent
                db_wallet.tx_count = tx_count
                db_wallet.first_seen_timestamp = first_seen
                db_wallet.last_seen_timestamp = last_seen
                db.commit()

            return WalletStatsResponse(
                address=clean_addr,
                address_type=val["type"],
                total_received_sats=total_received,
                total_received_btc=sats_to_btc(total_received),
                total_sent_sats=total_sent,
                total_sent_btc=sats_to_btc(total_sent),
                balance_sats=balance,
                balance_btc=sats_to_btc(balance),
                tx_count=tx_count,
                first_activity_time=first_seen,
                first_activity_iso=format_timestamp_iso(first_seen),
                latest_activity_time=last_seen,
                latest_activity_iso=format_timestamp_iso(last_seen),
                incoming_tx_count=incoming_count,
                outgoing_tx_count=outgoing_count,
                data_source="Public Bitcoin Blockchain (Mempool API)",
                cached=False
            )

        except Exception as e:
            logger.warning(f"Live blockchain query failed for {clean_addr}: {e}")
            if db_wallet and db_wallet.tx_count is not None:
                # Return cached data if available
                txs = db.query(Transaction).filter(Transaction.wallet_id == db_wallet.id).all()
                first_time = db_wallet.first_seen_timestamp
                last_time = db_wallet.last_seen_timestamp
                return WalletStatsResponse(
                    address=clean_addr,
                    address_type=val["type"],
                    total_received_sats=db_wallet.total_received_sats,
                    total_received_btc=sats_to_btc(db_wallet.total_received_sats),
                    total_sent_sats=db_wallet.total_sent_sats,
                    total_sent_btc=sats_to_btc(db_wallet.total_sent_sats),
                    balance_sats=db_wallet.balance_sats,
                    balance_btc=sats_to_btc(db_wallet.balance_sats),
                    tx_count=db_wallet.tx_count,
                    first_activity_time=first_time,
                    first_activity_iso=format_timestamp_iso(first_time),
                    latest_activity_time=last_time,
                    latest_activity_iso=format_timestamp_iso(last_time),
                    incoming_tx_count=sum(1 for t in txs if t.flow_direction == "INCOMING"),
                    outgoing_tx_count=sum(1 for t in txs if t.flow_direction == "OUTGOING"),
                    data_source="Cached Forensic Record (Offline)",
                    cached=True
                )
            raise RuntimeError(
                f"Public Bitcoin API lookup failed ({str(e)}). "
                f"You can continue investigating demonstration addresses (e.g. 1DemoRansomCollectionWallet002 or 13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94) in Demo Mode."
            )

    async def get_wallet_transactions(
        self,
        address: str,
        db: Session,
        limit: int = 50
    ) -> List[TransactionResponse]:
        """
        Retrieves public transactions for the address with inputs, outputs,
        values in Satoshis/BTC, fees, and flow direction (INCOMING/OUTGOING).
        """
        clean_addr = address.strip()
        val = validate_bitcoin_address(clean_addr)
        if not val["valid"]:
            raise ValueError(val["reason"])

        # -----------------------------------------------------------------
        # MODE 1: Check Local Demonstration Dataset
        # -----------------------------------------------------------------
        db_wallet = db.query(Wallet).filter(Wallet.address == clean_addr).first()
        is_demo_addr = clean_addr.startswith(("1Demo", "3Demo", "bc1demo")) or (
            db_wallet is not None and (
                "SYNTHETIC" in (db_wallet.label or "") or
                (db_wallet.case and "Simulated" in (db_wallet.case.incident_type or "")) or
                (db_wallet.case and "WannaCry" in (db_wallet.case.title or ""))
            )
        )

        if is_demo_addr:
            if not db_wallet:
                return []

            db_txs = db.query(Transaction).filter(
                Transaction.wallet_id == db_wallet.id
            ).order_by(Transaction.block_time.desc()).limit(limit).all()

            results: List[TransactionResponse] = []
            for tx in db_txs:
                inp = [TxIO(address=i.get("address"), value_sats=i.get("value_sats", 0), value_btc=i.get("value_btc", 0.0)) for i in (tx.raw_inputs or [])]
                out = [TxIO(address=o.get("address"), value_sats=o.get("value_sats", 0), value_btc=o.get("value_btc", 0.0)) for o in (tx.raw_outputs or [])]
                results.append(TransactionResponse(
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
                    data_source=DEMO_DATA_LABEL
                ))
            return results

        # -----------------------------------------------------------------
        # MODE 2: Optional Live Public Bitcoin Blockchain Lookup
        # -----------------------------------------------------------------
        try:
            txs_raw = await mempool_client.get_address_transactions(clean_addr)
            normalized_txs: List[TransactionResponse] = []

            for raw_tx in txs_raw[:limit]:
                norm = normalize_tx_data(raw_tx, target_address=clean_addr)
                tx_resp = TransactionResponse(
                    txid=norm["txid"],
                    block_height=norm["block_height"],
                    block_time=norm["block_time"],
                    block_time_iso=norm["block_time_iso"],
                    confirmed=norm["confirmed"],
                    fee_sats=norm["fee_sats"],
                    fee_btc=norm["fee_btc"],
                    size_bytes=norm["size_bytes"],
                    net_value_sats=norm["net_value_sats"],
                    net_value_btc=norm["net_value_btc"],
                    flow_direction=norm["flow_direction"],
                    inputs=norm["inputs"],
                    outputs=norm["outputs"],
                    data_source="Public Bitcoin Blockchain (Mempool)"
                )
                normalized_txs.append(tx_resp)

            return normalized_txs
        except Exception as e:
            logger.warning(f"Live transactions fetch failed for {clean_addr}: {e}")
            if db_wallet:
                db_txs = db.query(Transaction).filter(
                    Transaction.wallet_id == db_wallet.id
                ).order_by(Transaction.block_time.desc()).limit(limit).all()
                if db_txs:
                    results = []
                    for tx in db_txs:
                        inp = [TxIO(address=i.get("address"), value_sats=i.get("value_sats", 0), value_btc=i.get("value_btc", 0.0)) for i in (tx.raw_inputs or [])]
                        out = [TxIO(address=o.get("address"), value_sats=o.get("value_sats", 0), value_btc=o.get("value_btc", 0.0)) for o in (tx.raw_outputs or [])]
                        results.append(TransactionResponse(
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
                            data_source="Cached Forensic Record (Offline)"
                        ))
                    return results
            raise RuntimeError(
                f"Failed to retrieve transactions from public blockchain ({str(e)}). "
                f"Please verify network connection or select a demonstration address."
            )

    async def get_transaction_details(self, txid: str, db: Session) -> TransactionResponse:
        """Retrieves single transaction details by txid."""
        clean_txid = txid.strip()

        # Check DB first
        db_tx = db.query(Transaction).filter(Transaction.txid == clean_txid).first()
        if db_tx:
            inp = [TxIO(address=i.get("address"), value_sats=i.get("value_sats", 0), value_btc=i.get("value_btc", 0.0)) for i in (db_tx.raw_inputs or [])]
            out = [TxIO(address=o.get("address"), value_sats=o.get("value_sats", 0), value_btc=o.get("value_btc", 0.0)) for o in (db_tx.raw_outputs or [])]
            return TransactionResponse(
                txid=db_tx.txid,
                block_height=db_tx.block_height,
                block_time=db_tx.block_time,
                block_time_iso=format_timestamp_iso(db_tx.block_time),
                confirmed=True,
                fee_sats=db_tx.fee_sats or 0,
                fee_btc=sats_to_btc(db_tx.fee_sats or 0),
                size_bytes=db_tx.size_bytes,
                net_value_sats=db_tx.net_value_sats or 0,
                net_value_btc=sats_to_btc(db_tx.net_value_sats or 0),
                flow_direction=db_tx.flow_direction,
                inputs=inp,
                outputs=out,
                data_source=DEMO_DATA_LABEL if "demo" in db_tx.txid else "Forensic Database"
            )

        if not re.match(r"^[0-9a-fA-F]{64}$", clean_txid):
            raise ValueError("Invalid Bitcoin transaction ID format. Expected 64-character hexadecimal.")

        raw_tx = await mempool_client.get_transaction(clean_txid)
        norm = normalize_tx_data(raw_tx)

        return TransactionResponse(
            txid=norm["txid"],
            block_height=norm["block_height"],
            block_time=norm["block_time"],
            block_time_iso=norm["block_time_iso"],
            confirmed=norm["confirmed"],
            fee_sats=norm["fee_sats"],
            fee_btc=norm["fee_btc"],
            size_bytes=norm["size_bytes"],
            net_value_sats=norm["net_value_sats"],
            net_value_btc=norm["net_value_btc"],
            flow_direction=norm["flow_direction"],
            inputs=norm["inputs"],
            outputs=norm["outputs"],
            data_source="Public Bitcoin Blockchain (Mempool)"
        )


blockchain_service = BlockchainService()
