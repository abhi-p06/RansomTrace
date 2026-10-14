"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Cpu,
  ShieldAlert,
  Search,
  AlertTriangle,
  CheckCircle2,
  Info,
  Clock,
  Database,
  ArrowRight,
  TrendingUp,
  BarChart3,
  Layers,
  Sparkles,
  Copy,
  Check,
  ChevronRight,
  FileText,
  HelpCircle,
  Activity,
  Zap,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { runMLAnalysis, getMLHistory, getMLModelInfo, getCases } from "@/lib/api";
import {
  MLAnalysisResponse,
  MLAnalysisHistoryItem,
  ModelInfo,
  InvestigationCase,
  FeatureItem,
} from "@/lib/types";

// Preset known wallets for quick investigator demonstrations
const DEMO_PRESETS = [
  {
    label: "Demonstration Ransomware Simulation (Active Case)",
    address: "1DemoRansomCollectionWallet002",
    type: "Demonstration Extortion Vault (Synthetic)",
  },
  {
    label: "WannaCry Ransomware Pool",
    address: "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
    type: "Known Ransomware Syndicate (High Inflow/Peeling)",
  },
  {
    label: "Satoshi Genesis / Dormant",
    address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    type: "Historic Genesis Inflow (Low Outflow)",
  },
];

