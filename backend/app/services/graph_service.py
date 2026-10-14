"""
Simplified Fund Flow Graph Engine for RansomTrace
Designed for beginner undergraduate students.

Core Principles:
1. NO recursive crawling or multi-depth traversals (Depth is strictly 1: direct neighbors only).
2. Uses ONLY transaction records already available for the current investigation.
3. Model:
   - Wallet / Address = GraphNode
   - Transaction = GraphEdge (directed from sender to receiver)
4. Transparent, explainable topology:
   - Inflow Senders -> Investigated Target Wallet -> Outflow Recipients
5. Contains all required edge fields:
   - transaction ID (txid)
   - amount (Satoshis & BTC)
   - timestamp (epoch & ISO)
   - flow direction
"""

import logging
from typing import Dict, Any, List, Set, Optional
import networkx as nx
from sqlalchemy.orm import Session

from backend.app.schemas.wallet import TransactionResponse
from backend.app.schemas.graph import GraphNode, GraphEdge, GraphMetrics, FundFlowGraphResponse
from backend.app.services.blockchain_service import blockchain_service, sats_to_btc, format_timestamp_iso
from backend.app.services.mempool_client import validate_bitcoin_address

logger = logging.getLogger(__name__)

SATS_PER_BTC = 100_000_000


def make_short_label(address: str) -> str:
    """Creates a readable, compact label: e.g. 1DemoRa...et002"""
    if len(address) <= 14:
        return address
    return f"{address[:6]}...{address[-4:]}"


