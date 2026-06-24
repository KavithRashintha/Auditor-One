import { Loader2, CheckCircle2, Clock, Globe } from 'lucide-react';

export type PipelineStage = 'idle' | 'scraping' | 'analysing' | 'done';

interface StatusBarProps {
  stage: PipelineStage;
  traceMeta?: { trace_id: string; path: string } | null;
}

export function StatusBar({ stage, traceMeta }: StatusBarProps) {
  if (stage === 'idle') return null;

  return (
    <div className="w-full max-w-2xl mx-auto mb-8 bg-slate-800/80 border border-slate-700/50 rounded-lg p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-6">
        <StatusItem 
          active={stage === 'scraping'} 
          completed={stage === 'analysing' || stage === 'done'} 
          icon={<Globe size={18} />} 
          label="Scraping & Harvesting" 
        />
        <div className="w-8 h-px bg-slate-700 hidden sm:block"></div>
        <StatusItem 
          active={stage === 'analysing'} 
          completed={stage === 'done'} 
          icon={<Clock size={18} />} 
          label="AI Analysis" 
        />
      </div>
      
      {stage === 'done' && traceMeta && (
        <div className="text-xs text-slate-500 font-mono bg-slate-900 px-3 py-1.5 rounded-md border border-slate-800 flex flex-col items-end">
          <span className="text-[10px] uppercase text-slate-600">Trace Log Saved</span>
          {traceMeta.trace_id.split('-')[0]}...
        </div>
      )}
    </div>
  );
}

function StatusItem({ active, completed, icon, label }: { active: boolean; completed: boolean; icon: React.ReactNode; label: string }) {
  const colorClass = completed 
    ? 'text-emerald-400' 
    : active 
      ? 'text-blue-400' 
      : 'text-slate-600';

  return (
    <div className={`flex items-center gap-2 ${colorClass} transition-colors duration-500`}>
      {active ? <Loader2 size={18} className="animate-spin" /> : completed ? <CheckCircle2 size={18} /> : icon}
      <span className={`text-sm ${active ? 'font-medium' : ''}`}>{label}</span>
    </div>
  );
}
