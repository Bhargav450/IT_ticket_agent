import sqlite3
import json
import os

db_path = 'it_support_agent.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    SELECT c.id, d.title, d.category, d.filename, c.chunk_index, c.content, c.embedding, c.created_at
    FROM document_chunks c
    JOIN knowledge_documents d ON c.document_id = d.id
    ORDER BY d.id ASC, c.chunk_index ASC
''')
rows = cursor.fetchall()

chunks_data = []
for r in rows:
    emb = json.loads(r[6]) if r[6] else {}
    chunks_data.append({
        'id': r[0],
        'doc_title': r[1],
        'category': r[2],
        'filename': r[3],
        'chunk_index': r[4],
        'content': r[5],
        'embedding': emb,
        'embedding_type': 'Dense Neural Vector' if isinstance(emb, list) else 'Sparse Lexical Vector',
        'embedding_size': len(emb),
        'created_at': str(r[7])
    })

cursor.execute('SELECT id, title, category, filename, length(content) FROM knowledge_documents')
docs_data = [{'id': r[0], 'title': r[1], 'category': r[2], 'filename': r[3], 'chars': r[4]} for r in cursor.fetchall()]

chunks_json = json.dumps(chunks_data)
docs_options = ''.join(f'<option value="{d["title"]}">{d["title"]}</option>' for d in docs_data)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>AegisOps Vector Database Viewer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Inter', sans-serif; }}
    code, pre {{ font-family: 'JetBrains Mono', monospace; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-6">
  <div class="max-w-7xl mx-auto space-y-6">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
      <div>
        <div class="flex items-center gap-3">
          <span class="px-2.5 py-1 text-xs font-semibold uppercase tracking-wider rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">SQLite Vector DB</span>
          <h1 class="text-2xl font-bold text-white">AegisOps Vector Database Viewer</h1>
        </div>
        <p class="text-xs text-slate-400 mt-1">Database: <code class="text-indigo-300">it_support_agent.db</code> &bull; Tables: <code class="text-indigo-300">knowledge_documents</code> &bull; <code class="text-indigo-300">document_chunks</code></p>
      </div>
      <div class="flex gap-3">
        <div class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <span class="text-slate-500 font-medium">Documents:</span> <strong class="text-white font-bold">{len(docs_data)}</strong>
        </div>
        <div class="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <span class="text-slate-500 font-medium">Vector Chunks:</span> <strong class="text-indigo-400 font-bold">{len(chunks_data)}</strong>
        </div>
      </div>
    </header>

    <!-- Search & Filter Controls -->
    <div class="flex flex-col sm:flex-row gap-3 bg-slate-900/90 p-4 rounded-xl border border-slate-800">
      <input
        id="search-input"
        type="text"
        placeholder="Search keywords, token weights, runbook titles, or content..."
        class="flex-1 bg-slate-800/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
        oninput="filterChunks()"
      />
      <select
        id="doc-filter"
        class="bg-slate-800/80 border border-slate-700/80 rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none"
        onchange="filterChunks()"
      >
        <option value="">All Documents ({len(docs_data)})</option>
        {docs_options}
      </select>
    </div>

    <!-- Results Counter -->
    <div id="results-count" class="text-xs text-slate-400 font-medium">
      Showing all {len(chunks_data)} chunks
    </div>

    <!-- Chunks Grid -->
    <div id="chunks-container" class="space-y-4"></div>
  </div>

  <script>
    const chunks = {chunks_json};

    function renderChunks(items) {{
      const container = document.getElementById('chunks-container');
      const countLabel = document.getElementById('results-count');
      countLabel.textContent = `Showing ${{items.length}} of ${{chunks.length}} chunks`;

      if (items.length === 0) {{
        container.innerHTML = `<div class="text-center py-12 text-slate-500 text-sm bg-slate-900/50 rounded-xl border border-slate-800">No matching vector chunks found.</div>`;
        return;
      }}

      container.innerHTML = items.map(c => {{
        const embKeys = typeof c.embedding === 'object' && !Array.isArray(c.embedding) ? Object.entries(c.embedding).slice(0, 10) : [];
        const isDense = Array.isArray(c.embedding);

        return `
          <div class="bg-slate-900/80 rounded-xl border border-slate-800/90 p-5 hover:border-slate-700 transition-all">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800/60">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-800 text-indigo-400 border border-indigo-500/20">Chunk #${{c.chunk_index}} (ID: ${{c.id}})</span>
                <span class="text-xs font-semibold text-white">${{c.doc_title}}</span>
              </div>
              <div class="flex items-center gap-2 text-xs text-slate-400">
                <span class="px-2 py-0.5 rounded bg-slate-800/70 border border-slate-700/50 text-[11px]">${{c.category}}</span>
                <span class="px-2 py-0.5 rounded bg-indigo-950/70 border border-indigo-800/40 text-indigo-300 text-[11px]">${{c.embedding_type}}: ${{c.embedding_size}} weights</span>
              </div>
            </div>

            <div class="mt-3">
              <div class="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-1">Text Snippet</div>
              <pre class="text-xs text-slate-200 bg-slate-950/80 p-3 rounded-lg border border-slate-800 whitespace-pre-wrap overflow-x-auto leading-relaxed max-h-48 overflow-y-auto">${{c.content.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</pre>
            </div>

            <div class="mt-3 pt-3 border-t border-slate-800/60">
              <div class="flex items-center justify-between mb-2">
                <div class="text-xs text-indigo-400 font-semibold uppercase tracking-wider">Vector Weights / Embeddings</div>
                <button
                  type="button"
                  onclick="toggleRaw(${{c.id}})"
                  class="text-[11px] font-medium text-slate-400 hover:text-white px-2.5 py-1 rounded bg-slate-800 border border-slate-700/50 transition-colors"
                >
                  View Full Vector JSON
                </button>
              </div>

              ${{!isDense ? `
                <div class="flex flex-wrap gap-1.5">
                  ${{embKeys.map(([k, v]) => `
                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/60 text-[11px]">
                      <span class="text-slate-300 font-mono">${{k}}:</span>
                      <strong class="text-indigo-400 font-mono">${{typeof v === 'number' ? v.toFixed(4) : v}}</strong>
                    </span>
                  `).join('')}}
                  ${{Object.keys(c.embedding).length > 10 ? `<span class="text-xs text-slate-500 self-center pl-1">+${{Object.keys(c.embedding).length - 10}} more tokens</span>` : ''}}
                </div>
              ` : `
                <div class="text-xs font-mono text-indigo-300 bg-slate-950 p-2 rounded border border-slate-800">
                  [${{c.embedding.slice(0, 8).map(v => v.toFixed(5)).join(', ')}}, ... (${{c.embedding.length}} dims)]
                </div>
              `}}

              <div id="raw-${{c.id}}" class="hidden mt-2">
                <pre class="text-[11px] font-mono text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800/80 max-h-56 overflow-y-auto overflow-x-auto">${{JSON.stringify(c.embedding, null, 2)}}</pre>
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function toggleRaw(id) {{
      const el = document.getElementById(`raw-${{id}}`);
      if (el) el.classList.toggle('hidden');
    }}

    function filterChunks() {{
      const query = document.getElementById('search-input').value.toLowerCase().trim();
      const doc = document.getElementById('doc-filter').value;

      const filtered = chunks.filter(c => {{
        const matchDoc = !doc || c.doc_title === doc;
        if (!matchDoc) return false;
        if (!query) return true;

        const inContent = c.content.toLowerCase().includes(query);
        const inTitle = c.doc_title.toLowerCase().includes(query);
        const inEmbedding = typeof c.embedding === 'object' && !Array.isArray(c.embedding)
          ? Object.keys(c.embedding).some(k => k.toLowerCase().includes(query))
          : false;

        return inContent || inTitle || inEmbedding;
      }});

      renderChunks(filtered);
    }}

    renderChunks(chunks);
  </script>
</body>
</html>
"""

output_path = "vector_db_viewer.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"Generated {output_path} successfully ({len(chunks_data)} chunks, {len(docs_data)} documents).")

