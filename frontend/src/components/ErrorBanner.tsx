import { AlertCircle, Terminal } from 'lucide-react';

interface ErrorBannerProps {
  error: { stage: string; message: string } | null;
  onDismiss: () => void;
}

export function ErrorBanner({ error, onDismiss }: ErrorBannerProps) {
  if (!error) return null;

  return (
    <div className="w-full max-w-4xl mx-auto mb-8 bg-red-950/40 border border-red-500/50 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in slide-in-from-top-4 fade-in duration-300">
      <div className="flex items-start gap-4">
        <div className="p-2 bg-red-500/20 rounded-full mt-0.5 sm:mt-0">
          <AlertCircle size={24} className="text-red-400" />
        </div>
        <div>
          <h3 className="text-red-300 font-semibold text-lg flex items-center gap-2">
            Pipeline Error
            <span className="text-xs font-mono bg-red-900/50 text-red-200 px-2 py-0.5 rounded border border-red-800">
              STAGE: {error.stage}
            </span>
          </h3>
          <div className="text-red-200/80 mt-1 flex items-start gap-2 bg-red-950/50 p-2 rounded text-sm font-mono mt-2">
            <Terminal size={14} className="mt-0.5 shrink-0 opacity-70" />
            {error.message}
          </div>
        </div>
      </div>
      
      <button 
        onClick={onDismiss}
        className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-300 rounded border border-red-500/30 transition-colors whitespace-nowrap self-end sm:self-auto"
      >
        Dismiss
      </button>
    </div>
  );
}
