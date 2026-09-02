# -*- coding: utf-8 -*-
import os

fe_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\frontend"

def write_f(rel_path, code):
    p = os.path.join(fe_root, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")
    print(f"Created: {rel_path}")

# 1. tsconfig.json
write_f("tsconfig.json", """
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""")

# 2. next.config.js
write_f("next.config.js", """
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
""")

# 3. postcss.config.js
write_f("postcss.config.js", """
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
""")

# 4. tailwind.config.js
write_f("tailwind.config.js", """
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F17',
        surface: '#111827',
        'surface-elevated': '#1F2937',
        border: '#374151',
        primary: {
          DEFAULT: '#10B981',
          foreground: '#064E3B',
          50: '#ECFDF5',
          500: '#10B981',
          600: '#059669',
          700: '#047857'
        },
        accent: {
          blue: '#3B82F6',
          amber: '#F59E0B',
          rose: '#F43F5E',
          purple: '#8B5CF6'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
};
""")

# 5. app/globals.css
write_f("app/globals.css", """
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-[#0B0F17] text-slate-100 antialiased selection:bg-emerald-500 selection:text-black;
    font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  }
}

/* Custom Scrollbars */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: #0B0F17;
}
::-webkit-scrollbar-thumb {
  background: #1F2937;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #374151;
}
""")

# 6. lib/api.ts
write_f("lib/api.ts", """
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api';

export interface Company {
  id: number;
  name: string;
  cin?: string;
  sector: string;
  target_ipo_date?: string;
  description?: string;
  created_at: string;
  document_count?: number;
  metric_count?: number;
  risk_count?: number;
  readiness_score?: number;
}

export interface DocumentItem {
  id: number;
  company_id: number;
  filename: string;
  file_hash: string;
  document_type: string;
  fiscal_year?: string;
  page_count: number;
  file_size_bytes: number;
  processing_status: 'UPLOADED' | 'PROCESSING' | 'PARSED' | 'INDEXED' | 'FAILED' | 'NEEDS_REVIEW';
  processing_duration_ms: number;
  error_message?: string;
  created_at: string;
  chunk_count?: number;
}

export interface FinancialMetric {
  id: number;
  company_id: number;
  document_id?: number;
  metric_name: string;
  raw_value_str: string;
  normalized_value_inr: number;
  currency: string;
  unit: string;
  fiscal_year: string;
  statement_type: string;
  source_document_name: string;
  source_page?: number;
  source_cell_ref?: string;
  confidence_score: number;
  status: 'EXTRACTED' | 'VERIFIED' | 'FLAGGED' | 'REJECTED';
  created_at: string;
}

export interface ConsistencyCheck {
  id: number;
  company_id: number;
  metric_name: string;
  fiscal_year: string;
  source_a_doc_name: string;
  source_a_page_or_cell?: string;
  source_a_value_raw: string;
  source_a_value_normalized: number;
  source_b_doc_name: string;
  source_b_page_or_cell?: string;
  source_b_value_raw: string;
  source_b_value_normalized: number;
  variance_amount: number;
  variance_percentage: number;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'MODIFIED';
  resolution_notes?: string;
  created_at: string;
}

export interface FinancialRisk {
  id: number;
  company_id: number;
  risk_type: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  evidence: string;
  formula_used?: string;
  source_citation: string;
  confidence_score: number;
  recommended_action: string;
  is_resolved: boolean;
  created_at: string;
}

export interface IPOReadiness {
  id: number;
  company_id: number;
  overall_score: number;
  financial_completeness_score: number;
  financial_consistency_score: number;
  profitability_score: number;
  cashflow_score: number;
  debt_health_score: number;
  growth_score: number;
  document_coverage_score: number;
  breakdown_details: any;
  created_at: string;
}

export interface ReviewItem {
  id: number;
  company_id: number;
  item_type: string;
  reference_id?: number;
  reason: string;
  original_payload: any;
  modified_payload?: any;
  review_status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'MODIFIED';
  notes?: string;
  reviewed_at?: string;
  created_at: string;
}

export interface AuditLog {
  id: number;
  company_id: number;
  action_type: string;
  query_text?: string;
  steps_executed: any[];
  tools_used?: any[];
  calculations?: any[];
  final_output?: string;
  latency_ms: number;
  created_at: string;
}

export interface ChatResponse {
  answer: string;
  confidence_score: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  sources: Array<{
    source_document: string;
    page_number?: number;
    cell_reference?: string;
    snippet: string;
    confidence: number;
  }>;
  tools_executed: Array<{
    tool_name: string;
    arguments: any;
    result: any;
    execution_time_ms: number;
  }>;
  calculations: Array<{
    formula: string;
    inputs: any;
    result: any;
    explanation: string;
  }>;
  guardrail_status: string;
  latency_ms: number;
  audit_log_id: number;
}

export interface EvaluationReport {
  total_evaluated: number;
  answer_accuracy_pct: number;
  citation_accuracy_pct: number;
  retrieval_precision_pct: number;
  retrieval_recall_pct: number;
  hallucination_rate_pct: number;
  unsupported_claim_rate_pct: number;
  average_latency_ms: number;
  average_confidence_pct: number;
  results: Array<{
    id: number;
    question: string;
    category: string;
    expected_answer: string;
    actual_answer: string;
    expected_source: string;
    sources_cited: string[];
    is_correct: boolean;
    citation_accurate: boolean;
    confidence: number;
    latency_ms: number;
  }>;
}

export const api = {
  getCompanies: async (): Promise<Company[]> => {
    const res = await fetch(`${API_BASE}/companies`);
    return res.json();
  },
  seedDemo: async (): Promise<Company> => {
    const res = await fetch(`${API_BASE}/demo/seed`, { method: 'POST' });
    return res.json();
  },
  getDocuments: async (companyId: number): Promise<DocumentItem[]> => {
    const res = await fetch(`${API_BASE}/documents?company_id=${companyId}`);
    return res.json();
  },
  getMetrics: async (companyId: number): Promise<FinancialMetric[]> => {
    const res = await fetch(`${API_BASE}/financial-metrics?company_id=${companyId}`);
    return res.json();
  },
  getReadiness: async (companyId: number): Promise<IPOReadiness> => {
    const res = await fetch(`${API_BASE}/ipo-readiness/${companyId}`);
    return res.json();
  },
  getRisks: async (companyId: number): Promise<FinancialRisk[]> => {
    const res = await fetch(`${API_BASE}/risks/${companyId}`);
    return res.json();
  },
  getConsistency: async (companyId: number): Promise<ConsistencyCheck[]> => {
    const res = await fetch(`${API_BASE}/consistency-checks/${companyId}`);
    return res.json();
  },
  getReviews: async (companyId: number): Promise<ReviewItem[]> => {
    const res = await fetch(`${API_BASE}/reviews?company_id=${companyId}`);
    return res.json();
  },
  actionReview: async (itemId: number, action: string, notes?: string): Promise<ReviewItem> => {
    const res = await fetch(`${API_BASE}/reviews/${itemId}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, notes })
    });
    return res.json();
  },
  getAuditLogs: async (companyId: number): Promise<AuditLog[]> => {
    const res = await fetch(`${API_BASE}/audit-logs?company_id=${companyId}`);
    return res.json();
  },
  chat: async (companyId: number, query: string): Promise<ChatResponse> => {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_id: companyId, query })
    });
    return res.json();
  },
  runEvaluation: async (companyId: number): Promise<EvaluationReport> => {
    const res = await fetch(`${API_BASE}/evaluations/run?company_id=${companyId}`, { method: 'POST' });
    return res.json();
  },
  getSystemMetrics: async () => {
    const res = await fetch(`${API_BASE}/system/metrics`);
    return res.json();
  }
};
""")

print("Frontend core files and API client generated.")
