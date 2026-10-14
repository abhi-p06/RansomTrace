"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  FolderLock,
  Clock,
  ShieldAlert,
  Building,
  AlertTriangle,
  CheckCircle2,
  Trash2,
  Edit3,
  X,
  FileCheck,
  Cpu,
  Archive,
  RefreshCw,
  Coins,
  GitFork,
  FileDown,
  Activity,
  Hash,
  Scale,
  ExternalLink,
  ChevronRight,
  ShieldCheck
} from "lucide-react";
import {
  getCase,
  updateCase,
  deleteCase,
  getCaseEvidence,
  getReportPreview,
  getReportPdfUrl,
  verifyEvidenceIntegrity,
  EvidenceItem,
  ReportPreviewResponse
} from "@/lib/api";
import { InvestigationCase, CaseStatus, CaseSeverity, CaseUpdateInput } from "@/lib/types";

type CaseTab =
  | "summary"
  | "wallets"
  | "transactions"
  | "graph"
  | "ml"
  | "risk"
  | "evidence"
  | "custody"
  | "reports";

const SEVERITY_COLORS: Record<CaseSeverity, { bg: string; text: string; border: string }> = {
  Low: { bg: "bg-slate-900/60", text: "text-slate-300", border: "border-slate-700/50" },
  Medium: { bg: "bg-amber-950/60", text: "text-amber-300", border: "border-amber-800/50" },
  High: { bg: "bg-orange-950/60", text: "text-orange-300", border: "border-orange-800/50" },
  Critical: { bg: "bg-rose-950/60", text: "text-rose-300", border: "border-rose-800/60" },
};

const STATUS_COLORS: Record<CaseStatus, { bg: string; text: string; border: string }> = {
  Open: { bg: "bg-cyan-950/60", text: "text-cyan-300", border: "border-cyan-800/50" },
  Investigating: { bg: "bg-blue-950/60", text: "text-blue-300", border: "border-blue-800/50" },
  Contained: { bg: "bg-emerald-950/60", text: "text-emerald-300", border: "border-emerald-800/50" },
  Closed: { bg: "bg-slate-900/60", text: "text-slate-400", border: "border-slate-800/60" },
};

