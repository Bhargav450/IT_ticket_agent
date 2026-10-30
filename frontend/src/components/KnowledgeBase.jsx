import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Search, 
  Upload, 
  FileText, 
  Layers, 
  CheckCircle, 
  ChevronRight, 
  Sparkles,
  ExternalLink 
} from 'lucide-react';
import { api } from '../api/client';

export default function KnowledgeBase() {
  const [docs, setDocs] = useState([]);
  const [searchQuery, setSearchQuery] = useState('How to resolve HTTP 500 Internal Server Error in API Gateway');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('RUNBOOK');
  const [selectedDoc, setSelectedDoc] = useState(null);

  const loadDocs = async () => {
    try {
      const data = await api.getKnowledgeDocs();
      setDocs(data);
      if (data.length > 0 && !selectedDoc) {
        setSelectedDoc(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadDocs();
    handleSearch();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await api.searchKnowledge(searchQuery);
      setSearchResults(res.citations || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    if (uploadTitle) formData.append('title', uploadTitle);
    formData.append('category', uploadCategory);

    try {
      await api.uploadKnowledgeDoc(formData);
      setUploadFile(null);
      setUploadTitle('');
      await loadDocs();
    } catch (err) {
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & RAG Search Explorer */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5">
        <div className="flex items-center gap-2 mb-2">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h2 className="text-base font-bold text-white">Knowledge Base & RAG Semantic Search</h2>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          Vectorized internal runbooks, postmortems, and SOPs. Used autonomously by the Knowledge Agent to extract troubleshooting steps and citations.
        </p>

        {/* Live Search Bar */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Query internal runbooks using vector semantic retrieval..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isSearching ? 'Retrieving...' : 'Search RAG'}</span>
          </button>
        </div>

        {/* Search Results Preview */}
        {searchResults.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-800 space-y-2">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
              Top Semantic Citations ({searchResults.length} ranked chunks):
            </span>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {searchResults.map((cit, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-blue-500/20 text-xs">
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="font-semibold text-slate-200 line-clamp-1">{cit.document_title}</span>
                    <span className="text-[10px] font-mono text-blue-400 font-bold shrink-0">
                      {cit.similarity_score}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500 block mb-2 font-mono">
                    {cit.section || 'General'} ({cit.filename})
                  </span>
                  <p className="text-[11px] text-slate-400 line-clamp-3 font-mono leading-relaxed bg-slate-900/50 p-1.5 rounded">
                    {cit.excerpt}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: Upload & Document Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Runbook Panel */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Upload className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Ingest Troubleshooting Doc
            </h3>
          </div>

          <form onSubmit={handleUpload} className="space-y-3">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Document Title</label>
              <input
                type="text"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                placeholder="e.g. SOP-500 Microservice Failover"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Category</label>
              <select
                value={uploadCategory}
                onChange={(e) => setUploadCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="RUNBOOK">Standard Runbook (SOP)</option>
                <option value="POSTMORTEM">Postmortem Incident Review</option>
                <option value="ARCHITECTURE">System Architecture Doc</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] text-slate-400 mb-1">File (PDF, DOCX, Markdown, TXT)</label>
              <input
                type="file"
                accept=".pdf,.docx,.md,.txt"
                onChange={(e) => setUploadFile(e.target.files[0])}
                className="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-600/20 file:text-blue-300 hover:file:bg-blue-600/30"
              />
            </div>

            <button
              type="submit"
              disabled={!uploadFile || isUploading}
              className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all disabled:opacity-50"
            >
              {isUploading ? 'Chunking & Ingesting...' : 'Upload & Vectorize'}
            </button>
          </form>

          {/* Document List */}
          <div className="pt-3 border-t border-slate-800 space-y-2">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block">
              Ingested Knowledge Docs ({docs.length})
            </span>
            <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
              {docs.map(doc => (
                <div
                  key={doc.id}
                  onClick={() => setSelectedDoc(doc)}
                  className={`p-2.5 rounded-lg border text-xs cursor-pointer flex items-center justify-between ${
                    selectedDoc?.id === doc.id
                      ? 'bg-blue-950/40 border-blue-500/50 text-slate-200'
                      : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <FileText className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    <span className="truncate font-medium">{doc.title}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 shrink-0">
                    {doc.category}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Document Content Viewer */}
        <div className="lg:col-span-2 bg-slate-900/60 rounded-xl border border-slate-800 p-5 flex flex-col h-[550px]">
          {selectedDoc ? (
            <>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
                <div>
                  <h3 className="text-sm font-bold text-white">{selectedDoc.title}</h3>
                  <span className="text-[11px] font-mono text-slate-500">{selectedDoc.filename}</span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  {selectedDoc.category}
                </span>
              </div>
              <div className="flex-1 overflow-y-auto bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                {selectedDoc.content}
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-xs text-slate-500">
              Select a runbook to inspect full content.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

