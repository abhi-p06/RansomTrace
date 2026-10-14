"""
Simplified Forensic Transaction Analytics Engine
Designed for undergraduate cybersecurity students.

Calculates ONLY the 10 core metrics from observable blockchain transaction data:
1. Total transactions
2. Incoming transactions
3. Outgoing transactions
4. Total received
5. Total sent
6. Average transaction amount
7. Largest transaction
8. Smallest transaction
9. Number of unique counterparties
10. Average time between transactions

All calculations are implemented as transparent, standalone reusable functions.
No advanced statistical black-boxes. No fabricated values.
"""

from collections import defaultdict
from datetime import datetime, timezone
import logging
from typing import List, Dict, Any, Optional, Set

from backend.app.schemas.wallet import TransactionResponse
from backend.app.schemas.analytics import (
    WalletAnalyticsResponse,
    TimeSeriesPoint,
    AmountDistributionBucket,
    CounterpartyMetric,
    ActivityBurst,
)
from backend.app.services.blockchain_service import sats_to_btc, format_timestamp_iso

logger = logging.getLogger(__name__)

SATS_PER_BTC = 100_000_000
INSUFFICIENT_DATA_MSG = "Insufficient transaction data"


# =====================================================================
# 10 INDIVIDUAL REUSABLE CALCULATION FUNCTIONS
# =====================================================================

def calculate_total_transactions(txs: List[TransactionResponse]) -> int:
    """1. Total number of observed transactions."""
    return len(txs)


def calculate_incoming_transactions(txs: List[TransactionResponse]) -> int:
    """2. Number of incoming deposits/inflows."""
    return sum(1 for tx in txs if tx.flow_direction == "INCOMING")


def calculate_outgoing_transactions(txs: List[TransactionResponse]) -> int:
    """3. Number of outgoing withdrawals/outflows."""
    return sum(1 for tx in txs if tx.flow_direction == "OUTGOING")


def calculate_total_received(txs: List[TransactionResponse]) -> Dict[str, Any]:
    """4. Total value received in Satoshis and Bitcoins."""
    total_sats = sum(abs(tx.net_value_sats) for tx in txs if tx.flow_direction == "INCOMING")
    return {
        "sats": total_sats,
        "btc": sats_to_btc(total_sats)
    }


def calculate_total_sent(txs: List[TransactionResponse]) -> Dict[str, Any]:
    """5. Total value sent out in Satoshis and Bitcoins."""
    total_sats = sum(abs(tx.net_value_sats) for tx in txs if tx.flow_direction == "OUTGOING")
    return {
        "sats": total_sats,
        "btc": sats_to_btc(total_sats)
    }


def calculate_average_transaction_amount(txs: List[TransactionResponse]) -> Dict[str, Any]:
    """6. Arithmetic mean transaction magnitude."""
    magnitudes = [abs(tx.net_value_sats) for tx in txs if abs(tx.net_value_sats) > 0]
    if not magnitudes:
        return {"sats": 0, "btc": 0.0}
    avg_sats = int(sum(magnitudes) / len(magnitudes))
    return {
        "sats": avg_sats,
        "btc": sats_to_btc(avg_sats)
    }


def calculate_largest_transaction(txs: List[TransactionResponse]) -> float:
    """7. Maximum observed single transaction amount in BTC."""
    magnitudes = [abs(tx.net_value_btc) for tx in txs if abs(tx.net_value_btc) > 0]
    return max(magnitudes) if magnitudes else 0.0


def calculate_smallest_transaction(txs: List[TransactionResponse]) -> float:
    """8. Minimum observed non-zero single transaction amount in BTC."""
    magnitudes = [abs(tx.net_value_btc) for tx in txs if abs(tx.net_value_btc) > 0]
    return min(magnitudes) if magnitudes else 0.0


