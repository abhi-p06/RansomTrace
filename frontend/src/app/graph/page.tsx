"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import * as d3 from "d3";
import {
  GitFork,
  Search,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Sliders,
  Layers,
  ArrowRight,
  ShieldAlert,
  Coins,
  Copy,
  ExternalLink,
  Clock,
  CheckCircle2,
  AlertTriangle,
  X,
  Activity,
  Terminal
} from "lucide-react";
import { getWalletGraph } from "@/lib/api";
import { FundFlowGraphResponse, GraphNode, GraphEdge } from "@/lib/types";

const SAMPLE_TARGETS = [
  { name: "Demo Investigation (Active)", address: "1DemoRansomCollectionWallet002" },
  { name: "WannaCry Extortion Hub", address: "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94" },
  { name: "DarkSide Ransomware", address: "145EUshA4pwv6VPupsmBJAa3kwnY4o6D7S" },
  { name: "Genesis Block Reward", address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" },
];

function getNodeColor(node: GraphNode): string {
  if (node.is_target) return "#00e5ff"; // Electric Cyan
  if (node.node_type === "INFLOW_SENDER") return "#10b981"; // Emerald
  if (node.node_type === "OUTFLOW_RECEIVER") return "#f43f5e"; // Crimson
  return "#f59e0b"; // Amber Transit
}

function getNodeRadius(node: GraphNode): number {
  if (node.is_target) return 22;
  const base = 12;
  const degreeBoost = Math.min(node.degree * 1.5, 12);
  return base + degreeBoost;
}

function FundFlowContent() {
  const searchParams = useSearchParams();
  const initialAddr = searchParams.get("address") || "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94";

  const [addressInput, setAddressInput] = useState(initialAddr);
  const [depth, setDepth] = useState<number>(1);
  const [maxNodes, setMaxNodes] = useState<number>(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Graph Data
  const [graphData, setGraphData] = useState<FundFlowGraphResponse | null>(null);

  // Selection states for inspector panel
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  // D3 Canvas Ref
  const svgRef = useRef<SVGSVGElement | null>(null);
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphEdge> | null>(null);

  const fetchGraph = async (targetAddr?: string, targetDepth?: number) => {
    const addr = (targetAddr || addressInput).trim();
    if (!addr) {
      setError("Please enter a valid Bitcoin address to generate flow topology.");
      return;
    }

    const curDepth = targetDepth !== undefined ? targetDepth : depth;
    setLoading(true);
    setError(null);
    setSelectedNode(null);
    setSelectedEdge(null);

    try {
      const data = await getWalletGraph(addr, curDepth, maxNodes);
      setGraphData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate fund-flow graph.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialAddr) {
      const timer = setTimeout(() => {
        setAddressInput(initialAddr);
        fetchGraph(initialAddr, depth);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [initialAddr]);

  // Render D3 Interactive Force Directed Graph
  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clean previous render

    const width = svgRef.current.clientWidth || 900;
    const height = 620;

    // Create container group for zoom/pan
    const g = svg.append("g").attr("class", "graph-container");

    // Configure D3 Zoom & Pan
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.15, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);
    zoomBehaviorRef.current = zoom;

    // Define Arrowhead Markers in SVG Defs
    const defs = svg.append("defs");
    defs.append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 26) // offset for node radius
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#64748b");

    defs.append("marker")
      .attr("id", "arrowhead-selected")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 26)
      .attr("refY", 0)
      .attr("markerWidth", 8)
      .attr("markerHeight", 8)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#00e5ff");

    // Deep copy nodes and edges for D3 mutation
    const nodes: GraphNode[] = graphData.nodes.map((n) => ({ ...n }));
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));

    const links: GraphEdge[] = graphData.edges
      .filter((e) => nodeMap.has(e.source as string) && nodeMap.has(e.target as string))
      .map((e) => ({
        ...e,
        source: nodeMap.get(e.source as string)!,
        target: nodeMap.get(e.target as string)!,
      }));

    // Setup Force Simulation
    const simulation = d3.forceSimulation<GraphNode, GraphEdge>(nodes)
      .force(
        "link",
        d3.forceLink<GraphNode, GraphEdge>(links)
          .id((d) => d.id)
          .distance((d) => {
            const srcId = typeof d.source === "string" ? d.source : d.source.id;
            const tgtId = typeof d.target === "string" ? d.target : d.target.id;
            const isTargetLink = (srcId === graphData.target_address || tgtId === graphData.target_address);
            return isTargetLink ? 160 : 120;
          })
      )
      .force("charge", d3.forceManyBody().strength(-380))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide<GraphNode>().radius((d) => getNodeRadius(d) + 14));

    simulationRef.current = simulation;

    // Render Edges (Links)
    const link = g.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#334155")
      .attr("stroke-width", (d) => Math.max(1.5, Math.min(d.amount_btc * 1.5, 6)))
      .attr("stroke-opacity", 0.75)
      .attr("marker-end", "url(#arrowhead)")
      .attr("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation();
        setSelectedEdge(d);
        setSelectedNode(null);
        link.attr("stroke", (l) => (l.id === d.id ? "#00e5ff" : "#334155"))
            .attr("marker-end", (l) => (l.id === d.id ? "url(#arrowhead-selected)" : "url(#arrowhead)"));
      });

    // Render Nodes Group
    const nodeGroup = g.append("g")
      .attr("class", "nodes")
      .selectAll<SVGGElement, GraphNode>("g")
      .data(nodes)
      .enter()
      .append("g")
      .attr("cursor", "pointer")
      .call(
        d3.drag<SVGGElement, GraphNode>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      )
      .on("click", (event, d) => {
        event.stopPropagation();
        setSelectedNode(d);
        setSelectedEdge(null);
      });

    // Target Pulse Ring
    nodeGroup.filter((d) => Boolean(d.is_target))
      .append("circle")
      .attr("r", 32)
      .attr("fill", "none")
      .attr("stroke", "#00e5ff")
      .attr("stroke-width", 1.5)
      .attr("stroke-dasharray", "4 4")
      .attr("opacity", 0.7);

    // Node Circle
    nodeGroup.append("circle")
      .attr("r", (d) => getNodeRadius(d))
      .attr("fill", (d) => getNodeColor(d))
      .attr("stroke", "#0f172a")
      .attr("stroke-width", 2.5)
      .attr("class", "transition-all hover:brightness-125");

    // Node Label Text
    nodeGroup.append("text")
      .text((d) => d.short_label)
      .attr("x", 0)
      .attr("y", (d) => getNodeRadius(d) + 14)
      .attr("text-anchor", "middle")
      .attr("fill", "#94a3b8")
      .attr("font-size", "10px")
      .attr("font-family", "ui-monospace, monospace")
      .attr("pointer-events", "none");

    // Tick update
    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (typeof d.source === "object" ? d.source.x ?? 0 : 0))
        .attr("y1", (d) => (typeof d.source === "object" ? d.source.y ?? 0 : 0))
        .attr("x2", (d) => (typeof d.target === "object" ? d.target.x ?? 0 : 0))
        .attr("y2", (d) => (typeof d.target === "object" ? d.target.y ?? 0 : 0));

      nodeGroup.attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    // Clicking background clears selection
    svg.on("click", () => {
      setSelectedNode(null);
      setSelectedEdge(null);
      link.attr("stroke", "#334155").attr("marker-end", "url(#arrowhead)");
    });

  }, [graphData]);

  // Zoom controls
  const handleZoom = (scaleFactor: number) => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    d3.select(svgRef.current)
      .transition()
      .duration(300)
      .call(zoomBehaviorRef.current.scaleBy, scaleFactor);
  };

  const handleResetZoom = () => {
    if (!svgRef.current || !zoomBehaviorRef.current) return;
    d3.select(svgRef.current)
      .transition()
      .duration(400)
      .call(zoomBehaviorRef.current.transform, d3.zoomIdentity);
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Heading */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-[#1b2848] gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono mb-1">
            <GitFork className="w-3.5 h-3.5" />
            <span className="uppercase tracking-widest font-semibold">
              Module 2 & 4 · Cryptocurrency Fund Flow Graph
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Public Bitcoin Transaction Flow Graph
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Directed topological representation of Bitcoin fund movements between publicly observable wallet addresses.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            href={`/analytics?address=${encodeURIComponent(addressInput)}`}
            className="bg-[#121c33] hover:bg-[#1a2b4d] text-cyan-300 border border-[#1e2f54] px-3 py-1.5 rounded text-xs font-mono flex items-center space-x-1.5 transition-all"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Behavioural Profiling →</span>
          </Link>
        </div>
      </div>

      {/* Target Address & Depth Controls Card */}
      <div className="bg-[#0e1628] border border-[#1b2848] p-5 rounded-lg space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetchGraph();
          }}
          className="flex flex-col md:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Enter Bitcoin address to build multi-hop fund-flow graph..."
              value={addressInput}
              onChange={(e) => setAddressInput(e.target.value)}
              className="w-full bg-[#121c33] border border-[#1e2f54] text-xs text-white pl-10 pr-4 py-3 rounded-md focus:outline-none focus:border-cyan-500 font-mono tracking-wide placeholder:font-sans"
            />
          </div>

          {/* Depth Selector Pills */}
          <div className="flex items-center space-x-1.5 bg-[#121c33] p-1.5 rounded-md border border-[#1e2f54]">
            <span className="text-[10px] font-mono text-slate-400 uppercase px-2">Depth:</span>
            {[1, 2, 3].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => {
                  setDepth(d);
                  fetchGraph(addressInput, d);
                }}
                className={`px-3 py-1.5 rounded text-xs font-mono transition-all ${
                  depth === d
                    ? "bg-cyan-600 text-black font-bold shadow-md"
                    : "text-slate-400 hover:text-white hover:bg-[#1b2848]"
                }`}
              >
                Depth {d}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-xs px-6 py-3 rounded-md shadow-lg shadow-cyan-600/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50 font-mono uppercase tracking-wider"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Tracing Network...</span>
              </>
            ) : (
              <>
                <GitFork className="w-4 h-4" />
                <span>Generate Graph</span>
              </>
            )}
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#18233c] text-xs">
          <span className="text-[11px] font-mono text-slate-400">Sample Ransomware Hubs:</span>
          {SAMPLE_TARGETS.map((sample) => (
            <button
              key={sample.address}
              onClick={() => {
                setAddressInput(sample.address);
                fetchGraph(sample.address, depth);
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

      {/* Main Graph Canvas & Interactive Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Column: Interactive D3 Graph Canvas (3 cols) */}
        <div className="lg:col-span-3 bg-[#0a0f1d] border border-[#1b2848] rounded-xl overflow-hidden flex flex-col relative">
          {/* Canvas Top Action Strip */}
          <div className="bg-[#0e1628] border-b border-[#1b2848] p-3 px-4 flex items-center justify-between text-xs font-mono">
            <div className="flex items-center space-x-4">
              <span className="text-white font-bold flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                <span>Graph View (Depth {depth})</span>
              </span>
              {graphData && (
                <span className="text-slate-400 text-[11px]">
                  Nodes: <strong className="text-cyan-300">{graphData.metrics.total_nodes}</strong> ·
                  Edges: <strong className="text-cyan-300">{graphData.metrics.total_edges}</strong> ·
                  Density: <strong className="text-cyan-300">{graphData.metrics.density}</strong>
                </span>
              )}
            </div>

            {/* Zoom / Reset Buttons */}
            <div className="flex items-center space-x-1 bg-[#121c33] p-1 rounded border border-[#1e2f54]">
              <button
                onClick={() => handleZoom(1.3)}
                className="p-1 rounded text-slate-400 hover:text-white hover:bg-[#1b2848]"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleZoom(0.7)}
                className="p-1 rounded text-slate-400 hover:text-white hover:bg-[#1b2848]"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleResetZoom}
                className="p-1 rounded text-slate-400 hover:text-white hover:bg-[#1b2848]"
                title="Center & Reset View"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* SVG Canvas Area */}
          <div className="relative h-[620px] w-full bg-[#070b14] overflow-hidden select-none">
            {loading && (
              <div className="absolute inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-20 text-xs font-mono text-cyan-300 space-x-2">
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Simulating NetworkX fund flow physics...</span>
              </div>
            )}

            <svg ref={svgRef} className="w-full h-full" />

            {/* In-Canvas Floating Legend */}
            <div className="absolute bottom-4 left-4 bg-[#0a0f1d]/90 backdrop-blur border border-[#1e2f54] p-3 rounded-lg text-[10px] font-mono space-y-1.5 shadow-xl pointer-events-none">
              <span className="text-slate-400 uppercase tracking-widest block font-bold mb-1">
                Topology Legend
              </span>
              <div className="flex items-center space-x-2 text-cyan-300">
                <span className="w-2.5 h-2.5 rounded-full bg-[#00e5ff] shadow-sm shadow-cyan-400" />
                <span>Target Wallet (Investigated Hub)</span>
              </div>
              <div className="flex items-center space-x-2 text-emerald-300">
                <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]" />
                <span>Inflow Senders (Ransom Payments)</span>
              </div>
              <div className="flex items-center space-x-2 text-rose-300">
                <span className="w-2.5 h-2.5 rounded-full bg-[#f43f5e]" />
                <span>Outflow Receivers (Peel / Liquidation)</span>
              </div>
              <div className="flex items-center space-x-2 text-amber-300">
                <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]" />
                <span>Transit Nodes (Multi-Hop Routers)</span>
              </div>
              <div className="flex items-center space-x-2 text-slate-400 pt-1 border-t border-[#1e2f54]">
                <ArrowRight className="w-3 h-3 text-slate-400" />
                <span>Directed Edge = Fund Flow</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Inspector Side Panel (1 col) */}
        <div className="bg-[#0e1628] border border-[#1b2848] rounded-xl p-5 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#1b2848]">
              <h3 className="text-xs font-bold text-white uppercase font-mono tracking-wider flex items-center space-x-1.5">
                <Terminal className="w-4 h-4 text-cyan-400" />
                <span>Forensic Inspector</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-400">
                {selectedNode ? "Wallet Selected" : selectedEdge ? "Edge Selected" : "Click Node/Edge"}
              </span>
            </div>

            {/* Inspector Content */}
            {selectedNode ? (
              <div className="mt-4 space-y-3 text-xs font-mono">
                <div className="bg-[#121c33] p-3 rounded border border-[#1e2f54] space-y-1">
                  <span className="text-[10px] text-cyan-400 uppercase tracking-wider block">
                    {selectedNode.is_target ? "Investigated Target Wallet" : `${selectedNode.node_type}`}
                  </span>
                  <span className="text-white font-bold break-all block text-xs">
                    {selectedNode.address}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">Received BTC</span>
                    <span className="text-emerald-400 font-bold mt-0.5 block">{selectedNode.received_btc} BTC</span>
                  </div>
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">Sent BTC</span>
                    <span className="text-rose-400 font-bold mt-0.5 block">{selectedNode.sent_btc} BTC</span>
                  </div>
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">Network Degree</span>
                    <span className="text-cyan-300 font-bold mt-0.5 block">{selectedNode.degree} Connections</span>
                  </div>
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">Hop Depth</span>
                    <span className="text-slate-200 font-bold mt-0.5 block">Depth {selectedNode.depth}</span>
                  </div>
                </div>

                {/* Actions for Selected Node */}
                <div className="space-y-2 pt-2">
                  <button
                    onClick={() => {
                      setAddressInput(selectedNode.address);
                      fetchGraph(selectedNode.address, depth);
                    }}
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-black font-bold py-2 rounded text-xs transition-all flex items-center justify-center space-x-1.5"
                  >
                    <GitFork className="w-3.5 h-3.5" />
                    <span>Re-Center Graph on this Wallet</span>
                  </button>

                  <Link
                    href={`/analytics?address=${encodeURIComponent(selectedNode.address)}`}
                    className="w-full bg-[#16233d] hover:bg-[#1e2f54] text-cyan-300 border border-[#213459] py-2 rounded text-xs transition-all flex items-center justify-center space-x-1.5"
                  >
                    <Activity className="w-3.5 h-3.5" />
                    <span>View Behavioural Analytics</span>
                  </Link>

                  <a
                    href={`https://mempool.space/address/${selectedNode.address}`}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full bg-[#121c33] hover:bg-[#1a2b4d] text-slate-300 border border-[#1e2f54] py-2 rounded text-xs transition-all flex items-center justify-center space-x-1.5"
                  >
                    <span>Inspect on Mempool Explorer</span>
                    <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                  </a>
                </div>
              </div>
            ) : selectedEdge ? (
              <div className="mt-4 space-y-3 text-xs font-mono">
                <div className="bg-[#121c33] p-3 rounded border border-[#1e2f54] space-y-1">
                  <span className="text-[10px] text-cyan-400 uppercase tracking-wider block">
                    Public Transaction Flow
                  </span>
                  <span className="text-emerald-400 font-bold text-sm block">
                    {selectedEdge.amount_btc} BTC
                  </span>
                  <span className="text-[10px] text-slate-400 block">
                    {selectedEdge.amount_sats.toLocaleString()} Sats
                  </span>
                </div>

                <div className="space-y-2 text-[11px]">
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">TXID</span>
                    <span className="text-cyan-300 break-all">{selectedEdge.txid}</span>
                  </div>
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">Sender Address</span>
                    <span className="text-slate-300 break-all">{typeof selectedEdge.source === "object" ? selectedEdge.source.id : selectedEdge.source}</span>
                  </div>
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">Recipient Address</span>
                    <span className="text-slate-300 break-all">{typeof selectedEdge.target === "object" ? selectedEdge.target.id : selectedEdge.target}</span>
                  </div>
                  <div className="bg-[#121c33] p-2.5 rounded border border-[#1e2f54]">
                    <span className="text-slate-400 block text-[10px]">Confirmation Time</span>
                    <span className="text-slate-200">{selectedEdge.block_time_iso || "Unconfirmed"}</span>
                  </div>
                </div>

                <a
                  href={`https://mempool.space/tx/${selectedEdge.txid}`}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full bg-[#121c33] hover:bg-[#1a2b4d] text-cyan-300 border border-[#1e2f54] py-2 rounded text-xs transition-all flex items-center justify-center space-x-1.5 block text-center"
                >
                  <span>View TX on Mempool</span>
                  <ExternalLink className="w-3.5 h-3.5 text-cyan-400 inline" />
                </a>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-500 font-mono space-y-2">
                <Sliders className="w-8 h-8 mx-auto text-slate-600" />
                <p>Click any node or transaction edge to inspect its forensic ledger attributes.</p>
              </div>
            )}
          </div>

          {/* Bottom Academic Notice */}
          <div className="p-3 bg-[#0a0f1d] border border-[#18233c] rounded text-[10px] text-slate-400 font-mono space-y-1">
            <span className="text-cyan-400 font-bold block uppercase">Graph Analysis Standard</span>
            <p className="leading-relaxed">
              Visualizes public blockchain UTXO movements. Does not imply private identity or legal culpability.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FundFlowPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-slate-400 font-mono">Loading fund-flow canvas...</div>}>
      <FundFlowContent />
    </Suspense>
  );
}
