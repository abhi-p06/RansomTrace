"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Search,
  Terminal,
  ShieldAlert,
  ArrowDownLeft,
  ArrowUpRight,
  RefreshCw,
  Clock,
  Layers,
  CheckCircle2,
  AlertCircle,
  Copy,
  ExternalLink,
  Coins,
  ChevronDown,
  ChevronUp,
  Cpu,
  Eye,
  X
} from "lucide-react";
import { getWalletInfo, getWalletTransactions } from "@/lib/api";
import { WalletStatsResponse, TransactionResponse } from "@/lib/types";

// Known public forensic test addresses
const SAMPLE_ADDRESSES = [
  {
    name: "Demonstration Ransomware Simulation (Active Case)",
    address: "1DemoRansomCollectionWallet002",
    type: "Demonstration Extortion Vault (Synthetic)",
  },
  {
    name: "WannaCry 2017 Primary Extortion",
    address: "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
    type: "Ransomware Extortion Hub",
  },
  {
    name: "DarkSide / Colonial Pipeline Ransom",
    address: "145EUshA4pwv6VPupsmBJAa3kwnY4o6D7S",
    type: "Critical Infrastructure Attack",
  },
  {
    name: "Genesis Block Reward Address",
    address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    type: "Historical Reference",
  },
];

