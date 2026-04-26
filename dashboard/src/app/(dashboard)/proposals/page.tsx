"use client";

import { useState, useEffect } from "react";
import useSWR from "swr";
import {
  fetcher,
  fetchAllProposals,
  fetchProposalStats,
  updateProposal,
  type Proposal,
  type ProposalStats,
} from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
  FileText,
  TrendingUp,
  Send,
  Eye,
  MousePointerClick,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  DollarSign,
  ChevronDown,
} from "lucide-react";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: typeof FileText }> = {
  draft: { label: "Draft", color: "bg-gray-500", icon: FileText },
  needs_revision: { label: "Needs Revision", color: "bg-yellow-500", icon: FileText },
  reviewed: { label: "Reviewed", color: "bg-blue-500", icon: Eye },
  sent: { label: "Sent", color: "bg-indigo-500", icon: Send },
  replied: { label: "Replied", color: "bg-purple-500", icon: MousePointerClick },
  accepted: { label: "Accepted", color: "bg-green-500", icon: CheckCircle },
  rejected: { label: "Rejected", color: "bg-red-500", icon: XCircle },
  cold: { label: "Cold", color: "bg-slate-500", icon: Clock },
};

function formatCurrency(cents: number | null, currency: string = "IDR") {
  if (cents === null) return "—";
  return new Intl.NumberFormat("id-ID", { style: "currency", currency, minimumFractionDigits: 0 }).format(cents / 100);
}

function formatScore(score: number | null | undefined) {
  if (score == null) return "—";
  return `${Number(score).toFixed(1)}/10`;
}

function funnelPercent(count: number, total: number) {
  if (total === 0) return 0;
  return Math.round((count / total) * 100);
}

