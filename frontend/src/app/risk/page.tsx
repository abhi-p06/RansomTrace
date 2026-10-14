"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  ShieldAlert,
  Search,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Scale,
  Zap,
  Clock,
  Layers,
  Sparkles,
  Copy,
  Check,
  TrendingUp,
  Activity,
  BarChart3,
  HelpCircle,
  FileText,
  Sliders,
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
import { assessWalletRisk, getRiskHistory, getCases } from "@/lib/api";
import {
  RiskAssessmentResponse,
  RiskAssessmentHistoryItem,
  InvestigationCase,
  RuleContribution,
} from "@/lib/types";

const DEMO_PRESETS = [
  {
    label: "Demonstration Ransomware Simulation (Active Case)",
    address: "1DemoRansomCollectionWallet002",
    type: "Demonstration Extortion Vault (Synthetic)",
  },
  {
    label: "WannaCry Ransomware Pool",
    address: "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94",
    type: "Confirmed Ransomware Inflow/Peeling Pool",
  },
  {
    label: "Satoshi Genesis / Inactive",
    address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    type: "Historic Genesis Inflow (Low Outflow)",
  },
];

function RiskAnalysisContent() {
  const searchParams = useSearchParams();
  const initialAddr = searchParams.get("address") || "";
  const initialCase = searchParams.get("case_id") || "";

  const [addressInput, setAddressInput] = useState(initialAddr);
  const [selectedCaseId, setSelectedCaseId] = useState<string>(initialCase);
  const [includeMl, setIncludeMl] = useState<boolean>(true);
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [assessment, setAssessment] = useState<RiskAssessmentResponse | null>(null);
  const [historyList, setHistoryList] = useState<RiskAssessmentHistoryItem[]>([]);
  const [copiedReasons, setCopiedReasons] = useState(false);

  useEffect(() => {
    async function loadCases() {
      try {
        const cList = await getCases().catch(() => []);
        setCases(cList);
        if (initialCase) {
          setSelectedCaseId(initialCase);
        } else if (cList.length > 0) {
          const demo = cList.find(c => c.case_id.includes("DEMO") || c.case_id.includes("WANNACRY"));
          if (demo) setSelectedCaseId(demo.id);
        }
      } catch (err) {
        console.error("Error loading cases:", err);
      }
    }
    loadCases();
  }, [initialCase]);

  useEffect(() => {
    if (initialAddr) {
      setAddressInput(initialAddr);
      const timer = setTimeout(() => {
        handleAssessRisk(initialAddr);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [initialAddr]);

  const handleAssessRisk = async (targetAddr?: string) => {
    const addr = (targetAddr || addressInput).trim();
    if (!addr) {
      setError("Please enter a valid Bitcoin wallet address to assess.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await assessWalletRisk(addr, selectedCaseId || undefined, includeMl);
      setAssessment(res);
      setAddressInput(addr);

      // Load history
      const hist = await getRiskHistory(addr).catch(() => []);
      setHistoryList(hist);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to run risk assessment";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const copyReasonsToClipboard = () => {
    if (!assessment) return;
    const text = [
      `RANSOMTRACE INVESTIGATIVE RISK ASSESSMENT`,
      `Wallet: ${assessment.wallet_address}`,
      `Final Score: ${assessment.final_score}/100 (${assessment.risk_level})`,
      `Rule Score: ${assessment.rule_score}/100 (Weight: ${assessment.weights.rule_weight})`,
      `ML Anomaly Score: ${assessment.ml_score ?? "N/A"}/100 (Weight: ${assessment.weights.ml_weight})`,
      `\nContributing Factors:`,
      ...assessment.reasons.map((r, i) => `${i + 1}. ${r}`),
      `\nDISCLAIMER: ${assessment.disclaimer}`,
    ].join("\n");

    navigator.clipboard.writeText(text);
    setCopiedReasons(true);
    setTimeout(() => setCopiedReasons(false), 2000);
  };

  // Color styles per risk tier
  const getTierStyles = (tier: string) => {
    switch (tier) {
      case "CRITICAL":
        return {
          badgeBg: "bg-rose-950/60 border-rose-600/80 text-rose-300",
          dot: "bg-rose-500 shadow-[0_0_10px_#f43f5e]",
          text: "text-rose-400",
          barColor: "bg-rose-500",
          summary: "Severe topological anomalies, rapid peeling cascades, and clustered bursts.",
        };
      case "HIGH":
        return {
          badgeBg: "bg-orange-950/60 border-orange-600/80 text-orange-300",
          dot: "bg-orange-500 shadow-[0_0_10px_#f97316]",
          text: "text-orange-400",
          barColor: "bg-orange-500",
          summary: "Significant risk indicators, rapid velocity, and broad counterparty churn.",
        };
      case "MEDIUM":
        return {
          badgeBg: "bg-amber-950/60 border-amber-600/80 text-amber-300",
          dot: "bg-amber-500 shadow-[0_0_10px_#f59e0b]",
          text: "text-amber-400",
          barColor: "bg-amber-500",
          summary: "Moderate behavioral deviations or minor burst clustering.",
        };
      default:
        return {
          badgeBg: "bg-emerald-950/60 border-emerald-600/80 text-emerald-300",
          dot: "bg-emerald-500 shadow-[0_0_10px_#10b981]",
          text: "text-emerald-400",
          barColor: "bg-emerald-500",
          summary: "Standard transactional profile within normal personal boundaries.",
        };
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono uppercase tracking-wider text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800">
              Module 7 • Forensic Risk Scoring
            </span>
            <span className="text-xs font-mono text-slate-500">Hybrid Behavioral & ML Engine</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-100 flex items-center gap-3">
            <ShieldAlert className="w-7 h-7 text-rose-400" />
            Hybrid Investigative Risk Engine
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Calculates an investigative prioritization risk score (0–100) combining 7 transparent behavioral
            rules with unsupervised Isolation Forest ML anomaly scoring.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono flex items-center gap-2 text-slate-300">
            <Scale className="w-3.5 h-3.5 text-cyan-400" />
            Formula: 50% Rules + 50% ML
          </div>
        </div>
      </div>

      {/* Query Bar */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
          <div className="md:col-span-6 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Enter Bitcoin address (e.g. 13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94)..."
              value={addressInput}
              onChange={(e) => setAddressInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAssessRisk()}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-rose-500 transition-colors"
            />
          </div>

          <div className="md:col-span-3">
            <select
              value={selectedCaseId}
              onChange={(e) => setSelectedCaseId(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-300 focus:outline-none focus:border-rose-500 transition-colors cursor-pointer"
            >
              <option value="">-- Associate Case (Optional) --</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  [{c.case_id}] {c.title.substring(0, 28)}
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-3 flex gap-2">
            <button
              onClick={() => handleAssessRisk()}
              disabled={loading}
              className="flex-1 py-2.5 px-4 bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 text-white rounded-lg text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-rose-950/50 disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  Scoring...
                </>
              ) : (
                <>
                  <ShieldAlert className="w-4 h-4" />
                  Assess Risk
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preset Wallets & ML Toggle */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800/80 text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-slate-400 font-mono flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Presets:
            </span>
            {DEMO_PRESETS.map((p) => (
              <button
                key={p.address}
                onClick={() => {
                  setAddressInput(p.address);
                  handleAssessRisk(p.address);
                }}
                className="px-2.5 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-rose-700/60 rounded text-slate-300 font-mono transition-colors flex items-center gap-1.5 cursor-pointer"
              >
                <span>{p.label}</span>
                <span className="text-[10px] text-slate-500">({p.address.substring(0, 8)}...)</span>
              </button>
            ))}
          </div>

          <label className="flex items-center gap-2 cursor-pointer text-slate-300 font-mono select-none">
            <input
              type="checkbox"
              checked={includeMl}
              onChange={(e) => setIncludeMl(e.target.checked)}
              className="rounded bg-slate-950 border-slate-800 text-rose-500 focus:ring-rose-500 h-3.5 w-3.5"
            />
            <span className="text-xs">Include ML Isolation Forest Contribution</span>
          </label>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-800/60 text-rose-300 text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-rose-200">Assessment Error</div>
            <div className="text-xs text-rose-300/80 mt-0.5">{error}</div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {assessment && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Top Primary Indicators Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* FINAL RISK SCORE & TIER CARD */}
            <div className="lg:col-span-5 p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
                <ShieldAlert className="w-32 h-32 text-rose-500" />
              </div>

              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                    FINAL RISK SCORE
                  </span>
                  <span className="text-xs font-mono text-slate-500">Scale: 0.0 - 100.0</span>
                </div>

                <div className="flex items-baseline gap-4 mb-2">
                  <span className="text-6xl font-extrabold tracking-tight text-white font-mono">
                    {assessment.final_score.toFixed(1)}
                  </span>
                  <div className="space-y-0.5">
                    <span className="text-xs font-mono text-slate-400">/ 100.0 Priority</span>
                    <div className="text-xs font-mono text-slate-500">
                      Tier: <span className="font-bold text-slate-200">{assessment.risk_level}</span>
                    </div>
                  </div>
                </div>

                {/* Score Progress Bar */}
                {(() => {
                  const style = getTierStyles(assessment.risk_level);
                  return (
                    <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800 mb-4">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${style.barColor}`}
                        style={{ width: `${Math.max(5, assessment.final_score)}%` }}
                      ></div>
                    </div>
                  );
                })()}

                {/* RISK LEVEL BADGE */}
                {(() => {
                  const style = getTierStyles(assessment.risk_level);
                  return (
                    <div className={`p-4 rounded-lg border flex items-center justify-between gap-3 ${style.badgeBg}`}>
                      <div className="flex items-center gap-3">
                        <span className={`w-3.5 h-3.5 rounded-full ${style.dot}`}></span>
                        <div>
                          <div className="text-base font-extrabold tracking-wider font-mono">
                            RISK LEVEL: {assessment.risk_level}
                          </div>
                          <div className="text-xs text-slate-300 mt-0.5">{style.summary}</div>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* Dual Sub-Score Indicators */}
                <div className="grid grid-cols-2 gap-3 mt-4">
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-[11px] font-mono text-slate-400 uppercase">RULE-BASED SCORE</div>
                    <div className="text-lg font-bold text-amber-400 font-mono mt-0.5">
                      {assessment.rule_score.toFixed(1)}{" "}
                      <span className="text-xs text-slate-500">
                        (Weight: {intPercent(assessment.weights.rule_weight)}%)
                      </span>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-[11px] font-mono text-slate-400 uppercase">ML ANOMALY SCORE</div>
                    <div className="text-lg font-bold text-cyan-400 font-mono mt-0.5">
                      {assessment.ml_score !== null && assessment.ml_score !== undefined
                        ? `${assessment.ml_score.toFixed(1)} `
                        : "N/A "}
                      <span className="text-xs text-slate-500">
                        (Weight: {intPercent(assessment.weights.ml_weight)}%)
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Assessment Meta Footer */}
              <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between font-mono">
                <span>Address: {assessment.wallet_address.substring(0, 16)}...</span>
                <span>Assessed: {new Date(assessment.assessed_at).toLocaleTimeString()}</span>
              </div>
            </div>

            {/* CONTRIBUTING FACTORS & REASONS */}
            <div className="lg:col-span-7 p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between shadow-xl">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-rose-400" />
                    <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                      CONTRIBUTING FACTORS & REASONS
                    </h2>
                  </div>
                  <button
                    onClick={copyReasonsToClipboard}
                    className="px-2.5 py-1 text-xs font-mono text-slate-400 hover:text-slate-200 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    {copiedReasons ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        Copy Dossier Note
                      </>
                    )}
                  </button>
                </div>

                <div className="space-y-2 mb-4">
                  {assessment.reasons.map((reason, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 text-slate-200 text-xs leading-relaxed flex items-start gap-2.5 font-sans"
                    >
                      <span className="w-4 h-4 rounded-full bg-slate-900 border border-slate-700 text-slate-400 flex items-center justify-center text-[10px] font-mono shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span>{reason}</span>
                    </div>
                  ))}
                </div>

                {/* Score Breakdown Bar Visualization */}
                <div className="space-y-2">
                  <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                    Hybrid Weight Composition:
                  </span>
                  <div className="w-full bg-slate-950 h-5 rounded-md overflow-hidden flex border border-slate-800 font-mono text-[10px]">
                    <div
                      className="bg-amber-600/70 h-full flex items-center justify-center text-amber-200 font-bold transition-all"
                      style={{ width: `${intPercent(assessment.weights.rule_weight)}%` }}
                    >
                      Rules ({intPercent(assessment.weights.rule_weight)}%)
                    </div>
                    {assessment.weights.ml_weight > 0 && (
                      <div
                        className="bg-cyan-600/70 h-full flex items-center justify-center text-cyan-200 font-bold transition-all"
                        style={{ width: `${intPercent(assessment.weights.ml_weight)}%` }}
                      >
                        ML Anomaly ({intPercent(assessment.weights.ml_weight)}%)
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* MANDATORY INVESTIGATIVE DISCLAIMER */}
              <div className="mt-4 p-3.5 rounded-lg bg-amber-950/20 border border-amber-800/50 text-[11px] text-amber-300/90 leading-relaxed font-sans">
                <span className="font-bold text-amber-200 font-mono block mb-0.5 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  MANDATORY INVESTIGATIVE DISCLAIMER
                </span>
                {assessment.disclaimer}
              </div>
            </div>
          </div>

          {/* RULE-BASED INDICATORS BREAKDOWN TABLE */}
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-400" />
                <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                  RULE-BASED INDICATORS (TRANSPARENT FORENSIC RULES)
                </h2>
              </div>
              <span className="text-xs font-mono text-slate-500">
                Rule Contribution: {assessment.rule_score.toFixed(1)} / 100.0 pts
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/60">
                    <th className="py-2.5 px-3">Rule Name</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Observed On-Chain Value</th>
                    <th className="py-2.5 px-3">Trigger Threshold</th>
                    <th className="py-2.5 px-3">Points Awarded</th>
                    <th className="py-2.5 px-3">Forensic Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {assessment.rule_contributions.map((rule) => (
                    <tr
                      key={rule.rule_id}
                      className={rule.triggered ? "bg-slate-950/40 hover:bg-slate-800/40" : "hover:bg-slate-800/20"}
                    >
                      <td className="py-3 px-3 font-semibold text-slate-200">{rule.rule_name}</td>
                      <td className="py-3 px-3 text-slate-400">{rule.category}</td>
                      <td className="py-3 px-3">
                        {rule.triggered ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950/70 text-rose-300 border border-rose-800 flex items-center gap-1 w-fit">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse"></span>
                            TRIGGERED
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-500 bg-slate-950 border border-slate-800">
                            Clear
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 text-cyan-300 font-bold">{rule.observed_value}</td>
                      <td className="py-3 px-3 text-slate-400">{rule.threshold}</td>
                      <td className="py-3 px-3 font-bold">
                        <span className={rule.triggered ? "text-amber-400" : "text-slate-500"}>
                          +{rule.score_contribution.toFixed(1)} / {rule.max_score.toFixed(0)}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-400 font-sans text-[11px] max-w-xs">
                        {rule.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* ML ANOMALY DETAILS & WEIGHTING CARD */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6 p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                  ML ANOMALY COMPONENT
                </h2>
              </div>

              {assessment.ml_contribution.available ? (
                <div className="space-y-3 text-xs font-mono">
                  <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-400">ML Engine Status:</span>
                      <span className="text-emerald-400 font-bold">Active & Integrated</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Algorithm:</span>
                      <span className="text-slate-200">Isolation Forest (100 Trees)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Normalized Anomaly Score:</span>
                      <span className="text-cyan-400 font-bold">
                        {assessment.ml_contribution.normalized_score?.toFixed(1)} / 100.0
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Raw Decision Score:</span>
                      <span className="text-slate-300">
                        {assessment.ml_contribution.raw_anomaly_score?.toFixed(4)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">ML Classification Tier:</span>
                      <span className="text-amber-300 font-bold">
                        {assessment.ml_contribution.classification}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Model Weight in Final Score:</span>
                      <span className="text-slate-200">
                        {intPercent(assessment.ml_contribution.weight)}%
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
                  <div className="font-semibold text-slate-300 font-mono">ML Score Not Active / Fallback Mode</div>
                  <div>
                    The assessment engine gracefully operated in 100% transparent behavioral rule mode.
                  </div>
                </div>
              )}
            </div>

            {/* RISK TIERS SITEMAP & GUIDELINES */}
            <div className="lg:col-span-6 p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-rose-400" />
                <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                  RISK TIER THRESHOLDS & INTERPRETATION
                </h2>
              </div>

              <div className="grid grid-cols-2 gap-2.5 text-xs font-mono">
                <div className="p-3 rounded-lg bg-slate-950 border border-emerald-900/60">
                  <div className="font-bold text-emerald-400">LOW (0 - 29)</div>
                  <div className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Standard personal or dormant wallet behavior.
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-amber-900/60">
                  <div className="font-bold text-amber-400">MEDIUM (30 - 59)</div>
                  <div className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Minor burst clustering or asymmetric counterparty churn.
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-orange-900/60">
                  <div className="font-bold text-orange-400">HIGH (60 - 79)</div>
                  <div className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Elevated velocity, multiple bursts, and fund dispersion.
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-rose-900/60">
                  <div className="font-bold text-rose-400">CRITICAL (80 - 100)</div>
                  <div className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Extensive peel chains, rapid liquidation, and severe ML outlier.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Audit History Drawer */}
          {historyList.length > 0 && (
            <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
                    Prior Risk Assessments for this Address
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
                      <th className="py-2.5 px-3">Assessment ID</th>
                      <th className="py-2.5 px-3">Risk Level</th>
                      <th className="py-2.5 px-3">Final Score</th>
                      <th className="py-2.5 px-3">Assessed At (UTC)</th>
                      <th className="py-2.5 px-3">Case</th>
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
                              h.risk_tier === "CRITICAL"
                                ? "text-rose-300 bg-rose-950/50"
                                : h.risk_tier === "HIGH"
                                ? "text-orange-300 bg-orange-950/50"
                                : h.risk_tier === "MEDIUM"
                                ? "text-amber-300 bg-amber-950/50"
                                : "text-emerald-300 bg-emerald-950/50"
                            }`}
                          >
                            {h.risk_tier}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-200 font-bold">
                          {h.risk_score.toFixed(1)} / 100
                        </td>
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

function intPercent(val: number): number {
  return Math.round(val * 100);
}

export default function RiskAnalysisPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-400">Loading risk analysis...</div>}>
      <RiskAnalysisContent />
    </Suspense>
  );
}
