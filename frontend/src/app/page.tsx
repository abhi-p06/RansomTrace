"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  FolderLock,
  Cpu,
  Activity,
  Archive,
  ShieldAlert,
  AlertTriangle,
  Clock,
  ExternalLink,
  RefreshCw,
  PlusCircle,
  FileDown,
  FileCheck,
  Hash,
  Coins,
  ChevronRight,
  TrendingUp,
  Scale
} from "lucide-react";
import { getDashboardSummary, DashboardStatsResponse } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const fetchDashboard = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDashboardSummary();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    getDashboardSummary()
      .then((data) => {
        if (isMounted) setStats(data);
      })
      .catch((err) => {
        if (isMounted) setError(err instanceof Error ? err.message : "Failed to load dashboard metrics.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2500);
  };

  const getSeverityBadgeClass = (severity: string) => {
    const s = severity.toLowerCase();
    if (s.includes("critical")) return "bg-rose-950/80 text-rose-300 border-rose-800/80";
    if (s.includes("high")) return "bg-orange-950/80 text-orange-300 border-orange-800/80";
    if (s.includes("medium") || s.includes("elevated")) return "bg-amber-950/80 text-amber-300 border-amber-800/80";
    return "bg-emerald-950/80 text-emerald-300 border-emerald-800/80";
  };

  const getStatusBadgeClass = (status: string) => {
    const s = status.toLowerCase();
    if (s.includes("open")) return "bg-cyan-950/80 text-cyan-300 border-cyan-800/80";
    if (s.includes("investigating")) return "bg-blue-950/80 text-blue-300 border-blue-800/80";
    if (s.includes("contained")) return "bg-emerald-950/80 text-emerald-300 border-emerald-800/80";
    return "bg-slate-900 text-slate-400 border-slate-800";
  };

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Top Banner / Heading */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono mb-1">
            <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="uppercase tracking-widest font-semibold">
              Cybercrime Investigation & Cryptocurrency Forensics Platform
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Security Operations & Forensic Command Center
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-3xl">
            Real-time telemetry, Bitcoin ledger dispersal tracking, Isolation Forest anomaly heuristics,
            and court-admissible Section 65B forensic report synthesis.
          </p>
        </div>

        {/* Global Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboard}
            disabled={loading}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono rounded-lg flex items-center gap-2 transition-all disabled:opacity-50"
            title="Refresh Real-time Metrics"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
            Sync
          </button>
          <Link
            href="/cases"
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold rounded-lg flex items-center gap-2 shadow-lg shadow-cyan-950/50 transition-all"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            New Investigation
          </Link>
        </div>
      </div>

      {/* Error State Banner */}
      {error && (
        <div className="p-4 bg-red-950/50 border border-red-800 text-red-300 rounded-xl flex items-center justify-between gap-3 text-sm">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchDashboard}
            className="px-3 py-1 bg-red-900/60 hover:bg-red-800 text-white text-xs font-mono rounded border border-red-700"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && !stats ? (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-24 bg-slate-900/60 border border-slate-800 rounded-xl animate-pulse" />
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 h-96 bg-slate-900/60 border border-slate-800 rounded-xl animate-pulse" />
            <div className="h-96 bg-slate-900/60 border border-slate-800 rounded-xl animate-pulse" />
          </div>
        </div>
      ) : stats?.is_empty ? (
        /* Empty State */
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-16 text-center max-w-xl mx-auto my-12 space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-cyan-950/50 border border-cyan-800/60 flex items-center justify-center mx-auto text-cyan-400">
            <FolderLock className="w-8 h-8" />
          </div>
          <h2 className="text-lg font-bold text-white">No investigations yet</h2>
          <p className="text-sm text-slate-400 max-w-sm mx-auto leading-relaxed">
            Create your first investigation to begin tracking ransomware extortion payments, analyzing Bitcoin UTXOs,
            and generating forensic reports.
          </p>
          <div className="pt-2">
            <Link
              href="/cases"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-lg text-sm shadow-lg shadow-cyan-950/50"
            >
              <PlusCircle className="w-4 h-4" />
              Create First Investigation
            </Link>
          </div>
        </div>
      ) : stats ? (
        /* Operational Metrics & Sections */
        <div className="space-y-6">
          {/* 6 Key Stat Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {/* Card 1: Active Cases */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                <span>ACTIVE CASES</span>
                <FolderLock className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-bold font-mono text-white block">
                  {stats.active_cases_count}
                </span>
                <span className="text-[11px] text-cyan-400 font-mono">Open & Investigating</span>
              </div>
            </div>

            {/* Card 2: Total Investigations */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                <span>TOTAL DOSSIERS</span>
                <Activity className="w-4 h-4 text-blue-400" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-bold font-mono text-white block">
                  {stats.total_cases_count}
                </span>
                <span className="text-[11px] text-slate-400 font-mono">All-time Dockets</span>
              </div>
            </div>

            {/* Card 3: Wallets Analyzed */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                <span>WALLETS ANALYZED</span>
                <Cpu className="w-4 h-4 text-amber-400" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-bold font-mono text-amber-300 block">
                  {stats.wallets_analyzed_count}
                </span>
                <span className="text-[11px] text-slate-400 font-mono">Distinct Addresses</span>
              </div>
            </div>

            {/* Card 4: Transactions Analyzed */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                <span>TRANSACTIONS</span>
                <Coins className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-bold font-mono text-emerald-300 block">
                  {stats.transactions_analyzed_count}
                </span>
                <span className="text-[11px] text-slate-400 font-mono">Ledger Spends & Snapshots</span>
              </div>
            </div>

            {/* Card 5: Evidence Items */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                <span>EVIDENCE ITEMS</span>
                <Archive className="w-4 h-4 text-purple-400" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-bold font-mono text-purple-300 block">
                  {stats.evidence_items_count}
                </span>
                <span className="text-[11px] text-slate-400 font-mono">SHA-256 Sealed</span>
              </div>
            </div>

            {/* Card 6: High/Critical Cases */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                <span>HIGH / CRITICAL</span>
                <ShieldAlert className="w-4 h-4 text-rose-400" />
              </div>
              <div className="mt-2">
                <span className="text-2xl font-bold font-mono text-rose-400 block">
                  {stats.high_critical_risk_cases_count}
                </span>
                <span className="text-[11px] text-rose-300 font-mono">Immediate Priority</span>
              </div>
            </div>
          </div>

          {/* Main 2-Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column (2 Cols): Recent Cases + Recent Evidence + Anomalies */}
            <div className="lg:col-span-2 space-y-6">
              {/* 1. Recent Investigations */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                      <FolderLock className="w-4 h-4 text-cyan-400" />
                      RECENT INVESTIGATION DOSSIERS
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Active ransomware extortion and fund-tracing cases in command center.
                    </p>
                  </div>
                  <Link
                    href="/cases"
                    className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                  >
                    View All Cases <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="py-2.5 px-3">CASE ID</th>
                        <th className="py-2.5 px-3">INCIDENT TITLE</th>
                        <th className="py-2.5 px-3">SEVERITY</th>
                        <th className="py-2.5 px-3">STATUS</th>
                        <th className="py-2.5 px-3 text-right">ACTION</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {stats.recent_cases.map((c) => (
                        <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-2.5 px-3 font-bold text-white">
                            <Link href={`/cases/${c.id}`} className="hover:text-cyan-400 transition-colors">
                              {c.case_id}
                            </Link>
                          </td>
                          <td className="py-2.5 px-3 font-sans text-slate-200 max-w-xs truncate">
                            {c.title}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${getSeverityBadgeClass(c.severity)}`}>
                              {c.severity.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded text-[11px] font-medium border ${getStatusBadgeClass(c.status)}`}>
                              {c.status}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-right">
                            <Link
                              href={`/cases/${c.id}`}
                              className="text-cyan-400 hover:text-cyan-300 font-sans text-xs underline font-medium"
                            >
                              Inspect Dossier
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 2. Transaction Activity (Blockchain Ledger Telemetry) */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                      <Coins className="w-4 h-4 text-emerald-400" />
                      TRANSACTION ACTIVITY & LEDGER SPENDS
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Real-time Bitcoin blockchain transaction flow and observed wallet dispersals.
                    </p>
                  </div>
                  <Link
                    href="/analytics"
                    className="text-xs font-mono text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                  >
                    Analytics Matrix <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                {(!stats.recent_transactions || stats.recent_transactions.length === 0) ? (
                  <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-400 text-center">
                    Zero transaction spends recorded yet. Query an address in Blockchain Ingestion.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-2.5 px-3">TRANSACTION HASH</th>
                          <th className="py-2.5 px-3">ASSOCIATED WALLET</th>
                          <th className="py-2.5 px-3">AMOUNT (BTC)</th>
                          <th className="py-2.5 px-3">FLOW DIRECTION</th>
                          <th className="py-2.5 px-3 text-right">STATUS</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-slate-300">
                        {stats.recent_transactions.map((tx, idx) => (
                          <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                            <td className="py-2.5 px-3">
                              <button
                                onClick={() => copyToClipboard(tx.tx_hash)}
                                className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 group"
                                title="Click to copy Tx Hash"
                              >
                                <span className="truncate max-w-[150px]">{tx.tx_hash}</span>
                                <Hash className="w-3 h-3 text-slate-500 group-hover:text-cyan-400" />
                              </button>
                            </td>
                            <td className="py-2.5 px-3 text-slate-400 max-w-[140px] truncate">
                              {tx.wallet_address || "Multi-Input Tap"}
                            </td>
                            <td className="py-2.5 px-3 font-bold text-white">
                              {tx.amount_btc.toFixed(4)} BTC
                            </td>
                            <td className="py-2.5 px-3">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                tx.direction === "INCOMING"
                                  ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                                  : "bg-rose-950 text-rose-300 border-rose-800"
                              }`}>
                                {tx.direction}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-right">
                              <span className="text-[11px] text-emerald-400 font-bold">
                                {tx.status} ✓
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* 3. Recent Evidence Preserved */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                      <Archive className="w-4 h-4 text-emerald-400" />
                      RECENT EVIDENCE ARTIFACTS
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Cryptographically preserved digital evidence with RFC 8785 SHA-256 hashes.
                    </p>
                  </div>
                  <Link
                    href="/evidence"
                    className="text-xs font-mono text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                  >
                    Evidence Locker <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="py-2.5 px-3">EVIDENCE ID</th>
                        <th className="py-2.5 px-3">TYPE</th>
                        <th className="py-2.5 px-3">SHA-256 DIGEST</th>
                        <th className="py-2.5 px-3">SEIZED BY</th>
                        <th className="py-2.5 px-3 text-right">TIMESTAMP</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {stats.recent_evidence.map((ev) => (
                        <tr key={ev.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-2.5 px-3 text-slate-400">{ev.id.slice(0, 8)}...</td>
                          <td className="py-2.5 px-3">
                            <span className="px-2 py-0.5 rounded text-[11px] bg-slate-950 border border-slate-800 text-cyan-300">
                              {ev.artifact_type}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <button
                              onClick={() => copyToClipboard(ev.sha256_hash)}
                              className="flex items-center gap-1.5 text-sky-400 hover:text-sky-300 group"
                              title="Click to copy SHA-256"
                            >
                              <span className="truncate max-w-[160px]">{ev.sha256_hash}</span>
                              <Hash className="w-3 h-3 text-slate-500 group-hover:text-cyan-400" />
                            </button>
                          </td>
                          <td className="py-2.5 px-3 font-sans text-slate-300">{ev.captured_by}</td>
                          <td className="py-2.5 px-3 text-right text-slate-400">
                            {new Date(ev.seized_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 3. Recent Anomalous Activity (ML Isolation Forest) */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                      <Cpu className="w-4 h-4 text-rose-400" />
                      RECENT ANOMALOUS ACTIVITY (ML ISOLATION FOREST)
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Unsupervised anomaly partitions measuring topological deviation from public ledger norms.
                    </p>
                  </div>
                  <Link
                    href="/ml-risk"
                    className="text-xs font-mono text-rose-400 hover:text-rose-300 flex items-center gap-1"
                  >
                    AI Matrix <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                {stats.recent_anomalies.length === 0 ? (
                  <div className="text-center py-6 text-slate-500 text-xs font-mono">
                    No machine learning anomaly scans logged yet.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {stats.recent_anomalies.map((anom) => (
                      <div
                        key={anom.id}
                        className="p-3 bg-slate-950/80 border border-slate-800/80 rounded-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-cyan-300 font-bold">
                              {anom.wallet_address || "Multi-Address Scan"}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950 text-rose-300 border border-rose-800">
                              {anom.classification}
                            </span>
                          </div>
                          <p className="text-slate-400 font-sans text-xs">
                            {anom.explanation || "Topological clustering indicative of automated rapid liquidation."}
                          </p>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="text-lg font-bold font-mono text-rose-400 block">
                            {anom.normalized_score.toFixed(1)} <span className="text-[10px] text-slate-500">/ 100</span>
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            Raw Score: {anom.raw_anomaly_score.toFixed(4)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right Column (1 Col): Risk Distribution + Timeline */}
            <div className="space-y-6">
              {/* 1. Risk Tier Distribution */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    RISK TIER DISTRIBUTION
                  </h3>
                  <Link href="/risk" className="text-xs text-amber-400 hover:text-amber-300 font-mono">
                    Scoring Engine →
                  </Link>
                </div>

                <div className="space-y-3 text-xs">
                  {/* Critical */}
                  <div>
                    <div className="flex justify-between mb-1 font-mono">
                      <span className="text-rose-400 font-bold flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-rose-500" /> CRITICAL (80–100)
                      </span>
                      <span className="text-white font-bold">{stats.risk_distribution.critical} cases</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="bg-rose-500 h-full rounded-full transition-all"
                        style={{
                          width: `${Math.min(100, (stats.risk_distribution.critical / Math.max(1, stats.total_cases_count)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* High */}
                  <div>
                    <div className="flex justify-between mb-1 font-mono">
                      <span className="text-orange-400 font-bold flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-orange-500" /> HIGH (60–79)
                      </span>
                      <span className="text-white font-bold">{stats.risk_distribution.high} cases</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="bg-orange-500 h-full rounded-full transition-all"
                        style={{
                          width: `${Math.min(100, (stats.risk_distribution.high / Math.max(1, stats.total_cases_count)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Medium */}
                  <div>
                    <div className="flex justify-between mb-1 font-mono">
                      <span className="text-amber-400 font-bold flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-amber-500" /> MEDIUM (30–59)
                      </span>
                      <span className="text-white font-bold">{stats.risk_distribution.medium} cases</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="bg-amber-500 h-full rounded-full transition-all"
                        style={{
                          width: `${Math.min(100, (stats.risk_distribution.medium / Math.max(1, stats.total_cases_count)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Low */}
                  <div>
                    <div className="flex justify-between mb-1 font-mono">
                      <span className="text-emerald-400 font-bold flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-500" /> LOW (0–29)
                      </span>
                      <span className="text-white font-bold">{stats.risk_distribution.low} cases</span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="bg-emerald-500 h-full rounded-full transition-all"
                        style={{
                          width: `${Math.min(100, (stats.risk_distribution.low / Math.max(1, stats.total_cases_count)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-slate-950/80 rounded border border-slate-800 text-[11px] text-slate-400 leading-relaxed font-sans">
                  Risk distributions combine behavioral rule contributions (50%) and unsupervised Isolation Forest anomaly scoring (50%)
                  to guide investigator prioritization.
                </div>
              </div>

              {/* 2. Investigation Timeline */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                    <Clock className="w-4 h-4 text-cyan-400" />
                    INVESTIGATION TIMELINE
                  </h3>
                  <span className="text-xs text-slate-500 font-mono">Audit Trail</span>
                </div>

                {stats.timeline_events.length === 0 ? (
                  <div className="text-center py-6 text-slate-500 text-xs font-mono">
                    No chronological events recorded yet.
                  </div>
                ) : (
                  <div className="relative pl-4 space-y-4 before:content-[''] before:absolute before:left-1 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                    {stats.timeline_events.map((evt) => (
                      <div key={evt.event_id} className="relative text-xs">
                        <div className="absolute -left-[19px] top-1 w-2.5 h-2.5 rounded-full bg-cyan-500 ring-4 ring-slate-900" />
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-white font-mono">{evt.title}</span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {new Date(evt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <p className="text-slate-400 font-sans text-[11px] mt-0.5 leading-relaxed">
                          {evt.description}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 3. Quick Forensic Navigation */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                <h4 className="text-xs font-bold text-white uppercase font-mono tracking-wider">
                  Investigative Subsystems
                </h4>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <Link
                    href="/ingestion"
                    className="p-2.5 bg-slate-950 hover:bg-slate-800 rounded border border-slate-800 text-slate-300 hover:text-cyan-400 flex items-center gap-2 transition-colors"
                  >
                    <Coins className="w-3.5 h-3.5 text-amber-400" />
                    Ledger Lookup
                  </Link>
                  <Link
                    href="/graph"
                    className="p-2.5 bg-slate-950 hover:bg-slate-800 rounded border border-slate-800 text-slate-300 hover:text-cyan-400 flex items-center gap-2 transition-colors"
                  >
                    <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                    Fund Flow
                  </Link>
                  <Link
                    href="/evidence"
                    className="p-2.5 bg-slate-950 hover:bg-slate-800 rounded border border-slate-800 text-slate-300 hover:text-cyan-400 flex items-center gap-2 transition-colors"
                  >
                    <Archive className="w-3.5 h-3.5 text-purple-400" />
                    Evidence Locker
                  </Link>
                  <Link
                    href="/reports"
                    className="p-2.5 bg-slate-950 hover:bg-slate-800 rounded border border-slate-800 text-slate-300 hover:text-cyan-400 flex items-center gap-2 transition-colors"
                  >
                    <FileDown className="w-3.5 h-3.5 text-rose-400" />
                    PDF Reports
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
