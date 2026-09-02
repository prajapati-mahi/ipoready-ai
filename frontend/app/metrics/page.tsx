'use client';

import React, { useState, useEffect } from 'react';
import { 
  Layers, Filter, ArrowUpDown, CheckCircle2, AlertCircle, 
  ExternalLink, FileSpreadsheet, TrendingUp, DollarSign
} from 'lucide-react';
import { api, FinancialMetric } from '@/lib/api';

export default function FinancialMetricsPage() {
  const [metrics, setMetrics] = useState<FinancialMetric[]>([]);
  const [unitMode, setUnitMode] = useState<'SOURCE' | 'INR_CR' | 'USD_MN'>('SOURCE');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const list = await api.getMetrics(companies[0].id);
        setMetrics(list);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (m: FinancialMetric) => {
    if (unitMode === 'SOURCE') return m.raw_value_str;
    if (unitMode === 'INR_CR') {
      const cr = (m.normalized_value_inr / 10_000_000).toFixed(2);
      return `₹${cr} Cr`;
    }
    if (unitMode === 'USD_MN') {
      const usd = (m.normalized_value_inr / (83 * 1_000_000)).toFixed(2);
      return `$${usd} Mn`;
    }
    return m.raw_value_str;
  };

  const filteredMetrics = metrics.filter(m => {
    const periodMatch = selectedPeriod === 'ALL' || m.fiscal_year === selectedPeriod;
    const searchMatch = m.metric_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        m.source_document_name.toLowerCase().includes(searchTerm.toLowerCase());
    return periodMatch && searchMatch;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Structured Financial Metrics Explorer</h1>
          <p className="text-xs text-slate-400">16+ normalized core financial metrics with verified cell and page references</p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 p-1 rounded-lg">
          <button
            onClick={() => setUnitMode('SOURCE')}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
              unitMode === 'SOURCE' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Source Units
          </button>
          <button
            onClick={() => setUnitMode('INR_CR')}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
              unitMode === 'INR_CR' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Normalize ₹ Cr
          </button>
          <button
            onClick={() => setUnitMode('USD_MN')}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
              unitMode === 'USD_MN' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Normalize $ USD Mn
          </button>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <input
          type="text"
          placeholder="Search metric name or source document..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-xl text-xs text-slate-200 placeholder-slate-500 w-full sm:w-72 outline-none focus:border-emerald-500"
        />

        <div className="flex items-center space-x-2">
          {['ALL', 'FY2024', 'FY2023', 'FY2022'].map((p) => (
            <button
              key={p}
              onClick={() => setSelectedPeriod(p)}
              className={`px-3 py-1 text-xs font-medium rounded-lg border transition-all ${
                selectedPeriod === p ? 'bg-slate-800 border-emerald-500 text-emerald-400' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Metric Name</th>
                <th className="py-3.5 px-4">Fiscal Period</th>
                <th className="py-3.5 px-4 text-right">Extracted / Normalized Value</th>
                <th className="py-3.5 px-4">Statement Type</th>
                <th className="py-3.5 px-4">Source Citation</th>
                <th className="py-3.5 px-4 text-center">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {filteredMetrics.map((m) => (
                <tr key={m.id} className="hover:bg-slate-800/30 transition-all">
                  <td className="py-3.5 px-4 font-bold text-white">
                    {m.metric_name}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 border border-slate-700 text-slate-300 font-mono">
                      {m.fiscal_year}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right font-bold text-emerald-400 text-sm font-mono">
                    {formatValue(m)}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">
                    {m.statement_type}
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center space-x-1.5 text-slate-300">
                      <span className="text-xs truncate max-w-[200px]">{m.source_document_name}</span>
                      {m.source_page && (
                        <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
                          Page {m.source_page}
                        </span>
                      )}
                      {m.source_cell_ref && (
                        <span className="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-1.5 py-0.5 rounded font-mono">
                          {m.source_cell_ref}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {(m.confidence_score * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
