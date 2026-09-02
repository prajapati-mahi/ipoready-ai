# -*- coding: utf-8 -*-
import os

fe_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\frontend"

docs_code = """'use client';

import React, { useState, useEffect } from 'react';
import { 
  FileText, UploadCloud, CheckCircle2, AlertCircle, 
  Clock, Hash, FileSpreadsheet, Layers, Eye, Download, Search
} from 'lucide-react';
import { api, DocumentItem } from '@/lib/api';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [chunks, setChunks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const cId = companies[0].id;
        const docs = await api.getDocuments(cId);
        setDocuments(docs);
        if (docs.length > 0) {
          setSelectedDocId(docs[0].id);
          fetchChunks(docs[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchChunks = async (docId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/documents/${docId}/chunks`);
      const data = await res.json();
      setChunks(data);
    } catch (e) {
      console.error('Chunks fetch error:', e);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    const companies = await api.getCompanies();
    if (companies.length === 0) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_id', companies[0].id.toString());
    formData.append('document_type', file.name.endsWith('.pdf') ? 'Annual Report / Filing' : 'Spreadsheet Model');
    formData.append('fiscal_year', 'FY2024');

    try {
      await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData
      });
      await loadDocs();
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const filteredDocs = documents.filter(d => 
    d.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.document_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Document Ingestion & Parsing Hub</h1>
          <p className="text-xs text-slate-400">High-fidelity PDF & Excel extraction with SHA-256 deduplication and page-level chunking</p>
        </div>

        <div className="flex items-center space-x-3">
          <label className="cursor-pointer flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-md shadow-emerald-600/20 transition-all">
            <UploadCloud className="h-4 w-4" />
            <span>{uploading ? 'Processing File...' : 'Upload Document'}</span>
            <input type="file" onChange={handleFileUpload} accept=".pdf,.xlsx,.xls,.csv,.docx" className="hidden" />
          </label>
        </div>
      </div>

      <div className="flex items-center bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-xl text-xs text-slate-300">
        <Search className="h-4 w-4 text-slate-500 mr-2" />
        <input 
          type="text" 
          placeholder="Filter filings by filename, document type, or period..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-transparent border-none outline-none w-full text-slate-200 placeholder-slate-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-bold text-white">Ingested Filings ({documents.length})</h2>
            <span className="text-[11px] text-slate-400">PDF, XLSX, CSV Supported</span>
          </div>

          <div className="divide-y divide-slate-800">
            {filteredDocs.map((doc) => {
              const isSelected = selectedDocId === doc.id;
              return (
                <div 
                  key={doc.id}
                  onClick={() => {
                    setSelectedDocId(doc.id);
                    fetchChunks(doc.id);
                  }}
                  className={`p-4 cursor-pointer transition-all flex items-start justify-between ${
                    isSelected ? 'bg-slate-800/60 border-l-4 border-emerald-500' : 'hover:bg-slate-800/30'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="p-2 rounded-lg bg-slate-800 border border-slate-700 mt-0.5">
                      {doc.filename.endsWith('.pdf') ? (
                        <FileText className="h-5 w-5 text-emerald-400" />
                      ) : (
                        <FileSpreadsheet className="h-5 w-5 text-blue-400" />
                      )}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white">{doc.filename}</h4>
                      <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-1">
                        <span className="text-emerald-400/90 font-medium">{doc.document_type}</span>
                        <span>•</span>
                        <span>{doc.page_count} Pages / Sheets</span>
                        <span>•</span>
                        <span>{(doc.file_size_bytes / 1024).toFixed(1)} KB</span>
                      </div>
                      <div className="flex items-center space-x-1.5 text-[10px] text-slate-500 font-mono mt-1">
                        <Hash className="h-3 w-3" />
                        <span>SHA: {doc.file_hash.substring(0, 16)}...</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle2 className="h-3 w-3 mr-1" /> INDEXED
                    </span>
                    <span className="block text-[10px] text-slate-500 mt-2">
                      Parsed in {doc.processing_duration_ms}ms
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="lg:col-span-5 bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col h-[600px]">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/40">
            <div>
              <h3 className="text-sm font-bold text-white">Extracted Chunks & Vector Index</h3>
              <p className="text-[11px] text-slate-400">Financial boundaries & citation tags</p>
            </div>
            <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-300 font-mono">
              {chunks.length} Chunks
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chunks.length === 0 ? (
              <div className="text-center py-16 text-slate-500 text-xs">
                Select a document to inspect its parsed chunks and bounding metadata.
              </div>
            ) : (
              chunks.map((ch, idx) => (
                <div key={idx} className="bg-slate-950/60 border border-slate-800 p-3 rounded-lg text-xs">
                  <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1.5 pb-1.5 border-b border-slate-800/60">
                    <span className="font-semibold text-emerald-400">Chunk #{ch.chunk_index + 1}</span>
                    <span className="text-slate-500 font-mono">{ch.section_title || 'Section'}</span>
                    <span>{ch.token_count} tokens</span>
                  </div>
                  <p className="text-slate-300 text-[11px] font-mono leading-relaxed whitespace-pre-wrap">
                    {ch.chunk_text}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
"""

os.makedirs(os.path.join(fe_root, "app", "documents"), exist_ok=True)
with open(os.path.join(fe_root, "app", "documents", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(docs_code.strip() + "\n")
print("Documents page created.")
