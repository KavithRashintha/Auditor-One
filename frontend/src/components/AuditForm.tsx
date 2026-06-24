import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

interface AuditFormProps {
  onAudit: (url: string) => void;
  isLoading: boolean;
}

export function AuditForm({ onAudit, isLoading }: AuditFormProps) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim() && !isLoading) {
      onAudit(url.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto mb-8">
      <div className="relative flex items-center w-full h-14 rounded-full bg-slate-800 border border-slate-700 shadow-lg focus-within:ring-2 focus-within:ring-blue-500 overflow-hidden transition-all duration-300">
        <div className="grid place-items-center h-full w-14 text-slate-400">
          <Search size={20} />
        </div>
        
        <input
          className="peer h-full w-full outline-none text-sm text-slate-200 bg-transparent pr-4 placeholder-slate-400"
          type="url"
          id="url"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          disabled={isLoading}
        />
        
        <button 
          type="submit" 
          disabled={isLoading}
          className="h-full px-6 bg-blue-600 hover:bg-blue-500 text-white font-medium transition-colors disabled:bg-slate-700 disabled:text-slate-400 flex items-center justify-center min-w-[120px]"
        >
          {isLoading ? <Loader2 className="animate-spin" size={20} /> : "Audit"}
        </button>
      </div>
    </form>
  );
}
