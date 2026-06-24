import { useState, useRef } from 'react';
import { AuditForm } from './components/AuditForm';
import { MetricsPanel } from './components/MetricsPanel';
import { InsightPanel } from './components/InsightPanel';
import { RecommendationCards } from './components/RecommendationCards';
import { StatusBar } from './components/StatusBar';
import type { PipelineStage } from './components/StatusBar';
import { ErrorBanner } from './components/ErrorBanner';
import { streamAudit } from './api/fetchSSE';
import type { ScrapedMetrics, RecommendationItem } from './types/audit';
import { Activity } from 'lucide-react';

function App() {
  const [, setUrl] = useState<string>('');
  const [stage, setStage] = useState<PipelineStage>('idle');
  const [error, setError] = useState<{ stage: string; message: string } | null>(null);
  
  const [metrics, setMetrics] = useState<ScrapedMetrics | null>(null);
  const [insightText, setInsightText] = useState<string>('');
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [traceMeta, setTraceMeta] = useState<{ trace_id: string; path: string } | null>(null);

  const isStreamingRef = useRef(false);

  const handleAudit = async (targetUrl: string) => {
    // Reset state
    setUrl(targetUrl);
    setStage('scraping');
    setError(null);
    setMetrics(null);
    setInsightText('');
    setRecommendations([]);
    setTraceMeta(null);
    
    isStreamingRef.current = true;

    await streamAudit(targetUrl, {
      onMetrics: (data) => {
        setMetrics(data);
        setStage('analysing');
      },
      onInsightChunk: (chunk) => {
        setInsightText(prev => prev + chunk);
      },
      onRecommendations: (recs) => {
        setRecommendations(recs);
      },
      onPromptLogMeta: (traceId, path) => {
        setTraceMeta({ trace_id: traceId, path });
      },
      onError: (errStage, message) => {
        setError({ stage: errStage, message });
        setStage('idle');
        isStreamingRef.current = false;
      },
      onDone: () => {
        setStage('done');
        isStreamingRef.current = false;
      }
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-8 font-sans selection:bg-blue-500/30">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <header className="flex flex-col items-center text-center mb-10 mt-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-xl shadow-lg shadow-blue-900/20">
              <Activity size={28} className="text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
              Auditor-One
            </h1>
          </div>
          <p className="text-slate-400 max-w-2xl text-lg">
            AI-Native Website Audit Tool. Deterministic harvesting combined with deep heuristic reasoning.
          </p>
        </header>

        {/* Input Form */}
        <AuditForm onAudit={handleAudit} isLoading={stage === 'scraping' || stage === 'analysing'} />

        {/* Error Banner */}
        <ErrorBanner error={error} onDismiss={() => setError(null)} />

        {/* Pipeline Status */}
        <StatusBar stage={stage} traceMeta={traceMeta} />

        {/* Main Dashboard Layout */}
        {(stage !== 'idle' || metrics) && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            {/* Column A: Fixed Metrics */}
            <div className="sticky top-8">
              <MetricsPanel metrics={metrics} />
            </div>

            {/* Column B: Streaming Insights & Recommendations */}
            <div className="space-y-6">
              <InsightPanel content={insightText} />
              
              <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
                <RecommendationCards recommendations={recommendations} />
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
