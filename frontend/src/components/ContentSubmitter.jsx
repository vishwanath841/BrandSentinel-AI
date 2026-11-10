import React, { useState } from 'react';
import {
  FileText, Upload, Image as ImageIcon, Sparkles, Send,
  AlertCircle, Check, HelpCircle, FileCheck
} from 'lucide-react';
import { createSubmission } from '../services/api';

const SAMPLE_TEMPLATES = [
  {
    name: 'Marketing Draft with Violations & Unsupported Claims',
    title: 'Q4 Global Product Launch Draft',
    channel: 'Press Release & Social',
    creator: 'Alex Rivera (Copywriter)',
    content: `We are thrilled to unveil our new magic cloud platform! Unlike legacy solutions where AWS is garbage, ApexCloud guarantees 100% bug-free performance with guaranteed zero downtime for every customer. Our insane synergistic architecture delivers sub-15ms p99 query latency, trusted by over 14,000 enterprise customers across 45 countries. We are gonna crush our rivals and ensure your data is 100% secure with ISO 27001 certification.`
  },
  {
    name: 'Contradictory SLA & Exaggerated Claims',
    title: 'Enterprise High-Availability Announcement',
    channel: 'Technical Landing Page',
    creator: 'Taylor Vance (Product Marketing)',
    content: `ApexCloud delivers an unbreakable platform backed by an unprecedented 99.999% monthly uptime SLA. Our world's first data fabric eliminates all downtime forever. Switch today or you will regret settling for inferior competitors who rip off customers.`
  },
  {
    name: 'Fully Compliant Enterprise Benchmark Report',
    title: '2024 Cloud Performance Benchmark Release',
    channel: 'Official Press Release',
    creator: 'Jordan Lee (Communications Lead)',
    content: `ApexCloud guarantees 99.99% monthly uptime SLA backed by automated financial service credits. Over 14,000 enterprise customers across 45 countries operate mission-critical workloads on ApexCloud. Our integrated architecture delivers sub-15ms p99 query latency across globally distributed multi-region clusters, independently certified for ISO 27001 and SOC 2 Type II compliance.`
  }
];

