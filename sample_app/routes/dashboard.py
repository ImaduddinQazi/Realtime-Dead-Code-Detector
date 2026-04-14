from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from analyzer import analyze_routes, analyze_tables

router = APIRouter(prefix="/dead-detector", tags=["dashboard"])

@router.get("/api/report")
def get_report():
    return {
        "routes": analyze_routes(),
        "tables": analyze_tables(),
    }

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(content=get_dashboard_html())

def get_dashboard_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dead Code Detector</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f8f7f2; color: #2c2c2a; padding: 24px; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .title { font-size: 20px; font-weight: 500; }
    .subtitle { font-size: 13px; color: #888780; margin-top: 4px; }
    .refresh-btn { font-size: 13px; background: #fff; border: 0.5px solid #d3d1c7; border-radius: 8px; padding: 8px 16px; cursor: pointer; }
    .refresh-btn:hover { background: #f1efe8; }
    .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
    .stat { background: #f1efe8; border-radius: 8px; padding: 16px; }
    .stat-label { font-size: 12px; color: #888780; margin-bottom: 6px; }
    .stat-value { font-size: 24px; font-weight: 500; }
    .dead-val { color: #a32d2d; }
    .section-title { font-size: 14px; font-weight: 500; margin-bottom: 10px; }
    .table-wrap { background: #fff; border: 0.5px solid #d3d1c7; border-radius: 12px; overflow: hidden; margin-bottom: 24px; }
    table { width: 100%; border-collapse: collapse; }
    th { font-size: 12px; color: #888780; font-weight: 400; padding: 10px 16px; text-align: left; background: #f8f7f2; border-bottom: 0.5px solid #d3d1c7; }
    td { font-size: 13px; padding: 10px 16px; border-bottom: 0.5px solid #f1efe8; }
    tr:last-child td { border-bottom: none; }
    .badge { display: inline-block; font-size: 11px; font-weight: 500; padding: 3px 8px; border-radius: 6px; }
    .badge-dead { background: #fcebeb; color: #a32d2d; }
    .badge-warn { background: #faeeda; color: #854f0b; }
    .badge-active { background: #eaf3de; color: #3b6d11; }
    .mono { font-family: monospace; font-size: 12px; color: #5f5e5a; }
    .method { font-family: monospace; font-size: 11px; font-weight: 500; padding: 2px 6px; border-radius: 4px; background: #f1efe8; color: #5f5e5a; }
    .bar-wrap { width: 80px; height: 6px; background: #f1efe8; border-radius: 3px; display: inline-block; vertical-align: middle; margin-right: 6px; }
    .bar { height: 6px; border-radius: 3px; }
    .bar-dead { background: #e24b4a; }
    .bar-warn { background: #ef9f27; }
    .bar-active { background: #639922; }
    .muted { color: #888780; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="title">Dead code detector</div>
      <div class="subtitle" id="last-updated">Loading...</div>
    </div>
    <button class="refresh-btn" onclick="loadData()">↻ Refresh</button>
  </div>

  <div class="stats">
    <div class="stat"><div class="stat-label">Total routes</div><div class="stat-value" id="total-routes">—</div></div>
    <div class="stat"><div class="stat-label">Dead routes</div><div class="stat-value dead-val" id="dead-routes">—</div></div>
    <div class="stat"><div class="stat-label">Tables tracked</div><div class="stat-value" id="total-tables">—</div></div>
    <div class="stat"><div class="stat-label">Dead tables</div><div class="stat-value dead-val" id="dead-tables">—</div></div>
  </div>

  <div class="section-title">Route analysis</div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Method</th><th>Path</th><th>Status</th><th>Calls</th><th>Last seen</th><th>Confidence</th></tr></thead>
      <tbody id="routes-body"><tr><td colspan="6" class="muted" style="padding:20px">Loading...</td></tr></tbody>
    </table>
  </div>

  <div class="section-title">Table analysis</div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Table</th><th>Status</th><th>Hits</th><th>Last seen</th><th>Confidence</th></tr></thead>
      <tbody id="tables-body"><tr><td colspan="5" class="muted" style="padding:20px">Loading...</td></tr></tbody>
    </table>
  </div>

  <script>
    function badge(status) {
      const cls = status === 'DEAD' ? 'dead' : status === 'WARN' ? 'warn' : 'active';
      return `<span class="badge badge-${cls}">${status.charAt(0) + status.slice(1).toLowerCase()}</span>`;
    }

    function bar(confidence, status) {
      const cls = status === 'DEAD' ? 'dead' : status === 'WARN' ? 'warn' : 'active';
      return `<div class="bar-wrap"><div class="bar bar-${cls}" style="width:${confidence}%"></div></div>${confidence}%`;
    }

    async function loadData() {
      const res = await fetch('/dead-detector/api/report');
      const data = await res.json();

      document.getElementById('total-routes').textContent = data.routes.length;
      document.getElementById('dead-routes').textContent = data.routes.filter(r => r.status === 'DEAD').length;
      document.getElementById('total-tables').textContent = data.tables.length;
      document.getElementById('dead-tables').textContent = data.tables.filter(t => t.status === 'DEAD').length;
      document.getElementById('last-updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();

      document.getElementById('routes-body').innerHTML = data.routes.map(r => `
        <tr>
          <td><span class="method">${r.method}</span></td>
          <td><span class="mono">${r.path}</span></td>
          <td>${badge(r.status)}</td>
          <td>${r.total_calls}</td>
          <td class="${r.last_seen === 'never' ? 'muted' : ''}">${r.last_seen}</td>
          <td>${bar(r.confidence, r.status)}</td>
        </tr>`).join('');

      document.getElementById('tables-body').innerHTML = data.tables.map(t => `
        <tr>
          <td><span class="mono">${t.table}</span></td>
          <td>${badge(t.status)}</td>
          <td>${t.total_hits}</td>
          <td class="${t.last_seen === 'never' ? 'muted' : ''}">${t.last_seen}</td>
          <td>${bar(t.confidence, t.status)}</td>
        </tr>`).join('');
    }

    loadData();
    setInterval(loadData, 30000);
  </script>
</body>
</html>
"""