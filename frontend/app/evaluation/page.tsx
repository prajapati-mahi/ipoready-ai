'use client';

import React, { useState, useEffect } from 'react';
import { 
  Activity, Play, CheckCircle2, XCircle, AlertCircle, 
  Sparkles, Gauge, Target, ShieldCheck, Clock, Layers
} from 'lucide-react';
import { api, EvaluationReport } from '@/lib/api';

export default function EvaluationPage() {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [running, setRunning] = useState(false);
  const [filterCategory, setFilterCategory] = useState<string>('ALL');

  useEffect(() => {
    runBenchmark();
  }, []);

  const runBenchmark = async () => {
    setRunning(true);
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const rep = await api.runEvaluation(companies[0].id);
        setReport(rep);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  const categories = ['ALL', 'Metric Extraction', 'Financial Math', 'Comparative Analysis', 'Negative Test / Missing Data', 'Risk Analysis'];

  const filteredResults = report?.results.filter(r => 
    filterCategory === 'ALL' || r.category === filterCategory
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Autonomous AI Evaluation & Golden Benchmark</h1>
          <p className="text-xs text-slate-400">Live evaluation against 35 golden questions measuring authentic accuracy, citation precision, and hallucination rate</p>
        </div>

        <button
          onClick={runBenchmark}
          disabled={running}
          className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-md shadow-emerald-600/20 transition-all"
        >
          <Play className="h-3.5 w-3.5" />
          <span>{running ? 'Running 35 Evaluations...' : 'Re-Run Benchmark'}</span>
        </button>
      </div>

      {report && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Answer Accuracy</span>
            <span className="text-xl font-extrabold text-emerald-400 font-mono">{report.answer_accuracy_pct}%</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Citation Precision</span>
            <span className="text-xl font-extrabold text-emerald-400 font-mono">{report.citation_accuracy_pct}%</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Retrieval Precision</span>
            <span className="text-xl font-extrabold text-blue-400 font-mono">{report.retrieval_precision_pct}%</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Hallucination Rate</span>
            <span className="text-xl font-extrabold text-emerald-400 font-mono">{report.hallucination_rate_pct}%</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Average Latency</span>
            <span className="text-xl font-extrabold text-purple-400 font-mono">{report.average_latency_ms} ms</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Confidence Score</span>
            <span className="text-xl font-extrabold text-amber-400 font-mono">{report.average_confidence_pct}%</span>
          </div>
        </div>
      )}

      <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
        {categories.map((c) => (
          <button
            key={c}
            onClick={() => setFilterCategory(c)}
            className={`px-3 py-1 font-medium rounded-lg border whitespace-nowrap transition-all ${
              filterCategory === c ? 'bg-slate-800 border-emerald-500 text-emerald-400' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800'
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">#</th>
                <th className="py-3 px-4">Evaluation Question</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Expected Ground Truth</th>
                <th className="py-3 px-4">AI Agent Output</th>
                <th className="py-3 px-4 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {filteredResults.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/30 transition-all">
                  <td className="py-3 px-4 text-slate-500 font-mono">{item.id}</td>
                  <td className="py-3 px-4 font-medium text-white max-w-xs">{item.question}</td>
                  <td className="py-3 px-4 text-slate-400">{item.category}</td>
                  <td className="py-3 px-4 font-mono text-emerald-400 font-bold">{item.expected_answer}</td>
                  <td className="py-3 px-4 text-slate-300 max-w-sm truncate">{item.actual_answer}</td>
                  <td className="py-3 px-4 text-center">
                    {item.is_correct ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="h-3 w-3 mr-1" /> PASS
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        <XCircle className="h-3 w-3 mr-1" /> FAIL
                      </span>
                    )}
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