def calculate_unique_counterparties(txs: List[TransactionResponse], target_address: str) -> Dict[str, Any]:
    """
    9. Number and breakdown of unique external counterparties (senders & receivers).
    """
    clean_target = target_address.strip()
    counterparty_map: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"sats": 0, "tx_count": 0, "is_sender": False, "is_recipient": False}
    )

    for tx in txs:
        # Inputs = senders to this wallet
        for vin in tx.inputs:
            if vin.address and vin.address != clean_target:
                counterparty_map[vin.address]["sats"] += vin.value_sats
                counterparty_map[vin.address]["tx_count"] += 1
                counterparty_map[vin.address]["is_sender"] = True

        # Outputs = receivers from this wallet
        for vout in tx.outputs:
            if vout.address and vout.address != clean_target:
                counterparty_map[vout.address]["sats"] += vout.value_sats
                counterparty_map[vout.address]["tx_count"] += 1
                counterparty_map[vout.address]["is_recipient"] = True

    unique_count = len(counterparty_map)

    # Convert to structured metric list
    metrics_list: List[CounterpartyMetric] = []
    for addr, data in counterparty_map.items():
        role = "BOTH" if (data["is_sender"] and data["is_recipient"]) else ("SENDER" if data["is_sender"] else "RECIPIENT")
        metrics_list.append(CounterpartyMetric(
            address=addr,
            role=role,
            tx_count=data["tx_count"],
            total_sats=data["sats"],
            total_btc=sats_to_btc(data["sats"])
        ))

    # Sort descending by value transferred
    metrics_list.sort(key=lambda x: x.total_sats, reverse=True)

    return {
        "count": unique_count,
        "counterparties": metrics_list
    }


def calculate_average_time_between_tx_hours(txs: List[TransactionResponse]) -> float:
    """
    10. Mean time interval between successive transactions in hours.
    Requires at least 2 timestamped transactions.
    """
    timestamps = sorted([tx.block_time for tx in txs if tx.block_time is not None])
    if len(timestamps) < 2:
        return 0.0
    
    # Calculate intervals between consecutive transactions
    intervals = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
    avg_interval_seconds = sum(intervals) / len(intervals)
    return round(avg_interval_seconds / 3600.0, 2)


# =====================================================================
# REUSABLE SUPPORTING VISUALIZATION BUILDERS (FOR EXISTING FRONTEND UI)
# =====================================================================

def build_volume_over_time(txs: List[TransactionResponse]) -> List[TimeSeriesPoint]:
    """Generates chronological daily volume aggregated from real transactions."""
    daily_aggregates: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"incoming_sats": 0, "outgoing_sats": 0, "tx_count": 0, "timestamp": 0}
    )

    for tx in txs:
        if not tx.block_time:
            continue
        day_str = datetime.fromtimestamp(tx.block_time, timezone.utc).strftime("%Y-%m-%d")
        daily_aggregates[day_str]["tx_count"] += 1
        daily_aggregates[day_str]["timestamp"] = tx.block_time

        if tx.flow_direction == "INCOMING":
            daily_aggregates[day_str]["incoming_sats"] += abs(tx.net_value_sats)
        elif tx.flow_direction == "OUTGOING":
            daily_aggregates[day_str]["outgoing_sats"] += abs(tx.net_value_sats)

    sorted_days = sorted(daily_aggregates.keys())
    result: List[TimeSeriesPoint] = []

    for day in sorted_days:
        info = daily_aggregates[day]
        in_btc = sats_to_btc(info["incoming_sats"])
        out_btc = sats_to_btc(info["outgoing_sats"])
        result.append(TimeSeriesPoint(
            date=day,
            timestamp=info["timestamp"],
            incoming_sats=info["incoming_sats"],
            incoming_btc=in_btc,
            outgoing_sats=info["outgoing_sats"],
            outgoing_btc=out_btc,
            total_btc=round(in_btc + out_btc, 8),
            tx_count=info["tx_count"]
        ))
    return result


def build_amount_distribution(txs: List[TransactionResponse]) -> List[AmountDistributionBucket]:
    """Groups real transaction amounts into 5 simple threshold tiers."""
    tiers = [
        {"label": "Micro (< 0.01)", "range_btc": "< 0.01 BTC", "min": 0.0, "max": 0.01, "count": 0},
        {"label": "Small (0.01 - 0.1)", "range_btc": "0.01 - 0.1 BTC", "min": 0.01, "max": 0.1, "count": 0},
        {"label": "Medium (0.1 - 1.0)", "range_btc": "0.1 - 1.0 BTC", "min": 0.1, "max": 1.0, "count": 0},
        {"label": "Large (1.0 - 5.0)", "range_btc": "1.0 - 5.0 BTC", "min": 1.0, "max": 5.0, "count": 0},
        {"label": "Major (> 5.0)", "range_btc": "> 5.0 BTC", "min": 5.0, "max": float("inf"), "count": 0},
    ]

    valid_tx_count = 0
    for tx in txs:
        val_btc = abs(tx.net_value_btc)
        if val_btc > 0:
            valid_tx_count += 1
            for tier in tiers:
                if tier["min"] <= val_btc < tier["max"]:
                    tier["count"] += 1
                    break

    result: List[AmountDistributionBucket] = []
    for tier in tiers:
        pct = round((tier["count"] / valid_tx_count) * 100.0, 1) if valid_tx_count > 0 else 0.0
        result.append(AmountDistributionBucket(
            label=tier["label"],
            range_btc=tier["range_btc"],
            count=tier["count"],
            percentage=pct
        ))
    return result