export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params?.id as string;

  const [activeTab, setActiveTab] = useState<CaseTab>("summary");
  const [caseData, setCaseData] = useState<InvestigationCase | null>(null);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [preview, setPreview] = useState<ReportPreviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Verification state
  const [verifyingId, setVerifyingId] = useState<string | null>(null);
  const [verifyMessage, setVerifyMessage] = useState<string | null>(null);

  // Edit Modal State
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState<CaseUpdateInput>({});
  const [saving, setSaving] = useState(false);

  const loadCaseDetails = async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getCase(caseId);
      setCaseData(data);
      setEditForm({
        title: data.title,
        incident_type: data.incident_type,
        target_label: data.target_label || "",
        description: data.description || "",
      });

      // Fetch case evidence and report synthesis preview in parallel
      try {
        const [evs, prev] = await Promise.all([
          getCaseEvidence(data.id),
          getReportPreview(data.id),
        ]);
        setEvidenceList(evs);
        setPreview(prev);
      } catch {
        // Fallback if preview or evidence is empty
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Case not found");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        const c = await getCase(caseId);
        if (!isMounted) return;
        setCaseData(c);

        try {
          const [evs, prev] = await Promise.all([
            getCaseEvidence(caseId),
            getReportPreview(caseId),
          ]);
          if (!isMounted) return;
          setEvidenceList(evs);
          setPreview(prev);
        } catch {
          // Fallback if preview or evidence is empty
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Case not found");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }, 0);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [caseId]);

  const handleStatusChange = async (newStatus: CaseStatus) => {
    if (!caseData) return;
    try {
      const updated = await updateCase(caseData.id, { status: newStatus });
      setCaseData(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update status");
    }
  };

  const handleSeverityChange = async (newSeverity: CaseSeverity) => {
    if (!caseData) return;
    try {
      const updated = await updateCase(caseData.id, { severity: newSeverity });
      setCaseData(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update severity");
    }
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseData) return;
    setSaving(true);
    try {
      const updated = await updateCase(caseData.id, editForm);
      setCaseData(updated);
      setShowEditModal(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save changes");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteCase = async () => {
    if (!caseData) return;
    if (confirm(`Are you sure you want to permanently delete case ${caseData.case_id}?`)) {
      try {
        await deleteCase(caseData.id);
        router.push("/cases");
      } catch (err) {
        alert(err instanceof Error ? err.message : "Failed to delete case");
      }
    }
  };

  const handleVerifyEvidence = async (evidenceId: string) => {
    try {
      setVerifyingId(evidenceId);
      const res = await verifyEvidenceIntegrity(evidenceId);
      setVerifyMessage(
        res.verified
          ? "INTEGRITY VERIFIED: SHA-256 matches canonical snapshot exactly."
          : `TAMPER DETECTED: Computed hash ${res.computed_hash.slice(0, 12)} differs!`
      );
      setTimeout(() => setVerifyMessage(null), 4000);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Verification error");
    } finally {
      setVerifyingId(null);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
        <p className="text-sm font-mono text-slate-400">Loading investigation case dossier...</p>
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="p-8 bg-red-950/40 border border-red-800 rounded-xl space-y-4 text-center max-w-lg mx-auto my-12">
        <AlertTriangle className="w-10 h-10 text-red-400 mx-auto" />
        <h2 className="text-lg font-bold text-white font-mono">Case Inquest Error</h2>
        <p className="text-xs text-red-300 font-sans">{error || "Investigation case not found."}</p>
        <Link
          href="/cases"
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-700 text-xs font-mono text-cyan-400 rounded-lg hover:bg-slate-800"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Return to Case Directory
        </Link>
      </div>
    );
  }

  const targetWallet = preview?.target_wallet || caseData.target_label || "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94";

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Back button & Action Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div className="space-y-1">
          <Link
            href="/cases"
            className="inline-flex items-center gap-1.5 text-xs font-mono text-slate-400 hover:text-cyan-400 transition-colors mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Case Dossiers
          </Link>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-white font-mono">
              {caseData.case_id}
            </h1>
            <span className={`px-2.5 py-0.5 text-xs font-bold rounded border ${SEVERITY_COLORS[caseData.severity as CaseSeverity].bg} ${SEVERITY_COLORS[caseData.severity as CaseSeverity].text} ${SEVERITY_COLORS[caseData.severity as CaseSeverity].border}`}>
              {caseData.severity.toUpperCase()}
            </span>
            <span className={`px-2.5 py-0.5 text-xs font-medium rounded border ${STATUS_COLORS[caseData.status as CaseStatus].bg} ${STATUS_COLORS[caseData.status as CaseStatus].text} ${STATUS_COLORS[caseData.status as CaseStatus].border}`}>
              {caseData.status}
            </span>
          </div>
          <p className="text-xs text-slate-400">{caseData.title}</p>
        </div>

        {/* Global Toolbar */}
        <div className="flex items-center gap-2.5">
          <a
            href={getReportPdfUrl(caseData.id)}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold rounded-lg flex items-center gap-2 shadow-lg shadow-cyan-950/50"
          >
            <FileDown className="w-3.5 h-3.5" />
            Generate PDF Report
          </a>
          <button
            onClick={() => setShowEditModal(true)}
            className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono rounded-lg flex items-center gap-1.5"
          >
            <Edit3 className="w-3.5 h-3.5" /> Edit
          </button>
          <button
            onClick={handleDeleteCase}
            className="px-3 py-2 bg-red-950/40 hover:bg-red-900/60 border border-red-800/60 text-red-300 text-xs font-mono rounded-lg flex items-center gap-1.5"
            title="Delete Dossier"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Global Verification Toast */}
      {verifyMessage && (
        <div className="p-3 bg-emerald-950/80 border border-emerald-700 text-emerald-300 rounded-lg text-xs font-mono flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{verifyMessage}</span>
        </div>
      )}

      {/* Navigation Tabs Bar */}
      <div className="flex items-center gap-1 border-b border-slate-800 overflow-x-auto text-xs font-mono">
        {[
          { id: "summary", label: "Case Summary", icon: FolderLock },
          { id: "wallets", label: "Wallets", icon: Cpu },
          { id: "transactions", label: "Transactions", icon: Coins },
          { id: "graph", label: "Fund Flow", icon: GitFork },
          { id: "ml", label: "AI Analysis", icon: Activity },
          { id: "risk", label: "Risk", icon: ShieldAlert },
          { id: "evidence", label: `Evidence (${evidenceList.length})`, icon: Archive },
          { id: "custody", label: "Chain of Custody", icon: FileCheck },
          { id: "reports", label: "Reports", icon: FileDown },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as CaseTab)}
              className={`px-3.5 py-2.5 rounded-t-lg border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
                isActive
                  ? "border-cyan-500 bg-slate-900/90 text-cyan-400 font-bold"
                  : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB CONTENT AREAS */}

      {/* 1. Case Summary Tab */}
      {activeTab === "summary" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-500 text-xs font-mono block">INCIDENT CLASSIFICATION</span>
              <span className="text-sm font-bold text-white mt-1 block">{caseData.incident_type}</span>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-500 text-xs font-mono block">TARGET ORGANIZATION</span>
              <span className="text-sm font-bold text-slate-200 mt-1 block">
                {caseData.target_label || "National Infrastructure"}
              </span>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-500 text-xs font-mono block">EVIDENCE INVENTORY</span>
              <span className="text-sm font-bold text-purple-300 mt-1 block">
                {evidenceList.length} Sealed Artifacts
              </span>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <span className="text-slate-500 text-xs font-mono block">PRIMARY WALLET</span>
              <span className="text-xs font-mono text-cyan-400 mt-1 block truncate">
                {targetWallet}
              </span>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase font-mono tracking-wider">
              Incident Narrative & Scope
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-wrap">
              {caseData.description || "No formal incident description entered yet."}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
              <span className="text-xs font-bold text-white font-mono flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-cyan-400" /> Operational Status Controls
              </span>
              <div className="flex flex-wrap gap-2 pt-1">
                {(["Open", "Investigating", "Contained", "Closed"] as CaseStatus[]).map((st) => (
                  <button
                    key={st}
                    onClick={() => handleStatusChange(st)}
                    className={`px-3 py-1 text-xs font-mono rounded border transition-colors ${
                      caseData.status === st
                        ? "bg-cyan-950 border-cyan-700 text-cyan-300 font-bold"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
              <span className="text-xs font-bold text-white font-mono flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-400" /> Severity Level Assignment
              </span>
              <div className="flex flex-wrap gap-2 pt-1">
                {(["Low", "Medium", "High", "Critical"] as CaseSeverity[]).map((sv) => (
                  <button
                    key={sv}
                    onClick={() => handleSeverityChange(sv)}
                    className={`px-3 py-1 text-xs font-mono rounded border transition-colors ${
                      caseData.severity === sv
                        ? "bg-rose-950 border-rose-700 text-rose-300 font-bold"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
                    }`}
                  >
                    {sv}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. Wallets Tab */}
      {activeTab === "wallets" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <Cpu className="w-4 h-4 text-cyan-400" />
                Target Extortion Wallets Under Investigation
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Public Bitcoin ledger addresses mapped to this extortion case docket.
              </p>
            </div>
            <Link
              href={`/ingestion?address=${encodeURIComponent(targetWallet)}`}
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              Live Blockchain Ingestion <ExternalLink className="w-3 h-3" />
            </Link>
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="text-[11px] text-slate-500 font-mono">PRIMARY EXTORTION ADDRESS</div>
              <div className="font-mono text-sm text-cyan-300 break-all">{targetWallet}</div>
              <div className="text-[11px] text-slate-400 font-mono">
                Format: Legacy Base58Check (P2PKH) • Mempool API Synchronized
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href={`/analytics?address=${encodeURIComponent(targetWallet)}`}
                className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono text-slate-200 rounded"
              >
                Behavioural Analytics
              </Link>
              <Link
                href={`/graph?address=${encodeURIComponent(targetWallet)}`}
                className="px-3 py-1.5 bg-cyan-950/80 hover:bg-cyan-900/60 border border-cyan-800 text-xs font-mono text-cyan-300 rounded"
              >
                Fund Flow Graph
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* 3. Transactions Tab */}
      {activeTab === "transactions" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <Coins className="w-4 h-4 text-emerald-400" />
                Case Blockchain Transactions
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Observed transaction spends, ransom inflows, and consolidating hops.
              </p>
            </div>
            <Link
              href={`/analytics?address=${encodeURIComponent(targetWallet)}`}
              className="text-xs font-mono text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
            >
              Full Behavioural Breakdown <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {preview?.analytics_summary ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">TOTAL TXS</span>
                <span className="text-lg font-bold text-white block mt-1">
                  {preview.analytics_summary.total_tx_count}
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">INFLOW (BTC)</span>
                <span className="text-lg font-bold text-emerald-400 block mt-1">
                  {preview.analytics_summary.total_received_btc.toFixed(4)}
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">SENT / DRAINED</span>
                <span className="text-lg font-bold text-rose-400 block mt-1">
                  {preview.analytics_summary.total_sent_btc.toFixed(4)}
                </span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-slate-500 block">BALANCE</span>
                <span className="text-lg font-bold text-cyan-400 block mt-1">
                  {preview.analytics_summary.current_balance_btc.toFixed(4)}
                </span>
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-500 font-mono py-4 text-center">
              No transactions recorded for this docket yet. Query wallet in Blockchain Ingestion.
            </div>
          )}
        </div>
      )}

      {/* 4. Fund Flow Tab */}
      {activeTab === "graph" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <GitFork className="w-4 h-4 text-cyan-400" />
                Cryptocurrency Fund Flow Topology
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Directed transaction graph and multi-hop peel chain traversal.
              </p>
            </div>
            <Link
              href={`/graph?address=${encodeURIComponent(targetWallet)}`}
              className="px-3 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded text-xs flex items-center gap-1.5"
            >
              Open Interactive Full-Screen Graph <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-6 bg-slate-950 border border-slate-800 rounded-lg text-center space-y-3">
            <GitFork className="w-12 h-12 text-cyan-400 mx-auto opacity-70" />
            <h4 className="text-sm font-bold text-white font-mono">
              Fund Flow Traversal Ready for {targetWallet.slice(0, 16)}...
            </h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              NetworkX topological engine renders up to 3 depth levels of counterparty hops,
              asymmetric peeling chain patterns, and consolidations.
            </p>
            <div className="pt-2">
              <Link
                href={`/graph?address=${encodeURIComponent(targetWallet)}`}
                className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 border border-cyan-800 text-cyan-400 hover:bg-slate-800 rounded text-xs font-mono"
              >
                Inspect Directed Graph (Depth 1–3) →
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* 5. AI Analysis Tab */}
      {activeTab === "ml" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <Activity className="w-4 h-4 text-rose-400" />
                Unsupervised Machine Learning Anomaly Detection
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Isolation Forest topological outlier score (c(n) depth heuristic).
              </p>
            </div>
            <Link
              href={`/ml-risk?address=${encodeURIComponent(targetWallet)}`}
              className="text-xs font-mono text-rose-400 hover:text-rose-300 flex items-center gap-1"
            >
              Open AI Matrix <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-mono text-slate-400">CLASSIFICATION STATUS</span>
              <span className="px-2.5 py-0.5 rounded font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
                {preview?.ml_classification || "HIGH ANOMALY"}
              </span>
            </div>
            <p className="text-slate-300 leading-relaxed font-sans">
              The observed transaction behaviour was classified as highly anomalous according to the configured
              investigative model. Average path length isolation efficiency reflects rapid fund velocity and counterparty dispersion.
            </p>
          </div>
        </div>
      )}

      {/* 6. Risk Tab */}
      {activeTab === "risk" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                Hybrid Investigative Risk Scoring Engine
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Transparent rule contributions (50%) + ML Isolation score (50%).
              </p>
            </div>
            <Link
              href={`/risk?address=${encodeURIComponent(targetWallet)}`}
              className="text-xs font-mono text-amber-400 hover:text-amber-300 flex items-center gap-1"
            >
              Configure Rule Weights <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {preview?.risk_summary ? (
            <div className="space-y-4">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="text-slate-500 text-xs font-mono block">FINAL COMPOSITE RISK SCORE</span>
                  <span className="text-3xl font-black font-mono text-rose-400 block mt-1">
                    {preview.risk_summary.final_score.toFixed(1)}{" "}
                    <span className="text-xs text-slate-500 font-normal">/ 100</span>
                  </span>
                </div>
                <span className="px-3 py-1 text-xs font-bold font-mono rounded bg-rose-950 border border-rose-800 text-rose-300">
                  {preview.risk_summary.risk_level.toUpperCase()}
                </span>
              </div>

              <div className="space-y-2">
                <span className="text-xs font-mono text-slate-400 block">Contributing Behavioral Indicators:</span>
                {preview.risk_summary.rule_triggers.map((trig, idx) => (
                  <div key={idx} className="p-2.5 bg-slate-950/70 border border-slate-800 rounded text-xs text-slate-300 font-sans">
                    • {trig}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-500 font-mono py-4 text-center">
              No risk record evaluated yet for this docket.
            </div>
          )}
        </div>
      )}

      {/* 7. Evidence Tab */}
      {activeTab === "evidence" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <Archive className="w-4 h-4 text-purple-400" />
                Case Evidence Inventory & Integrity Verification
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Deterministic RFC 8785 canonical hashes with instant zero-tamper verification.
              </p>
            </div>
            <Link
              href="/evidence"
              className="text-xs font-mono text-purple-400 hover:text-purple-300 flex items-center gap-1"
            >
              Evidence Locker <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {evidenceList.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs font-mono">
              Zero evidence preserved for this docket. Use &apos;PRESERVE AS EVIDENCE&apos; in Module 8.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-2.5 px-3">EVIDENCE ID</th>
                    <th className="py-2.5 px-3">TYPE</th>
                    <th className="py-2.5 px-3">SHA-256 INTEGRITY HASH</th>
                    <th className="py-2.5 px-3">SEIZED BY</th>
                    <th className="py-2.5 px-3 text-right">INTEGRITY CHECK</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {evidenceList.map((ev) => (
                    <tr key={ev.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-2.5 px-3 text-slate-400">{ev.id.slice(0, 8)}...</td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 rounded text-[11px] bg-slate-950 border border-slate-800 text-cyan-300">
                          {ev.artifact_type}
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="text-sky-400 font-mono">{ev.sha256_hash.slice(0, 24)}...</span>
                      </td>
                      <td className="py-2.5 px-3 font-sans text-slate-300">{ev.captured_by}</td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => handleVerifyEvidence(ev.id)}
                          disabled={verifyingId === ev.id}
                          className="px-2.5 py-1 bg-cyan-950 border border-cyan-800 hover:bg-cyan-900 text-cyan-300 rounded text-[11px] transition-colors"
                        >
                          {verifyingId === ev.id ? "Verifying..." : "Verify Hash"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* 8. Chain of Custody Tab */}
      {activeTab === "custody" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <FileCheck className="w-4 h-4 text-emerald-400" />
                Append-Only Chain of Custody Provenance Log
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Section 65B Indian Evidence Act & ISO/IEC 27037 electronic evidence audit trail.
              </p>
            </div>
            <Link
              href="/custody"
              className="text-xs font-mono text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
            >
              Custody Vault <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-2 text-xs">
            <div className="flex items-center justify-between font-mono">
              <span className="text-slate-400">TOTAL CUSTODIAL LOGS FOR CASE</span>
              <span className="font-bold text-emerald-400">{preview?.chain_of_custody_count || 0} Events</span>
            </div>
            <p className="text-slate-400 font-sans leading-relaxed">
              Every seized artifact in this docket is bound to an immutable SHA-256 hash chain with recorded investigator signatures.
            </p>
          </div>
        </div>
      )}

      {/* 9. Reports Tab */}
      {activeTab === "reports" && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 font-mono">
                <FileDown className="w-4 h-4 text-rose-400" />
                Forensic PDF Investigation Report
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Publication-quality court report with vector charts, SHA-256 evidence digests, and Section 65B IT Act seal.
              </p>
            </div>
            <Link
              href="/reports"
              className="text-xs font-mono text-rose-400 hover:text-rose-300 flex items-center gap-1"
            >
              Reports Dashboard <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-6 bg-slate-950 border border-slate-800 rounded-lg text-center space-y-4">
            <FileDown className="w-12 h-12 text-rose-400 mx-auto" />
            <div>
              <h4 className="text-sm font-bold text-white font-mono">
                Forensic Investigation Report for {caseData.case_id}
              </h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                Generates a multi-page PDF dossier with full tripartite evidentiary distinction,
                vector fund-flow and risk charts, and verified SHA-256 hash tables.
              </p>
            </div>
            <div>
              <a
                href={getReportPdfUrl(caseData.id)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-semibold rounded-lg text-xs shadow-lg shadow-rose-950/50"
              >
                <FileDown className="w-4 h-4" />
                GENERATE FORENSIC REPORT (PDF)
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Edit Case Modal */}
      {showEditModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0e1628] border border-[#1b2848] rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#1b2848]">
              <h3 className="text-sm font-bold text-white uppercase font-mono">
                Edit Investigation Dossier
              </h3>
              <button
                onClick={() => setShowEditModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                  Incident Title *
                </label>
                <input
                  type="text"
                  required
                  value={editForm.title || ""}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                  Incident Classification
                </label>
                <input
                  type="text"
                  value={editForm.incident_type || ""}
                  onChange={(e) => setEditForm({ ...editForm, incident_type: e.target.value })}
                  className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                  Target / Organization Label
                </label>
                <input
                  type="text"
                  value={editForm.target_label || ""}
                  onChange={(e) => setEditForm({ ...editForm, target_label: e.target.value })}
                  className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                  Description & Forensic Notes
                </label>
                <textarea
                  rows={4}
                  value={editForm.description || ""}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                  className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500 font-sans"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-[#1b2848]">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-3 py-1.5 rounded text-slate-400 hover:text-white font-mono"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="bg-cyan-600 hover:bg-cyan-500 text-black font-bold px-4 py-1.5 rounded font-mono disabled:opacity-50"
                >
                  <span>{saving ? "Saving Changes..." : "Commit Update"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