class GraphService:
    """Constructs a simple, explainable directed fund-flow graph for a single wallet."""

    async def build_fund_flow_graph(
        self,
        target_address: str,
        db: Session,
        depth: int = 1,
        max_nodes: int = 50
    ) -> FundFlowGraphResponse:
        """
        Builds a direct (depth 1) fund-flow graph connecting the target wallet
        to all observed counterparty addresses from its already-retrieved transactions.
        """
        clean_target = target_address.strip()
        val = validate_bitcoin_address(clean_target)
        if not val["valid"]:
            raise ValueError(val["reason"])

        # Retrieve transactions already available for this wallet
        txs: List[TransactionResponse] = await blockchain_service.get_wallet_transactions(
            clean_target, db, limit=max_nodes
        )

        # NetworkX directed graph for structural analysis
        G = nx.DiGraph()

        # Node tracker: address -> Dict
        node_stats: Dict[str, Dict[str, Any]] = {
            clean_target: {
                "id": clean_target,
                "address": clean_target,
                "short_label": make_short_label(clean_target),
                "node_type": "TARGET",
                "tx_count": len(txs),
                "received_sats": sum(abs(t.net_value_sats) for t in txs if t.flow_direction == "INCOMING"),
                "received_btc": sum(abs(t.net_value_btc) for t in txs if t.flow_direction == "INCOMING"),
                "sent_sats": sum(abs(t.net_value_sats) for t in txs if t.flow_direction == "OUTGOING"),
                "sent_btc": sum(abs(t.net_value_btc) for t in txs if t.flow_direction == "OUTGOING"),
                "is_target": True,
                "degree": 0,
                "depth": 0,
            }
        }
        G.add_node(clean_target, **node_stats[clean_target])

        # Edges dictionary: edge_key -> GraphEdge
        edges_map: Dict[str, GraphEdge] = {}

        # Build depth-1 directed edges from direct transactions
        for tx in txs:
            amt_sats = abs(tx.net_value_sats)
            amt_btc = abs(tx.net_value_btc)
            b_time = tx.block_time
            b_time_iso = tx.block_time_iso or format_timestamp_iso(b_time)

            if tx.flow_direction == "INCOMING":
                # Deposits: External Senders -> Target Wallet
                senders = [inp.address for inp in tx.inputs if inp.address and inp.address != clean_target]
                if not senders:
                    senders = ["ExternalInflowSender"]

                for sender_addr in senders:
                    # Register sender node (depth 1)
                    if sender_addr not in node_stats:
                        node_stats[sender_addr] = {
                            "id": sender_addr,
                            "address": sender_addr,
                            "short_label": make_short_label(sender_addr),
                            "node_type": "INFLOW_SENDER",
                            "tx_count": 1,
                            "received_sats": 0,
                            "received_btc": 0.0,
                            "sent_sats": amt_sats,
                            "sent_btc": amt_btc,
                            "is_target": False,
                            "degree": 0,
                            "depth": 1,
                        }
                        G.add_node(sender_addr, **node_stats[sender_addr])
                    else:
                        node_stats[sender_addr]["sent_sats"] += amt_sats
                        node_stats[sender_addr]["sent_btc"] = round(node_stats[sender_addr]["sent_btc"] + amt_btc, 8)
                        node_stats[sender_addr]["tx_count"] += 1

                    # Create directed edge: sender -> target
                    edge_id = f"edge_{tx.txid}_{sender_addr}_{clean_target}"
                    if edge_id not in edges_map:
                        edge_obj = GraphEdge(
                            id=edge_id,
                            source=sender_addr,
                            target=clean_target,
                            txid=tx.txid,
                            amount_sats=amt_sats,
                            amount_btc=amt_btc,
                            block_time=b_time,
                            block_time_iso=b_time_iso,
                            confirmed=tx.confirmed
                        )
                        edges_map[edge_id] = edge_obj
                        G.add_edge(sender_addr, clean_target, **edge_obj.model_dump())

            elif tx.flow_direction == "OUTGOING":
                # Withdrawals: Target Wallet -> External Recipients
                recipients = [out.address for out in tx.outputs if out.address and out.address != clean_target]
                if not recipients:
                    recipients = ["ExternalOutflowRecipient"]

                for recipient_addr in recipients:
                    # Register recipient node (depth 1)
                    if recipient_addr not in node_stats:
                        node_stats[recipient_addr] = {
                            "id": recipient_addr,
                            "address": recipient_addr,
                            "short_label": make_short_label(recipient_addr),
                            "node_type": "OUTFLOW_RECEIVER",
                            "tx_count": 1,
                            "received_sats": amt_sats,
                            "received_btc": amt_btc,
                            "sent_sats": 0,
                            "sent_btc": 0.0,
                            "is_target": False,
                            "degree": 0,
                            "depth": 1,
                        }
                        G.add_node(recipient_addr, **node_stats[recipient_addr])
                    else:
                        node_stats[recipient_addr]["received_sats"] += amt_sats
                        node_stats[recipient_addr]["received_btc"] = round(node_stats[recipient_addr]["received_btc"] + amt_btc, 8)
                        node_stats[recipient_addr]["tx_count"] += 1

                    # Create directed edge: target -> recipient
                    edge_id = f"edge_{tx.txid}_{clean_target}_{recipient_addr}"
                    if edge_id not in edges_map:
                        edge_obj = GraphEdge(
                            id=edge_id,
                            source=clean_target,
                            target=recipient_addr,
                            txid=tx.txid,
                            amount_sats=amt_sats,
                            amount_btc=amt_btc,
                            block_time=b_time,
                            block_time_iso=b_time_iso,
                            confirmed=tx.confirmed
                        )
                        edges_map[edge_id] = edge_obj
                        G.add_edge(clean_target, recipient_addr, **edge_obj.model_dump())

        # Update node degrees using NetworkX
        nodes_list: List[GraphNode] = []
        for addr, data in node_stats.items():
            degree_val = G.degree(addr) if addr in G else 0
            data["degree"] = degree_val
            nodes_list.append(GraphNode(**data))

        edges_list: List[GraphEdge] = list(edges_map.values())

        # Compute graph structural metrics
        total_n = len(nodes_list)
        total_e = len(edges_list)
        density_val = round(total_e / max(1, total_n), 3)

        metrics = GraphMetrics(
            total_nodes=total_n,
            total_edges=total_e,
            density=density_val,
            max_depth_reached=1 if total_n > 1 else 0,
            hub_addresses=[clean_target]
        )

        is_synthetic = any("synthetic" in (tx.data_source or "").lower() or "demo" in (tx.txid or "").lower() for tx in txs)
        src_label = "DEMONSTRATION DATA — SYNTHETIC (Direct Fund Flow Graph)" if is_synthetic else "Public Bitcoin Blockchain Ledger (Direct Fund Flow Graph)"

        return FundFlowGraphResponse(
            target_address=clean_target,
            depth_requested=1,
            nodes=nodes_list,
            edges=edges_list,
            metrics=metrics,
            data_source=src_label
        )


graph_service = GraphService()
