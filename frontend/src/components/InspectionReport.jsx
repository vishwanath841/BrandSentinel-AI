import React, { useState } from 'react';
import {
  ShieldAlert, CheckCircle, AlertTriangle, XCircle, ArrowRight,
  Sparkles, RefreshCw, Layers, CheckCheck, SlidersHorizontal, BookOpen, Download,
  FileText, CheckCircle2, ShieldCheck, Compass, ArrowUpRight, FileSpreadsheet,
  Image as ImageIcon
} from 'lucide-react';
import ClaimGuardPanel from './ClaimGuardPanel';
import VisualInspectorCard from './VisualInspectorCard';
import DocumentAISummary from './DocumentAISummary';
import DocumentReader from './DocumentReader';

export default function InspectionReport({ submission, onOpenReviewModal, onReinspect }) {
  const [activeViewTab, setActiveViewTab] = useState('summary'); // 'summary', 'findings', 'claimguard', 'reader', 'visual'
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');

  function handleExportReport() {
    if (!submission) return;
    const reportData = {
      project: 'BrandSentinel AI Governance Audit',
      submission_title: submission.title,
      creator_name: submission.creator_name,
      intended_channel: submission.intended_channel,
      content_type: submission.content_type,
      status: submission.status,
      exported_at: new Date().toISOString(),
      overall_compliance_score: submission.report?.overall_score,
      risk_level: submission.report?.risk_level,
      engine_used: submission.report?.engine_used,
      findings_count: submission.report?.findings?.length || 0,
      report: submission.report,
      audit_reviews: submission.reviews
    };
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `BrandSentinel_Audit_${(submission.title || 'report').replace(/[^a-zA-Z0-9]/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!submission || !submission.report) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
        <Sparkles className="h-8 w-8 text-sky-400 mx-auto mb-3 animate-pulse" />
        <p className="text-sm font-semibold text-white">No analysis report available.</p>
        <p className="text-xs text-slate-500 mt-1">Submit content above to generate an inspection report.</p>
      </div>
    );
  }

  const { report } = submission;
  const findings = report.findings || [];
  const pendingCount = findings.filter((f) => f.review_status === 'PENDING').length;

  // Filter findings for the findings tab
  const filteredFindings = findings.filter((f) => {
    const matchesCategory = categoryFilter === 'ALL' || f.category === categoryFilter;
    const matchesSeverity = severityFilter === 'ALL' || f.severity === severityFilter;
    return matchesCategory && matchesSeverity;
  });

  return (
    <div className="space-y-6">
      {/* Top Global Action Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-1">
              <h2 className="text-xl font-extrabold text-white">{submission.title}</h2>
              <span
                className={`text-xs font-bold uppercase tracking-wider px-3 py-0.5 rounded-full ${
                  submission.status === 'APPROVED'
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                    : submission.status === 'CHANGES_REQUESTED'
                    ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                    : submission.status === 'REJECTED'
                    ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                    : 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                }`}
              >
                {submission.status.replace('_', ' ')}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span>Creator: <strong className="text-slate-300">{submission.creator_name}</strong></span>
              <span>•</span>
              <span>Channel: <strong className="text-slate-300">{submission.intended_channel}</strong></span>
              <span>•</span>
              <span>Format: <strong className="text-slate-300">{submission.content_type}</strong></span>
              <span>•</span>
              <span className="font-mono text-[11px] text-slate-500">
                {new Date(submission.created_at).toLocaleString()}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={handleExportReport}
              className="flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition border border-slate-700"
              title="Export complete compliance report as JSON"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export Audit</span>
            </button>

            <button
              onClick={() => onReinspect(submission.id)}
              className="flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition border border-slate-700"
              title="Re-run inspection pipeline"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Re-inspect</span>
            </button>

            <button
              onClick={onOpenReviewModal}
              className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-sky-600/25 transition"
            >
              <CheckCheck className="h-4 w-4" />
              <span>Human Review & Approval ({pendingCount} pending)</span>
            </button>
          </div>
        </div>

        {/* High-Visibility View Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-2 mt-5 pt-4 border-t border-slate-800/80">
          <button
            onClick={() => setActiveViewTab('summary')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeViewTab === 'summary'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800/80'
            }`}
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>AI Document Summary & Briefing</span>
          </button>

          <button
            onClick={() => setActiveViewTab('findings')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeViewTab === 'findings'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800/80'
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Audit Findings ({findings.length})</span>
          </button>

          <button
            onClick={() => setActiveViewTab('claimguard')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeViewTab === 'claimguard'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800/80'
            }`}
          >
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>ClaimGuard Fact Verification</span>
          </button>

          <button
            onClick={() => setActiveViewTab('reader')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeViewTab === 'reader'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800/80'
            }`}
          >
            <BookOpen className="h-3.5 w-3.5" />
            <span>Document Reader & Text</span>
          </button>

          {submission.content_type === 'IMAGE' && (
            <button
              onClick={() => setActiveViewTab('visual')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition ${
                activeViewTab === 'visual'
                  ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                  : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800/80'
              }`}
            >
              <ImageIcon className="h-3.5 w-3.5" />
              <span>Visual Asset Analysis</span>
            </button>
          )}
        </div>
      </div>

      {/* VIEW TAB 1: AI Summary & Executive Briefing Page */}
      {activeViewTab === 'summary' && (
        <DocumentAISummary
          submission={submission}
          onSwitchTab={setActiveViewTab}
          onOpenReviewModal={onOpenReviewModal}
          onExportReport={handleExportReport}
        />
      )}

      {/* VIEW TAB 2: Findings & Smart Suggestions */}
      {activeViewTab === 'findings' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-800">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Layers className="h-4 w-4 text-sky-400" />
                <span>Evidence-Linked Findings & Smart Suggestions ({filteredFindings.length})</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Each issue is explained with specific brand rule citations and proposed intent-preserving corrections.
              </p>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-2">
              <select
                aria-label="Filter by Category"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none"
              >
                <option value="ALL">All Categories</option>
                <option value="TERMINOLOGY">Terminology</option>
                <option value="CLAIM_GUARD">ClaimGuard</option>
                <option value="TONE">Tone & Voice</option>
                <option value="VISUAL">Visual</option>
                <option value="ACCESSIBILITY">Accessibility</option>
              </select>

              <select
                aria-label="Filter by Severity"
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none"
              >
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          {/* Findings List */}
          {filteredFindings.length === 0 ? (
            <div className="p-8 text-center bg-slate-950/40 rounded-xl text-slate-500 text-xs">
              No issues match current filters. Content adheres to evaluated criteria.
            </div>
          ) : (
            <div className="space-y-4">
              {filteredFindings.map((finding) => (
                <div
                  key={finding.id}
                  className="p-5 bg-slate-950/60 border border-slate-800/90 hover:border-slate-700 rounded-xl space-y-3 transition group"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                          finding.severity === 'CRITICAL'
                            ? 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
                            : finding.severity === 'HIGH'
                            ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                            : 'bg-sky-500/15 text-sky-400 border border-sky-500/20'
                        }`}
                      >
                        {finding.severity}
                      </span>
                      <span className="text-xs font-semibold text-slate-400 font-mono">
                        [{finding.category}]
                      </span>
                    </div>

                    <span
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                        finding.review_status === 'ACCEPTED'
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                          : finding.review_status === 'EDITED'
                          ? 'bg-sky-500/15 text-sky-400 border border-sky-500/20'
                          : finding.review_status === 'REJECTED'
                          ? 'bg-slate-700 text-slate-400'
                          : 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      Status: {finding.review_status}
                    </span>
                  </div>

                  {/* Flagged Text */}
                  <div className="text-xs">
                    <span className="text-[11px] text-slate-400 font-medium block mb-1">Flagged Content:</span>
                    <div className="bg-rose-950/20 border border-rose-500/30 text-rose-200 p-2.5 rounded-lg font-medium">
                      "{finding.flagged_text}"
                    </div>
                  </div>

                  {/* Explanation & Evidence */}
                  <div className="text-xs text-slate-300 space-y-1">
                    <p>{finding.explanation}</p>
                    {finding.evidence && (
                      <div className="p-2 bg-slate-900 rounded border border-slate-800 text-[11px] text-slate-400">
                        <strong className="text-slate-300">Rule Citation / Evidence:</strong> {finding.evidence}
                      </div>
                    )}
                  </div>

                  {/* Intent-Preserving Suggested Revision */}
                  {finding.suggested_revision && (
                    <div className="pt-2 border-t border-slate-800/80 text-xs">
                      <span className="text-[11px] text-emerald-400 font-semibold block mb-1">
                        Intent-Preserving Smart Revision:
                      </span>
                      <div className="bg-emerald-950/20 border border-emerald-500/30 text-emerald-200 p-2.5 rounded-lg font-medium">
                        "{finding.suggested_revision}"
                      </div>
                      {finding.revision_rationale && (
                        <p className="text-[11px] text-slate-400 italic mt-1">
                          Why this works: {finding.revision_rationale}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* VIEW TAB 3: ClaimGuard Panel */}
      {activeViewTab === 'claimguard' && (
        <ClaimGuardPanel findings={findings} />
      )}

      {/* VIEW TAB 4: Document Reader */}
      {activeViewTab === 'reader' && (
        <DocumentReader
          submission={submission}
          onSwitchTab={setActiveViewTab}
        />
      )}

      {/* VIEW TAB 5: Visual Asset Inspector */}
      {activeViewTab === 'visual' && submission.content_type === 'IMAGE' && (
        <VisualInspectorCard
          visualDetails={report.visual_details}
          visualScore={report.visual_score}
        />
      )}
    </div>
  );
}
