import type { ScrapedMetrics } from '../types/audit';
import { Type, Link, Image as ImageIcon, MousePointerClick, FileText, LayoutTemplate } from 'lucide-react';

interface MetricsPanelProps {
  metrics: ScrapedMetrics | null;
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  if (!metrics) {
    return (
      <div className="h-[600px] w-full rounded-xl border border-slate-800 bg-slate-900/50 flex items-center justify-center text-slate-500">
        Waiting for page analysis...
      </div>
    );
  }

  return (
    <div className="h-[600px] w-full rounded-xl border border-slate-700 bg-slate-800/80 p-6 overflow-y-auto space-y-6 scrollbar-thin scrollbar-thumb-slate-600">
      <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2 mb-6">
        <LayoutTemplate className="text-blue-400" />
        Page Metrics
      </h2>

      <div className="grid grid-cols-2 gap-4">
        {/* Words */}
        <MetricCard
          icon={<Type size={20} className="text-emerald-400" />}
          label="Word Count"
          value={metrics.word_count.toLocaleString()}
        />

        {/* CTAs */}
        <MetricCard
          icon={<MousePointerClick size={20} className="text-amber-400" />}
          label="Call-to-Actions"
          value={metrics.cta_count.toLocaleString()}
        />

        {/* Links */}
        <MetricCard
          icon={<Link size={20} className="text-indigo-400" />}
          label="Total Links"
          value={(metrics.links.internal + metrics.links.external).toLocaleString()}
          subtext={`${metrics.links.internal} Internal / ${metrics.links.external} External`}
        />

        {/* Images */}
        <MetricCard
          icon={<ImageIcon size={20} className="text-pink-400" />}
          label="Images"
          value={metrics.images.total.toLocaleString()}
          subtext={`${metrics.images.missing_alt} Missing Alt (${metrics.images.missing_alt_percentage.toFixed(1)}%)`}
          isAlert={metrics.images.missing_alt_percentage > 50}
        />
      </div>

      {/* Headings */}
      <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-700/50">
        <div className="text-sm text-slate-400 mb-2 font-medium">Heading Structure</div>
        <div className="flex justify-between items-center text-slate-300">
          <div className="flex flex-col items-center">
            <span className="text-lg font-bold text-slate-100">{metrics.headings.h1}</span>
            <span className="text-xs">H1</span>
          </div>
          <div className="h-8 w-px bg-slate-700"></div>
          <div className="flex flex-col items-center">
            <span className="text-lg font-bold text-slate-100">{metrics.headings.h2}</span>
            <span className="text-xs">H2</span>
          </div>
          <div className="h-8 w-px bg-slate-700"></div>
          <div className="flex flex-col items-center">
            <span className="text-lg font-bold text-slate-100">{metrics.headings.h3}</span>
            <span className="text-xs">H3</span>
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-700/50">
        <div className="flex items-center gap-2 text-sm text-slate-400 mb-2 font-medium">
          <FileText size={16} />
          Metadata
        </div>
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-500 uppercase tracking-wider">Title</span>
              {metrics.metadata.title_length !== null && (
                <LengthBadge length={metrics.metadata.title_length} min={30} max={60} />
              )}
            </div>
            <div className="text-sm text-slate-200 line-clamp-2">
              {metrics.metadata.title || <span className="text-red-400 italic">Missing</span>}
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-500 uppercase tracking-wider">Description</span>
              {metrics.metadata.description_length !== null && (
                <LengthBadge length={metrics.metadata.description_length} min={70} max={160} />
              )}
            </div>
            <div className="text-sm text-slate-200 line-clamp-3">
              {metrics.metadata.description || <span className="text-red-400 italic">Missing</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value, subtext, isAlert }: { icon: React.ReactNode, label: string, value: string | number, subtext?: string, isAlert?: boolean }) {
  return (
    <div className={`bg-slate-900/60 rounded-lg p-4 border ${isAlert ? 'border-red-500/50' : 'border-slate-700/50'}`}>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-sm text-slate-400 font-medium">{label}</span>
      </div>
      <div className="text-2xl font-bold text-slate-100">{value}</div>
      {subtext && <div className={`text-xs mt-1 ${isAlert ? 'text-red-400' : 'text-slate-500'}`}>{subtext}</div>}
    </div>
  );
}

function LengthBadge({ length, min, max }: { length: number; min: number; max: number }) {
  const isInRange = length >= min && length <= max;
  const isBorderline = !isInRange && length >= min - 10 && length <= max + 10;

  let bgClass = "bg-rose-500/10 text-rose-400 border border-rose-500/20";
  let dotColor = "bg-rose-400";

  if (isInRange) {
    bgClass = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
    dotColor = "bg-emerald-400";
  } else if (isBorderline) {
    bgClass = "bg-amber-500/10 text-amber-400 border border-amber-500/20";
    dotColor = "bg-amber-400";
  }

  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-semibold tracking-wide ${bgClass}`}>
      <span className={`w-1 h-1 rounded-full ${dotColor}`} />
      {length} / {min}-{max}
    </span>
  );
}
