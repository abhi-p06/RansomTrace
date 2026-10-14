"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  FileDown,
  ShieldCheck,
  AlertTriangle,
  FolderLock,
  Cpu,
  Archive,
  FileText,
  Activity,
  CheckCircle2,
  Clock,
  ExternalLink,
  RefreshCw,
  Scale,
  Hash,
  ShieldAlert,
  Coins,
  ChevronRight,
  Printer
} from "lucide-react";
import {
  getCases,
  getReportPreview,
  getReportPdfUrl,
  InvestigationCase,
  ReportPreviewResponse
} from "@/lib/api";

function ReportsContent() {
  const searchParams = useSearchParams();
  const initialCaseParam = searchParams.get("case_id") || "";

  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>(initialCaseParam);
  const [preview, setPreview] = useState<ReportPreviewResponse | null>(null);
  const [loadingCases, setLoadingCases] = useState(true);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Fetch available cases
  useEffect(() => {
    async function loadCases() {
      try {
        setLoadingCases(true);
        const data = await getCases();
        setCases(data);
        if (data.length > 0) {
          if (initialCaseParam) {
            const matched = data.find(c => c.id === initialCaseParam || c.case_id === initialCaseParam);
            setSelectedCaseId(matched ? matched.id : initialCaseParam);
          } else {
            const demo = data.find((c) => c.case_id.includes("DEMO") || c.case_id.includes("WANNACRY"));
            setSelectedCaseId(demo ? demo.id : data[0].id);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load cases.");
      } finally {
        setLoadingCases(false);
      }
    }
    loadCases();
  }, [initialCaseParam]);

  // Fetch report preview when case changes
  useEffect(() => {
    if (!selectedCaseId) return;

    async function loadPreview() {
      try {
        setLoadingPreview(true);
        setError(null);
        const data = await getReportPreview(selectedCaseId);
        setPreview(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report preview.");
        setPreview(null);
      } finally {
        setLoadingPreview(false);
      }
    }
    loadPreview();
  }, [selectedCaseId]);

  const handleDownloadPdf = async () => {
    if (!selectedCaseId) return;
    try {
      setDownloadingPdf(true);
      const url = getReportPdfUrl(selectedCaseId);
      
      // Fetch as blob to trigger direct save
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Report compilation failed (${res.status})`);
      }
      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      const caseCode = preview?.case_info.case_id || selectedCaseId;
      a.download = `RansomTrace_Forensic_Report_${caseCode}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error generating PDF report.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2500);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 text-xs font-mono bg-cyan-950/80 text-cyan-400 border border-cyan-800/80 rounded">
              PHASE 9 FORENSIC PUBLICATION
            </span>
            <span className="px-2 py-0.5 text-xs font-mono bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 rounded flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" /> ISO 27037 & SEC 65B
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1.5 flex items-center gap-2.5">
            <FileDown className="w-7 h-7 text-cyan-400" />
            Forensic PDF Investigation Report Generator
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Automated compilation of court-admissible forensic dossiers with cryptographic SHA-256 evidence verification,
            vector fund-flow charts, and tripartite evidentiary classification.
          </p>
        </div>

        {/* Global Generate Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadPdf}
            disabled={!selectedCaseId || downloadingPdf || loadingPreview}
            className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 via-sky-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-lg shadow-lg shadow-cyan-950/50 flex items-center gap-2.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            id="generate-forensic-report-btn"
          >
            {downloadingPdf ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-white" />
                Compiling ReportLab Dossier...
              </>
            ) : (
              <>
                <FileDown className="w-4 h-4 text-white" />
                GENERATE FORENSIC REPORT
              </>
            )}
          </button>
        </div>
      </div>

      {/* Case Selector Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <FolderLock className="w-5 h-5 text-cyan-400 shrink-0" />
          <span className="text-xs uppercase font-mono text-slate-400 tracking-wider">
            Select Investigation Docket:
          </span>
          <select
            value={selectedCaseId}
            onChange={(e) => setSelectedCaseId(e.target.value)}
            disabled={loadingCases}
            className="bg-slate-950 border border-slate-700 text-white text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-cyan-500 font-mono"
          >
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                [{c.case_id}] {c.title} ({c.severity})
              </option>
            ))}
          </select>
        </div>

        {preview && (
          <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              Ingested: {new Date(preview.case_info.created_at).toLocaleDateString()}
            </span>
            <span className="text-slate-600">•</span>
            <span className="flex items-center gap-1.5">
              <Archive className="w-3.5 h-3.5 text-cyan-400" />
              Evidence: <strong className="text-white">{preview.evidence_items.length}</strong> items
            </span>
            <span className="text-slate-600">•</span>
            <span className="flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-emerald-400" />
              Custody: <strong className="text-white">{preview.chain_of_custody_count}</strong> events
            </span>
          </div>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-950/50 border border-red-800 text-red-300 rounded-xl flex items-center gap-3 text-sm">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Mandatory Evidentiary Tripartite Standards Banner */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <Scale className="w-4 h-4 text-amber-400" />
          <h2 className="text-xs uppercase font-mono font-bold tracking-wider text-slate-300">
            Mandatory Forensic Evidentiary Distinction (Tripartite Model)
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-emerald-950/20 border border-emerald-800/40 rounded-lg">
            <div className="font-bold text-emerald-400 font-mono flex items-center gap-1.5 mb-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> OBSERVED FACTS
            </div>
            <p className="text-slate-400 leading-relaxed">
              Directly verifiable, immutable data recorded on the public Bitcoin ledger (block heights, transaction hashes, inputs, outputs, timestamps, and fees).
            </p>
          </div>

          <div className="p-3 bg-sky-950/20 border border-sky-800/40 rounded-lg">
            <div className="font-bold text-sky-400 font-mono flex items-center gap-1.5 mb-1">
              <Activity className="w-3.5 h-3.5" /> ANALYTICAL INDICATORS
            </div>
            <p className="text-slate-400 leading-relaxed">
              Algorithmic behavioral scores, NetworkX topology metrics, and scikit-learn Isolation Forest anomaly partitions measuring deviation from typical usage baselines.
            </p>
          </div>

          <div className="p-3 bg-amber-950/20 border border-amber-800/40 rounded-lg">
            <div className="font-bold text-amber-400 font-mono flex items-center gap-1.5 mb-1">
              <AlertTriangle className="w-3.5 h-3.5" /> INVESTIGATOR INTERPRETATION
            </div>
            <p className="text-slate-400 leading-relaxed">
              Investigative prioritization notes, hypotheses, and procedural recommendations. Does NOT constitute direct legal attribution without off-chain corroborative proof.
            </p>
          </div>
        </div>
      </div>

      {/* Main Preview Container */}
      {loadingPreview ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-16 text-center">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-3" />
          <p className="text-sm font-mono text-slate-400">Synthesizing case findings & cryptographic hashes...</p>
        </div>
      ) : preview ? (
        <div className="space-y-6">
          {/* Top Dossier Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Case Details Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs uppercase font-mono text-slate-400 tracking-wider flex items-center gap-1.5">
                  <FolderLock className="w-4 h-4 text-cyan-400" /> Case Dossier
                </span>
                <span className="px-2 py-0.5 text-xs font-bold rounded bg-rose-950 border border-rose-800 text-rose-300">
                  {preview.case_info.severity.toUpperCase()}
                </span>
              </div>

              <div className="space-y-2.5 text-sm">
                <div>
                  <div className="text-xs text-slate-500 font-mono">CASE IDENTIFIER</div>
                  <div className="font-bold text-white font-mono">{preview.case_info.case_id}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-mono">INCIDENT TITLE</div>
                  <div className="text-slate-200">{preview.case_info.title}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-mono">INCIDENT TYPE</div>
                  <div className="text-slate-300">{preview.case_info.incident_type}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-mono">TARGET ORGANIZATION</div>
                  <div className="text-slate-300">{preview.case_info.target_label || "National Infrastructure"}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-mono">STATUS</div>
                  <div className="inline-block px-2 py-0.5 rounded text-xs font-semibold bg-emerald-950 border border-emerald-800 text-emerald-300">
                    {preview.case_info.status}
                  </div>
                </div>
              </div>
            </div>

            {/* Target Wallet & Blockchain Summary */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs uppercase font-mono text-slate-400 tracking-wider flex items-center gap-1.5">
                  <Coins className="w-4 h-4 text-amber-400" /> Target Blockchain Ledger
                </span>
                <span className="px-2 py-0.5 text-xs font-mono rounded bg-slate-800 text-slate-300 border border-slate-700">
                  OBSERVED FACTS
                </span>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="text-xs text-slate-500 font-mono">INVESTIGATED WALLET</div>
                  <div className="font-mono text-xs text-cyan-300 break-all bg-slate-950 p-2 rounded border border-slate-800 mt-1">
                    {preview.target_wallet || "Multi-Address Inquest"}
                  </div>
                </div>

                {preview.analytics_summary ? (
                  <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                    <div className="bg-slate-950/80 p-2.5 rounded border border-slate-800/80">
                      <span className="text-slate-500 block font-mono">TOTAL TXS</span>
                      <span className="text-sm font-bold text-white font-mono">
                        {preview.analytics_summary.total_tx_count}
                      </span>
                    </div>
                    <div className="bg-slate-950/80 p-2.5 rounded border border-slate-800/80">
                      <span className="text-slate-500 block font-mono">TOTAL INFLOW</span>
                      <span className="text-sm font-bold text-emerald-400 font-mono">
                        {preview.analytics_summary.total_received_btc.toFixed(4)} BTC
                      </span>
                    </div>
                    <div className="bg-slate-950/80 p-2.5 rounded border border-slate-800/80">
                      <span className="text-slate-500 block font-mono">DISPERSED / SENT</span>
                      <span className="text-sm font-bold text-rose-400 font-mono">
                        {preview.analytics_summary.total_sent_btc.toFixed(4)} BTC
                      </span>
                    </div>
                    <div className="bg-slate-950/80 p-2.5 rounded border border-slate-800/80">
                      <span className="text-slate-500 block font-mono">BALANCE</span>
                      <span className="text-sm font-bold text-cyan-400 font-mono">
                        {preview.analytics_summary.current_balance_btc.toFixed(4)} BTC
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-xs text-slate-400">Zero transaction metrics populated.</div>
                )}
              </div>
            </div>

            {/* Risk & Anomaly Score Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs uppercase font-mono text-slate-400 tracking-wider flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-rose-400" /> Risk & AI Classification
                </span>
                <span className="px-2 py-0.5 text-xs font-mono rounded bg-slate-800 text-slate-300 border border-slate-700">
                  INDICATORS
                </span>
              </div>

              {preview.risk_summary ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs text-slate-500 font-mono">HYBRID RISK SCORE</div>
                      <div className="text-2xl font-black text-rose-400 font-mono">
                        {preview.risk_summary.final_score.toFixed(1)}{" "}
                        <span className="text-xs text-slate-500 font-normal">/ 100</span>
                      </div>
                    </div>
                    <span className="px-3 py-1 text-xs font-bold font-mono rounded bg-rose-950 text-rose-300 border border-rose-800">
                      {preview.risk_summary.risk_level.toUpperCase()}
                    </span>
                  </div>

                  {/* Components */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 bg-slate-950 rounded border border-slate-800">
                      <span className="text-slate-500 block font-mono">RULE SCORE (50%)</span>
                      <span className="font-bold text-white font-mono">
                        {preview.risk_summary.rule_score.toFixed(1)} pts
                      </span>
                    </div>
                    <div className="p-2 bg-slate-950 rounded border border-slate-800">
                      <span className="text-slate-500 block font-mono">ML SCORE (50%)</span>
                      <span className="font-bold text-white font-mono">
                        {preview.risk_summary.ml_score !== undefined
                          ? `${preview.risk_summary.ml_score.toFixed(1)} pts`
                          : "N/A"}
                      </span>
                    </div>
                  </div>

                  {/* ML Tag */}
                  <div>
                    <div className="text-xs text-slate-500 font-mono">ISOLATION FOREST MATRIX</div>
                    <div className="text-xs font-mono text-slate-300 mt-0.5">
                      Status:{" "}
                      <strong className="text-rose-400">
                        {preview.ml_classification || "ANOMALY_CONFIRMED"}
                      </strong>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-400 p-4 bg-slate-950 rounded border border-slate-800">
                  No risk evaluation record attached. Run Module 7 Risk Assessment to compute.
                </div>
              )}
            </div>
          </div>

          {/* Digital Evidence Inventory Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Archive className="w-4 h-4 text-cyan-400" />
                  Digital Evidence Inventory & Cryptographic SHA-256 Hashes
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  RFC 8785 canonical serialization ensures deterministic hash reproducibility and zero-tamper chain of custody.
                </p>
              </div>
              <span className="px-2.5 py-1 text-xs font-mono bg-cyan-950/80 text-cyan-400 border border-cyan-800/80 rounded-lg">
                {preview.evidence_items.length} Artifacts Sealed
              </span>
            </div>

            {preview.evidence_items.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-xs font-mono">
                Zero evidence preserved for this docket. Use &apos;PRESERVE AS EVIDENCE&apos; in Module 8.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">EVIDENCE ID</th>
                      <th className="py-2.5 px-3">ARTIFACT TYPE</th>
                      <th className="py-2.5 px-3">DESCRIPTION</th>
                      <th className="py-2.5 px-3">SHA-256 INTEGRITY DIGEST</th>
                      <th className="py-2.5 px-3 text-right">SEIZED (UTC)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {preview.evidence_items.map((ev) => (
                      <tr key={ev.evidence_id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-2.5 px-3 text-slate-400">{ev.evidence_id.slice(0, 8)}...</td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded text-[11px] bg-cyan-950 border border-cyan-800 text-cyan-300">
                            {ev.artifact_type}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-sans text-slate-300 max-w-xs truncate">
                          {ev.description || "Forensic artifact preserved."}
                        </td>
                        <td className="py-2.5 px-3">
                          <button
                            onClick={() => copyToClipboard(ev.sha256_hash)}
                            className="flex items-center gap-1.5 text-sky-400 hover:text-sky-300 group"
                            title="Click to copy SHA-256"
                          >
                            <span className="truncate max-w-[200px]">{ev.sha256_hash}</span>
                            <Hash className="w-3 h-3 text-slate-500 group-hover:text-cyan-400" />
                          </button>
                        </td>
                        <td className="py-2.5 px-3 text-right text-slate-400">
                          {new Date(ev.seized_at).toISOString().slice(0, 16).replace("T", " ")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Statutory Disclaimer Box */}
          <div className="bg-amber-950/20 border border-amber-800/50 rounded-xl p-4 text-xs space-y-1.5">
            <div className="font-bold text-amber-400 flex items-center gap-2">
              <Scale className="w-4 h-4" /> STATUTORY JURISPRUDENCE & SECTION 65B IT ACT NOTICE
            </div>
            <p className="text-amber-200/80 leading-relaxed font-sans">
              This forensic report has been compiled automatically by the RansomTrace cryptocurrency forensics platform.
              All calculated risk scores and machine learning anomaly classifications represent investigative triage indicators.
              They do not establish criminal guilt, liability, or natural person attribution. Electronic evidence snapshots
              are hashed via canonical SHA-256 in strict accordance with ISO/IEC 27037 digital evidence preservation standards.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function ReportsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-400">Loading forensic reports...</div>}>
      <ReportsContent />
    </Suspense>
  );
}
