"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  FolderPlus,
  Search,
  Filter,
  ShieldAlert,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  Trash2,
  X,
  CheckCircle2,
  RefreshCw,
  FolderLock
} from "lucide-react";
import { getCases, createCase, updateCase, deleteCase } from "@/lib/api";
import { InvestigationCase, CaseStatus, CaseSeverity, CaseCreateInput } from "@/lib/types";

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

export default function CasesPage() {
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [severityFilter, setSeverityFilter] = useState<string>("");

  // Create Modal State
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [formData, setFormData] = useState<CaseCreateInput>({
    case_id: "",
    title: "",
    incident_type: "Ransomware Extortion",
    target_label: "",
    severity: "Medium",
    status: "Open",
    description: "",
  });

  const loadCases = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCases({
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
        search: search.trim() || undefined,
      });
      setCases(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load cases");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    getCases({
      status: statusFilter || undefined,
      severity: severityFilter || undefined,
      search: search.trim() || undefined,
    })
      .then((data: InvestigationCase[]) => {
        if (isMounted) setCases(data);
      })
      .catch((err) => {
        if (isMounted) setError(err instanceof Error ? err.message : "Failed to load cases");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [statusFilter, severityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadCases();
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      setFormError("Case title is required");
      return;
    }
    setSubmitting(true);
    setFormError(null);
    try {
      await createCase({
        ...formData,
        case_id: formData.case_id?.trim() || undefined,
        title: formData.title.trim(),
        incident_type: formData.incident_type.trim(),
        target_label: formData.target_label?.trim() || undefined,
        description: formData.description?.trim() || undefined,
      });
      setShowModal(false);
      setFormData({
        case_id: "",
        title: "",
        incident_type: "Ransomware Extortion",
        target_label: "",
        severity: "Medium",
        status: "Open",
        description: "",
      });
      await loadCases();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to create case");
    } finally {
      setSubmitting(false);
    }
  };

  const handleInlineStatusChange = async (caseItem: InvestigationCase, newStatus: CaseStatus) => {
    try {
      await updateCase(caseItem.id, { status: newStatus });
      setCases((prev) =>
        prev.map((c) => (c.id === caseItem.id ? { ...c, status: newStatus } : c))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update status");
    }
  };

  const handleInlineSeverityChange = async (caseItem: InvestigationCase, newSeverity: CaseSeverity) => {
    try {
      await updateCase(caseItem.id, { severity: newSeverity });
      setCases((prev) =>
        prev.map((c) => (c.id === caseItem.id ? { ...c, severity: newSeverity } : c))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update severity");
    }
  };

  const handleDelete = async (caseId: string, caseTitle: string) => {
    if (!confirm(`Are you sure you want to purge investigation dossier: "${caseTitle}"?`)) {
      return;
    }
    try {
      await deleteCase(caseId);
      setCases((prev) => prev.filter((c) => c.id !== caseId && c.case_id !== caseId));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete case");
    }
  };

  // Metrics
  const totalCount = cases.length;
  const activeCount = cases.filter((c) => c.status === "Investigating" || c.status === "Open").length;
  const criticalCount = cases.filter((c) => c.severity === "Critical").length;
  const containedCount = cases.filter((c) => c.status === "Contained" || c.status === "Closed").length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1b2848] gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono mb-1">
            <FolderLock className="w-3.5 h-3.5" />
            <span className="uppercase tracking-widest font-semibold">
              Module 1 & 2 · Forensic Incident Repository
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Cybercrime Investigation Case Dossiers
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage active ransomware extortion cases with relational database persistence and chain-of-custody logging.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="bg-cyan-600 hover:bg-cyan-500 text-black font-semibold text-xs px-4 py-2 rounded-md shadow-lg shadow-cyan-600/20 flex items-center space-x-2 transition-all"
        >
          <FolderPlus className="w-4 h-4" />
          <span>Initialize New Case</span>
        </button>
      </div>

      {/* Metric Counters */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Total Dossiers</span>
          <span className="text-2xl font-bold font-mono text-white mt-1 block">{totalCount}</span>
        </div>
        <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider block">Active Enquiries</span>
          <span className="text-2xl font-bold font-mono text-cyan-400 mt-1 block">{activeCount}</span>
        </div>
        <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
          <span className="text-[10px] font-mono text-rose-400 uppercase tracking-wider block">Critical Threats</span>
          <span className="text-2xl font-bold font-mono text-rose-400 mt-1 block">{criticalCount}</span>
        </div>
        <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg">
          <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider block">Resolved / Contained</span>
          <span className="text-2xl font-bold font-mono text-emerald-400 mt-1 block">{containedCount}</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#0e1628] border border-[#1b2848] p-4 rounded-lg flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex items-center space-x-2 w-full">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by case title, serial ID (e.g. RT-2026), or victim label..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#121c33] border border-[#1e2f54] text-xs text-white pl-9 pr-3 py-2 rounded focus:outline-none focus:border-cyan-500 font-sans"
            />
          </div>
          <button
            type="submit"
            className="bg-[#16233d] hover:bg-cyan-950 text-cyan-300 border border-[#213459] hover:border-cyan-500 text-xs px-3 py-2 rounded font-mono transition-all"
          >
            Search
          </button>
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#121c33] border border-[#1e2f54] text-xs text-slate-300 py-2 px-3 rounded focus:outline-none focus:border-cyan-500 font-mono"
          >
            <option value="">Status: All</option>
            <option value="Open">Open</option>
            <option value="Investigating">Investigating</option>
            <option value="Contained">Contained</option>
            <option value="Closed">Closed</option>
          </select>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-[#121c33] border border-[#1e2f54] text-xs text-slate-300 py-2 px-3 rounded focus:outline-none focus:border-cyan-500 font-mono"
          >
            <option value="">Severity: All</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>

          <button
            onClick={() => {
              setSearch("");
              setStatusFilter("");
              setSeverityFilter("");
              loadCases();
            }}
            className="p-2 rounded bg-[#121c33] border border-[#1e2f54] text-slate-400 hover:text-white"
            title="Refresh / Reset filters"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Case Dossier Table */}
      <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400 font-mono">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-cyan-400 mb-2" />
            <span>Querying relational database...</span>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-xs text-rose-400 font-mono">
            <span>Error: {error}</span>
          </div>
        ) : cases.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400 font-mono space-y-3">
            <FolderLock className="w-8 h-8 mx-auto text-slate-500" />
            <p>No investigation dossiers found matching current filter parameters.</p>
            <button
              onClick={() => setShowModal(true)}
              className="inline-flex items-center space-x-1.5 text-cyan-400 underline hover:text-cyan-300"
            >
              <FolderPlus className="w-3.5 h-3.5" />
              <span>Initialize your first case dossier</span>
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0a0f1d] border-b border-[#1b2848] text-slate-400 font-mono uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Case ID</th>
                  <th className="py-3 px-4">Title & Target</th>
                  <th className="py-3 px-4">Incident Type</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#16233d]">
                {cases.map((c) => {
                  const sevStyle = SEVERITY_COLORS[c.severity] || SEVERITY_COLORS.Medium;
                  const statStyle = STATUS_COLORS[c.status] || STATUS_COLORS.Open;
                  return (
                    <tr key={c.id} className="hover:bg-[#121c33]/70 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">
                        <Link href={`/cases/${c.case_id}`} className="hover:underline flex items-center space-x-1">
                          <span>{c.case_id}</span>
                          <ArrowUpRight className="w-3 h-3 opacity-60" />
                        </Link>
                      </td>
                      <td className="py-3.5 px-4">
                        <Link href={`/cases/${c.case_id}`} className="font-semibold text-slate-200 hover:text-cyan-300 block">
                          {c.title}
                        </Link>
                        {c.target_label && (
                          <span className="text-[11px] text-slate-400 font-mono">
                            Target: {c.target_label}
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-slate-300 font-mono text-[11px]">
                        {c.incident_type}
                      </td>
                      {/* Inline Severity Selector */}
                      <td className="py-3.5 px-4">
                        <select
                          value={c.severity}
                          onChange={(e) => handleInlineSeverityChange(c, e.target.value as CaseSeverity)}
                          className={`text-[10px] font-mono font-bold px-2 py-1 rounded border focus:outline-none cursor-pointer ${sevStyle.bg} ${sevStyle.text} ${sevStyle.border}`}
                        >
                          <option value="Low">Low</option>
                          <option value="Medium">Medium</option>
                          <option value="High">High</option>
                          <option value="Critical">Critical</option>
                        </select>
                      </td>
                      {/* Inline Status Selector */}
                      <td className="py-3.5 px-4">
                        <select
                          value={c.status}
                          onChange={(e) => handleInlineStatusChange(c, e.target.value as CaseStatus)}
                          className={`text-[10px] font-mono font-bold px-2 py-1 rounded border focus:outline-none cursor-pointer ${statStyle.bg} ${statStyle.text} ${statStyle.border}`}
                        >
                          <option value="Open">Open</option>
                          <option value="Investigating">Investigating</option>
                          <option value="Contained">Contained</option>
                          <option value="Closed">Closed</option>
                        </select>
                      </td>
                      <td className="py-3.5 px-4 text-[11px] text-slate-400 font-mono">
                        {new Date(c.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <Link
                            href={`/cases/${c.case_id}`}
                            className="bg-[#1b2a4a] hover:bg-cyan-600 text-cyan-300 hover:text-white px-2.5 py-1 rounded text-[11px] font-mono transition-all"
                          >
                            Open Dossier
                          </Link>
                          <button
                            onClick={() => handleDelete(c.id, c.title)}
                            className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                            title="Purge case dossier"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Initialize New Case Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0e1628] border border-[#1b2848] rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#1b2848]">
              <div className="flex items-center space-x-2">
                <FolderPlus className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
                  Initialize Investigation Dossier
                </h3>
              </div>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {formError && (
              <div className="bg-rose-950/60 border border-rose-800 text-rose-300 px-3 py-2 rounded text-xs font-mono">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateCase} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                  Case Identifier (Optional, e.g. RT-2026-001)
                </label>
                <input
                  type="text"
                  placeholder="Auto-generated if left blank"
                  value={formData.case_id || ""}
                  onChange={(e) => setFormData({ ...formData, case_id: e.target.value })}
                  className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                  Incident Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. LockBit 3.0 Ransomware Healthcare Extortion"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                    Incident Classification
                  </label>
                  <select
                    value={formData.incident_type}
                    onChange={(e) => setFormData({ ...formData, incident_type: e.target.value })}
                    className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="Ransomware Extortion">Ransomware Extortion</option>
                    <option value="Double Extortion">Double Extortion</option>
                    <option value="Data Exfiltration">Data Exfiltration</option>
                    <option value="Supply Chain Compromise">Supply Chain Compromise</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                    Target / Organization Label
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Metropolitan Health Corp"
                    value={formData.target_label || ""}
                    onChange={(e) => setFormData({ ...formData, target_label: e.target.value })}
                    className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                    Severity Level
                  </label>
                  <select
                    value={formData.severity}
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value as CaseSeverity })}
                    className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Critical">Critical</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                    Investigation Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as CaseStatus })}
                    className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="Open">Open</option>
                    <option value="Investigating">Investigating</option>
                    <option value="Contained">Contained</option>
                    <option value="Closed">Closed</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-mono mb-1 text-[11px]">
                  Incident Description & Forensic Notes
                </label>
                <textarea
                  rows={3}
                  placeholder="Detail primary indicators of compromise, ransom note demands, and initial Bitcoin payment vector..."
                  value={formData.description || ""}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-[#121c33] border border-[#1e2f54] text-white px-3 py-2 rounded focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-[#1b2848]">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 rounded text-slate-400 hover:text-white font-mono"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-cyan-600 hover:bg-cyan-500 text-black font-bold px-4 py-1.5 rounded font-mono flex items-center space-x-1.5 disabled:opacity-50"
                >
                  <span>{submitting ? "Writing to Database..." : "Open Dossier"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
