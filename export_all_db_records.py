import sqlite3
import json
import os

db_path = 'it_support_agent.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. users
cursor.execute('SELECT id, email, full_name, role, is_active, created_at FROM users')
users = [dict(r) for r in cursor.fetchall()]

# 2. knowledge_documents
cursor.execute('SELECT id, filename, title, category, substr(content, 1, 200) as content_preview, length(content) as char_count, created_at FROM knowledge_documents')
docs = [dict(r) for r in cursor.fetchall()]

# 3. document_chunks
cursor.execute('''
    SELECT c.id, c.document_id, d.title as doc_title, c.chunk_index, c.content, c.embedding, c.created_at
    FROM document_chunks c
    LEFT JOIN knowledge_documents d ON c.document_id = d.id
    ORDER BY c.id ASC
''')
chunks = []
for r in cursor.fetchall():
    emb = json.loads(r['embedding']) if r['embedding'] else {}
    chunks.append({
        'id': r['id'],
        'document_id': r['document_id'],
        'doc_title': r['doc_title'],
        'chunk_index': r['chunk_index'],
        'content': r['content'],
        'vector_type': 'Dense Vector' if isinstance(emb, list) else 'Sparse Lexical Vector',
        'vector_dimensions': len(emb),
        'embedding_sample': list(emb.items())[:6] if isinstance(emb, dict) else (emb[:6] if isinstance(emb, list) else []),
        'embedding_full': emb,
        'created_at': str(r['created_at'])
    })

# 4. incidents (all 197)
cursor.execute('''
    SELECT id, ticket_number, title, severity, status, category, affected_service, 
           reporter_email, proposed_action, action_risk_level, human_approval_status,
           resolution_notes, created_at, resolved_at
    FROM incidents 
    ORDER BY id DESC
''')
incidents = [dict(r) for r in cursor.fetchall()]

# 5. agent_step_logs (latest 50)
cursor.execute('''
    SELECT id, incident_id, node_name, status, substr(thought_summary, 1, 150) as thought_preview, 
           tool_name, tool_input, tool_output, created_at
    FROM agent_step_logs
    ORDER BY id DESC
    LIMIT 50
''')
step_logs = [dict(r) for r in cursor.fetchall()]

