"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  Cell
} from "recharts";
import {
  Activity,
  Search,
  RefreshCw,
  Coins,
  TrendingUp,
  Clock,
  Zap,
  Users,
  AlertTriangle,
  ArrowDownLeft,
  ArrowUpRight,
  ShieldAlert,
  Copy,
  ExternalLink,
  SlidersHorizontal,
  Flame
} from "lucide-react";
import { getWalletAnalytics } from "@/lib/api";
import { WalletAnalyticsResponse } from "@/lib/types";

const SAMPLE_TARGETS = [
  { name: "Demo Investigation (Active)", address: "1DemoRansomCollectionWallet002" },
  { name: "WannaCry Extortion Hub", address: "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94" },
  { name: "DarkSide Ransomware", address: "145EUshA4pwv6VPupsmBJAa3kwnY4o6D7S" },
  { name: "Genesis Block Reward", address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" },
];

const HISTOGRAM_COLORS = ["#00e5ff", "#38bdf8", "#818cf8", "#f59e0b", "#ef4444"];

function AnalyticsContent() {
  const searchParams = useSearchParams();
  const initialAddr = searchParams.get("address") || "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94";

  const [addressInput, setAddressInput] = useState(initialAddr);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<WalletAnalyticsResponse | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const fetchAnalytics = async (targetAddr?: string) => {
    const addr = (targetAddr || addressInput).trim();
    if (!addr) {
      setError("Please provide a valid Bitcoin address to analyze.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getWalletAnalytics(addr, 100);
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compute behavioral analytics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialAddr) {
      const timer = setTimeout(() => {
        setAddressInput(initialAddr);
        fetchAnalytics(initialAddr);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [initialAddr]);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1b2848] gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono mb-1">
            <Activity className="w-3.5 h-3.5" />
            <span className="uppercase tracking-widest font-semibold">
              Module 4 & 5 · Behavioural Cryptocurrency Profiling
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Wallet Behavioural & Flow Analytics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real calculated metrics extracted from public blockchain transactions: temporal velocity, volume dynamics, burst detection, and counterparty graphs.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            href={`/ingestion?address=${encodeURIComponent(addressInput)}`}
            className="bg-[#121c33] hover:bg-[#1a2b4d] text-cyan-300 border border-[#1e2f54] px-3 py-1.5 rounded text-xs font-mono flex items-center space-x-1.5 transition-all"
          >
            <span>Raw Ingestion Ledger →</span>
          </Link>
        </div>
      </div>

      {/* Target Search & Query Bar */}
      <div className="bg-[#0e1628] border border-[#1b2848] p-5 rounded-lg space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetchAnalytics();
          }}
          className="flex flex-col md:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Enter Bitcoin address for forensic behavioral profiling..."
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
                <span>Computing Metrics...</span>
              </>
            ) : (
              <>
                <Activity className="w-4 h-4" />
                <span>Analyze Behavior</span>
              </>
            )}
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#18233c] text-xs">
          <span className="text-[11px] font-mono text-slate-400">Exemplary Target Profiles:</span>
          {SAMPLE_TARGETS.map((sample) => (
            <button
              key={sample.address}
              onClick={() => {
                setAddressInput(sample.address);
                fetchAnalytics(sample.address);
              }}
              className="bg-[#121c33] hover:bg-[#1b2a4a] text-cyan-300 border border-[#1e2f54] hover:border-cyan-500/40 px-2.5 py-1 rounded text-[11px] font-mono transition-all"
            >
              <span>{sample.name}</span>
            </button>
          ))}
        </div>

        {error && (
          <div className="bg-rose-950/60 border border-rose-800 text-rose-300 p-3 rounded-md text-xs font-mono flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Main Analytics Dashboard */}
      {analytics && (
        <div className="space-y-6">
          {/* Target Identity Strip */}
          <div className="bg-[#0e1628] border border-cyan-500/30 p-4 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-cyan-950/70 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
                <Coins className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider">
                    {analytics.address_type} Target
                  </span>
                  <span className="text-slate-600">·</span>
                  <span className="text-[10px] font-mono text-emerald-400">
                    {analytics.total_tx_count} Transactions Processed
                  </span>
                </div>
                <span className="text-sm font-bold font-mono text-white tracking-wide break-all">
                  {analytics.address}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => copyToClipboard(analytics.address, "addr")}
                className="bg-[#121c33] hover:bg-[#1a2b4d] text-slate-300 px-3 py-1.5 rounded text-xs font-mono flex items-center space-x-1.5 border border-[#1e2f54]"
              >
                <Copy className="w-3.5 h-3.5 text-cyan-400" />
                <span>{copiedText === "addr" ? "Copied!" : "Copy"}</span>
              </button>
            </div>
          </div>

          {/* 6 Key Statistical & Velocity Indicator Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {/* Avg Tx Amount */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-3 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Mean Tx Value
              </span>
              <span className="text-base font-bold font-mono text-white mt-1 block">
                {analytics.avg_tx_amount_btc} BTC
              </span>
              <span className="text-[10px] font-mono text-slate-500 block">
                {analytics.avg_tx_amount_sats.toLocaleString()} Sats
              </span>
            </div>

            {/* Median Tx Amount */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-3 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Median Value
              </span>
              <span className="text-base font-bold font-mono text-cyan-300 mt-1 block">
                {analytics.median_tx_amount_btc} BTC
              </span>
              <span className="text-[10px] font-mono text-slate-500 block">
                {analytics.median_tx_amount_sats.toLocaleString()} Sats
              </span>
            </div>

            {/* Standard Deviation */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-3 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Amount Std Dev
              </span>
              <span className="text-base font-bold font-mono text-purple-300 mt-1 block">
                ±{analytics.tx_amount_std_dev_btc} BTC
              </span>
              <span className="text-[10px] font-mono text-slate-500 block">
                Variance Dispersion
              </span>
            </div>

            {/* Transaction Velocity */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-3 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Daily Velocity
              </span>
              <span className="text-base font-bold font-mono text-emerald-300 mt-1 block">
                {analytics.tx_frequency_per_day} TXs/Day
              </span>
              <span className="text-[10px] font-mono text-slate-500 block">
                Across {analytics.active_lifespan_days} Days
              </span>
            </div>

            {/* In/Out Ratio */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-3 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                In/Out Ratio
              </span>
              <span className="text-base font-bold font-mono text-amber-300 mt-1 block">
                {analytics.incoming_outgoing_ratio}:1
              </span>
              <span className="text-[10px] font-mono text-slate-500 block">
                {analytics.incoming_tx_count} In / {analytics.outgoing_tx_count} Out
              </span>
            </div>

            {/* Unique Counterparties */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-3 rounded-lg">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Counterparties
              </span>
              <span className="text-base font-bold font-mono text-cyan-400 mt-1 block">
                {analytics.unique_counterparties_count}
              </span>
              <span className="text-[10px] font-mono text-slate-500 block">
                Connected Wallets
              </span>
            </div>
          </div>

          {/* Interactive Chart 1: Transaction Volume Over Time (Inflow vs Outflow) */}
          <div className="bg-[#0e1628] border border-[#1b2848] p-5 rounded-lg space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-[#1b2848]">
              <div>
                <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-cyan-400" />
                  <span>1. Cryptocurrency Volume Dynamics Over Time</span>
                </h3>
                <span className="text-[11px] text-slate-400 font-mono">
                  Daily incoming extortion inflows (Green) vs. outgoing disbursement/peel outflows (Red)
                </span>
              </div>
            </div>

            {analytics.volume_over_time.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-xs text-slate-500 font-mono">
                No historical time points available for this wallet.
              </div>
            ) : (
              <div className="h-72 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics.volume_over_time}>
                    <defs>
                      <linearGradient id="colorIncoming" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                      </linearGradient>
                      <linearGradient id="colorOutgoing" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10, fill: "#94a3b8" }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10, fill: "#94a3b8" }} unit=" BTC" />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "11px", color: "#f8fafc" }}
                    />
                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                    <Area
                      type="monotone"
                      dataKey="incoming_btc"
                      name="Incoming Inflow (BTC)"
                      stroke="#10b981"
                      fillOpacity={1}
                      fill="url(#colorIncoming)"
                    />
                    <Area
                      type="monotone"
                      dataKey="outgoing_btc"
                      name="Outgoing Outflow (BTC)"
                      stroke="#f43f5e"
                      fillOpacity={1}
                      fill="url(#colorOutgoing)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Grid: Chart 2 (Amount Distribution) & Bursts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart 2: Amount Distribution Histogram */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-5 rounded-lg space-y-3">
              <div className="pb-3 border-b border-[#1b2848]">
                <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center space-x-2">
                  <SlidersHorizontal className="w-4 h-4 text-cyan-400" />
                  <span>2. Transaction Amount Distribution</span>
                </h3>
                <span className="text-[11px] text-slate-400 font-mono">
                  Histogram across Micro, Small, Medium, High, and Whale payment tiers
                </span>
              </div>

              <div className="h-64 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.amount_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="label" stroke="#64748b" tick={{ fontSize: 10, fill: "#94a3b8" }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10, fill: "#94a3b8" }} unit="%" />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "11px" }}
                      formatter={(val: unknown, _name: unknown, item: { payload?: { count?: number; range_btc?: string } }) => [
                        `${String(val)}% (${item.payload?.count ?? 0} TXs)`,
                        `Tier: ${item.payload?.range_btc ?? ""}`
                      ]}
                    />
                    <Bar dataKey="percentage" name="Percentage of Total Transfers" radius={[4, 4, 0, 0]}>
                      {analytics.amount_distribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={HISTOGRAM_COLORS[index % HISTOGRAM_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 3: Activity Bursts & Temporal Clusters */}
            <div className="bg-[#0e1628] border border-[#1b2848] p-5 rounded-lg space-y-3">
              <div className="pb-3 border-b border-[#1b2848] flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center space-x-2">
                    <Flame className="w-4 h-4 text-amber-400" />
                    <span>3. Activity Bursts & Rapid Clustering</span>
                  </h3>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Clusters of ≥3 transactions executed within a 60-minute window
                  </span>
                </div>
                <span className="text-xs font-mono font-bold text-amber-400 bg-amber-950/60 border border-amber-800/40 px-2 py-0.5 rounded">
                  {analytics.burst_count} Detected
                </span>
              </div>

              {analytics.activity_bursts.length === 0 ? (
                <div className="h-64 flex flex-col items-center justify-center text-xs text-slate-400 font-mono space-y-2">
                  <Clock className="w-8 h-8 text-slate-600" />
                  <p>No high-density activity bursts identified for this address.</p>
                  <span className="text-[10px] text-slate-500">Transfers were spaced over normal distribution intervals.</span>
                </div>
              ) : (
                <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
                  {analytics.activity_bursts.map((b, idx) => (
                    <div
                      key={idx}
                      className="bg-[#121c33] border border-[#1e2f54] hover:border-amber-500/40 p-3 rounded-md transition-all text-xs font-mono space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-amber-400 font-bold flex items-center space-x-1.5">
                          <Zap className="w-3.5 h-3.5 text-amber-400" />
                          <span>Burst #{idx + 1}: {b.tx_count} Transfers</span>
                        </span>
                        <span className="text-[11px] text-slate-400">Duration: {b.duration_minutes} min</span>
                      </div>
                      <div className="text-[11px] text-slate-300 flex items-center justify-between">
                        <span>Window: {b.start_time_iso}</span>
                        <span className="text-slate-500">→ {b.end_time_iso}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Table: Top Counterparties Analysis */}
          <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg overflow-hidden space-y-3">
            <div className="p-4 border-b border-[#1b2848]">
              <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider flex items-center space-x-2">
                <Users className="w-4 h-4 text-cyan-400" />
                <span>4. Connected Counterparty Ledger & Wallet Roles</span>
              </h3>
              <span className="text-[11px] text-slate-400 font-mono">
                Top unique wallets interacting with this investigated target ranked by satoshi volume
              </span>
            </div>

            {analytics.top_counterparties.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500 font-mono">
                No counterparties discovered in loaded transaction window.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0a0f1d] border-b border-[#1b2848] text-slate-400 font-mono uppercase text-[10px] tracking-wider">
                    <tr>
                      <th className="py-3 px-4">Counterparty Wallet</th>
                      <th className="py-3 px-4">Interaction Role</th>
                      <th className="py-3 px-4">Transfer Frequency</th>
                      <th className="py-3 px-4">Total Volume (BTC)</th>
                      <th className="py-3 px-4 text-right">Pivot Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#16233d]">
                    {analytics.top_counterparties.map((cp) => (
                      <tr key={cp.address} className="hover:bg-[#121c33]/70 transition-colors">
                        <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">
                          <span title={cp.address}>{cp.address}</span>
                        </td>
                        <td className="py-3.5 px-4 font-mono">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded border inline-flex items-center space-x-1 ${
                              cp.role === "SENDER"
                                ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/50"
                                : cp.role === "RECIPIENT"
                                ? "bg-rose-950/60 text-rose-400 border-rose-800/50"
                                : "bg-purple-950/60 text-purple-400 border-purple-800/50"
                            }`}
                          >
                            <span>{cp.role}</span>
                          </span>
                        </td>
                        <td className="py-3.5 px-4 font-mono text-slate-300">
                          {cp.tx_count} Transactions
                        </td>
                        <td className="py-3.5 px-4 font-mono font-bold text-white">
                          <span>{cp.total_btc} BTC</span>
                          <span className="text-[10px] text-slate-500 block font-normal">
                            {cp.total_sats.toLocaleString()} Sats
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <button
                            onClick={() => {
                              setAddressInput(cp.address);
                              fetchAnalytics(cp.address);
                            }}
                            className="bg-[#1b2a4a] hover:bg-cyan-600 text-cyan-300 hover:text-white px-2.5 py-1 rounded text-[11px] font-mono transition-all"
                          >
                            Pivot To Wallet
                          </button>
                        </td>
                      </tr>
                    ))}
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

export default function AnalyticsPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-slate-400 font-mono">Loading behavioral analytics...</div>}>
      <AnalyticsContent />
    </Suspense>
  );
}
