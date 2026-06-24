import type { RecommendationItem } from '../types/audit';
import { Target, AlertTriangle, Lightbulb } from 'lucide-react';

interface RecommendationCardsProps {
  recommendations: RecommendationItem[];
}

export function RecommendationCards({ recommendations }: RecommendationCardsProps) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="mt-8 space-y-4">
      <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2 mb-4">
        <Target className="text-emerald-400" />
        Actionable Recommendations
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.sort((a, b) => a.priority - b.priority).map((rec, idx) => (
          <div key={idx} className="bg-slate-800/80 border border-slate-700/50 rounded-xl p-5 hover:border-slate-600 transition-colors">
            <div className="flex items-start justify-between mb-3">
              <span className={`text-xs font-bold px-2 py-1 rounded-md uppercase tracking-wide
                ${rec.priority === 1 ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                  rec.priority === 2 ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 
                  'bg-blue-500/20 text-blue-400 border border-blue-500/30'}`}>
                Priority {rec.priority}
              </span>
              <span className="text-xs text-slate-500 font-mono bg-slate-900/50 px-2 py-1 rounded">
                {rec.metric_reference}
              </span>
            </div>
            
            <h4 className="text-slate-200 font-medium mb-2 flex items-start gap-2">
              <AlertTriangle size={16} className="text-amber-400 mt-0.5 shrink-0" />
              {rec.issue}
            </h4>
            
            <p className="text-sm text-slate-400 flex items-start gap-2 mt-3 bg-slate-900/40 p-3 rounded-lg border border-slate-800/50">
              <Lightbulb size={16} className="text-emerald-400 mt-0.5 shrink-0" />
              {rec.actionable_recommendation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