export default function ProposalsPage() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);

  const { data: statsData, mutate: mutateStats } = useSWR<ProposalStats>(
    "/api/v1/proposals/stats/overview",
    fetcher as any
  );

  const { data: proposalsData, mutate: mutateProposals } = useSWR<{ proposals: Proposal[]; total: number }>(
    statusFilter === "all"
      ? "/api/v1/proposals?limit=100"
      : `/api/v1/proposals?status=${encodeURIComponent(statusFilter)}&limit=100`,
    fetcher as any
  );

  const stats = statsData || ({} as ProposalStats);
  const proposals = proposalsData?.proposals || [];
  const total = proposalsData?.total || 0;
  const byStatus = stats.by_status || {};
  const conversionRates = stats.conversion_rates || {};

  const handleStatusChange = async (proposalId: number, newStatus: string) => {
    try {
      await updateProposal(proposalId, { status: newStatus });
      mutateProposals();
      mutateStats();
    } catch (err) {
      console.error("Failed to update proposal status:", err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileText className="h-6 w-6" />
          Proposals
        </h1>
        <div className="flex items-center gap-2">
          <select
            className="border rounded-md px-3 py-1.5 text-sm bg-neutral-800 border-neutral-700 text-neutral-200"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses</option>
            {Object.entries(STATUS_CONFIG).map(([key, { label }]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
          <Badge variant="secondary" className="text-xs">{total} proposals</Badge>
        </div>
      </div>


      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <Card className="bg-neutral-900 border-neutral-800">
          <CardContent className="p-3 text-center">
            <FileText className="h-4 w-4 mx-auto mb-1 text-orange-500" />
            <div className="text-xl font-bold">{stats.total || 0}</div>
            <div className="text-xs text-neutral-400">Total</div>
          </CardContent>
        </Card>
        <Card className="bg-neutral-900 border-neutral-800">
          <CardContent className="p-3 text-center">
            <Send className="h-4 w-4 mx-auto mb-1 text-indigo-400" />
            <div className="text-xl font-bold">{stats.total_sent || 0}</div>
            <div className="text-xs text-neutral-400">Sent</div>
          </CardContent>
        </Card>
        <Card className="bg-neutral-900 border-neutral-800">
          <CardContent className="p-3 text-center">
            <Eye className="h-4 w-4 mx-auto mb-1 text-blue-400" />
            <div className="text-xl font-bold">{stats.total_opened || 0}</div>
            <div className="text-xs text-neutral-400">Opened</div>
          </CardContent>
        </Card>
        <Card className="bg-neutral-900 border-neutral-800">
          <CardContent className="p-3 text-center">
            <MousePointerClick className="h-4 w-4 mx-auto mb-1 text-amber-400" />
            <div className="text-xl font-bold">{stats.total_clicked || 0}</div>
            <div className="text-xs text-neutral-400">Clicked</div>
          </CardContent>
        </Card>
        <Card className="bg-neutral-900 border-neutral-800">
          <CardContent className="p-3 text-center">
            <CheckCircle className="h-4 w-4 mx-auto mb-1 text-green-400" />
            <div className="text-xl font-bold">{stats.total_accepted || 0}</div>
            <div className="text-xs text-neutral-400">Accepted</div>
          </CardContent>
        </Card>
        <Card className="bg-neutral-900 border-neutral-800">
          <CardContent className="p-3 text-center">
            <DollarSign className="h-4 w-4 mx-auto mb-1 text-emerald-400" />
            <div className="text-xl font-bold">{formatCurrency(stats.total_value_cents || 0)}</div>
            <div className="text-xs text-neutral-400">Total Value</div>
          </CardContent>
        </Card>
      </div>


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Conversion Funnel
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {Object.entries(STATUS_CONFIG).map(([key, { label, color }]) => {
              const count = byStatus[key] || 0;
              const pct = funnelPercent(count, stats.total || 1);
              return (
                <div key={key} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-neutral-300">{label}</span>
                    <span className="text-neutral-400">{count} ({pct}%)</span>
                  </div>
                  <div className="h-2 bg-neutral-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${color} rounded-full transition-all`}
                      style={{ width: `${Math.max(pct, 2)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>

        <Card className="bg-neutral-900 border-neutral-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-300">Open Rate</span>
              <span className="text-sm font-medium text-blue-400">{stats.open_rate || 0}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-300">Click Rate</span>
              <span className="text-sm font-medium text-amber-400">{stats.click_rate || 0}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-300">Acceptance Rate</span>
              <span className="text-sm font-medium text-green-400">{stats.acceptance_rate || 0}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-300">Rejection Rate</span>
              <span className="text-sm font-medium text-red-400">{stats.rejection_rate || 0}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-300">Avg Score</span>
              <span className="text-sm font-medium">{formatScore(stats.avg_score)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-300">Avg Days to Accept</span>
              <span className="text-sm font-medium">{stats.avg_days_to_accept ?? "—"}</span>
            </div>
            <div className="border-t border-neutral-800 pt-2 mt-2">
              <div className="text-xs text-neutral-500 mb-2">Last 7 days</div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <div className="text-sm font-bold text-orange-400">{stats.recent_7d_created || 0}</div>
                  <div className="text-xs text-neutral-500">Created</div>
                </div>
                <div>
                  <div className="text-sm font-bold text-indigo-400">{stats.recent_7d_sent || 0}</div>
                  <div className="text-xs text-neutral-500">Sent</div>
                </div>
                <div>
                  <div className="text-sm font-bold text-green-400">{stats.recent_7d_accepted || 0}</div>
                  <div className="text-xs text-neutral-500">Accepted</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>


      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">All Proposals</CardTitle>
        </CardHeader>
        <CardContent>
          {proposals.length === 0 ? (
            <div className="text-center py-8 text-neutral-500">No proposals found. Create proposals from the Contacts or Conversations page.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-800 text-left text-neutral-400">
                    <th className="pb-2 pr-4 font-medium">Title</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">Score</th>
                    <th className="pb-2 pr-4 font-medium">Reviewed</th>
                    <th className="pb-2 pr-4 font-medium">Engagement</th>
                    <th className="pb-2 pr-4 font-medium">Value</th>
                    <th className="pb-2 pr-4 font-medium">Created</th>
                    <th className="pb-2 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {proposals.map((p) => {
                    const cfg = STATUS_CONFIG[p.status] || { label: p.status, color: "bg-gray-500", icon: FileText };
                    return (
                      <tr key={p.id} className="border-b border-neutral-800/50 hover:bg-neutral-800/40">
                        <td className="py-2 pr-4">
                          <button className="text-left text-neutral-200 hover:text-orange-400 transition-colors" onClick={() => setSelectedProposal(p)}>
                            {p.title}
                          </button>
                        </td>
                        <td className="py-2 pr-4">
                          <Badge variant="secondary" className={`${cfg.color} text-white text-xs`}>
                            {cfg.label}
                          </Badge>
                        </td>
                        <td className="py-2 pr-4 text-neutral-300">{formatScore(p.score)}</td>
                        <td className="py-2 pr-4">
                          {p.reviewed ? (
                            <Badge variant="outline" className="text-green-400 border-green-400/30 text-xs">Reviewed</Badge>
                          ) : (
                            <span className="text-neutral-500 text-xs">Pending</span>
                          )}
                        </td>
                        <td className="py-2 pr-4">
                          <div className="flex items-center gap-2 text-xs text-neutral-400">
                            <span title="Sent">{p.sent_count}↑</span>
                            <span title="Opened">{p.opened_count}👁</span>
                            <span title="Clicked">{p.clicked_count}🖱</span>
                          </div>
                        </td>
                        <td className="py-2 pr-4 text-neutral-300">{formatCurrency(p.value_cents, p.currency)}</td>
                        <td className="py-2 pr-4 text-neutral-400 text-xs">{p.created_at ? new Date(p.created_at).toLocaleDateString() : "—"}</td>
                        <td className="py-2">
                          <select
                            className="bg-neutral-800 border border-neutral-700 rounded text-xs px-1 py-0.5 text-neutral-300"
                            value={p.status}
                            onChange={(e) => handleStatusChange(p.id, e.target.value)}
                          >
                            {Object.entries(STATUS_CONFIG).map(([key, { label }]) => (
                              <option key={key} value={key}>{label}</option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>


      <Dialog open={!!selectedProposal} onOpenChange={() => setSelectedProposal(null)}>
        <DialogContent className="max-w-2xl bg-neutral-900 border-neutral-800">
          <DialogHeader>
            <DialogTitle>{selectedProposal?.title}</DialogTitle>
          </DialogHeader>
          {selectedProposal && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-neutral-400">Status</div>
                  <Badge variant="secondary" className={`${(STATUS_CONFIG[selectedProposal.status] || { color: "bg-gray-500" }).color} text-white`}>
                    {(STATUS_CONFIG[selectedProposal.status] || { label: selectedProposal.status }).label}
                  </Badge>
                </div>
                <div>
                  <div className="text-xs text-neutral-400">Score</div>
                  <div className="text-sm">{formatScore(selectedProposal.score)}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-400">Value</div>
                  <div className="text-sm">{formatCurrency(selectedProposal.value_cents, selectedProposal.currency)}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-400">Reviewed</div>
                  <div className="text-sm">{selectedProposal.reviewed ? `Yes (${selectedProposal.reviewed_at || ""})` : "No"}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-400">Sent</div>
                  <div className="text-sm">{selectedProposal.sent_at || "Not sent"}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-400">Accepted / Rejected</div>
                  <div className="text-sm">
                    {selectedProposal.accepted_at ? `✓ ${selectedProposal.accepted_at}` : selectedProposal.rejected_at ? `✗ ${selectedProposal.rejected_at}` : "—"}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 border-t border-neutral-800 pt-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-indigo-400">{selectedProposal.sent_count}</div>
                  <div className="text-xs text-neutral-400">Times Sent</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-400">{selectedProposal.opened_count}</div>
                  <div className="text-xs text-neutral-400">Opens</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-amber-400">{selectedProposal.clicked_count}</div>
                  <div className="text-xs text-neutral-400">Clicks</div>
                </div>
              </div>

              {selectedProposal.review_notes && (
                <div>
                  <div className="text-xs text-neutral-400 mb-1">Review Notes</div>
                  <div className="text-sm bg-neutral-800 p-3 rounded">{selectedProposal.review_notes}</div>
                </div>
              )}

              <div>
                <div className="text-xs text-neutral-400 mb-1">Content</div>
                <div className="text-sm bg-neutral-800 p-3 rounded max-h-64 overflow-y-auto whitespace-pre-wrap">{selectedProposal.content}</div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}