def build_activity_bursts(txs: List[TransactionResponse]) -> List[ActivityBurst]:
    """Identifies temporal clusters of transactions occurring within 60 minutes."""
    timestamps = sorted([tx for tx in txs if tx.block_time], key=lambda x: x.block_time)
    if len(timestamps) < 2:
        return []

    bursts: List[ActivityBurst] = []
    current_cluster: List[TransactionResponse] = [timestamps[0]]

    for i in range(1, len(timestamps)):
        prev_tx = timestamps[i - 1]
        curr_tx = timestamps[i]

        # Clustered if within 3600 seconds (1 hour)
        if (curr_tx.block_time - prev_tx.block_time) <= 3600:
            current_cluster.append(curr_tx)
        else:
            if len(current_cluster) >= 2:
                start_t = current_cluster[0].block_time
                end_t = current_cluster[-1].block_time
                dur_min = max(1, int((end_t - start_t) / 60))
                tot_btc = round(sum(abs(t.net_value_btc) for t in current_cluster), 8)
                bursts.append(ActivityBurst(
                    start_time_iso=format_timestamp_iso(start_t) or "",
                    end_time_iso=format_timestamp_iso(end_t) or "",
                    duration_minutes=dur_min,
                    tx_count=len(current_cluster),
                    total_btc=tot_btc
                ))
            current_cluster = [curr_tx]

    # Check trailing cluster
    if len(current_cluster) >= 2:
        start_t = current_cluster[0].block_time
        end_t = current_cluster[-1].block_time
        dur_min = max(1, int((end_t - start_t) / 60))
        tot_btc = round(sum(abs(t.net_value_btc) for t in current_cluster), 8)
        bursts.append(ActivityBurst(
            start_time_iso=format_timestamp_iso(start_t) or "",
            end_time_iso=format_timestamp_iso(end_t) or "",
            duration_minutes=dur_min,
            tx_count=len(current_cluster),
            total_btc=tot_btc
        ))

    return bursts[:10]  # Cap at top 10 bursts


# =====================================================================
# MAIN SERVICE CLASS
# =====================================================================