data = {
    'users': users,
    'knowledge_documents': docs,
    'document_chunks': chunks,
    'incidents': incidents,
    'agent_step_logs': step_logs
}

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AegisOps SQLite Full Database Explorer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
          <span class="px-2.5 py-1 text-xs font-semibold uppercase tracking-wider rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30">SQLite DB Explorer</span>
          <h1 class="text-2xl font-bold text-white">it_support_agent.db Records</h1>
        </div>
        <p class="text-xs text-slate-400 mt-1">Inspecting all tables and rows in your local database</p>
      </div>
      <div class="flex items-center gap-2">
        <input 
          id="global-search" 
          type="text" 
          placeholder="Filter rows..." 
          class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          oninput="applyFilter()"
        />
      </div>
    </header>

    <!-- Table Selector Tabs -->
    <div class="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
      <button onclick="switchTab('incidents')" id="tab-incidents" class="px-4 py-2 rounded-lg text-xs font-semibold transition-all bg-blue-600 text-white shadow-md">
        Incidents ({len(incidents)})
      </button>
      <button onclick="switchTab('document_chunks')" id="tab-document_chunks" class="px-4 py-2 rounded-lg text-xs font-semibold transition-all bg-slate-900 text-slate-300 hover:bg-slate-800">
        Vector Document Chunks ({len(chunks)})
      </button>
      <button onclick="switchTab('knowledge_documents')" id="tab-knowledge_documents" class="px-4 py-2 rounded-lg text-xs font-semibold transition-all bg-slate-900 text-slate-300 hover:bg-slate-800">
        Knowledge Documents ({len(docs)})
      </button>
      <button onclick="switchTab('users')" id="tab-users" class="px-4 py-2 rounded-lg text-xs font-semibold transition-all bg-slate-900 text-slate-300 hover:bg-slate-800">
        Users ({len(users)})
      </button>
      <button onclick="switchTab('agent_step_logs')" id="tab-agent_step_logs" class="px-4 py-2 rounded-lg text-xs font-semibold transition-all bg-slate-900 text-slate-300 hover:bg-slate-800">
        Recent Agent Step Logs ({len(step_logs)})
      </button>
    </div>

    <!-- Table View Container -->
    <div id="table-view" class="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto max-h-[70vh]">
        <table class="w-full text-left text-xs border-collapse">
          <thead id="table-head" class="bg-slate-950/90 sticky top-0 border-b border-slate-800 text-slate-400 font-semibold tracking-wider"></thead>
          <tbody id="table-body" class="divide-y divide-slate-800/60 font-mono text-slate-300"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Detail Modal -->
  <div id="detail-modal" class="hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 id="modal-title" class="text-sm font-bold text-white">Record Details</h3>
        <button onclick="closeModal()" class="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800">Close</button>
      </div>
      <div id="modal-content" class="max-h-96 overflow-y-auto space-y-2"></div>
    </div>
  </div>

  <script>
    const dbData = {json.dumps(data)};
    let currentTab = 'incidents';

    function switchTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('[id^="tab-"]').forEach(btn => {{
        btn.className = "px-4 py-2 rounded-lg text-xs font-semibold transition-all bg-slate-900 text-slate-300 hover:bg-slate-800";
      }});
      document.getElementById(`tab-${{tab}}`).className = "px-4 py-2 rounded-lg text-xs font-semibold transition-all bg-blue-600 text-white shadow-md";
      renderTable();
    }}

    function renderTable() {{
      const items = dbData[currentTab] || [];
      const query = document.getElementById('global-search').value.toLowerCase().trim();
      const filtered = items.filter(row => {{
        if (!query) return true;
        return Object.values(row).some(v => String(v || '').toLowerCase().includes(query));
      }});

      const thead = document.getElementById('table-head');
      const tbody = document.getElementById('table-body');

      if (filtered.length === 0) {{
        thead.innerHTML = '';
        tbody.innerHTML = `<tr><td class="p-8 text-center text-slate-500 font-sans">No matching records found</td></tr>`;
        return;
      }}

      // Build headers
      const cols = Object.keys(filtered[0]).filter(k => k !== 'embedding_full');
      thead.innerHTML = `<tr>${{cols.map(c => `<th class="p-3 text-[11px] whitespace-nowrap uppercase">${{c}}</th>`).join('')}}<th class="p-3"></th></tr>`;

      // Build rows
      tbody.innerHTML = filtered.map((row, idx) => {{
        return `
          <tr class="hover:bg-slate-800/40 transition-colors">
            ${{cols.map(c => {{
              let val = row[c];
              if (typeof val === 'object' && val !== null) val = JSON.stringify(val);
              let str = String(val || '');
              if (str.length > 50) str = str.slice(0, 50) + '...';
              return `<td class="p-3 whitespace-nowrap overflow-hidden text-ellipsis max-w-xs text-slate-300">${{str.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</td>`;
            }}).join('')}}
            <td class="p-3 whitespace-nowrap text-right">
              <button onclick="viewRecord('${{currentTab}}', ${{idx}})" class="text-blue-400 hover:text-blue-300 font-sans text-xs underline">
                View Full
              </button>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function viewRecord(tab, idx) {{
      const record = dbData[tab][idx];
      const modal = document.getElementById('detail-modal');
      const title = document.getElementById('modal-title');
      const content = document.getElementById('modal-content');

      title.textContent = `${{tab}} (Row #${{record.id || idx + 1}})`;
      content.innerHTML = Object.entries(record).map(([k, v]) => {{
        let displayVal = typeof v === 'object' ? JSON.stringify(v, null, 2) : String(v || '');
        return `
          <div class="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <span class="text-xs font-semibold text-blue-400 uppercase tracking-wider block mb-1">${{k}}</span>
            <pre class="text-xs text-slate-200 whitespace-pre-wrap font-mono max-h-40 overflow-y-auto">${{displayVal.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</pre>
          </div>
        `;
      }}).join('');

      modal.classList.remove('hidden');
    }}

    function closeModal() {{
      document.getElementById('detail-modal').classList.add('hidden');
    }}

    function applyFilter() {{
      renderTable();
    }}

    // Init
    renderTable();
  </script>
</body>
</html>
"""

with open('all_db_records.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Exported all_db_records.html successfully!")
