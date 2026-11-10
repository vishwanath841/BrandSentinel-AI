import React from 'react';
import { Palette, Eye, AlertTriangle, CheckCircle, ShieldCheck } from 'lucide-react';

export default function VisualInspectorCard({ visualDetails, visualScore }) {
  if (!visualDetails || Object.keys(visualDetails).length === 0) {
    return null;
  }

  const {
    dominant_colors = [],
    palette_matches = [],
    compliant_pixel_percentage = 0,
    contrast_ratio = 1.0,
    contrast_passes_wcag = true,
    dimensions = {}
  } = visualDetails;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <Palette className="h-5 w-5 text-sky-400" />
          <h3 className="text-sm font-bold text-white">Visual Brand Inspector (OpenCV Analysis)</h3>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-medium">Visual Compliance:</span>
          <span
            className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
              visualScore >= 80
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                : visualScore >= 60
                ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                : 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
            }`}
          >
            {visualScore}/100
          </span>
        </div>
      </div>

      {/* Dominant Colors & Palette Matching */}
      <div className="space-y-2">
        <span className="text-xs font-semibold text-slate-300 block">
          Extracted Dominant Color Palette (K-Means Clustering)
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {dominant_colors.map((color, idx) => (
            <div key={idx} className="bg-slate-800/60 p-2.5 rounded-xl border border-slate-700/50 space-y-1.5">
              <div
                className="h-12 w-full rounded-lg shadow-inner flex items-center justify-center font-mono text-[11px] font-bold text-white shadow-black/40"
                style={{ backgroundColor: color.hex }}
              >
                {color.hex}
              </div>
              <div className="flex justify-between text-[11px] text-slate-400 font-mono">
                <span>{color.percentage}%</span>
                <span className="text-slate-500 text-[10px]">Cluster #{idx + 1}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Measurable Visual Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Brand Palette Alignment</span>
          <div className="flex items-baseline space-x-2">
            <span className="text-lg font-bold text-sky-400">{compliant_pixel_percentage}%</span>
            <span className="text-[11px] text-slate-500">pixels match brand tolerance</span>
          </div>
        </div>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">WCAG Visual Contrast Ratio</span>
          <div className="flex items-center space-x-2">
            <span className="text-lg font-bold text-white font-mono">{contrast_ratio}:1</span>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                contrast_passes_wcag
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                  : 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
              }`}
            >
              {contrast_passes_wcag ? 'Passes (≥3.0:1)' : 'Low Contrast (<3.0:1)'}
            </span>
          </div>
        </div>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Asset Dimensions</span>
          <div className="flex items-baseline space-x-2">
            <span className="text-lg font-bold text-white font-mono">
              {dimensions.width}×{dimensions.height}
            </span>
            <span className="text-[11px] text-slate-500">{dimensions.format || 'IMAGE'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