class AnalyticsService:
    """Coordinates behavioral analytics computation using simple reusable functions."""

    def calculate_wallet_analytics(
        self,
        address: str,
        address_type: str,
        txs: List[TransactionResponse]
    ) -> WalletAnalyticsResponse:
        """
        Computes all 10 core metrics for the given wallet address.
        If no transactions exist, returns a clear 'Insufficient transaction data' response.
        """
        clean_addr = address.strip()

        # Handle Insufficient Transaction Data
        if not txs or len(txs) == 0:
            return WalletAnalyticsResponse(
                address=clean_addr,
                address_type=address_type,
                total_tx_count=0,
                incoming_tx_count=0,
                outgoing_tx_count=0,
                incoming_outgoing_ratio=0.0,
                total_received_sats=0,
                total_received_btc=0.0,
                total_sent_sats=0,
                total_sent_btc=0.0,
                current_balance_sats=0,
                current_balance_btc=0.0,
                avg_tx_amount_sats=0,
                avg_tx_amount_btc=0.0,
                median_tx_amount_sats=0,
                median_tx_amount_btc=0.0,
                tx_amount_std_dev_btc=0.0,
                min_amount_btc=0.0,
                max_amount_btc=0.0,
                tx_frequency_per_day=0.0,
                avg_time_between_tx_hours=0.0,
                first_activity_iso=None,
                latest_activity_iso=None,
                active_lifespan_days=0.0,
                burst_count=0,
                activity_bursts=[],
                unique_counterparties_count=0,
                top_counterparties=[],
                volume_over_time=[],
                amount_distribution=build_amount_distribution([]),
                data_source=f"{INSUFFICIENT_DATA_MSG} (0 transactions observed)"
            )

        # 1. Total transactions
        total_tx = calculate_total_transactions(txs)

        # 2. Incoming transactions
        in_tx = calculate_incoming_transactions(txs)

        # 3. Outgoing transactions
        out_tx = calculate_outgoing_transactions(txs)

        # 4. Total received
        recv = calculate_total_received(txs)

        # 5. Total sent
        sent = calculate_total_sent(txs)

        # Current balance
        balance_sats = max(0, recv["sats"] - sent["sats"])
        balance_btc = sats_to_btc(balance_sats)

        # 6. Average transaction amount
        avg_amt = calculate_average_transaction_amount(txs)

        # 7. Largest transaction
        max_amt = calculate_largest_transaction(txs)

        # 8. Smallest transaction
        min_amt = calculate_smallest_transaction(txs)

        # 9. Number of unique counterparties
        counterparties_data = calculate_unique_counterparties(txs, clean_addr)
        unique_cp_count = counterparties_data["count"]
        top_cp = counterparties_data["counterparties"]

        # 10. Average time between transactions
        avg_time_hours = calculate_average_time_between_tx_hours(txs)

        # Ratio incoming to outgoing
        ratio = round(in_tx / out_tx, 2) if out_tx > 0 else float(in_tx)

        # Activity timeline metrics
        timestamps = [tx.block_time for tx in txs if tx.block_time]
        first_iso = format_timestamp_iso(min(timestamps)) if timestamps else None
        latest_iso = format_timestamp_iso(max(timestamps)) if timestamps else None

        active_days = 0.0
        if timestamps and len(timestamps) >= 2:
            span_seconds = max(timestamps) - min(timestamps)
            active_days = round(max(0.1, span_seconds / 86400.0), 1)

        daily_velocity = round(total_tx / max(1.0, active_days), 2)

        # Median amount calculation
        magnitudes_sats = sorted([abs(t.net_value_sats) for t in txs if abs(t.net_value_sats) > 0])
        n = len(magnitudes_sats)
        if n == 0:
            median_sats = 0
        elif n % 2 == 1:
            median_sats = magnitudes_sats[n // 2]
        else:
            median_sats = int((magnitudes_sats[n // 2 - 1] + magnitudes_sats[n // 2]) / 2)
        median_btc = sats_to_btc(median_sats)

        # Supporting UI visualizations
        volume_chart = build_volume_over_time(txs)
        amount_dist = build_amount_distribution(txs)
        bursts = build_activity_bursts(txs)

        # Determine data source tag
        is_synthetic = any("synthetic" in (tx.data_source or "").lower() or "demo" in (tx.txid or "").lower() for tx in txs)
        data_src = "DEMONSTRATION DATA — SYNTHETIC" if is_synthetic else "Public Bitcoin Blockchain (Observable Data)"

        return WalletAnalyticsResponse(
            address=clean_addr,
            address_type=address_type,
            total_tx_count=total_tx,
            incoming_tx_count=in_tx,
            outgoing_tx_count=out_tx,
            incoming_outgoing_ratio=ratio,
            total_received_sats=recv["sats"],
            total_received_btc=recv["btc"],
            total_sent_sats=sent["sats"],
            total_sent_btc=sent["btc"],
            current_balance_sats=balance_sats,
            current_balance_btc=balance_btc,
            avg_tx_amount_sats=avg_amt["sats"],
            avg_tx_amount_btc=avg_amt["btc"],
            median_tx_amount_sats=median_sats,
            median_tx_amount_btc=median_btc,
            tx_amount_std_dev_btc=0.0,
            min_amount_btc=min_amt,
            max_amount_btc=max_amt,
            tx_frequency_per_day=daily_velocity,
            avg_time_between_tx_hours=avg_time_hours,
            first_activity_iso=first_iso,
            latest_activity_iso=latest_iso,
            active_lifespan_days=active_days,
            burst_count=len(bursts),
            activity_bursts=bursts,
            unique_counterparties_count=unique_cp_count,
            top_counterparties=top_cp[:15],
            volume_over_time=volume_chart,
            amount_distribution=amount_dist,
            data_source=data_src
        )


analytics_service = AnalyticsService()
