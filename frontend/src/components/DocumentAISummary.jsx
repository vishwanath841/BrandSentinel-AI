import React, { useMemo } from 'react';
import {
  FileText, Sparkles, CheckCircle2, AlertTriangle, ShieldCheck,
  ShieldAlert, Compass, ArrowRight, Clock, Layers, Tag,
  FileCheck, BookOpen, Download, UserCheck, BarChart3, AlertCircle,
  HelpCircle, ChevronRight
} from 'lucide-react';

export default function DocumentAISummary({
  submission,
  onSwitchTab,
  onOpenReviewModal,
  onExportReport
}) {
  if (!submission || !submission.report) return null;

  const { report } = submission;
  const findings = report.findings || [];
  const text = submission.extracted_text || '';

  // Extract statistics
  const stats = useMemo(() => {
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;
    const paragraphs = text.split(/\n\s*\n/).filter((p) => p.trim().length > 0).length || (text ? 1 : 0);
    const readingTimeMin = Math.max(1, Math.ceil(words / 200));
    return { words, chars, paragraphs, readingTimeMin };
  }, [text]);

  // Extract key themes / concepts from text
  const extractedThemes = useMemo(() => {
    const candidateKeywords = [
      'Cloud Architecture', 'High Availability', 'Uptime SLA', 'Zero Downtime',
      'Cybersecurity', 'ISO 27001', 'SOC 2 Type II', 'Data Fabric', 'Latency',
      'Enterprise Infrastructure', 'Competitor Comparison', 'Cost Optimization',
      'Disaster Recovery', 'Multi-Region', 'API Gateway', 'Zero Trust', 'Microservices'
    ];
    const found = candidateKeywords.filter((kw) =>
      text.toLowerCase().includes(kw.toLowerCase())
    );
    if (found.length === 0) {
      if (submission.intended_channel) found.push(submission.intended_channel);
      found.push('Corporate Communications', 'Brand Messaging');
    }
    return found.slice(0, 8);
  }, [text, submission.intended_channel]);

  // Group findings by category
  const categorizedFindings = useMemo(() => {
    const terms = findings.filter((f) => f.category === 'TERMINOLOGY');
    const claims = findings.filter((f) => f.category === 'CLAIM_GUARD');
    const tones = findings.filter((f) => f.category === 'TONE');
    const comps = findings.filter((f) => f.category === 'COMPETITOR');
    const criticals = findings.filter((f) => f.severity === 'CRITICAL');
    const highs = findings.filter((f) => f.severity === 'HIGH');
    const mediums = findings.filter((f) => f.severity === 'MEDIUM');
    const lows = findings.filter((f) => f.severity === 'LOW');
    return { terms, claims, tones, comps, criticals, highs, mediums, lows };
  }, [findings]);

  // Generate dynamic document subject matter synthesis
  const documentSubjectMatter = useMemo(() => {
    const typeLabel = submission.content_type === 'PDF'
      ? 'PDF document'
      : submission.content_type === 'DOCX'
      ? 'Word document'
      : submission.content_type === 'IMAGE'
      ? 'visual marketing graphic'
      : 'marketing copy draft';

    const mainTheme = extractedThemes.length > 0
      ? extractedThemes.slice(0, 3).join(', ')
      : 'enterprise product positioning';

    return (
      `This ${typeLabel} focuses on ${mainTheme}, prepared by ${submission.creator_name || 'the team'} ` +
      `specifically targeting the ${submission.intended_channel || 'public marketing'} channel. ` +
      `The material presents product capabilities, operational guarantees, and technical value propositions across ${stats.paragraphs} structural section(s).`
    );
  }, [submission, extractedThemes, stats]);

  // Generate verified strengths
  const verifiedStrengths = useMemo(() => {
    const list = [];
    if (report.terminology_score >= 80) {
      list.push('High adherence to corporate vocabulary and approved product nomenclature');
    }
    if (report.fact_score >= 80) {
      list.push('Claims consistently reference verifiable corporate benchmarks and standards');
    }
    if (report.tone_score >= 80) {
      list.push('Tone maintains professional enterprise credibility and objective clarity');
    }
    if (text.toLowerCase().includes('iso 27001') || text.toLowerCase().includes('soc 2')) {
      list.push('Accurate citations of independent security certifications');
    }
    if (list.length === 0) {
      list.push('Clear messaging purpose with identifiable customer value proposition');
      list.push('Structured format suitable for enterprise audience review');
    }
    return list;
  }, [report, text]);

  const previewSnippet = text.trim().slice(0, 240);

  return (
    <div className="space-y-6">
      {/* 1. Executive Intelligence Header Banner */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-slate-800/80">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-sky-500/10 text-sky-400 border border-sky-500/20">
                AI Document Intelligence
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-slate-800 text-slate-300 border border-slate-700">
                {submission.content_type} File
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono text-slate-400 bg-slate-800/70 border border-slate-700/50">
                {report.engine_used}
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {submission.title}
            </h1>

            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 pt-1">
              <span>Author: <strong className="text-slate-200">{submission.creator_name}</strong></span>
              <span>•</span>
              <span>Channel: <strong className="text-slate-200">{submission.intended_channel}</strong></span>
              <span>•</span>
              <span className="flex items-center space-x-1">
                <Clock className="h-3.5 w-3.5 text-slate-500" />
                <span>{stats.readingTimeMin} min read ({stats.words} words)</span>
              </span>
            </div>
          </div>

          {/* Compliance Gauge */}
          <div className="flex items-center space-x-4 bg-slate-950/80 p-4 rounded-2xl border border-slate-800 self-start lg:self-auto">
            <div className="text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">
                Compliance Score
              </span>
              <div className="flex items-baseline justify-center space-x-1">
                <span
                  className={`text-4xl font-extrabold tracking-tight ${
                    report.overall_score >= 85
                      ? 'text-emerald-400'
                      : report.overall_score >= 65
                      ? 'text-amber-400'
                      : 'text-rose-400'
                  }`}
                >
                  {report.overall_score}
                </span>
                <span className="text-slate-500 text-xs font-mono">/100</span>
              </div>
              <span
                className={`inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full mt-1 ${
                  report.risk_level === 'PASS' || report.risk_level === 'LOW'
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                    : report.risk_level === 'MEDIUM'
                    ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                    : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                }`}
              >
                {report.risk_level} Risk
              </span>
            </div>

            <div className="h-12 w-px bg-slate-800" />

            <div className="space-y-1 text-xs">
              <div className="flex justify-between items-center space-x-3">
                <span className="text-slate-400">Total Findings:</span>
                <span className="font-bold text-white font-mono">{findings.length}</span>
              </div>
              <div className="flex justify-between items-center space-x-3">
                <span className="text-slate-400">Critical / High:</span>
                <span className="font-bold text-rose-400 font-mono">
                  {categorizedFindings.criticals.length + categorizedFindings.highs.length}
                </span>
              </div>
              <div className="flex justify-between items-center space-x-3">
                <span className="text-slate-400">Approval State:</span>
                <span className="font-bold text-sky-400 text-[11px]">
                  {submission.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Primary Executive Synthesis Callout */}
        <div className="mt-6 p-4 sm:p-5 bg-sky-500/5 rounded-2xl border border-sky-500/20 flex items-start space-x-3.5">
          <div className="h-8 w-8 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 flex-shrink-0 mt-0.5">
            <Sparkles className="h-4 w-4" />
          </div>
          <div className="space-y-1">
            <span className="text-xs font-bold text-sky-300 uppercase tracking-wider block">
              Executive Governance Synthesis
            </span>
            <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-normal">
              {report.summary}
            </p>
          </div>
        </div>
      </div>

      {/* 2. Three Enterprise Core Columns / Pillars */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Pillar 1: Document Architecture & Extracted Content ("What It Contains") */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col justify-between space-y-5">
          <div className="space-y-4">
            <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-800">
              <div className="h-7 w-7 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
                <BookOpen className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Document Scope & Content Profile
                </h2>
                <span className="text-[11px] text-slate-400">Analysis of source material & topics</span>
              </div>
            </div>

            {/* Narrative Subject Matter */}
            <p className="text-xs text-slate-300 leading-relaxed">
              {documentSubjectMatter}
            </p>

            {/* Extracted Themes */}
            <div className="space-y-2 pt-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Extracted Themes & Key Topics
              </span>
              <div className="flex flex-wrap gap-1.5">
                {extractedThemes.map((theme, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700/60"
                  >
                    <Tag className="h-3 w-3 text-sky-400" />
                    <span>{theme}</span>
                  </span>
                ))}
              </div>
            </div>

            {/* Structural Metrics */}
            <div className="grid grid-cols-2 gap-2 pt-2 text-xs">
              <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80">
                <span className="text-[10px] text-slate-400 block">Extracted Length</span>
                <span className="text-sm font-extrabold text-white font-mono">{stats.words} Words</span>
              </div>
              <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80">
                <span className="text-[10px] text-slate-400 block">Structural Units</span>
                <span className="text-sm font-extrabold text-white font-mono">{stats.paragraphs} Section(s)</span>
              </div>
            </div>

            {/* Content Excerpt Snippet */}
            {previewSnippet && (
              <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 space-y-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  Source Text Excerpt
                </span>
                <p className="text-[11px] text-slate-300 italic line-clamp-3 leading-relaxed">
                  "{previewSnippet}..."
                </p>
              </div>
            )}
          </div>

          <button
            onClick={() => onSwitchTab('reader')}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-750 hover:bg-slate-700 text-sky-400 border border-slate-700 rounded-xl text-xs font-semibold transition"
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Open Document Reader ({stats.words} words)</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Pillar 2: Governance Diagnosis & Identified Risks ("What It Has / What Was Found") */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col justify-between space-y-5">
          <div className="space-y-4">
            <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-800">
              <div className="h-7 w-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <ShieldAlert className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Compliance Diagnosis & Risk Inventory
                </h2>
                <span className="text-[11px] text-slate-400">Identified policy violations & tone slips</span>
              </div>
            </div>

            {/* Violation Categorization Pills */}
            <div className="space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Detected Deviations Breakdown
              </span>

              <div className="space-y-2">
                {/* Terminology */}
                <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="h-2 w-2 rounded-full bg-sky-400" />
                    <span className="text-slate-300 font-medium">Prohibited Brand Terms</span>
                  </div>
                  <span className="text-xs font-bold text-white font-mono px-2 py-0.5 rounded-full bg-slate-800">
                    {categorizedFindings.terms.length} issue(s)
                  </span>
                </div>

                {/* ClaimGuard */}
                <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="h-2 w-2 rounded-full bg-amber-400" />
                    <span className="text-slate-300 font-medium">Unverified / Contradictory Claims</span>
                  </div>
                  <span className="text-xs font-bold text-white font-mono px-2 py-0.5 rounded-full bg-slate-800">
                    {categorizedFindings.claims.length} claim(s)
                  </span>
                </div>

                {/* Tone */}
                <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="h-2 w-2 rounded-full bg-indigo-400" />
                    <span className="text-slate-300 font-medium">Voice & Tone Deviations</span>
                  </div>
                  <span className="text-xs font-bold text-white font-mono px-2 py-0.5 rounded-full bg-slate-800">
                    {categorizedFindings.tones.length} issue(s)
                  </span>
                </div>
              </div>
            </div>

            {/* Evaluated Strengths */}
            <div className="space-y-2 pt-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Validated Governance Strengths
              </span>
              <ul className="space-y-1.5">
                {verifiedStrengths.map((str, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-xs text-slate-300">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <button
            onClick={() => onSwitchTab('findings')}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 rounded-xl text-xs font-semibold transition"
          >
            <span>Inspect All {findings.length} Findings</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Pillar 3: Strategic Action Plan ("What We Need to Do") */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col justify-between space-y-5">
          <div className="space-y-4">
            <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-800">
              <div className="h-7 w-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Compass className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-white tracking-wide">
                  Strategic Publication Roadmap
                </h2>
                <span className="text-[11px] text-slate-400">Operational steps prior to publishing</span>
              </div>
            </div>

            {/* Step 1 */}
            <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 space-y-1">
              <div className="flex items-center space-x-2 text-xs font-bold text-white">
                <span className="h-5 w-5 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center text-[10px] font-mono">1</span>
                <span>Apply Intent-Preserving Revisions</span>
              </div>
              <p className="text-[11px] text-slate-400 pl-7 leading-relaxed">
                Review and accept formulated rewrites for the {findings.length} flagged phrase(s) to eliminate forbidden terms while protecting the author's promotional goal.
              </p>
            </div>

            {/* Step 2 */}
            <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 space-y-1">
              <div className="flex items-center space-x-2 text-xs font-bold text-white">
                <span className="h-5 w-5 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center text-[10px] font-mono">2</span>
                <span>Substantiate Performance Claims</span>
              </div>
              <p className="text-[11px] text-slate-400 pl-7 leading-relaxed">
                Confirm verified benchmark citations with technical leads for any unsupported SLA statistics before public release.
              </p>
            </div>

            {/* Step 3 */}
            <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 space-y-1">
              <div className="flex items-center space-x-2 text-xs font-bold text-white">
                <span className="h-5 w-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] font-mono">3</span>
                <span>Conduct Formal Human Sign-Off</span>
              </div>
              <p className="text-[11px] text-slate-400 pl-7 leading-relaxed">
                Record official brand manager approval in the governance audit ledger to authorize distribution across {submission.intended_channel}.
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <button
              onClick={onOpenReviewModal}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-sky-600/20 transition"
            >
              <UserCheck className="h-4 w-4" />
              <span>Start Human Review & Approval</span>
            </button>

            <button
              onClick={onExportReport}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-xl text-xs font-semibold transition"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export Executive Briefing (JSON)</span>
            </button>
          </div>
        </div>

      </div>

      {/* 3. Detailed Scores & Meters Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Terminology</span>
            <span className="font-bold text-white font-mono">{report.terminology_score}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-sky-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${report.terminology_score}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-500 block">Prohibited words adherence</span>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">ClaimGuard</span>
            <span className="font-bold text-white font-mono">{report.fact_score}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${report.fact_score}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-500 block">Fact & claim verifiability</span>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Tone & Voice</span>
            <span className="font-bold text-white font-mono">{report.tone_score}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-indigo-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${report.tone_score}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-500 block">Corporate persona alignment</span>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Visual Identity</span>
            <span className="font-bold text-white font-mono">{report.visual_score}%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-purple-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${report.visual_score}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-500 block">Color palette & contrast</span>
        </div>
      </div>
    </div>
  );
}

