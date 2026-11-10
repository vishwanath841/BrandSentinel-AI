import React, { useState, useMemo } from 'react';
import {
  FileText, Search, Copy, Check, ExternalLink, AlertTriangle,
  Info, ArrowLeft, BookOpen, Layers
} from 'lucide-react';

export default function DocumentReader({ submission, onSwitchTab }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [copied, setCopied] = useState(false);

  const text = submission?.extracted_text || '';
  const findings = submission?.report?.findings || [];

  const paragraphs = useMemo(() => {
    if (!text.trim()) return [];
    return text.split(/\n\s*\n/).filter((p) => p.trim().length > 0);
  }, [text]);

  const flaggedPhrases = useMemo(() => {
    return findings.map((f) => ({
      text: f.flagged_text,
      severity: f.severity,
      category: f.category,
      explanation: f.explanation
    }));
  }, [findings]);

  function handleCopy() {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  // Filter paragraphs if searching
  const filteredParagraphs = useMemo(() => {
    if (!searchQuery.trim()) return paragraphs;
    const query = searchQuery.toLowerCase();
    return paragraphs.filter((p) => p.toLowerCase().includes(query));
  }, [paragraphs, searchQuery]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-sky-500/10 text-sky-400 border border-sky-500/20">
              Source Document Reader
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-300 border border-slate-700">
              {submission?.content_type}
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-white mt-1">
            {submission?.title}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Full text extracted from uploaded material ({paragraphs.length} paragraphs • {text.trim().split(/\s+/).filter(Boolean).length} words)
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-xl text-xs font-semibold transition"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{copied ? 'Copied' : 'Copy All Text'}</span>
          </button>

          <button
            onClick={() => onSwitchTab('summary')}
            className="flex items-center space-x-1.5 px-3 py-2 bg-sky-600/20 hover:bg-sky-600/30 text-sky-300 border border-sky-500/30 rounded-xl text-xs font-semibold transition"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Back to AI Summary</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search extracted document text..."
          className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50"
        />
        {searchQuery && (
          <span className="absolute right-3.5 top-2.5 text-[10px] text-slate-400">
            {filteredParagraphs.length} match(es)
          </span>
        )}
      </div>

      {/* Flagged legend */}
      {flaggedPhrases.length > 0 && (
        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex flex-wrap items-center gap-3 text-xs text-slate-400">
          <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
            Flagged Items ({flaggedPhrases.length}):
          </span>
          {flaggedPhrases.slice(0, 5).map((fp, i) => (
            <span
              key={i}
              className={`px-2 py-0.5 rounded-lg text-[10px] font-mono border ${
                fp.severity === 'CRITICAL'
                  ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                  : fp.severity === 'HIGH'
                  ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                  : 'bg-sky-500/10 text-sky-300 border-sky-500/30'
              }`}
            >
              "{fp.text}"
            </span>
          ))}
          {flaggedPhrases.length > 5 && (
            <span className="text-[10px] text-slate-500">+{flaggedPhrases.length - 5} more</span>
          )}
        </div>
      )}

      {/* Paragraphs Reader */}
      <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
        {filteredParagraphs.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs">
            No matching paragraphs found.
          </div>
        ) : (
          filteredParagraphs.map((paragraph, index) => (
            <div
              key={index}
              className="p-4 bg-slate-950/70 hover:bg-slate-950 rounded-2xl border border-slate-800/80 transition flex items-start space-x-3"
            >
              <span className="text-[10px] font-mono text-slate-600 select-none pt-0.5 flex-shrink-0 w-6">
                #{index + 1}
              </span>
              <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">
                {paragraph}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