function WalletInvestigationContent() {
  const searchParams = useSearchParams();
  const initialAddr = searchParams.get("address") || "";
  const caseIdParam = searchParams.get("case_id") || undefined;

  const [addressInput, setAddressInput] = useState(initialAddr);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Results state
  const [walletStats, setWalletStats] = useState<WalletStatsResponse | null>(null);
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [expandedTxid, setExpandedTxid] = useState<string | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const [filterDirection, setFilterDirection] = useState<string>("ALL");

  const runInvestigation = async (targetAddr?: string) => {
    const addr = (targetAddr || addressInput).trim();
    if (!addr) {
      setError("Please enter a valid Bitcoin wallet address to investigate.");
      return;
    }

    setLoading(true);
    setError(null);
    setWalletStats(null);
    setTransactions([]);

    try {
      // 1. Fetch wallet overview statistics
      const stats = await getWalletInfo(addr, caseIdParam);
      setWalletStats(stats);

      // 2. Fetch normalized public transaction history
      const txs = await getWalletTransactions(addr, 50);
      setTransactions(txs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze blockchain address.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialAddr) {
      const timer = setTimeout(() => {
        setAddressInput(initialAddr);
        runInvestigation(initialAddr);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [initialAddr]);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  // Filter transactions by flow direction
  const filteredTxs = transactions.filter((tx) => {
    if (filterDirection === "INCOMING") return tx.flow_direction === "INCOMING";
    if (filterDirection === "OUTGOING") return tx.flow_direction === "OUTGOING";
    return true;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1b2848] gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono mb-1">
            <Terminal className="w-3.5 h-3.5" />
            <span className="uppercase tracking-widest font-semibold">
              Module 2 & 4 · Live Blockchain Forensics
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Bitcoin Blockchain Wallet Investigation
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Query live, publicly accessible Bitcoin blockchain ledger records via Mempool API with input/output decomposition.
          </p>
        </div>

        {/* Public Data Notice Badge */}
        <div className="bg-[#0e1628] border border-cyan-800/40 px-3 py-2 rounded-md flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0" />
          <div className="text-[10px] font-mono text-slate-300">
            <span className="text-cyan-300 font-bold block uppercase">Public Ledger Analysis</span>
            <span>Zero private key interaction · Non-custodial</span>
          </div>
        </div>
      </div>

      {/* Search Bar / Input Card */}
      <div className="bg-[#0e1628] border border-[#1b2848] p-5 rounded-lg space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            runInvestigation();
          }}
          className="flex flex-col md:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Enter Bitcoin address (e.g. 13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94 or bc1q...)"
              value={addressInput}
              onChange={(e) => setAddressInput(e.target.value)}
              className="w-full bg-[#121c33] border border-[#1e2f54] text-xs text-white pl-10 pr-4 py-3 rounded-md focus:outline-none focus:border-cyan-500 font-mono tracking-wide placeholder:font-sans"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs px-6 py-3 rounded-md shadow-lg shadow-cyan-600/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50 font-mono uppercase tracking-wider"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Interrogating Ledger...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Start Investigation</span>
              </>
            )}
          </button>
        </form>

        {/* Quick Sample Address Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#18233c] text-xs">
          <span className="text-[11px] font-mono text-slate-400">Sample Ransomware Targets:</span>
          {SAMPLE_ADDRESSES.map((sample) => (
            <button
              key={sample.address}
              onClick={() => {
                setAddressInput(sample.address);
                runInvestigation(sample.address);
              }}
              className="bg-[#121c33] hover:bg-[#1b2a4a] text-cyan-300 border border-[#1e2f54] hover:border-cyan-500/40 px-2.5 py-1 rounded text-[11px] font-mono flex items-center space-x-1.5 transition-all"
            >
              <span>{sample.name}</span>
            </button>
          ))}
        </div>

        {error && (
          <div className="bg-rose-950/60 border border-rose-800 text-rose-300 p-3 rounded-md text-xs font-mono flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Results Section */}
      {walletStats && (
        <div className="space-y-6">
          {/* Target Identity & Public Verification Bar */}
          <div className="bg-[#0e1628] border border-cyan-500/40 p-4 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-cyan-950/70 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
                <Coins className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider block">
                  Identified Target Address · {walletStats.address_type}
                </span>
                <span className="text-sm font-bold font-mono text-white tracking-wide break-all">
                  {walletStats.address}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => copyToClipboard(walletStats.address, "address")}
                className="bg-[#121c33] hover:bg-[#1a2b4d] text-slate-300 px-3 py-1.5 rounded text-xs font-mono flex items-center space-x-1.5 border border-[#1e2f54] transition-all"
              >
                <Copy className="w-3.5 h-3.5 text-cyan-400" />
                <span>{copiedText === "address" ? "Copied!" : "Copy Address"}</span>
              </button>
              <Link
                href={`/analytics?address=${encodeURIComponent(walletStats.address)}`}
                className="bg-cyan-600 hover:bg-cyan-500 text-black px-3 py-1.5 rounded text-xs font-mono font-bold flex items-center space-x-1.5 transition-all"
              >
                <span>Behavioural Analytics →</span>
              </Link>
              <a
                href={`https://mempool.space/address/${walletStats.address}`}
                target="_blank"
                rel="noreferrer"
                className="bg-[#121c33] hover:bg-[#1a2b4d] text-cyan-300 px-3 py-1.5 rounded text-xs font-mono flex items-center space-x-1.5 border border-[#1e2f54] transition-all"
              >
                <span>View on Mempool</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          {/* 8 Metric Core Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* 1. Total Received */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Total Received
              </span>
              <span className="text-xl font-bold font-mono text-emerald-400 mt-1 block">
                {walletStats.total_received_btc.toLocaleString(undefined, { minimumFractionDigits: 8 })} BTC
              </span>
              <span className="text-[10px] font-mono text-slate-500 block mt-0.5">
                {walletStats.total_received_sats.toLocaleString()} Sats
              </span>
            </div>

            {/* 2. Total Sent */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Total Sent
              </span>
              <span className="text-xl font-bold font-mono text-rose-400 mt-1 block">
                {walletStats.total_sent_btc.toLocaleString(undefined, { minimumFractionDigits: 8 })} BTC
              </span>
              <span className="text-[10px] font-mono text-slate-500 block mt-0.5">
                {walletStats.total_sent_sats.toLocaleString()} Sats
              </span>
            </div>

            {/* 3. Current Balance */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Current Unspent Balance
              </span>
              <span className="text-xl font-bold font-mono text-cyan-400 mt-1 block">
                {walletStats.balance_btc.toLocaleString(undefined, { minimumFractionDigits: 8 })} BTC
              </span>
              <span className="text-[10px] font-mono text-slate-500 block mt-0.5">
                {walletStats.balance_sats.toLocaleString()} Sats
              </span>
            </div>

            {/* 4. Transaction Count */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Total Transactions
              </span>
              <span className="text-xl font-bold font-mono text-white mt-1 block">
                {walletStats.tx_count}
              </span>
              <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400 mt-0.5">
                <span className="text-emerald-400">+{walletStats.incoming_tx_count} In</span>
                <span>/</span>
                <span className="text-rose-400">-{walletStats.outgoing_tx_count} Out</span>
              </div>
            </div>

            {/* 5. First Activity */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                First Activity
              </span>
              <span className="text-xs font-bold font-mono text-slate-200 mt-1 block">
                {walletStats.first_activity_iso || "No timestamp recorded"}
              </span>
              <span className="text-[10px] font-mono text-slate-500 block mt-0.5">
                {walletStats.first_activity_time ? `UNIX: ${walletStats.first_activity_time}` : "-"}
              </span>
            </div>

            {/* 6. Latest Activity */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Latest Activity
              </span>
              <span className="text-xs font-bold font-mono text-slate-200 mt-1 block">
                {walletStats.latest_activity_iso || "No timestamp recorded"}
              </span>
              <span className="text-[10px] font-mono text-slate-500 block mt-0.5">
                {walletStats.latest_activity_time ? `UNIX: ${walletStats.latest_activity_time}` : "-"}
              </span>
            </div>

            {/* 7. Incoming Ratio */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider block">
                Incoming Transfers
              </span>
              <span className="text-xl font-bold font-mono text-emerald-300 mt-1 block">
                {walletStats.incoming_tx_count} TXs
              </span>
              <span className="text-[10px] font-mono text-slate-400 block mt-0.5">
                Extortion / Ransom Inflows
              </span>
            </div>

            {/* 8. Outgoing Ratio */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
              <span className="text-[10px] font-mono text-rose-400 uppercase tracking-wider block">
                Outgoing Transfers
              </span>
              <span className="text-xl font-bold font-mono text-rose-300 mt-1 block">
                {walletStats.outgoing_tx_count} TXs
              </span>
              <span className="text-[10px] font-mono text-slate-400 block mt-0.5">
                Peel / Disbursement Outflows
              </span>
            </div>
          </div>

          {/* Quick Investigative Workflow Navigation */}
          <div className="bg-[#0e1628] border border-[#1b2848] p-3 rounded-lg flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Continue Investigation on Wallet:</span>
              <strong className="text-cyan-300 font-mono truncate max-w-[200px]">{walletStats.address}</strong>
            </span>
            <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
              <Link
                href={`/analytics?address=${walletStats.address}${caseIdParam ? `&case_id=${caseIdParam}` : ""}`}
                className="px-3 py-1.5 bg-[#16233d] hover:bg-cyan-600 hover:text-white text-cyan-300 rounded border border-[#22355e] transition-all"
              >
                Deep Analytics →
              </Link>
              <Link
                href={`/graph?address=${walletStats.address}${caseIdParam ? `&case_id=${caseIdParam}` : ""}`}
                className="px-3 py-1.5 bg-[#16233d] hover:bg-cyan-600 hover:text-white text-cyan-300 rounded border border-[#22355e] transition-all"
              >
                Fund-Flow Graph →
              </Link>
              <Link
                href={`/ml-risk?address=${walletStats.address}${caseIdParam ? `&case_id=${caseIdParam}` : ""}`}
                className="px-3 py-1.5 bg-[#16233d] hover:bg-purple-600 hover:text-white text-purple-300 rounded border border-[#22355e] transition-all"
              >
                AI Anomaly →
              </Link>
              <Link
                href={`/risk?address=${walletStats.address}${caseIdParam ? `&case_id=${caseIdParam}` : ""}`}
                className="px-3 py-1.5 bg-[#16233d] hover:bg-amber-600 hover:text-white text-amber-300 rounded border border-[#22355e] transition-all"
              >
                Risk Scoring →
              </Link>
              <Link
                href={`/reports?case_id=${caseIdParam || ""}`}
                className="px-3 py-1.5 bg-[#16233d] hover:bg-emerald-600 hover:text-white text-emerald-300 rounded border border-[#22355e] transition-all"
              >
                Generate Report →
              </Link>
            </div>
          </div>

          {/* Transaction History Section */}
          <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg overflow-hidden space-y-3">
            <div className="p-4 border-b border-[#1b2848] flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  <span>Public Transaction Ledger ({filteredTxs.length} Loaded)</span>
                </h3>
                <span className="text-[11px] text-slate-400 font-mono">
                  Data Source: {walletStats.data_source}
                </span>
              </div>

              {/* Filter Direction Buttons */}
              <div className="flex items-center space-x-1.5 bg-[#121c33] p-1 rounded border border-[#1e2f54] text-xs font-mono">
                <button
                  onClick={() => setFilterDirection("ALL")}
                  className={`px-2.5 py-1 rounded text-[11px] transition-all ${
                    filterDirection === "ALL" ? "bg-cyan-600 text-black font-bold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  All ({transactions.length})
                </button>
                <button
                  onClick={() => setFilterDirection("INCOMING")}
                  className={`px-2.5 py-1 rounded text-[11px] transition-all ${
                    filterDirection === "INCOMING" ? "bg-emerald-600 text-black font-bold" : "text-emerald-400 hover:text-emerald-300"
                  }`}
                >
                  Incoming
                </button>
                <button
                  onClick={() => setFilterDirection("OUTGOING")}
                  className={`px-2.5 py-1 rounded text-[11px] transition-all ${
                    filterDirection === "OUTGOING" ? "bg-rose-600 text-white font-bold" : "text-rose-400 hover:text-rose-300"
                  }`}
                >
                  Outgoing
                </button>
              </div>
            </div>

            {/* Transactions Table */}
            {filteredTxs.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-400 font-mono">
                No transactions match the selected filter.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0a0f1d] border-b border-[#1b2848] text-slate-400 font-mono uppercase text-[10px] tracking-wider">
                    <tr>
                      <th className="py-3 px-4">TXID</th>
                      <th className="py-3 px-4">Direction</th>
                      <th className="py-3 px-4">Net Value (BTC)</th>
                      <th className="py-3 px-4">Miner Fee</th>
                      <th className="py-3 px-4">Block / Status</th>
                      <th className="py-3 px-4">Timestamp (UTC)</th>
                      <th className="py-3 px-4 text-right">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#16233d]">
                    {filteredTxs.map((tx) => {
                      const isExpanded = expandedTxid === tx.txid;
                      const isIncoming = tx.flow_direction === "INCOMING";
                      const isOutgoing = tx.flow_direction === "OUTGOING";

                      return (
                        <React.Fragment key={tx.txid}>
                          <tr className="hover:bg-[#121c33]/70 transition-colors">
                            {/* TXID */}
                            <td className="py-3.5 px-4 font-mono">
                              <div className="flex items-center space-x-1.5">
                                <span className="text-cyan-400 font-bold" title={tx.txid}>
                                  {tx.txid.slice(0, 8)}...{tx.txid.slice(-8)}
                                </span>
                                <button
                                  onClick={() => copyToClipboard(tx.txid, tx.txid)}
                                  className="text-slate-500 hover:text-cyan-300 p-0.5"
                                  title="Copy full TXID"
                                >
                                  <Copy className="w-3 h-3" />
                                </button>
                              </div>
                            </td>

                            {/* Direction */}
                            <td className="py-3.5 px-4 font-mono">
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded border inline-flex items-center space-x-1 ${
                                  isIncoming
                                    ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/50"
                                    : isOutgoing
                                    ? "bg-rose-950/60 text-rose-400 border-rose-800/50"
                                    : "bg-slate-900/60 text-slate-300 border-slate-700/50"
                                }`}
                              >
                                {isIncoming ? (
                                  <ArrowDownLeft className="w-3 h-3" />
                                ) : (
                                  <ArrowUpRight className="w-3 h-3" />
                                )}
                                <span>{tx.flow_direction}</span>
                              </span>
                            </td>

                            {/* Net Value */}
                            <td className="py-3.5 px-4 font-mono font-bold">
                              <span className={isIncoming ? "text-emerald-400" : isOutgoing ? "text-rose-400" : "text-slate-300"}>
                                {tx.net_value_btc > 0 ? `+${tx.net_value_btc}` : tx.net_value_btc} BTC
                              </span>
                              <span className="text-[10px] text-slate-500 block font-normal">
                                {tx.net_value_sats.toLocaleString()} Sats
                              </span>
                            </td>

                            {/* Miner Fee */}
                            <td className="py-3.5 px-4 font-mono text-slate-300 text-[11px]">
                              <span>{tx.fee_sats.toLocaleString()} Sats</span>
                              <span className="text-[10px] text-slate-500 block">
                                {tx.fee_btc} BTC
                              </span>
                            </td>

                            {/* Block / Confirmation */}
                            <td className="py-3.5 px-4 font-mono text-[11px]">
                              {tx.confirmed ? (
                                <div className="flex items-center space-x-1 text-emerald-400">
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  <span>Block #{tx.block_height}</span>
                                </div>
                              ) : (
                                <span className="text-amber-400 font-bold">0-Conf (Mempool)</span>
                              )}
                            </td>

                            {/* Timestamp */}
                            <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300">
                              {tx.block_time_iso || "Unconfirmed"}
                            </td>

                            {/* Expand Inputs/Outputs and Preserve */}
                            <td className="py-3.5 px-4 text-right">
                              <div className="flex items-center justify-end space-x-1.5">
                                <Link
                                  href={`/evidence?case_id=${caseIdParam || ""}&wallet=${walletStats.address}&txid=${tx.txid}&amount=${Math.abs(tx.net_value_btc)}`}
                                  className="bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 px-2 py-1 rounded text-[11px] font-mono transition-all inline-flex items-center"
                                  title="Preserve this transaction as forensic evidence"
                                >
                                  Preserve
                                </Link>
                                <button
                                  onClick={() => setExpandedTxid(isExpanded ? null : tx.txid)}
                                  className="bg-[#1b2a4a] hover:bg-cyan-600 text-cyan-300 hover:text-white px-2 py-1 rounded text-[11px] font-mono transition-all inline-flex items-center space-x-1"
                                >
                                  <span>{isExpanded ? "Hide" : "Inspect"}</span>
                                  {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                </button>
                              </div>
                            </td>
                          </tr>

                          {/* Expanded Inputs / Outputs Detail Drawer */}
                          {isExpanded && (
                            <tr className="bg-[#0b1220]">
                              <td colSpan={7} className="p-4 border-b border-[#1b2848]">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                                  {/* Inputs */}
                                  <div className="bg-[#10182a] border border-[#1b2848] p-3 rounded">
                                    <span className="text-[10px] uppercase font-bold text-rose-400 block mb-2">
                                      Inputs ({tx.inputs.length})
                                    </span>
                                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                                      {tx.inputs.map((inItem, idx) => (
                                        <div
                                          key={idx}
                                          className="flex items-center justify-between text-[11px] py-1 border-b border-[#18233c] last:border-0"
                                        >
                                          <span className="text-slate-300 truncate max-w-[200px]" title={inItem.address || "Coinbase / Unknown"}>
                                            {inItem.address || "Coinbase"}
                                          </span>
                                          <span className="text-slate-400">{inItem.value_btc} BTC</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>

                                  {/* Outputs */}
                                  <div className="bg-[#10182a] border border-[#1b2848] p-3 rounded">
                                    <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-2">
                                      Outputs ({tx.outputs.length})
                                    </span>
                                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                                      {tx.outputs.map((outItem, idx) => (
                                        <div
                                          key={idx}
                                          className="flex items-center justify-between text-[11px] py-1 border-b border-[#18233c] last:border-0"
                                        >
                                          <span className="text-slate-300 truncate max-w-[200px]" title={outItem.address || "OP_RETURN / Script"}>
                                            {outItem.address || "OP_RETURN"}
                                          </span>
                                          <span className="text-slate-400">{outItem.value_btc} BTC</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function WalletInvestigationPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-slate-400 font-mono">Loading investigation canvas...</div>}>
      <WalletInvestigationContent />
    </Suspense>
  );
}