export default function ContentSubmitter({ brand, onSubmissionCreated }) {
  const [submissionType, setSubmissionType] = useState('text'); // text, document, image
  const [title, setTitle] = useState('');
  const [creatorName, setCreatorName] = useState('Marketing Copywriter');
  const [intendedChannel, setIntendedChannel] = useState('Social Media & Web');
  const [textContent, setTextContent] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    setSelectedFile(file);
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (event) => setImagePreview(event.target.result);
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  }

  function handleLoadSample(sample) {
    setTitle(sample.title);
    setIntendedChannel(sample.channel);
    setCreatorName(sample.creator);
    setTextContent(sample.content);
    setSubmissionType('text');
    setSelectedFile(null);
    setImagePreview(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!brand) return;
    if (submissionType === 'text' && !textContent.trim()) {
      setError('Please enter text content to analyze.');
      return;
    }
    if ((submissionType === 'document' || submissionType === 'image') && !selectedFile) {
      setError('Please select a file to upload.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('brand_id', brand.id);
      formData.append('title', title || (selectedFile ? selectedFile.name : 'Untitled Submission'));
      formData.append('creator_name', creatorName);
      formData.append('intended_channel', intendedChannel);

      if (submissionType === 'text') {
        formData.append('text_content', textContent);
      } else if (selectedFile) {
        formData.append('file', selectedFile);
        if (textContent.trim()) {
          formData.append('text_content', textContent);
        }
      }

      const result = await createSubmission(formData);
      onSubmissionCreated(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <FileCheck className="h-5 w-5 text-sky-400" />
            <span>Pre-Publication Content Submission</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Submit marketing copy, whitepapers (PDF/DOCX), or promotional images to verify brand compliance.
          </p>
        </div>

        {/* Input Mode Selector */}
        <div className="flex bg-slate-800/80 p-1 rounded-xl border border-slate-700/60 self-start md:self-auto">
          <button
            type="button"
            onClick={() => { setSubmissionType('text'); setSelectedFile(null); }}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              submissionType === 'text'
                ? 'bg-sky-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Text Editor</span>
          </button>

          <button
            type="button"
            onClick={() => { setSubmissionType('document'); setImagePreview(null); }}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              submissionType === 'document'
                ? 'bg-sky-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Upload className="h-3.5 w-3.5" />
            <span>Document (PDF/DOCX)</span>
          </button>

          <button
            type="button"
            onClick={() => setSubmissionType('image')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              submissionType === 'image'
                ? 'bg-sky-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ImageIcon className="h-3.5 w-3.5" />
            <span>Image Asset</span>
          </button>
        </div>
      </div>

      {/* 1-Click Demo Samples */}
      <div className="my-4 p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
        <span className="text-[11px] font-semibold text-slate-400 flex items-center space-x-1.5 mb-2">
          <Sparkles className="h-3.5 w-3.5 text-amber-400" />
          <span>Quick Hackathon Test Samples (Click to Load):</span>
        </span>
        <div className="flex flex-wrap gap-2">
          {SAMPLE_TEMPLATES.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleLoadSample(sample)}
              className="text-left px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 hover:border-sky-500/40 rounded-lg text-xs text-slate-300 hover:text-white transition group"
            >
              <span className="font-semibold block text-[11px] text-sky-400 group-hover:underline">
                {sample.name}
              </span>
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-xl text-xs flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Submission Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="block text-slate-400 font-medium mb-1">Content Title</label>
            <input
              type="text"
              placeholder="e.g. Q4 Press Release Announcement"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
              required
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Creator / Author</label>
            <input
              type="text"
              placeholder="e.g. Content Copywriter"
              value={creatorName}
              onChange={(e) => setCreatorName(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Publishing Channel</label>
            <select
              value={intendedChannel}
              onChange={(e) => setIntendedChannel(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              <option value="Social Media (Twitter/LinkedIn)">Social Media (Twitter/LinkedIn)</option>
              <option value="Official Press Release">Official Press Release</option>
              <option value="Landing Page & Web Copy">Landing Page & Web Copy</option>
              <option value="Ad Campaign (Google / Meta)">Ad Campaign (Google / Meta)</option>
              <option value="Technical Whitepaper">Technical Whitepaper</option>
            </select>
          </div>
        </div>

        {/* Dynamic Input based on Type */}
        {submissionType === 'text' && (
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs text-slate-400 font-medium">Text Content to Inspect</label>
              <span className="text-[11px] text-slate-500 font-mono">
                {textContent.length} characters | {textContent.split(/\s+/).filter(Boolean).length} words
              </span>
            </div>
            <textarea
              rows={6}
              placeholder="Paste or write your promotional copy, draft blog post, or ad caption here..."
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              className="w-full bg-slate-950/70 border border-slate-700 rounded-xl p-3.5 text-white text-xs font-sans leading-relaxed focus:outline-none focus:ring-1 focus:ring-sky-500"
              required
            />
          </div>
        )}

        {(submissionType === 'document' || submissionType === 'image') && (
          <div className="border-2 border-dashed border-slate-700 hover:border-sky-500/60 rounded-xl p-8 text-center transition bg-slate-950/40">
            {submissionType === 'document' ? (
              <Upload className="h-10 w-10 text-sky-400 mx-auto mb-2" />
            ) : (
              <ImageIcon className="h-10 w-10 text-sky-400 mx-auto mb-2" />
            )}

            <label className="cursor-pointer">
              <span className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 rounded-xl text-xs font-semibold inline-block transition">
                {submissionType === 'document'
                  ? 'Choose Document (.pdf, .docx, .txt)'
                  : 'Choose Image (.png, .jpg, .webp)'}
              </span>
              <input
                type="file"
                accept={submissionType === 'document' ? '.pdf,.docx,.doc,.txt' : 'image/*'}
                className="hidden"
                onChange={handleFileChange}
              />
            </label>

            {selectedFile && (
              <div className="mt-3 text-xs text-emerald-400 font-medium">
                Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
              </div>
            )}

            {imagePreview && (
              <div className="mt-4 max-w-xs mx-auto">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="rounded-lg border border-slate-700 max-h-48 mx-auto shadow-md"
                />
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-[11px] text-slate-500 flex items-center space-x-1.5">
            <Sparkles className="h-3.5 w-3.5 text-sky-400" />
            <span>Inspection runs deterministic rules, ClaimGuard verification, tone analysis, and visual checks.</span>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="flex items-center space-x-2 px-6 py-2.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-sky-600/20 transition disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Inspecting Content...</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Run BrandSentinel Inspection</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