function AIAnalysisContent() {
  const searchParams = useSearchParams();
  const initialAddr = searchParams.get("address") || "";
  const initialCase = searchParams.get("case_id") || "";

  const [addressInput, setAddressInput] = useState(initialAddr);
  const [selectedCaseId, setSelectedCaseId] = useState<string>(initialCase);
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<MLAnalysisResponse | null>(null);
  const [historyList, setHistoryList] = useState<MLAnalysisHistoryItem[]>([]);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [copiedExplanation, setCopiedExplanation] = useState(false);

  // Load cases and model info on initial render
  useEffect(() => {
    async function loadMetadata() {
      try {
        const [casesRes, infoRes] = await Promise.all([
          getCases().catch(() => []),
          getMLModelInfo().catch(() => null),
        ]);
        setCases(casesRes);
        if (infoRes) setModelInfo(infoRes);
        if (initialCase) {
          setSelectedCaseId(initialCase);
        } else if (casesRes.length > 0) {
          const demo = casesRes.find(c => c.case_id.includes("DEMO") || c.case_id.includes("WANNACRY"));
          if (demo) setSelectedCaseId(demo.id);
        }
      } catch (err) {
        console.error("Error loading metadata:", err);
      }
    }
    loadMetadata();
  }, [initialCase]);

  useEffect(() => {
    if (initialAddr) {
      setAddressInput(initialAddr);
      const timer = setTimeout(() => {
        handleExecuteScan(initialAddr);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [initialAddr]);

  const handleExecuteScan = async (targetAddr?: string) => {
    const addr = (targetAddr || addressInput).trim();
    if (!addr) {
      setError("Please enter a valid Bitcoin wallet address to analyze.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await runMLAnalysis(addr, selectedCaseId || undefined);
      setAnalysisResult(result);
      setAddressInput(addr);

      // Refresh history list
      const hist = await getMLHistory(addr).catch(() => []);
      setHistoryList(hist);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to execute ML anomaly detection";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedExplanation(true);
    setTimeout(() => setCopiedExplanation(false), 2000);
  };

  // Color mappings based on classification
  const getClassificationBadge = (classification: string) => {
    switch (classification) {
      case "HIGH ANOMALY":
        return {
          bg: "bg-rose-950/40 border-rose-600/60 text-rose-300",
          dot: "bg-rose-500 shadow-[0_0_8px_#f43f5e]",
          desc: "Statistical outlier: Extreme velocity, peel chain splits, or clustered bursts.",
        };
      case "MEDIUM ANOMALY":
        return {
          bg: "bg-amber-950/40 border-amber-600/60 text-amber-300",
          dot: "bg-amber-500 shadow-[0_0_8px_#f59e0b]",
          desc: "Moderate deviation: Notable counterparty dispersion or burst clustering.",
        };
      case "LOW ANOMALY":
        return {
          bg: "bg-cyan-950/40 border-cyan-600/60 text-cyan-300",
          dot: "bg-cyan-500 shadow-[0_0_8px_#06b6d4]",
          desc: "Mild variance: Minor transactional deviation from baseline medians.",
        };
      default:
        return {
          bg: "bg-emerald-950/40 border-emerald-600/60 text-emerald-300",
          dot: "bg-emerald-500 shadow-[0_0_8px_#10b981]",
          desc: "Standard transactional profile within normal baseline behavioral thresholds.",
        };
    }
  };

  // Prepare chart data from feature breakdown (deviation ratios)
  const chartData = analysisResult
    ? analysisResult.feature_breakdown.map((f) => ({
        name: f.label.replace(" (BTC)", "").replace(" (tx/day)", "").replace(" (tx/hr)", ""),
        deviation: f.deviation_ratio,
        actual: f.value,
        median: f.baseline_median,
        unit: f.name.includes("btc") ? "BTC" : "",
      }))
    : [];

  return (
    <div className="space-y-8 pb-16">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
              Module 6 • Machine Learning Forensics
            </span>
            <span className="text-xs font-mono text-slate-500">Isolation Forest (scikit-learn)</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-100 flex items-center gap-3">
            <Cpu className="w-7 h-7 text-cyan-400" />
            AI Transaction Anomaly Detection
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Unsupervised behavioral outlier identification across 12 high-dimensional transaction vectors.
            Scores deviation from reference Bitcoin usage distributions without fabricated ground-truth accuracy.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Engine: IsolationForest (100 Trees)
          </div>
        </div>
      </div>

      {/* Query Bar */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
          <div className="md:col-span-7 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Enter Bitcoin address (Base58Check / Bech32 native segwit)..."
              value={addressInput}
              onChange={(e) => setAddressInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleExecuteScan()}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div className="md:col-span-3">
            <select
              value={selectedCaseId}
              onChange={(e) => setSelectedCaseId(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-300 focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer"
            >
              <option value="">-- Associate with Forensic Case (Optional) --</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  [{c.case_id}] {c.title.substring(0, 30)}
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <button
              onClick={() => handleExecuteScan()}
              disabled={loading}
              className="w-full h-full py-2.5 px-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-cyan-950/50 disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Run AI Scan
                </>
              )}
            </button>
          </div>
        </div>

        {/* Demo Presets Bar */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80 text-xs">
          <span className="text-slate-400 font-mono flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-amber-400" /> Presets:
          </span>
          {DEMO_PRESETS.map((p) => (
            <button
              key={p.address}
              onClick={() => {
                setAddressInput(p.address);
                handleExecuteScan(p.address);
              }}
              className="px-2.5 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-cyan-700/60 rounded text-slate-300 font-mono transition-colors flex items-center gap-1.5"
            >
              <span>{p.label}</span>
              <span className="text-[10px] text-slate-500">({p.address.substring(0, 8)}...)</span>
            </button>
          ))}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/60 text-rose-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-rose-200">Analysis Error</div>
            <div className="text-xs text-rose-300/80 mt-0.5">{error}</div>
          </div>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && !analysisResult && (
        <div className="p-12 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-4">
          <div className="inline-flex p-4 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-400 animate-pulse">
            <Cpu className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <div className="text-lg font-semibold text-slate-200 font-mono">
              Extracting High-Dimensional Blockchain Features...
            </div>
            <div className="text-xs text-slate-400 max-w-md mx-auto">
              Querying public Bitcoin ledger transactions, computing amount variance, peel chains,
              velocity clusters, and running tree partitioning in Isolation Forest...
            </div>
          </div>
        </div>
      )}

      {/* Results Deck */}
      {analysisResult && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Top Score Cards Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Anomaly Gauge & Score Card */}
            <div className="lg:col-span-5 p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between relative overflow-hidden shadow-xl">
              <div className="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
                <Cpu className="w-32 h-32 text-cyan-400" />
              </div>

              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                    Investigative Anomaly Indicator
                  </span>
                  <span className="text-xs font-mono text-slate-500">Scale: 0.0 - 100.0</span>
                </div>

                <div className="flex items-baseline gap-4 mb-2">
                  <span className="text-5xl lg:text-6xl font-extrabold tracking-tight text-white font-mono">
                    {analysisResult.normalized_score.toFixed(1)}
                  </span>
                  <div className="space-y-0.5">
                    <span className="text-xs font-mono text-slate-400">/ 100.0 Normalized</span>
                    <div className="text-xs font-mono text-slate-500">
                      Raw Score: <span className="text-slate-300">{analysisResult.raw_anomaly_score.toFixed(4)}</span>
                    </div>
                  </div>
                </div>

                {/* Progress Meter */}
                <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800 mb-4">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      analysisResult.normalized_score > 75
                        ? "bg-rose-500 shadow-[0_0_12px_#f43f5e]"
                        : analysisResult.normalized_score > 55
                        ? "bg-amber-500 shadow-[0_0_12px_#f59e0b]"
                        : analysisResult.normalized_score > 30
                        ? "bg-cyan-500 shadow-[0_0_12px_#06b6d4]"
                        : "bg-emerald-500 shadow-[0_0_12px_#10b981]"
                    }`}
                    style={{ width: `${Math.max(5, analysisResult.normalized_score)}%` }}
                  ></div>
                </div>

                {/* Classification Badge */}
                {(() => {
                  const badge = getClassificationBadge(analysisResult.classification);
                  return (
                    <div
                      className={`p-3.5 rounded-lg border flex items-center justify-between gap-3 ${badge.bg}`}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className={`w-3 h-3 rounded-full ${badge.dot}`}></span>
                        <div>
                          <div className="text-sm font-bold tracking-wider font-mono">
                            {analysisResult.classification}
                          </div>
                          <div className="text-[11px] text-slate-400 mt-0.5">{badge.desc}</div>
                        </div>
                      </div>
                      <div className="text-right text-[11px] font-mono text-slate-400">
                        {analysisResult.is_anomaly ? "Outlier Detected" : "Inlier Region"}
                      </div>
                    </div>
                  );
                })()}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between font-mono">
                <span>Address: {analysisResult.wallet_address.substring(0, 16)}...</span>
                <span>Scanned: {new Date(analysisResult.analysis_timestamp).toLocaleTimeString()}</span>
              </div>
            </div>

            {/* Forensic Behavioral Explanation Card */}
            <div className="lg:col-span-7 p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between shadow-xl">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                      Behavioural Anomaly Narrative
                    </h2>
                  </div>
                  <button
                    onClick={() => copyToClipboard(analysisResult.explanation)}
                    className="px-2.5 py-1 text-xs font-mono text-slate-400 hover:text-slate-200 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    {copiedExplanation ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        Copy Narrative
                      </>
                    )}
                  </button>
                </div>

                <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800/80 text-slate-200 text-sm leading-relaxed font-sans mb-4">
                  {analysisResult.explanation}
                </div>

                {/* Key Drivers Quick Badges */}
                <div className="space-y-2">
                  <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                    Primary Deviating Vectors:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.feature_breakdown
                      .filter((f) => f.deviation_ratio >= 2.0 && f.value > 0)
                      .slice(0, 4)
                      .map((f) => (
                        <div
                          key={f.name}
                          className="px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 flex items-center gap-1.5"
                        >
                          <TrendingUp className="w-3 h-3 text-cyan-400" />
                          <span>{f.label}:</span>
                          <span className="text-cyan-400 font-bold">{f.deviation_ratio}x</span>
                        </div>
                      ))}
                    {analysisResult.feature_breakdown.filter((f) => f.deviation_ratio >= 2.0).length ===
                      0 && (
                      <span className="text-xs font-mono text-emerald-400">
                        No extreme deviations detected (All features within 2x baseline)
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Forensic Safeguard Notice */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2 text-[11px] text-amber-400/90 font-mono">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                <span>
                  Investigative Indicator Only: Statistical deviation does NOT prove ransomware or criminal ownership.
                </span>
              </div>
            </div>
          </div>

          {/* Feature Breakdown Table & Deviation Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Chart: Feature Deviation Ratios */}
            <div className="lg:col-span-7 p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-cyan-400" />
                  <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                    Feature Deviation vs. Baseline Median
                  </h2>
                </div>
                <span className="text-xs font-mono text-slate-500">1.0x = Standard Profile Median</span>
              </div>

              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                    <XAxis
                      type="number"
                      stroke="#64748b"
                      fontSize={11}
                      tickFormatter={(v) => `${v}x`}
                    />
                    <YAxis
                      dataKey="name"
                      type="category"
                      stroke="#94a3b8"
                      fontSize={11}
                      tickLine={false}
                      width={120}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono shadow-xl space-y-1">
                              <div className="font-bold text-slate-200">{data.name}</div>
                              <div className="text-cyan-400">
                                Deviation: <span className="font-bold">{data.deviation}x baseline</span>
                              </div>
                              <div className="text-slate-400">
                                Observed Value: {data.actual} {data.unit}
                              </div>
                              <div className="text-slate-500">
                                Baseline Median: {data.median} {data.unit}
                              </div>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="deviation" radius={[0, 4, 4, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={
                            entry.deviation >= 5.0
                              ? "#f43f5e"
                              : entry.deviation >= 2.0
                              ? "#f59e0b"
                              : entry.deviation < 0.5
                              ? "#06b6d4"
                              : "#10b981"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Model Architecture & Academic Evaluation Methodology */}
            <div className="lg:col-span-5 p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Database className="w-4 h-4 text-cyan-400" />
                  <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                    Model Architecture & Governance
                  </h2>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 font-mono space-y-1.5">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Algorithm:</span>
                      <span className="text-cyan-300 font-semibold">Isolation Forest</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Ensemble Estimators:</span>
                      <span className="text-slate-200">100 Trees</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Contamination Factor:</span>
                      <span className="text-slate-200">0.10 (10% Prior)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Random State Seed:</span>
                      <span className="text-slate-200">42 (Strictly Deterministic)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Input Feature Dimensions:</span>
                      <span className="text-slate-200">12 Quantitative Vectors</span>
                    </div>
                  </div>

                  {/* Evaluation Methodology Callout */}
                  <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-cyan-400 font-mono font-semibold">
                      <HelpCircle className="w-3.5 h-3.5" />
                      Unsupervised Evaluation Method
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                      {analysisResult.evaluation_notes}
                    </p>
                  </div>
                </div>
              </div>

              {/* Full Legal / Forensic Disclaimer */}
              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/40 text-[11px] text-amber-300/80 leading-relaxed">
                <span className="font-bold text-amber-200 font-mono block mb-1">
                  CRITICAL FORENSIC LIMITATION
                </span>
                {analysisResult.disclaimer}
              </div>
            </div>
          </div>

          {/* Full 12-Feature Detail Table */}
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                  Extracted Behavioural Features Matrix
                </h2>
              </div>
              <span className="text-xs font-mono text-slate-500">12 Vectors Engineered</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/60">
                    <th className="py-2.5 px-3">Feature Name</th>
                    <th className="py-2.5 px-3">Extracted Value</th>
                    <th className="py-2.5 px-3">Baseline Median</th>
                    <th className="py-2.5 px-3">Deviation Ratio</th>
                    <th className="py-2.5 px-3">Forensic Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {analysisResult.feature_breakdown.map((f) => (
                    <tr key={f.name} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-2.5 px-3 font-semibold text-slate-200">{f.label}</td>
                      <td className="py-2.5 px-3 text-cyan-400 font-bold">
                        {f.value}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">{f.baseline_median}</td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                            f.deviation_ratio >= 5.0
                              ? "bg-rose-950/60 text-rose-300 border border-rose-800"
                              : f.deviation_ratio >= 2.0
                              ? "bg-amber-950/60 text-amber-300 border border-amber-800"
                              : "bg-slate-950 text-slate-400 border border-slate-800"
                          }`}
                        >
                          {f.deviation_ratio}x
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-400 font-sans text-[11px]">
                        {f.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Historical Scans Audit Drawer */}
          {historyList.length > 0 && (
            <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                    Audit Log: Previous ML Scans for this Address
                  </h2>
                </div>
                <span className="text-xs font-mono text-slate-500">
                  {historyList.length} scans preserved in DB
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/60">
                      <th className="py-2.5 px-3">Scan ID</th>
                      <th className="py-2.5 px-3">Classification</th>
                      <th className="py-2.5 px-3">Normalized Score</th>
                      <th className="py-2.5 px-3">Raw Score</th>
                      <th className="py-2.5 px-3">Timestamp (UTC)</th>
                      <th className="py-2.5 px-3">Case Association</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {historyList.map((h) => (
                      <tr key={h.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-2.5 px-3 text-slate-500 text-[11px]">
                          {h.id.substring(0, 8)}...
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              h.classification === "HIGH ANOMALY"
                                ? "text-rose-300 bg-rose-950/50"
                                : h.classification === "MEDIUM ANOMALY"
                                ? "text-amber-300 bg-amber-950/50"
                                : h.classification === "LOW ANOMALY"
                                ? "text-cyan-300 bg-cyan-950/50"
                                : "text-emerald-300 bg-emerald-950/50"
                            }`}
                          >
                            {h.classification}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-200 font-bold">
                          {h.normalized_score.toFixed(1)} / 100
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">{h.raw_anomaly_score.toFixed(4)}</td>
                        <td className="py-2.5 px-3 text-slate-400">
                          {new Date(h.created_at).toLocaleString()}
                        </td>
                        <td className="py-2.5 px-3 text-slate-500">
                          {h.case_id ? `Case ${h.case_id.substring(0, 8)}` : "Standalone"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function AIAnalysisPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-slate-400 font-mono">Loading AI anomaly canvas...</div>}>
      <AIAnalysisContent />
    </Suspense>
  );
}
