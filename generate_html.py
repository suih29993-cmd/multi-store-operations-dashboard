# -*- coding: utf-8 -*-
"""Render a self-contained, offline-capable operations dashboard."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data.json"
OUTPUT = ROOT / "dashboard.html"


def main() -> None:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DASHBOARD_DATA__", data_json)
    OUTPUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT}")


TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%232f6f5e'/%3E%3Cpath d='M17 43V29m10 14V21m10 22V33m10 10V16' stroke='white' stroke-width='5' stroke-linecap='round'/%3E%3C/svg%3E">
<title>Multi-store Operations Dashboard · Synthetic Demo</title>
<style>
:root{--bg:#f4f5f2;--panel:#fff;--ink:#1d2521;--muted:#6f7772;--line:#dfe3de;--accent:#2f6f5e;--accent-soft:#e7f0ec;--warn:#b95042;--warn-soft:#fbeeeb;--gold:#a9833f;--shadow:0 14px 44px rgba(29,37,33,.07)}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 8% 0%,#e8efe9 0,transparent 32%),var(--bg);color:var(--ink);font:14px/1.55 "Segoe UI","Noto Sans SC",sans-serif}
.shell{max-width:1440px;margin:auto;padding:26px 28px 44px}header{display:flex;align-items:center;justify-content:space-between;gap:24px;margin-bottom:20px}.brand{display:flex;align-items:center;gap:14px}.mark{width:48px;height:48px;border-radius:14px;background:linear-gradient(145deg,#244d42,#4d8b73);display:grid;place-items:center;color:#fff;font-weight:800;letter-spacing:-1px;box-shadow:var(--shadow)}h1{font-size:24px;line-height:1.2;margin:0;letter-spacing:-.4px}header p{margin:3px 0 0;color:var(--muted);font-size:12px}.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.controls label{font-size:11px;text-transform:uppercase;letter-spacing:.9px;color:var(--muted);display:block;margin-bottom:4px}select,input{height:36px;border:1px solid var(--line);border-radius:9px;background:#fff;padding:0 11px;color:var(--ink);min-width:130px;font:inherit}input{min-width:210px}
.notice{background:#fff8e8;border:1px solid #efd9a7;color:#70531c;padding:10px 14px;border-radius:10px;margin-bottom:18px;font-size:12px}.grid{display:grid;gap:16px}.kpis{grid-template-columns:repeat(6,minmax(0,1fr));margin-bottom:16px}.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}.kpi{padding:15px 16px;min-height:112px;display:flex;flex-direction:column;justify-content:space-between}.kpi .label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.7px}.kpi .value{font-size:27px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:-.7px}.kpi .delta{font-size:11px;color:var(--muted)}.delta.up{color:#2d765e}.delta.down{color:var(--warn)}.kpi.warn{background:var(--warn-soft);border-color:#efcbc4}
.split{grid-template-columns:minmax(0,1.65fr) minmax(340px,.85fr);margin-bottom:16px}.panel{padding:18px}.panel-head{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:14px}.panel h2{font-size:15px;margin:0}.panel .sub{font-size:11px;color:var(--muted)}.chart{height:250px;width:100%}.chart text{fill:var(--muted);font-size:10px}.chart .axis{stroke:#d8dcd7;stroke-width:1}.chart .line-a{fill:none;stroke:var(--accent);stroke-width:3}.chart .line-b{fill:none;stroke:var(--gold);stroke-width:3}.legend{display:flex;gap:16px;font-size:11px;color:var(--muted)}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px}
.mini-table{width:100%;border-collapse:collapse;font-size:12px}.mini-table th,.mini-table td{padding:8px 7px;border-bottom:1px solid #edf0ed;text-align:left}.mini-table th{font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);font-weight:600}.mini-table tr:last-child td{border-bottom:0}.mini-table .score{font-weight:700;font-variant-numeric:tabular-nums}
.table-card{overflow:hidden}.table-tools{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px}.table-wrap{overflow:auto;max-height:560px;border:1px solid #edf0ed;border-radius:10px}table.data{width:100%;border-collapse:collapse;min-width:980px;font-size:12px}table.data th{position:sticky;top:0;z-index:2;background:#f7f8f6;text-align:left;padding:10px 11px;border-bottom:1px solid var(--line);cursor:pointer;white-space:nowrap;font-size:10px;text-transform:uppercase;letter-spacing:.55px;color:var(--muted)}table.data td{padding:10px 11px;border-bottom:1px solid #eef1ee;white-space:nowrap}table.data tr:hover td{background:#fafbf9}table.data tr.selected td{background:var(--accent-soft)}.num{font-variant-numeric:tabular-nums}.muted{color:var(--muted)}.pill{display:inline-flex;padding:2px 7px;border-radius:99px;background:var(--accent-soft);color:var(--accent);font-size:10px;font-weight:600}.warn-text{color:var(--warn);font-weight:700}.status{font-size:10px;color:var(--muted)}.status.open{color:#2d765e}.btn{border:1px solid var(--line);background:#fff;border-radius:8px;height:32px;padding:0 12px;cursor:pointer;font:inherit;font-size:12px}.btn:hover{border-color:var(--accent);color:var(--accent)}footer{margin-top:22px;color:var(--muted);font-size:11px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(3,1fr)}.split{grid-template-columns:1fr}.shell{padding:20px 18px 36px}header{align-items:flex-start;flex-direction:column}.controls{width:100%}}
@media(max-width:620px){.kpis{grid-template-columns:repeat(2,1fr)}.shell{padding:16px 12px 30px}h1{font-size:20px}.controls>div{flex:1 1 45%}select,input{width:100%;min-width:0}.panel{padding:13px}.kpi .value{font-size:23px}}
</style>
</head>
<body>
<div class="shell">
<header>
  <div class="brand"><div class="mark">OA</div><div><h1>Multi-store Operations Dashboard</h1><p>Multi-period performance, ranking and supervisor analytics</p></div></div>
  <div class="controls">
    <div><label>Period</label><select id="period"></select></div>
    <div><label>Region</label><select id="region"></select></div>
    <div><label>City</label><select id="city"></select></div>
    <div><label>Supervisor</label><select id="supervisor"></select></div>
    <div><label>Search store</label><input id="search" placeholder="Store ID or name"></div>
  </div>
</header>
<div class="notice">Portfolio demonstration. All stores, ratings, rates and periods below are synthetic and must not be interpreted as real business performance.</div>
<section class="grid kpis" id="kpis"></section>
<section class="grid split">
  <div class="card panel">
    <div class="panel-head"><div><h2>Period trend</h2><div class="sub" id="trendSub"></div></div><div class="legend"><span><i class="dot" style="background:#2f6f5e"></i>Channel A score</span><span><i class="dot" style="background:#a9833f"></i>Channel B score</span></div></div>
    <svg class="chart" id="trend" viewBox="0 0 720 250" role="img" aria-label="Synthetic score trend"></svg>
  </div>
  <div class="card panel">
    <div class="panel-head"><div><h2>Bottom 5 stores</h2><div class="sub" id="bottomSub"></div></div><select id="bottomMetric" aria-label="Bottom metric"></select></div>
    <table class="mini-table"><thead><tr><th>Store</th><th>City</th><th>Value</th></tr></thead><tbody id="bottomBody"></tbody></table>
  </div>
</section>
<section class="card panel table-card">
  <div class="panel-head"><div><h2>Store ranking</h2><div class="sub" id="tableSub"></div></div><div class="table-tools"><button class="btn" id="export">Export filtered CSV</button><button class="btn" id="reset">Reset filters</button></div></div>
  <div class="table-wrap"><table class="data"><thead><tr>
    <th data-sort="name">Store</th><th data-sort="region">Region</th><th data-sort="city">City</th><th data-sort="supervisor">Supervisor</th>
    <th data-sort="channel_a_score">A score</th><th data-sort="channel_a_repeat">A repeat</th><th data-sort="channel_a_reply">A reply</th>
    <th data-sort="channel_b_score">B score</th><th data-sort="channel_b_reply">B reply</th><th data-sort="channel_b_cancel">B cancel</th><th>Status</th>
  </tr></thead><tbody id="storeBody"></tbody></table></div>
</section>
<section class="card panel" style="margin-top:16px">
  <div class="panel-head"><div><h2>Supervisor summary</h2><div class="sub">Aggregated from stores matching the current region, city and supervisor filters.</div></div></div>
  <div class="table-wrap"><table class="data" style="min-width:760px"><thead><tr><th>Supervisor</th><th>Region</th><th>Stores</th><th>A score</th><th>A reply</th><th>B score</th><th>B cancel</th></tr></thead><tbody id="supBody"></tbody></table></div>
</section>
<footer><span id="meta"></span><span>Synthetic portfolio demo · generated offline</span></footer>
</div>
<script>
const DATA=__DASHBOARD_DATA__;
const METRICS={
 channel_a_score:{label:'Channel A score',digits:2,warn:v=>v<4.5},channel_a_repeat:{label:'Channel A repeat rate',pct:true},channel_a_reply:{label:'Channel A reply rate',pct:true},
 channel_b_score:{label:'Channel B score',digits:2,warn:v=>v<4.5},channel_b_reply:{label:'Channel B reply rate',pct:true},channel_b_cancel:{label:'Channel B cancellation rate',pct:true,warn:v=>v>0.003}
};
const state={period:DATA.defaultPeriod,region:'All_Regions',city:'All cities',supervisor:'All supervisors',search:'',sort:'channel_a_score',direction:'desc',selected:null};
const $=id=>document.getElementById(id);
const current=()=>DATA.periods[state.period];
const fmt=(key,v)=>v==null?'—':(METRICS[key]?.pct?`${(v*100).toFixed(2)}%`:Number(v).toFixed(2));
const delta=(key,v)=>{if(v==null)return '—';const sign=v>0?'+':'';return sign+(METRICS[key]?.pct?`${(v*100).toFixed(2)} pp`:Number(v).toFixed(2));};
function filteredStores(){
 const q=state.search.toLowerCase();
 return current().stores.filter(s=>(state.region==='All_Regions'||s.region===state.region)&&(state.city==='All cities'||s.city===state.city)&&(state.supervisor==='All supervisors'||s.supervisor===state.supervisor)&&(!q||s.name.toLowerCase().includes(q)||s.id.toLowerCase().includes(q)));
}
function opt(select,values,labeler=x=>x){select.innerHTML=values.map(v=>`<option value="${v}">${labeler(v)}</option>`).join('');}
function refreshCities(){
 const stores=current().stores.filter(s=>state.region==='All_Regions'||s.region===state.region);
 const cities=['All cities',...new Set(stores.map(s=>s.city).sort())];
 if(!cities.includes(state.city))state.city='All cities';opt($('city'),cities);
 const sups=['All supervisors',...new Set(stores.map(s=>s.supervisor).sort())];
 if(!sups.includes(state.supervisor))state.supervisor='All supervisors';opt($('supervisor'),sups);
}
function selectedRegionSummary(){
 return current().region_summary.find(x=>x.name===state.region)||current().region_summary[0];
}
function renderKpis(){
 const m=selectedRegionSummary().metrics;
 const items=[['channel_a_score','A score'],['channel_a_repeat','A repeat'],['channel_a_reply','A reply'],['channel_b_score','B score'],['channel_b_reply','B reply'],['channel_b_cancel','B cancel']];
 $('kpis').innerHTML=items.map(([k,l])=>{const x=m[k];const worse=METRICS[k].warn?.(x.cur);const cls=worse?'warn':'';return `<div class="card kpi ${cls}"><div class="label">${l}</div><div class="value">${fmt(k,x.cur)}</div><div class="delta ${x.delta>0?'up':'down'}">Period change ${delta(k,x.delta)}</div></div>`}).join('');
}
function renderTrend(){
 const svg=$('trend'),W=720,H=250,P={l:46,r:18,t:18,b:34};
 const periods=DATA._order.map(id=>({id,label:DATA.periods[id].meta.period.split(' ~ ')[0],a:DATA.periods[id].region_summary.find(x=>x.name===state.region)?.metrics.channel_a_score.cur||0,b:DATA.periods[id].region_summary.find(x=>x.name===state.region)?.metrics.channel_b_score.cur||0}));
 const all=periods.flatMap(p=>[p.a,p.b]),min=Math.max(3,Math.min(...all)-.15),max=Math.min(5,Math.max(...all)+.15);
 const x=i=>P.l+(W-P.l-P.r)*(periods.length===1?.5:i/(periods.length-1));const y=v=>P.t+(H-P.t-P.b)*(1-(v-min)/(max-min||1));
 let out='';for(let i=0;i<5;i++){const v=min+(max-min)*i/4;const yy=y(v);out+=`<line class="axis" x1="${P.l}" y1="${yy}" x2="${W-P.r}" y2="${yy}"/><text x="8" y="${yy+3}">${v.toFixed(2)}</text>`}
 const line=k=>periods.map((p,i)=>`${i?'L':'M'}${x(i)},${y(p[k])}`).join(' ');const dots=k=>periods.map((p,i)=>`<circle cx="${x(i)}" cy="${y(p[k])}" r="4" fill="${k==='a'?'#2f6f5e':'#a9833f'}"/>`).join('');
 out+=`<path class="line-a" d="${line('a')}"/><path class="line-b" d="${line('b')}"/>${dots('a')}${dots('b')}`;
 periods.forEach((p,i)=>{out+=`<text x="${x(i)}" y="${H-10}" text-anchor="middle">${p.label}</text>`});
 svg.innerHTML=out;$('trendSub').textContent=`Region: ${state.region} · synthetic channel scores across ${periods.length} periods`;
}
function metricValue(store,key){return store.metrics[key].cur}
function renderBottom(){
 const key=$('bottomMetric').value,stores=filteredStores().filter(s=>s.status==='Open'&&metricValue(s,key)!=null);
 stores.sort((a,b)=>METRICS[key].warn?metricValue(a,key)-metricValue(b,key):metricValue(b,key)-metricValue(a,key));
 $('bottomBody').innerHTML=stores.slice(0,5).map(s=>`<tr><td>${s.name}</td><td>${s.city}</td><td class="score">${fmt(key,s.metrics[key].cur)}</td></tr>`).join('')||'<tr><td colspan="3" class="muted">No matching stores</td></tr>';
 $('bottomSub').textContent=METRICS[key]?.label||key;
}
function renderTable(){
 const rows=filteredStores().slice().sort((a,b)=>{let av=a.metrics[state.sort]?.cur??0,bv=b.metrics[state.sort]?.cur??0;if(typeof av==='string')return state.direction==='asc'?av.localeCompare(bv):bv.localeCompare(av);return state.direction==='asc'?av-bv:bv-av});
 $('tableSub').textContent=`${rows.length} stores shown · click a row to highlight · ${current().meta.period}`;
 $('storeBody').innerHTML=rows.map(s=>`<tr data-id="${s.id}" class="${s.id===state.selected?'selected':''}"><td><b>${s.name}</b><br><span class="muted">${s.id}</span></td><td>${s.region}</td><td>${s.city}</td><td>${s.supervisor}</td><td class="num ${s.metrics.channel_a_score.cur<4.5?'warn-text':''}">${fmt('channel_a_score',s.metrics.channel_a_score.cur)}</td><td class="num">${fmt('channel_a_repeat',s.metrics.channel_a_repeat.cur)}</td><td class="num">${fmt('channel_a_reply',s.metrics.channel_a_reply.cur)}</td><td class="num ${s.metrics.channel_b_score.cur<4.5?'warn-text':''}">${fmt('channel_b_score',s.metrics.channel_b_score.cur)}</td><td class="num">${fmt('channel_b_reply',s.metrics.channel_b_reply.cur)}</td><td class="num ${s.metrics.channel_b_cancel.cur>0.003?'warn-text':''}">${fmt('channel_b_cancel',s.metrics.channel_b_cancel.cur)}</td><td><span class="status ${s.status==='Open'?'open':''}">${s.status}</span></td></tr>`).join('');
 document.querySelectorAll('#storeBody tr').forEach(tr=>tr.onclick=()=>{state.selected=tr.dataset.id;renderTable()});
}
function renderSupervisors(){
 const rows=filteredStores();const groups={};rows.forEach(s=>{(groups[s.supervisor]??=[]).push(s)});
 $('supBody').innerHTML=Object.entries(groups).sort().map(([name,stores])=>{const avg=k=>stores.reduce((n,s)=>n+s.metrics[k].cur,0)/stores.length;const region=[...new Set(stores.map(s=>s.region))].join(', ');return `<tr><td><b>${name}</b></td><td>${region}</td><td>${stores.length}</td><td class="num">${avg('channel_a_score').toFixed(2)}</td><td class="num">${(avg('channel_a_reply')*100).toFixed(1)}%</td><td class="num">${avg('channel_b_score').toFixed(2)}</td><td class="num">${(avg('channel_b_cancel')*100).toFixed(2)}%</td></tr>`}).join('')||'<tr><td colspan="7" class="muted">No matching stores</td></tr>';
}
function renderMeta(){
 const m=current().meta;$('meta').textContent=`${m.period} · previous ${m.prevPeriod} · ${m.openTotal}/${m.storeTotal} stores open · ${m.dataSource}`;
}
function renderAll(){refreshCities();renderKpis();renderTrend();renderBottom();renderTable();renderSupervisors();renderMeta();}
function init(){
 opt($('period'),DATA._order,id=>DATA.periods[id].meta.period);
 opt($('region'),current().region_summary.map(x=>x.name));
 opt($('bottomMetric'),Object.keys(METRICS),k=>METRICS[k].label);
 $('period').value=state.period;$('region').value=state.region;
 $('period').onchange=e=>{state.period=e.target.value;state.city='All cities';state.supervisor='All supervisors';state.selected=null;opt($('region'),current().region_summary.map(x=>x.name));if(![...$('region').options].some(o=>o.value===state.region))state.region='All_Regions';$('region').value=state.region;renderAll()};
 $('region').onchange=e=>{state.region=e.target.value;state.city='All cities';state.supervisor='All supervisors';renderAll()};
 $('city').onchange=e=>{state.city=e.target.value;renderAll()};
 $('supervisor').onchange=e=>{state.supervisor=e.target.value;renderAll()};
 $('search').oninput=e=>{state.search=e.target.value.trim();renderAll()};
 $('bottomMetric').onchange=renderBottom;
 document.querySelectorAll('table.data th[data-sort]').forEach(th=>th.onclick=()=>{const key=th.dataset.sort;state.direction=state.sort===key&&state.direction==='desc'?'asc':'desc';state.sort=key;renderTable()});
 $('reset').onclick=()=>{state.region='All_Regions';state.city='All cities';state.supervisor='All supervisors';state.search='';state.selected=null;$('region').value=state.region;$('search').value='';renderAll()};
 $('export').onclick=()=>{const rows=filteredStores();const head=['store_id','store_name','region','city','supervisor','status','channel_a_score','channel_a_repeat','channel_a_reply','channel_b_score','channel_b_reply','channel_b_cancel'];const esc=v=>`"${String(v).replaceAll('"','""')}"`;const csv=[head.join(',')].concat(rows.map(s=>[s.id,s.name,s.region,s.city,s.supervisor,s.status,s.metrics.channel_a_score.cur,s.metrics.channel_a_repeat.cur,s.metrics.channel_a_reply.cur,s.metrics.channel_b_score.cur,s.metrics.channel_b_reply.cur,s.metrics.channel_b_cancel.cur].map(esc).join(','))).join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='synthetic-store-ranking.csv';a.click();URL.revokeObjectURL(a.href)};
 renderAll();
}
init();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
