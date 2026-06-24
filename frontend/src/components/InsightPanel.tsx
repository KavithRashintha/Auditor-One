import ReactMarkdown from 'react-markdown';
import { Sparkles } from 'lucide-react';

interface InsightPanelProps {
  content: string;
}

const DELIMITER = "---REC_SPLIT---";

export function InsightPanel({ content }: InsightPanelProps) {
  // Strip delimiter + everything after it if the backend didn't catch it
  const safeContent = content.includes(DELIMITER)
    ? content.substring(0, content.indexOf(DELIMITER)).trim()
    : content;

  if (!safeContent) {
    return (
      <div className="h-[600px] w-full rounded-xl border border-slate-800 bg-slate-900/50 flex flex-col items-center justify-center text-slate-500 gap-4">
        <Sparkles size={32} className="opacity-20" />
        <span>AI insights will appear here...</span>
      </div>
    );
  }

  return (
    <div className="h-[600px] w-full rounded-xl border border-slate-700 bg-slate-800/80 p-6 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 flex flex-col">
      <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2 mb-6 shrink-0">
        <Sparkles className="text-purple-400" />
        AI Analysis
      </h2>
      
      <div className="prose prose-invert prose-slate max-w-none prose-headings:text-slate-100 prose-a:text-blue-400 prose-p:text-slate-300 flex-grow">
        <ReactMarkdown>{safeContent}</ReactMarkdown>
      </div>
    </div>
  );
}
