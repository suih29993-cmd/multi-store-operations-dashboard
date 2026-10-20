# -*- coding: utf-8 -*-
"""Render the public synthetic dashboard using the restored original UI template."""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data.json"
OUTPUT = ROOT / "dashboard.html"

CHANNEL_METRIC_MAP = {
    "channel_a_goods_sat": "mt_goods_sat",
    "channel_a_pack_sat": "mt_pack_sat",
    "channel_a_repeat_score": "mt_repeat_score",
    "channel_a_food_safe": "mt_food_safe",
    "channel_a_reply_score": "mt_reply_score",
    "channel_a_service_fb": "mt_service_fb",
    "channel_a_repeat": "mt_repeat",
    "channel_a_reply": "mt_reply",
    "channel_a_quality": "mt_quality",
    "channel_a_service": "mt_service",
    "channel_a_score": "mt_score",
    "channel_b_taste_sat": "sg_taste_sat",
    "channel_b_pack_sat": "sg_pack_sat",
    "channel_b_repeat_score": "sg_repeat_score",
    "channel_b_food_safe": "sg_food_safe",
    "channel_b_reply_score": "sg_reply_score",
    "channel_b_service_fb": "sg_service_fb",
    "channel_b_reply": "sg_reply",
    "channel_b_cancel": "sg_cancel",
    "channel_b_quality": "sg_quality",
    "channel_b_service": "sg_service",
    "channel_b_score": "sg_score",
}
STATUS_MAP = {"Open": "营业中", "Preparing": "筹备中", "Closed": "已闭店"}


def _map_metrics(metrics: dict) -> dict:
    return {CHANNEL_METRIC_MAP.get(key, key): value for key, value in metrics.items()}


def _map_store(store: dict) -> dict:
    mapped = dict(store)
    mapped["status"] = STATUS_MAP.get(store.get("status"), store.get("status"))
    mapped["metrics"] = _map_metrics(store["metrics"])
    return mapped


def _map_summary(rows: list) -> list:
    return [{**row, "metrics": _map_metrics(row["metrics"])} for row in rows]


def _map_period(period: dict) -> dict:
    meta = dict(period["meta"])
    meta["dataSource"] = "合成演示数据（固定种子 20261020）"
    meta["mtMatched"] = meta.get("matchedStores", meta.get("storeTotal", 0))
    return {
        "meta": meta,
        "region_summary": _map_summary(period["region_summary"]),
        "supervisor_summary": _map_summary(period["supervisor_summary"]),
        "city_summary": _map_summary(period["city_summary"]),
        "stores": [_map_store(store) for store in period["stores"]],
    }


def load_payload() -> dict:
    source = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {
        "defaultPeriod": source["defaultPeriod"],
        "_order": source["_order"],
        "periods": {period_id: _map_period(period) for period_id, period in source["periods"].items()},
    }


LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Operations Analytics">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#45684A"/><stop offset="1" stop-color="#8CA68D"/></linearGradient></defs>
  <rect x="3" y="3" width="58" height="58" rx="15" fill="url(#g)"/>
  <path d="M17 43V30m10 13V21m10 22V34m10 9V16" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
</svg>"""
LOGO_URI = "data:image/svg+xml;base64," + base64.b64encode(LOGO_SVG.encode("utf-8")).decode("ascii")


def main() -> None:
    payload = load_payload()
    periods_json = json.dumps(payload["periods"], ensure_ascii=False).replace("</", "<\\/")
    order_json = json.dumps(payload["_order"], ensure_ascii=False)
    default_json = json.dumps(payload["defaultPeriod"], ensure_ascii=False)
    html = (TEMPLATE.replace("__PERIODS__", periods_json)
                    .replace("__ORDER__", order_json)
                    .replace("__DEFAULT__", default_json)
                    .replace("__LOGO__", LOGO_URI))
    OUTPUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT} ({len(html)} bytes)")


TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index,follow">
<title>Northline Retail · 多门店运营数据看板</title>
<link rel="icon" href="__LOGO__">
<style>
  /* ============ Design Tokens ============ */
  :root{
    --bg:#F9F8F6;          /* 暖白页面背景 */
    --card:#FFFFFF;        /* 卡片/容器背景 */
    --ink:#1A1A1A;         /* 主要文字：墨黑 */
    --sub:#6E6B66;         /* 次要文字：暖灰 */
    --line:#E8E6E1;        /* 边框/分割线 */
    --accent:#45684A;      /* 品牌墨绿（强调） */
    --good:#5E7E5A;        /* 改善：鼠尾草绿 */
    --bad:#BE554B;         /* 恶化：砖红 */
    --neu:#A3A09A;         /* 无变化 */
    --warn-bg:#F9EFEC;     /* 异常背景 */
    --th-bg:#F1F0EC;       /* 表头背景 */
    --font-sans:"Noto Sans SC","PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif;
    --font-num:"Inter","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
    --num-size:15px;       /* 表格里的本期数值字号（下面小字=环比，保持 12px） */
  }
  *{box-sizing:border-box}
  html{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
  body{margin:0;font-family:var(--font-sans);background:var(--bg);color:var(--ink);font-size:14px;line-height:1.5}

  /* ============ Header（暖白 + 文字导航） ============ */
  header{background:var(--bg);padding:24px 32px 0;display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:18px;border-bottom:1px solid var(--line);position:relative}
  header .brand{display:flex;gap:12px;align-items:center}
  header .brand .logo{height:56px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  header .brand .logo svg, header .brand .logo img{height:56px;width:auto;display:block}
  header .brand .titles{flex:1}
  header .brand h1{margin:0;font-family:"Noto Serif SC","Songti SC","STSong",serif;font-size:22px;font-weight:600;letter-spacing:.5px;color:var(--ink)}
  header .brand .meta{margin-top:4px;font-size:12.5px;color:var(--sub);font-family:var(--font-num)}
  header .brand .meta .dot{margin:0 10px;color:#D4D1C9}
  .tabs{display:flex;gap:28px;align-self:flex-end}
  .tabs button{background:none;border:none;color:#4F4B45;padding:0 0 10px;cursor:pointer;font-size:15px;font-weight:500;letter-spacing:.3px;position:relative;font-family:var(--font-sans)}
  .tabs button::after{content:'';position:absolute;left:0;right:0;bottom:-1px;height:2px;background:transparent;border-radius:1px;transition:background .2s}
  .tabs button:hover{color:var(--ink)}
  .tabs button.active{color:var(--accent);font-weight:600}
  .tabs button.active::after{background:var(--accent)}
  .periodbar{position:absolute;top:16px;right:30px;display:flex;align-items:center;gap:6px;z-index:5}
  .periodbar label{font-size:12px;color:var(--sub);white-space:nowrap}
  .periodbar select{min-width:150px;padding:4px 24px 4px 10px;font-size:12px;border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--ink)}

  main{padding:26px 32px 36px;max-width:1320px;margin:0 auto}
  .sec{display:none}
  .sec.active{display:block}
  h2{font-size:18px;margin:2px 0 16px;color:var(--ink);font-weight:600;letter-spacing:.3px;font-family:var(--font-sans)}
  h3{font-size:16px;margin:20px 0 10px;color:var(--ink);font-weight:600;font-family:var(--font-sans)}
  h3:first-child{margin-top:4px}

  /* ============ 卡片 / 面板 ============ */
  .region-block{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 22px;margin-bottom:18px;box-shadow:0 1px 3px rgba(23,23,23,.05)}
  .panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;box-shadow:0 1px 3px rgba(23,23,23,.05)}
  .panel-tight{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;box-shadow:0 1px 3px rgba(23,23,23,.05)}
  .panel-tight table.tbl th,.panel-tight table.tbl td{padding:8px 12px}

  /* ============ 区域 Tab ============ */
  .region-tabs{display:flex;gap:26px;border-bottom:1px solid var(--line);margin-bottom:22px;flex-wrap:wrap}
  .region-tabs button{background:none;border:none;color:var(--sub);padding:0 0 12px;cursor:pointer;font-size:15px;font-weight:500;position:relative;font-family:var(--font-sans)}
  .region-tabs button::after{content:'';position:absolute;left:0;right:0;bottom:-1px;height:1px;background:transparent}
  .region-tabs button:hover{color:var(--ink)}
  .region-tabs button.active{color:var(--accent);font-weight:600}
  .region-tabs button.active::after{background:var(--accent)}

  /* ============ KPI 卡片 ============ */
  /* KPI 卡片：所有卡片同排，标签 / 数值 / 环比 逐行水平对齐（列数 = 指标数，由 JS 写入 --kpi-cols） */
  .kpi-grid{display:grid;grid-template-columns:repeat(var(--kpi-cols,7),minmax(0,1fr));gap:0;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(23,23,23,.05)}
  .kpi{padding:18px 20px;border-right:1px solid var(--line);display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
  .kpi:last-child{border-right:none}
  .kpi-label{font-size:12.5px;color:#45423D;margin-bottom:12px;font-family:var(--font-sans);font-weight:500;letter-spacing:.2px;min-height:3em;display:flex;align-items:flex-end;justify-content:center;text-align:center}
  /* 所有卡片数值盒模型一致（line-height + padding），预警卡只加底色，保证各行严格同水平线 */
  .kpi-val{font-size:32px;font-weight:600;line-height:1.2;padding:2px 6px;border-radius:6px;display:inline-block;font-family:var(--font-num);letter-spacing:-.5px;color:var(--ink);font-variant-numeric:tabular-nums}
  .kpi-delta{font-size:12px;margin-top:9px;font-family:var(--font-num);font-weight:500;font-variant-numeric:tabular-nums}
  .kpi.warn .kpi-val{background:var(--warn-bg)}
  .good{color:var(--good);font-weight:600}
  .bad{color:var(--bad);font-weight:600}
  .neu{color:var(--neu)}

  /* ============ 筛选栏 ============ */
  .filters{display:flex;gap:12px;flex-wrap:nowrap;align-items:center;background:none;border:none;border-radius:0;padding:0 0 14px;margin-bottom:6px;box-shadow:none}
  .fitem{display:flex;align-items:center;gap:6px;flex:0 1 auto;min-width:0}
  .fitem label{font-size:12.5px;color:var(--sub);white-space:nowrap}
  .fitem .search-wrap{position:relative;display:inline-flex;align-items:center}
  .fitem .search-wrap input{padding-right:32px}
  .fitem .search-wrap .ic{position:absolute;right:10px;color:var(--sub);font-size:14px;pointer-events:none}
  select{padding:7px 30px 7px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;font-size:13px;color:var(--ink);min-width:150px;font-family:var(--font-sans);cursor:pointer;appearance:none;-webkit-appearance:none;background-image:url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="6" viewBox="0 0 10 6"><path fill="%23A3A09A" d="M0 0l5 6 5-6z"/></svg>");background-repeat:no-repeat;background-position:right 12px center}
  .filters select{height:36px}
  input[type=text]{padding:6px 11px;border:1px solid var(--line);border-radius:8px;background:#fff;font-size:13px;color:var(--ink);font-family:var(--font-sans)}
  select:focus{outline:none;border-color:var(--accent)}
  .help{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:50%;border:1.5px solid #C7C4BE;color:#8A8781;font-size:11px;font-weight:600;line-height:1;cursor:pointer;margin-left:3px;vertical-align:middle;font-family:var(--font-sans);background:#fff}
  .help:hover{border-color:var(--accent);color:var(--accent)}
  .help-tip{position:fixed;z-index:60;display:none;max-width:320px;width:max-content;background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 24px rgba(23,23,23,.12);padding:10px 12px;font-size:12px;line-height:1.6;color:var(--ink);white-space:normal}

  /* ============ 表格 ============ */
  table th,table td{vertical-align:middle;text-align:center}
  table.tbl{width:100%;table-layout:fixed;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:13px}
  table.tbl th{background:var(--th-bg);color:var(--ink);text-align:center;padding:10px 12px;font-weight:600;border-bottom:1px solid var(--line);font-family:var(--font-sans);vertical-align:middle;overflow-wrap:anywhere}
  table.tbl td{padding:10px 12px;border-bottom:1px solid var(--line);background:var(--card);color:var(--ink);font-family:var(--font-sans);text-align:center;vertical-align:middle;overflow-wrap:anywhere}
  table.tbl td.num,table.tbl td .num{font-family:var(--font-num);font-variant-numeric:tabular-nums;font-size:var(--num-size);line-height:1.25}
  table.tbl td b.num{font-family:var(--font-num)}   /* Bottom 5 表：本期数值保持原字号 */
  table.tbl tr:last-child td{border-bottom:none}
  table.tbl tbody tr:hover{background:#FAF9F6}
  table.tbl tbody tr:hover td{background:#FAF9F6}
  .metric-name{font-weight:600;color:var(--ink);font-family:var(--font-sans)}
  /* 分组表头（渠道 A/B）：浅灰底 + 细分割 */
  table.tbl th.group-mt{background:var(--th-bg);color:var(--ink);text-align:center;border-right:1px solid var(--line)}
  table.tbl th.group-sg{background:var(--th-bg);color:var(--ink);text-align:center}
  #supStoreTable .tbl th{text-align:center}
  .tbl th.mt-col{background:var(--th-bg);color:var(--ink);border-right:1px solid var(--line)}
  .tbl th.sg-col{background:var(--th-bg);color:var(--ink)}
  .tbl th.mt-last{border-right:2px solid #C7C4BE !important}
  .tbl td.mt-last{border-right:2px solid #C7C4BE !important}
  /* 督导视图（督导表现 + 门店明细）：正文字号与本期数值一致；环比小字仍走 .dtext */
  #supTable table.tbl,#supStoreTable table.tbl{font-size:var(--num-size)}
  /* 异常：仅预警单元格使用浅红底；其余默认白底 */
  .tbl td.warn{background:var(--warn-bg) !important}
  .dtext{font-size:12px;font-weight:600;white-space:nowrap;font-family:var(--font-num);font-variant-numeric:tabular-nums}
  .sort-acc{color:var(--accent);font-weight:700}
  .rank-no{color:var(--accent);font-family:var(--font-num);font-weight:600;letter-spacing:.5px;font-variant-numeric:tabular-nums}
  .legend{font-size:12.5px;color:var(--sub);margin:10px 0 14px;line-height:1.7}
  .legend b.good{color:var(--good);font-weight:600} .legend b.bad{color:var(--bad);font-weight:600}
  .legend .neu{color:var(--neu)}

  footer{text-align:center;color:var(--sub);font-size:12px;padding:22px 0 30px;border-top:1px solid var(--line);margin-top:8px}
  .tag{display:inline-block;font-size:11px;padding:3px 9px;border-radius:6px;background:#F1F0EC;color:#4F4B45;margin-left:10px;font-weight:500;line-height:1.4;vertical-align:.5px}
  .mini{padding:5px 12px;font-size:12px;border:1px solid var(--line);background:#fff;border-radius:8px;cursor:pointer;color:var(--ink)}
  .mini:hover{background:#F1F0EC}

  /* ============ 树形多选器 ============ */
  .tree-dropdown{position:relative;display:inline-block;min-width:0;max-width:100%}
  .tree-trigger{display:inline-flex;align-items:center;gap:8px;min-width:150px;justify-content:space-between;padding:7px 30px 7px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;font-size:13px;cursor:pointer;max-width:220px;color:var(--ink);background-image:url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="6" viewBox="0 0 10 6"><path fill="%23A3A09A" d="M0 0l5 6 5-6z"/></svg>");background-repeat:no-repeat;background-position:right 12px center;appearance:none;-webkit-appearance:none}
  .tree-trigger>span{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:left}
  .tree-trigger:hover,.tree-trigger:focus{border-color:var(--accent)}
  .tree-trigger:hover{border-color:var(--accent)}
  .tree-panel{position:absolute;z-index:20;top:calc(100% + 6px);left:0;width:440px;max-width:94vw;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 10px 32px rgba(23,23,23,.10);padding:14px 16px;display:none}
  .tree-panel.open{display:block}
  .tree-search{width:100%;padding:8px 12px;border:1px solid var(--line);border-radius:8px;font-size:13px;margin-bottom:10px;font-family:var(--font-sans)}
  .tree-hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
  .tree-count{font-size:12px;color:var(--sub)}
  .tree-box{max-height:min(78vh,720px);overflow:auto;border:1px solid var(--line);border-radius:8px;padding:8px 0;background:#fff}
  #b3cityBox,#v2cityBox,#metricBox{max-height:none}
  .tree-node{font-size:13px}
  .tree-row{display:flex;align-items:center;gap:4px;padding:4px 12px;cursor:pointer;user-select:none}
  .tree-row:hover{background:#F7F6F2}
  .tree-arrow{width:16px;height:16px;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;color:var(--sub);flex-shrink:0}
  .tree-arrow::after{content:'▶';font-size:10px}
  .tree-arrow.open::after{content:'▼'}
  .tree-spacer{width:16px;flex-shrink:0}
  .tree-cb{width:14px;height:14px;margin:0 4px 0 0;cursor:pointer;flex-shrink:0;accent-color:var(--accent)}
  .tree-label{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:var(--font-sans)}
  .tree-match{background:#F3EFE5;border-radius:4px;padding:0 4px}
  .tree-children{display:block}
  .tree-group{font-size:11px;color:var(--sub);font-weight:600;padding:6px 12px 2px;letter-spacing:.5px}
  .metric-row.tree-sel{background:#F3F1EC;font-weight:600;color:var(--accent)}
  .metric-row.tree-sel::after{content:'✓';margin-left:auto;color:var(--accent);font-weight:700;padding-right:4px}

  /* ============ 平板 / 移动端自适应（纯样式，不动数据与逻辑） ============ */
  @media (max-width:1024px){
    header{padding:18px 18px 0}
    main{padding:20px 18px 30px}
    .filters{flex-wrap:wrap;gap:8px 10px}
    .fitem{flex:0 1 auto;min-width:0}
    .fitem .tree-dropdown,.fitem .search-wrap{max-width:100%}
    .kpi{padding:14px 12px}
    .kpi-val{font-size:26px}
    .panel, .panel-tight{overflow-x:auto}
    table.tbl{min-width:560px}
    .help-tip{max-width:calc(100vw - 24px)}
  }
  @media (max-width:760px){
    header{padding:14px 14px 0;gap:10px}
    header .brand .logo, header .brand .logo svg, header .brand .logo img{height:40px}
    header .brand h1{font-size:17px}
    header .brand .meta{font-size:11.5px}
    header .brand .meta .dot{margin:0 6px}
    .periodbar{position:static;width:100%;align-self:stretch;justify-content:flex-end;margin:2px 0 8px}
    .periodbar select{flex:1;min-width:0}
    .tabs{width:100%;gap:20px;overflow-x:auto;padding-top:2px}
    .tabs button{font-size:14px;white-space:nowrap}
    main{padding:16px 12px 26px}
    h2{font-size:16.5px}
    h3{font-size:15px;margin:16px 0 8px}
    .region-block{padding:14px 14px;margin-bottom:14px}
    .panel{padding:12px;border-radius:10px}
    .panel-tight{padding:8px}
    .kpi-grid{grid-template-columns:1fr 1fr}
    .kpi{padding:14px 14px;border-bottom:1px solid var(--line)}
    .kpi:nth-child(2n), .kpi:last-child{border-right:none}
    .kpi:last-child{border-bottom:none}
    .kpi-label{margin-bottom:8px;min-height:2.6em}
    .kpi-val{font-size:24px}
    .filters{padding-bottom:10px}
    .fitem{flex:1 1 100%;min-width:0}
    .fitem .tree-dropdown, .fitem .search-wrap{width:100%}
    .fitem .search-wrap input{width:100%}
    .tree-trigger{width:100%;min-width:0;max-width:100%}
    .tree-panel{left:0;right:auto;width:100%;max-width:100%}
    table.tbl{min-width:660px;font-size:12px}
    :root{--num-size:13.5px}
    table.tbl th, table.tbl td{padding:7px 8px}
    .dtext{font-size:11px}
    .legend{font-size:11.5px}
    footer{padding:16px 12px 24px}
  }
  @media (max-width:420px){
    .kpi{padding:12px}
    .kpi-val{font-size:21px}
    .kpi-label{font-size:11.5px}
    table.tbl{min-width:600px}
  }
</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="logo" aria-label="Northline Retail"><img class="brand-svg" src="__LOGO__" alt="Northline Retail"></div>
    <div class="titles">
      <h1>Northline · 运营数据看板</h1>
      <div class="meta" id="hdrMeta"></div>
    </div>
  </div>
  <div class="tabs">
    <button data-v="v1" class="active">区域周报总览</button>
    <button data-v="v3">督导视图</button>
    <button data-v="v2">门店全景排名</button>
  </div>
  <div class="periodbar">
    <label>数据周期</label>
    <select id="periodSel"></select>
  </div>
</header>
<main>
  <!-- 视图1 -->
  <section class="sec active" id="v1">
    <h2>区域周报总览 <span class="tag">数据源：合成评分数据 · 区域汇总</span></h2>
    <div class="region-tabs" id="regionTabs"></div>
    <div id="regionCards"></div>
    <h3>各区 Bottom 5 门店（按核心指标末位）<span class="tag">数据源：合成评分数据</span></h3>
    <div class="filters">
      <div class="fitem"><label>区域</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="b3regionTrigger"><span id="b3regionTriggerTxt">全部区域</span></div>
          <div class="tree-panel" id="b3regionPanel">
            <div class="tree-hd">
              <div><b>区域（可多选）</b> <span class="tree-count" id="b3regionCount"></span></div>
              <div>
                <button type="button" class="mini" id="b3regionCheckAll">全选</button>
                <button type="button" class="mini" id="b3regionClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="b3regionBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>城市</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="b3cityTrigger"><span id="b3cityTriggerTxt">全部城市</span></div>
          <div class="tree-panel" id="b3cityPanel">
            <div class="tree-hd">
              <div><b>城市（可多选）</b> <span class="tree-count" id="b3cityCount"></span></div>
              <div>
                <button type="button" class="mini" id="b3cityCheckAll">全选</button>
                <button type="button" class="mini" id="b3cityClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="b3cityBox"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="panel panel-tight"><div id="bottom3"></div></div>
  </section>

  <!-- 视图2 -->
  <section class="sec" id="v2">
    <h2>门店全景排名 <span class="tag">数据源：合成评分数据 · 门店维度</span></h2>
    <div class="filters">
      <div class="fitem"><label>区域</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="v2regionTrigger"><span id="v2regionTriggerTxt">全部区域</span></div>
          <div class="tree-panel" id="v2regionPanel">
            <div class="tree-hd">
              <div><b>区域（可多选）</b> <span class="tree-count" id="v2regionCount"></span></div>
              <div>
                <button type="button" class="mini" id="v2regionCheckAll">全选</button>
                <button type="button" class="mini" id="v2regionClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="v2regionBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>城市</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="v2cityTrigger"><span id="v2cityTriggerTxt">全部城市</span></div>
          <div class="tree-panel" id="v2cityPanel">
            <div class="tree-hd">
              <div><b>城市（可多选）</b> <span class="tree-count" id="v2cityCount"></span></div>
              <div>
                <button type="button" class="mini" id="v2cityCheckAll">全选</button>
                <button type="button" class="mini" id="v2cityClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="v2cityBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>督导</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="v2supTrigger"><span id="v2supTriggerTxt">全部督导</span></div>
          <div class="tree-panel" id="v2supPanel">
            <div class="tree-hd">
              <div><b>督导（可多选）</b> <span class="tree-count" id="v2supCount"></span></div>
              <div>
                <button type="button" class="mini" id="v2supCheckAll">全选</button>
                <button type="button" class="mini" id="v2supClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="v2supBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>门店</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="treeTrigger"><span id="treeTriggerTxt">⌕ 请输入门店名称</span></div>
          <div class="tree-panel" id="treePanel">
            <div class="tree-hd">
              <div><b>门店筛选</b> <span class="tree-count" id="treeCount"></span></div>
              <div>
                <button type="button" class="mini" id="treeExpand">全部展开</button>
                <button type="button" class="mini" id="treeCollapse">全部折叠</button>
                <button type="button" class="mini" id="treeCheckAll">全选</button>
                <button type="button" class="mini" id="treeClear">清空</button>
              </div>
            </div>
            <input type="text" class="tree-search" id="treeSearch" placeholder="请输入门店、城市，回车搜索">
            <div class="tree-box" id="treeBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>渠道</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="v2platformTrigger"><span id="v2platformTriggerTxt">全部渠道</span></div>
          <div class="tree-panel" id="v2platformPanel">
            <div class="tree-hd">
              <div><b>渠道（可多选）</b> <span class="tree-count" id="v2platformCount"></span></div>
              <div>
                <button type="button" class="mini" id="v2platformCheckAll">全选</button>
                <button type="button" class="mini" id="v2platformClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="v2platformBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>指标</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="metricTrigger"><span id="metricTriggerTxt">请选择指标</span></div>
          <div class="tree-panel" id="metricPanel">
            <div class="tree-hd">
              <div><b>指标（可多选）</b> <span class="tree-count" id="metricCount"></span></div>
              <div>
                <button type="button" class="mini" id="metricAll">全选</button>
                <button type="button" class="mini" id="metricClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="metricBox"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="legend">说明：评分 / 回复率 / 满意度类指标 <b class="good">越高越好</b>；商责取消率 <b class="good">越低越好</b>。仅统计「营业中」门店。差值 <b class="good">改善</b> / <b class="bad">恶化</b> / <span class="neu">无变化</span>。单元格 <span style="padding:1px 6px;border-radius:4px;background:#FBF1EF">浅红=未达标预警</span>：评分 / 商品质量分 / 服务体验分 / 满意度 &lt; 4.5；复购率指标得分 / 食品安全负反馈率 / 消息回复率得分 / 服务负反馈率 低于同组合后 10%；商责取消率 &gt; 0.3%。</div>
    <h3>门店明细</h3>
    <div class="panel" id="storeView"></div>
  </section>

  <!-- 视图3 -->
  <section class="sec" id="v3">
    <h2>督导视图 <span class="tag">数据源：合成评分数据 · 督导维度</span></h2>
    <div class="filters">
      <div class="fitem"><label>区域</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="v3regionTrigger"><span id="v3regionTriggerTxt">全部区域</span></div>
          <div class="tree-panel" id="v3regionPanel">
            <div class="tree-hd">
              <div><b>区域（可多选）</b> <span class="tree-count" id="v3regionCount"></span></div>
              <div>
                <button type="button" class="mini" id="v3regionCheckAll">全选</button>
                <button type="button" class="mini" id="v3regionClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="v3regionBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>督导</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="v3supTrigger"><span id="v3supTriggerTxt">全部督导</span></div>
          <div class="tree-panel" id="v3supPanel">
            <div class="tree-hd">
              <div><b>督导（可多选）</b> <span class="tree-count" id="v3supCount"></span></div>
              <div>
                <button type="button" class="mini" id="v3supCheckAll">全选</button>
                <button type="button" class="mini" id="v3supClear">清空</button>
              </div>
            </div>
            <div class="tree-box" id="v3supBox"></div>
          </div>
        </div>
      </div>
      <div class="fitem"><label>门店</label>
        <div class="tree-dropdown">
          <div class="tree-trigger" id="v3treeTrigger"><span id="v3treeTriggerTxt">⌕ 请输入门店名称</span></div>
          <div class="tree-panel" id="v3treePanel">
            <div class="tree-hd">
              <div><b>门店筛选</b> <span class="tree-count" id="v3treeCount"></span></div>
              <div>
                <button type="button" class="mini" id="v3treeExpand">全部展开</button>
                <button type="button" class="mini" id="v3treeCollapse">全部折叠</button>
                <button type="button" class="mini" id="v3treeCheckAll">全选</button>
                <button type="button" class="mini" id="v3treeClear">清空</button>
              </div>
            </div>
            <input type="text" class="tree-search" id="v3treeSearch" placeholder="请输入门店、城市，回车搜索">
            <div class="tree-box" id="v3treeBox"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="legend">说明：评分 / 商品质量分 / 服务体验分 <b class="good">越高越好</b>；商责取消率 <b class="good">越低越好</b>。<br>6 项底层指标权重合计 100%（商品类 4 项合计 80%、服务类 2 项合计 20%）。商品质量分 =（商品满意度×30% + 包装满意度×10% + 复购率指标得分×20% + 食品安全负反馈率×20%）÷ 80%，服务体验分 =（消息回复率×10% + 服务负反馈率×10%）÷ 20%，两者归一化后都是 5 分制；综合体验分（即平台评分）= 商品质量分×80% + 服务体验分×20%（渠道B取口味满意度）。仅统计「营业中」门店。差值 <b class="good">改善</b> / <b class="bad">恶化</b> / <span class="neu">无变化</span>。单元格 <span style="padding:1px 6px;border-radius:4px;background:#FBF1EF">浅红=未达标预警</span>：评分 / 商品质量分 / 服务体验分 &lt; 4.5；商责取消率 &gt; 0.3%。选择督导后可进一步勾选其下属门店查看明细。</div>
    <h3>督导表现</h3>
    <div class="panel" id="supTable"></div>
    <div class="panel" id="supStoreTable" style="margin-top:18px;display:none"></div>
  </section>
</main>
<footer id="ftr"></footer>

<script>
const PERIODS = __PERIODS__;
const PERIOD_ORDER = __ORDER__;
const DEFAULT_PERIOD = __DEFAULT__;
let DATA = PERIODS[DEFAULT_PERIOD];
let CUR_PERIOD = DEFAULT_PERIOD;
const savedPeriod = localStorage.getItem('operations_demo_period');
if (savedPeriod && PERIODS[savedPeriod]) { CUR_PERIOD = savedPeriod; DATA = PERIODS[savedPeriod]; }
const METRICS = {
  mt_score:{name:'渠道A评分',ch:'渠道A',unit:'score',dir:'high'},
  mt_goods_sat:{name:'商品满意度',ch:'渠道A',unit:'score',dir:'high'},
  mt_pack_sat:{name:'包装满意度',ch:'渠道A',unit:'score',dir:'high'},
  mt_repeat_score:{name:'复购率指标得分',ch:'渠道A',unit:'score',dir:'high'},
  mt_food_safe:{name:'食品安全负反馈率',ch:'渠道A',unit:'score',dir:'high'},
  mt_reply_score:{name:'消息回复率得分',ch:'渠道A',unit:'score',dir:'high'},
  mt_reply:{name:'消息回复率',ch:'渠道A',unit:'pct',dir:'high'},
  mt_service_fb:{name:'服务负反馈率',ch:'渠道A',unit:'score',dir:'high'},
  mt_repeat:{name:'复购率',ch:'渠道A',unit:'pct',dir:'high'},
  mt_quality:{name:'商品质量分',ch:'渠道A',unit:'score',dir:'high'},
  mt_service:{name:'服务体验分',ch:'渠道A',unit:'score',dir:'high'},
  sg_score:{name:'渠道B评分',ch:'渠道B',unit:'score',dir:'high'},
  sg_taste_sat:{name:'口味满意度',ch:'渠道B',unit:'score',dir:'high'},
  sg_pack_sat:{name:'包装满意度',ch:'渠道B',unit:'score',dir:'high'},
  sg_repeat_score:{name:'复购率指标得分',ch:'渠道B',unit:'score',dir:'high'},
  sg_food_safe:{name:'食品安全负反馈率',ch:'渠道B',unit:'score',dir:'high'},
  sg_reply_score:{name:'消息回复率得分',ch:'渠道B',unit:'score',dir:'high'},
  sg_reply:{name:'消息回复率',ch:'渠道B',unit:'pct',dir:'high'},
  sg_service_fb:{name:'服务负反馈率',ch:'渠道B',unit:'score',dir:'high'},
  sg_cancel:{name:'商责取消率',ch:'渠道B',unit:'pct',dir:'low'},
  sg_quality:{name:'商品质量分',ch:'渠道B',unit:'score',dir:'high'},
  sg_service:{name:'服务体验分',ch:'渠道B',unit:'score',dir:'high'},
};
const SAT_FORMULA=' =（1×一星评价数 + 2×二星评价数 + 3×三星评价数 + 4×四星评价数 + 5×五星评价数）÷ 总评价数';
const MT_RANK='（与同市&饮品品类的商家进行排名比较计分。每个名次区间依次递减0.1分，如第一个区间5分，第二个区间4.9分，依次递减。）';
const HELP_MT_REPEAT='复购率=下单两次及以上的顾客人数÷总下单顾客数'+MT_RANK;
const METRIC_HELP={
  mt_score:'渠道A评分（综合体验分）= 商品质量分×80% + 服务体验分×20%。商品质量分 =（商品满意度×30% + 包装满意度×10% + 复购率指标得分×20% + 食品安全负反馈率×20%）÷ 80%，服务体验分 =（消息回复率×10% + 服务负反馈率×10%）÷ 20%。6 项底层指标权重合计 100%（商品类 80%、服务类 20%），两个分类分各自按本维度总权重归一化到 5 分制，因此与评分同一量纲。',
  sg_score:'渠道B评分（综合体验分）= 商品质量分×80% + 服务体验分×20%。商品质量分 =（口味满意度×30% + 包装满意度×10% + 复购率指标得分×20% + 食品安全负反馈率×20%）÷ 80%，服务体验分 =（消息回复率×10% + 服务负反馈率×10%）÷ 20%。6 项底层指标权重合计 100%（商品类 80%、服务类 20%），两个分类分各自按本维度总权重归一化到 5 分制，因此与评分同一量纲。',
  mt_repeat:HELP_MT_REPEAT,
  mt_goods_sat:'商品满意度：近60天内所有计分评价中商品评分和口味评分的平均值，反映顾客对商家所售商品的满意程度。商品满意度=（1×一星评价数+2×二星评价数+3×三星评价数+4×四星评价数+5×五星评价数）÷ 总评价数',
  sg_taste_sat:'统计近60天内(T-2至T-61)口味评价的好、中、差评，计算口味满意度得分平均值。计算公式为：口味满意度'+SAT_FORMULA+'。',
  mt_pack_sat:'包装满意度：近60天内所有计分评价中包装评分的平均值，反映顾客对商品包装的满意程度。包装满意度=（1×一星评价数+2×二星评价数+3×三星评价数+4×四星评价数+5×五星评价数）÷ 总评价数',
  sg_pack_sat:'统计近60天内(T-2至T-61)包装评价的好、中、差评，计算包装满意度得分平均值。计算公式为：包装满意度'+SAT_FORMULA+'。',
  mt_repeat_score:'复购率指标得分：复购率 = 下单两次及以上的顾客人数 ÷ 总下单顾客数。得分计算方法为：与同二级城市、同品类、同客单价区间的商家进行排名比较计分。每个名次区间依次递减0.1分，如第一个区间5分，第二个区间4.9分，依次递减',
  sg_repeat_score:'复购率指标得分：统计门店近30天(T-2至T-31)复购率，并在同城市、同品类、同客单价的商户中排序，根据排名先后赋予相应分数。复购率越高，得分越高。',
  mt_food_safe:'食品安全负反馈率衡量的是每万单中涉及食品安全问题的加权负反馈订单数量，其公式为：（各渠道各场景反馈订单量 × 对应渠道权重 × 对应场景权重）的总和 ÷ 总订单量 × 10000。得分计算方法为：与同二级城市、同品类、同客单价区间的商家进行排名比较计分。每个名次区间依次递减0.1分，如第一个区间5分，第二个区间4.9分，依次递减',
  sg_food_safe:'食品安全负反馈：统计门店过往30天食品安全事件，根据食安事件等级（P0、P1、P2、P3）由高到低设置权重系数，计算食安事件占比=（食安事件数 x 对应等级权重系数）的总和 / 近30天门店总订单数，并在同城市、同商圈、同品类的商户中排序，根据门店排序赋予相应分数。食安事件越少、食安事件严重程度越低，则门店得分越高。',
  mt_reply_score:'消息回复率得分：消息回复率=5分钟内回复的会话数÷顾客主动发起的总会话数。得分计算方法为：与同二级城市、同品类、同客单价区间的商家进行排名比较计分。每个名次区间依次递减0.1分，如第一个区间5分，第二个区间4.9分，依次递减',
  mt_reply:'消息回复率：近30天内，收到顾客会话后5分钟内做出回复的会话占比（含人工回复和智能机器人回复），反映商家及时响应顾客消息的情况。消息回复率=5分钟内回复的会话数÷顾客主动发起的总会话数',
  sg_reply_score:'消息回复率得分：统计门店近30天(T-2至T-31)消息回复率，并在同城市、同商圈、同品类的商户中排序，根据排名先后赋予相应分数（满分 5 分）。消息回复率越高，得分越高。',
  sg_reply:'消息回复率：渠道B门店近30天(T-2至T-31)的消息回复率百分比（5 分钟内回复的会话数 ÷ 顾客主动发起的总会话数），越高越好。这是原始百分比；按排名折算的 0-5 分见「消息回复率得分」。',
  mt_service_fb:'服务负反馈率衡量的是每万单中收到加权负向反馈订单的数量，其公式为：(各渠道反馈订单量 × 对应权重) 的总和 ÷ 总订单量 × 10000。得分计算方法为：与同二级城市、同品类、同客单价区间的商家进行排名比较计分，每个名次区间依次递减0.1分，如第一个区间5分，第二个区间4.9分，依次递减',
  sg_service_fb:'服务负反馈率：统计门店近30天(T-2至T-31)的服务负反馈事件，计算门店负反馈事件占比=（负反馈问题订单数/近30天门店总订单数），并在同城市、同商圈、同品类的商户中排序，根据排名先后赋予相应分数。服务负反馈事件数越少，得分越高。',
  sg_cancel:'商责取消率：商家责任导致的订单取消占比，越低越好。',
  mt_quality:'商品质量分 =（商品满意度×30% + 包装满意度×10% + 复购率指标得分×20% + 食品安全负反馈率×20%）÷ 80%：4 项权重合计 80%，除以本维度总权重归一化到 5 分制（满分 5 分，越高越好）。综合体验分 = 商品质量分×80% + 服务体验分×20% = 渠道A评分。',
  mt_service:'服务体验分 =（消息回复率×10% + 服务负反馈率×10%）÷ 20%：2 项权重合计 20%，除以本维度总权重归一化到 5 分制（满分 5 分，越高越好）。综合体验分 = 商品质量分×80% + 服务体验分×20% = 渠道A评分。',
  sg_quality:'商品质量分 =（口味满意度×30% + 包装满意度×10% + 复购率指标得分×20% + 食品安全负反馈率×20%）÷ 80%：4 项权重合计 80%，除以本维度总权重归一化到 5 分制（满分 5 分，越高越好）。综合体验分 = 商品质量分×80% + 服务体验分×20% = 渠道B评分。',
  sg_service:'服务体验分 =（消息回复率×10% + 服务负反馈率×10%）÷ 20%：2 项权重合计 20%，除以本维度总权重归一化到 5 分制（满分 5 分，越高越好）。综合体验分 = 商品质量分×80% + 服务体验分×20% = 渠道B评分。',
};
const REGION_METRICS=['mt_score','mt_quality','mt_service','sg_score','sg_quality','sg_service','sg_cancel'];   // 区域周报总览 KPI
const BOTTOM_METRICS=['mt_score','mt_quality','mt_service','mt_reply','sg_score','sg_quality','sg_service','sg_reply','sg_cancel'];   // Bottom 5 表（比 KPI 多渠道A/渠道B消息回复率）
const ALL_M=Object.keys(METRICS);
const V3_MT_ORDER=['mt_score','mt_quality','mt_service'];
const V3_SG_ORDER=['sg_score','sg_quality','sg_service','sg_cancel'];
const V3_MT_HEADERS=['评分','商品质量分','服务体验分'];
const V3_SG_HEADERS=['评分','商品质量分','服务体验分','商责取消率'];

const CITY_TO_PROV=Object.fromEntries(DATA.stores.map(s=>[s.city,s.province]));
const PROVINCE_ORDER=[...new Set(DATA.stores.map(s=>s.province))];

// 视图1 指标名：带渠道前缀；评分显示为「总评分」以区别于商品质量分/服务体验分
function mLbl(mk){ return METRICS[mk].ch+(mk==='mt_score'||mk==='sg_score'?'总评分':METRICS[mk].name); }
function fmt(mk,v){
  if(v===null||v===undefined) return '—';
  const u=METRICS[mk].unit;
  if(u==='pct') return (v*100).toFixed(2)+'%';
  if(u==='score') return v.toFixed(2);
  return v.toFixed(1);
}
function dclass(mk,d){
  if(d===null||d===undefined) return 'neu';
  if(d===0) return 'neu';
  const dir=METRICS[mk].dir;
  const imp=(d>0&&dir==='high')||(d<0&&dir==='low');
  return imp?'good':'bad';
}
function dtext(mk,d){
  if(d===null||d===undefined) return '<span class="neu dtext">—</span>';
  const cls=dclass(mk,d);
  const ar=d>0?'▲':(d<0?'▼':'—');
  const u=METRICS[mk].unit;
  const dv=u==='pct'?(Math.abs(d)*100).toFixed(2)+'%':Math.abs(d).toFixed(u==='score'?2:1);
  return '<span class="'+cls+' dtext">'+ar+' '+dv+'</span>';
}
function opt(v,t){return '<option value="'+v+'">'+t+'</option>';}
function helpIcon(mk){
  const t=METRIC_HELP[mk];
  if(!t) return '';
  return ' <span class="help" data-mk="'+mk+'" tabindex="0">?</span>';
}
const _tip=document.createElement('div');_tip.id='helpTip';_tip.className='help-tip';document.body.appendChild(_tip);
function _showHelp(h){
  const mk=h.getAttribute('data-mk');
  const txt=METRIC_HELP[mk];
  if(!txt) return;
  _tip.textContent=txt;
  _tip.style.display='block';
  const r=h.getBoundingClientRect();
  const tw=_tip.offsetWidth||320, th=_tip.offsetHeight||20;
  let left=r.left+r.width/2-tw/2;
  left=Math.max(8,Math.min(left,window.innerWidth-tw-8));
  let top=r.bottom+6;
  if(top+th>window.innerHeight-8) top=r.top-th-6;
  _tip.style.left=Math.round(left)+'px';
  _tip.style.top=Math.round(top)+'px';
}
function _hideHelp(){ _tip.style.display='none'; }
document.addEventListener('mouseover',function(e){const h=e.target.closest('.help'); if(h)_showHelp(h);});
document.addEventListener('mouseout',function(e){const h=e.target.closest('.help'); if(h&&!h.contains(e.relatedTarget))_hideHelp();});
document.addEventListener('click',function(e){const h=e.target.closest('.help'); if(h)_showHelp(h); else _hideHelp();});
// ---- 视图1 ----
let v1RegionIdx=0; // 当前选中的区域 Tab 下标（默认第一个=全部区域）
function kpiState(mk,cur,delta){
  // 返回 KPI 卡片的预警状态：'warn' 未达标 → 当前值以浅红高亮；'great' / '' 一律白底
  // 异常优先：未达标判定统一走 isWarn()（见文件末尾规则表）
  if(isWarn(mk,cur)) return 'warn';
  // 优秀：评分>=4.8
  if((mk==='mt_score'||mk==='sg_score')&&cur!==null&&cur>=4.8) return 'great';
  return '';
}
function renderRegion(){
  const tabs=document.getElementById('regionTabs');
  const wrap=document.getElementById('regionCards');
  const regs=DATA.region_summary;
  // Tab 槽位（仅 3 个有数据的区域）
  const allNames=DATA.region_summary.map(r=>r.name);
  const dataIdxFor=n=>regs.findIndex(r=>r.name===n);
  if(v1RegionIdx>=allNames.length) v1RegionIdx=0;
  // 渲染 Tab
  tabs.innerHTML='';
  allNames.forEach((n,i)=>{
    const b=document.createElement('button');
    b.textContent=n;
    if(i===v1RegionIdx) b.classList.add('active');
    const di=dataIdxFor(n);
    if(di<0){ b.disabled=true; b.style.opacity='.35'; b.style.cursor='default'; }
    else { b.onclick=()=>{ v1RegionIdx=i; renderRegion(); }; }
    tabs.appendChild(b);
  });
  // 渲染当前区域 KPI（无数据则提示）
  const curName=allNames[v1RegionIdx];
  const curDataIdx=dataIdxFor(curName);
  if(curDataIdx<0){
    wrap.innerHTML='<div class="region-block"><div style="color:var(--sub);font-size:13px;padding:24px 0;text-align:center">'+curName+' 暂无数据</div></div>';
    return;
  }
  const r=regs[curDataIdx];
  let cards='';
  REGION_METRICS.forEach(mk=>{
    const mm=r.metrics[mk];
    const st=kpiState(mk,mm.cur,mm.delta);
      cards+='<div class="kpi'+(st?' '+st:'')+'"><div class="kpi-label">'+mLbl(mk)+'</div>'+
      '<div class="kpi-val">'+fmt(mk,mm.cur)+'</div>'+
      '<div class="kpi-delta">'+dtext(mk,mm.delta)+'</div></div>';
  });
  wrap.innerHTML='<div class="kpi-grid" style="--kpi-cols:'+REGION_METRICS.length+'">'+cards+'</div>';
}
function renderBottom3(){
  const regs=b3RegTree.getChecked();
  const cities=b3CityTree.getChecked();
  let html='<table class="tbl"><thead><tr><th>指标</th><th>Bottom 1</th><th>Bottom 2</th><th>Bottom 3</th><th>Bottom 4</th><th>Bottom 5</th></tr></thead><tbody>';
  BOTTOM_METRICS.forEach(mk=>{
    let list=DATA.stores.filter(s=>s.status==='营业中'&&s.metrics[mk].cur!==null&&(regs.length===0||regs.includes(s.region))&&(cities.length===0||cities.includes(s.city)));
    const dir=METRICS[mk].dir;
    list.sort((a,b)=>dir==='high'?a.metrics[mk].cur-b.metrics[mk].cur:b.metrics[mk].cur-a.metrics[mk].cur);
    const b3=list.slice(0,5);
    const cells=b3.map(s=>'<td>'+s.name+'<br><b class="num">'+fmt(mk,s.metrics[mk].cur)+'</b></td>').join('');
    html+='<tr><td class="metric-name">'+mLbl(mk)+'</td>'+cells+'</tr>';
  });
  html+='</tbody></table>';
  document.getElementById('bottom3').innerHTML=html;
}

// ---- 视图2 ----
const PLATFORMS={'渠道A':['mt_score','mt_goods_sat','mt_pack_sat','mt_repeat_score','mt_food_safe','mt_reply_score','mt_reply','mt_service_fb'],
                 '渠道B':['sg_score','sg_taste_sat','sg_pack_sat','sg_repeat_score','sg_food_safe','sg_reply_score','sg_reply','sg_service_fb','sg_cancel']};
const SUB_MT=['mt_goods_sat','mt_pack_sat','mt_repeat_score','mt_food_safe','mt_reply_score','mt_service_fb'];
const SUB_SG=['sg_taste_sat','sg_pack_sat','sg_repeat_score','sg_food_safe','sg_reply_score','sg_service_fb'];
const SUB_OF={'mt_score':SUB_MT,'sg_score':SUB_SG};   // 评分指标可展开的二级指标
// ---- 通用门店树形多选组件（视图2/视图3 复用）----
// 触发器（选项卡）文案：直接显示当前选中的选项，超过 3 项时截断为「前 2 项 等 N 项」
function trigLabel(labels,allText,unit){
  if(!labels.length) return allText;
  if(labels.length>3) return labels.slice(0,2).join('、')+' 等 '+labels.length+' '+(unit||'项');
  return labels.join('、');
}
function makeStoreTree(cfg){
  // cfg: {box, count, trigTxt, panel, getAvailable, onChange}
  let treeData=[];
  const $=id=>document.getElementById(id);
  function updateNodeFromChildren(node){
    if(!node.children||node.children.length===0)return;
    const all=node.children.every(c=>c.checked&&!c.indeterminate);
    const some=node.children.some(c=>c.checked||c.indeterminate);
    node.checked=all; node.indeterminate=!all&&some;
  }
  function setNodeChecked(node,checked){node.checked=checked;node.indeterminate=false;if(node.children)node.children.forEach(c=>setNodeChecked(c,checked));}
  function propagateUp(node){if(!node.parent)return;updateNodeFromChildren(node.parent);propagateUp(node.parent);}
  function getCheckedStoreNames(){const set=new Set();(function walk(ns){ns.forEach(n=>{if(n.type==='store'&&n.checked)set.add(n.id);if(n.children)walk(n.children);});})(treeData);return [...set];}
  function findNode(id,nodes){for(const n of (nodes||treeData)){if(n.id===id)return n;if(n.children){const f=findNode(id,n.children);if(f)return f;}}return null;}
  function toggleNode(id){const n=findNode(id);if(n){n.expanded=!n.expanded;renderTree();}}
  function onNodeCheck(id,checked){const n=findNode(id);if(!n)return;setNodeChecked(n,checked);propagateUp(n);renderTree();if(cfg.onChange)cfg.onChange();}
  function renderNode(node,depth){
    const el=document.createElement('div');el.className='tree-node';
    const hasChildren=node.children&&node.children.length>0;
    const row=document.createElement('div');row.className='tree-row';row.style.paddingLeft=(depth*18+8)+'px';
    const arrow=document.createElement('span');
    if(hasChildren){arrow.className='tree-arrow'+(node.expanded?' open':'');arrow.onclick=(e)=>{e.stopPropagation();toggleNode(node.id);};}
    else{arrow.className='tree-spacer';}
    const cb=document.createElement('input');cb.type='checkbox';cb.className='tree-cb';cb.checked=node.checked;cb.indeterminate=node.indeterminate;
    cb.onchange=(e)=>{e.stopPropagation();onNodeCheck(node.id,e.target.checked);};
    const label=document.createElement('span');label.className='tree-label'+(node.match?' tree-match':'');label.textContent=node.label;
    row.appendChild(arrow);row.appendChild(cb);row.appendChild(label);
    row.onclick=(e)=>{if(e.target.tagName!=='INPUT'&&e.target.className.indexOf('tree-arrow')===-1){cb.click();}};
    el.appendChild(row);
    if(hasChildren&&node.expanded){const wrap=document.createElement('div');wrap.className='tree-children';node.children.forEach(c=>wrap.appendChild(renderNode(c,depth+1)));el.appendChild(wrap);}
    return el;
  }
  function updateTreeCount(){
    const total=cfg.getAvailable().length;
    const checked=getCheckedStoreNames().length;
    const cnt=$(cfg.count); if(cnt) cnt.textContent='已选 '+checked+' / '+total+' 家门店';
    const trig=$(cfg.trigTxt);
    if(trig){
      const names=getCheckedStoreNames();
      if(checked===0) trig.textContent='⌕ 未选门店';
      else if(checked===total) trig.textContent='⌕ 全部门店（'+total+' 家）';
      else if(checked<=2) trig.textContent='⌕ '+names.join('、');
      else trig.textContent='⌕ 已选 '+checked+' 家：'+names.slice(0,2).join('、')+'…';
    }
  }
  function renderTree(){const box=$(cfg.box);box.innerHTML='';treeData.forEach(n=>box.appendChild(renderNode(n,0)));updateTreeCount();}
  function build(){
    const stores=cfg.getAvailable();
    const prev=getCheckedStoreNames();
    const map={};
    stores.forEach(s=>{
      const prov=CITY_TO_PROV[s.city]||'其他';
      if(!map[prov])map[prov]={type:'province',id:prov,label:prov,expanded:true,children:{},parent:null};
      if(!map[prov].children[s.city])map[prov].children[s.city]={type:'city',id:s.city,label:s.city,expanded:true,children:{},parent:map[prov]};
      map[prov].children[s.city].children[s.name]={type:'store',id:s.name,label:s.name,expanded:false,store:s,parent:map[prov].children[s.city]};
    });
    treeData=PROVINCE_ORDER.filter(p=>map[p]).concat(Object.keys(map).filter(p=>!PROVINCE_ORDER.includes(p)).sort()).map(prov=>{
      const pnode=map[prov];
      pnode.children=Object.keys(pnode.children).sort().map(city=>{const cnode=pnode.children[city];cnode.children=Object.keys(cnode.children).sort().map(name=>cnode.children[name]);return cnode;});
      return pnode;
    });
    const checkedSet=new Set(prev.filter(n=>stores.some(s=>s.name===n)));
    if(checkedSet.size===0&&stores.length>0)stores.forEach(s=>checkedSet.add(s.name));
    treeData.forEach(p=>{p.children.forEach(c=>{c.children.forEach(st=>{st.checked=checkedSet.has(st.id);});updateNodeFromChildren(c);});updateNodeFromChildren(p);});
  }
  function onSearch(q){
    const lower=q.trim().toLowerCase();
    function mark(ns){ns.forEach(n=>{let cm=false;if(n.children)cm=mark(n.children);n.match=lower!==''&&n.label.toLowerCase().includes(lower);if(cm)n.expanded=true;});return lower===''?false:ns.some(n=>n.match||(n.children&&n.children.some(c=>c.match||(c.children&&c.children.some(st=>st.match)))));}
    mark(treeData);
    if(lower!=='')treeData.forEach(p=>p.expanded=true);
    renderTree();
  }
  function toggle(){const p=$(cfg.panel);if(p)p.classList.toggle('open');}
  function expandAll(){function exp(ns){ns.forEach(n=>{if(n.type!=='store')n.expanded=true;if(n.children)exp(n.children);});}exp(treeData);renderTree();}
  function collapseAll(){function col(ns){ns.forEach(n=>{if(n.type!=='store')n.expanded=false;if(n.children)col(n.children);});}col(treeData);renderTree();}
  function checkAll(){treeData.forEach(p=>setNodeChecked(p,true));renderTree();if(cfg.onChange)cfg.onChange();}
  function clearAll(){treeData.forEach(p=>setNodeChecked(p,false));renderTree();if(cfg.onChange)cfg.onChange();}
  return {build,render:renderTree,getChecked:getCheckedStoreNames,toggle,onSearch,expandAll,collapseAll,checkAll,clearAll};
}
function makeCityTree(cfg){
  const $=id=>document.getElementById(id);
  let treeData=[];
  function getCities(){return cfg.getCities();}
  function recomputeProv(p){
    const all=p.children.length>0&&p.children.every(c=>c.checked);
    const some=p.children.some(c=>c.checked);
    p.indeterminate=some&&!all;
    p.checked=all;
  }
  function onNodeCheck(node,checked){
    if(node.kind==='province'){node.children.forEach(c=>c.checked=checked);}
    else{node.checked=checked;}
    treeData.forEach(recomputeProv);
    renderTree();
    if(cfg.onChange)cfg.onChange();
  }
  function renderNode(node,depth){
    const el=document.createElement('div');el.className='tree-node';
    const row=document.createElement('div');row.className='tree-row';row.style.paddingLeft=(depth*18+8)+'px';
    const arrow=document.createElement('span');
    if(node.kind==='province'){arrow.className='tree-arrow'+(node.expanded?' open':'');arrow.onclick=(e)=>{e.stopPropagation();node.expanded=!node.expanded;renderTree();};}
    else{arrow.className='tree-spacer';}
    const cb=document.createElement('input');cb.type='checkbox';cb.className='tree-cb';cb.checked=node.checked;cb.indeterminate=node.indeterminate;
    cb.onchange=(e)=>{e.stopPropagation();onNodeCheck(node,e.target.checked);};
    const label=document.createElement('span');label.className='tree-label';label.textContent=node.label;
    row.appendChild(arrow);row.appendChild(cb);row.appendChild(label);
    row.onclick=(e)=>{if(e.target.tagName!=='INPUT'&&e.target.className.indexOf('tree-arrow')===-1){cb.click();}};
    el.appendChild(row);
    if(node.kind==='province'&&node.expanded){
      const wrap=document.createElement('div');wrap.className='tree-children';
      node.children.forEach(c=>wrap.appendChild(renderNode(c,depth+1)));
      el.appendChild(wrap);
    }
    return el;
  }
  function updateCount(){
    const total=getCities().length;
    const checked=getChecked().length;
    const cnt=$(cfg.count); if(cnt) cnt.textContent='共 '+total+' 个城市';
    const trig=$(cfg.trigger); if(trig) trig.textContent=(checked===0||checked===total)?'全部城市':trigLabel(getChecked(),'全部城市','城');
  }
  function renderTree(){const box=$(cfg.box);box.innerHTML='';treeData.forEach(n=>box.appendChild(renderNode(n,0)));updateCount();}
  function rebuild(){
    const cities=getCities();
    const prevSet=new Set(getChecked());
    const map={};
    cities.forEach(c=>{
      const p=CITY_TO_PROV[c]||'其他';
      if(!map[p])map[p]={kind:'province',id:p,label:p,expanded:true,checked:false,indeterminate:false,children:[]};
      map[p].children.push({kind:'city',id:c,label:c,checked:prevSet.has(c)});
    });
    treeData=Object.keys(map).sort((a,b)=>{
      const ia=PROVINCE_ORDER.indexOf(a), ib=PROVINCE_ORDER.indexOf(b);
      return (ia<0?99:ia)-(ib<0?99:ib);
    }).map(p=>{
      map[p].children.sort((a,b)=>a.label.localeCompare(b.label));
      return map[p];
    });
    treeData.forEach(recomputeProv);
    renderTree();
  }
  function getChecked(){const out=[];treeData.forEach(p=>p.children.forEach(c=>{if(c.checked)out.push(c.id);}));return out;}
  function checkAll(){treeData.forEach(p=>onNodeCheck(p,true));}
  function clear(){treeData.forEach(p=>onNodeCheck(p,false));}
  function toggle(){const p=$(cfg.panel);if(p)p.classList.toggle('open');}
  return {rebuild,getChecked,clear,checkAll,toggle};
}
// ---- 通用平面多选下拉（区域/督导/平台）----
function makeCheckTree(cfg){
  const $=id=>document.getElementById(id);
  let options=[];
  let checkedSet=new Set();
  function renderOptions(){
    const box=$(cfg.box);
    box.innerHTML='';
    if(options.length===0){box.innerHTML='<div class="tree-empty">暂无可选项</div>';updateTrigger();return;}
    options.forEach(op=>{
      const row=document.createElement('div');row.className='tree-row';
      const cb=document.createElement('input');cb.type='checkbox';cb.className='tree-cb';cb.checked=checkedSet.has(op.value);
      cb.onchange=()=>{if(cb.checked)checkedSet.add(op.value);else checkedSet.delete(op.value);renderOptions();if(cfg.onChange)cfg.onChange();};
      const label=document.createElement('span');label.className='tree-label';label.textContent=op.label;
      row.appendChild(cb);row.appendChild(label);
      row.onclick=(e)=>{if(e.target.tagName!=='INPUT')cb.click();};
      box.appendChild(row);
    });
    updateTrigger();
  }
  function updateTrigger(){
    const n=checkedSet.size;
    const labels=options.filter(o=>checkedSet.has(o.value)).map(o=>o.label);
    const trig=$(cfg.trigger);
    if(trig) trig.textContent = (n===0 || n===options.length) ? cfg.allText : trigLabel(labels,cfg.allText,'项');
    const cnt=$(cfg.count); if(cnt) cnt.textContent='共 '+options.length+' 项';
  }
  function rebuild(arr,checked){
    options=arr.map(x=>typeof x==='string'?{value:x,label:x}:{value:x.value,label:x.label});
    const valid=new Set(options.map(o=>o.value));
    if(checked!==undefined) checkedSet=new Set(checked.filter(v=>valid.has(v)));
    else checkedSet=new Set([...checkedSet].filter(v=>valid.has(v)));
    renderOptions();
  }
  function getChecked(){return [...checkedSet];}
  function checkAll(){options.forEach(o=>checkedSet.add(o.value));renderOptions();if(cfg.onChange)cfg.onChange();}
  function clear(){checkedSet.clear();renderOptions();if(cfg.onChange)cfg.onChange();}
  function toggle(){const p=$(cfg.panel);if(p)p.classList.toggle('open');}
  return {rebuild,getChecked,clear,checkAll,toggle};
}
const REGION_OPTS=DATA.region_summary.map(r=>r.name).filter(n=>n!=='All_Regions').map(n=>({value:n,label:n}));
const PLATFORM_OPTS=[{value:'渠道A',label:'渠道A'},{value:'渠道B',label:'渠道B'}];
const b3RegTree=makeCheckTree({box:'b3regionBox',count:'b3regionCount',trigger:'b3regionTriggerTxt',panel:'b3regionPanel',allText:'全部区域',onChange:()=>{b3CityTree.rebuild();renderBottom3();}});
const v2RegTree=makeCheckTree({box:'v2regionBox',count:'v2regionCount',trigger:'v2regionTriggerTxt',panel:'v2regionPanel',allText:'全部区域',onChange:()=>{fillSups();v2CityTree.rebuild();v2Tree.build();v2Tree.render();renderStore();}});
const v2SupTree=makeCheckTree({box:'v2supBox',count:'v2supCount',trigger:'v2supTriggerTxt',panel:'v2supPanel',allText:'全部督导',onChange:()=>{v2CityTree.rebuild();v2Tree.build();v2Tree.render();renderStore();}});
const v2PlatTree=makeCheckTree({box:'v2platformBox',count:'v2platformCount',trigger:'v2platformTriggerTxt',panel:'v2platformPanel',allText:'全部渠道',onChange:()=>{fillMetrics();renderStore();}});
const v3RegTree=makeCheckTree({box:'v3regionBox',count:'v3regionCount',trigger:'v3regionTriggerTxt',panel:'v3regionPanel',allText:'全部区域',onChange:()=>{fillV3Sups();v3Tree.build();v3Tree.render();renderSup();}});
const v3SupTree=makeCheckTree({box:'v3supBox',count:'v3supCount',trigger:'v3supTriggerTxt',panel:'v3supPanel',allText:'全部督导',onChange:()=>{v3Tree.build();v3Tree.render();renderSup();}});
const b3CityTree=makeCityTree({
  box:'b3cityBox',count:'b3cityCount',trigger:'b3cityTriggerTxt',panel:'b3cityPanel',
  getCities:()=>{
    const regs=b3RegTree.getChecked();
    return [...new Set(DATA.stores.filter(s=>s.status==='营业中'&&(regs.length===0||regs.includes(s.region))).map(s=>s.city))].sort();
  },
  onChange:renderBottom3
});
const v2CityTree=makeCityTree({
  box:'v2cityBox',count:'v2cityCount',trigger:'v2cityTriggerTxt',panel:'v2cityPanel',
  getCities:()=>{
    const regs=v2RegTree.getChecked();
    const sups=v2SupTree.getChecked();
    return [...new Set(DATA.stores.filter(s=>s.status==='营业中' && (regs.length===0||regs.includes(s.region)) && (sups.length===0||sups.includes(s.supervisor))).map(s=>s.city))].sort();
  },
  onChange:()=>{v2Tree.build(); v2Tree.render(); renderStore();}
});
function getV2AvailableStores(){
  const regs=v2RegTree.getChecked();
  const sups=v2SupTree.getChecked();
  const cities=v2CityTree.getChecked();
  return DATA.stores.filter(s=>s.status==='营业中' && (regs.length===0||regs.includes(s.region)) && (sups.length===0||sups.includes(s.supervisor)) && (cities.length===0||cities.includes(s.city)));
}
function getV3AvailableStores(){
  const regs=v3RegTree.getChecked();
  const sups=v3SupTree.getChecked();
  return DATA.stores.filter(s=>s.status==='营业中' && (regs.length===0||regs.includes(s.region)) && (sups.length===0||sups.includes(s.supervisor)));
}
const v2Tree=makeStoreTree({box:'treeBox',count:'treeCount',trigTxt:'treeTriggerTxt',panel:'treePanel',getAvailable:getV2AvailableStores,onChange:renderStore});
const v3Tree=makeStoreTree({box:'v3treeBox',count:'v3treeCount',trigTxt:'v3treeTriggerTxt',panel:'v3treePanel',getAvailable:getV3AvailableStores,onChange:renderSup});

function closeTreeOutside(e){
  const panels=document.querySelectorAll('.tree-panel.open');
  panels.forEach(p=>{
    const t=p.previousElementSibling;
    if(!p.contains(e.target) && !(t&&t.contains(e.target))) p.classList.remove('open');
  });
}
function closeTreePanelsExcept(keep){
  document.querySelectorAll('.tree-panel.open').forEach(p=>{if(p!==keep)p.classList.remove('open');});
}
function fillSups(){
  const regs=v2RegTree.getChecked();
  const sups=[...new Set(DATA.supervisor_summary.filter(s=>regs.length===0||regs.includes(s.region)).map(s=>s.name))].sort();
  v2SupTree.rebuild(sups.map(x=>({value:x,label:x})));
}
function getMetricPool(){
  const plats=v2PlatTree.getChecked();
  if(plats.length===0) return ALL_M.slice();
  return [...new Set(plats.flatMap(p=>PLATFORMS[p]||[]))];
}
function metricGroups(pool){
  const groups=[];
  const mt=PLATFORMS['渠道A'].filter(m=>pool.includes(m));
  if(mt.length){
    groups.push({label:'渠道A',items:mt.map(m=>[m,METRICS[m].name])});
  }
  const sg=PLATFORMS['渠道B'].filter(m=>pool.includes(m));
  if(sg.length){
    groups.push({label:'渠道B',items:sg.map(m=>[m,METRICS[m].name])});
  }
  return groups;
}
let v2SelMets=[];
let v2ShowSub=false; // 渠道A商家评分（综合）表头点击展开/收起 5 项二级指标
function fillMetrics(){
  const pool=getMetricPool();
  v2ShowSub=false; // 切换平台时收起明细
  // 保留仍属于当前平台 pool 的已选指标；若清空则默认选第一个
  v2SelMets=v2SelMets.filter(m=>pool.includes(m));
  if(v2SelMets.length===0 && pool.length) v2SelMets=[pool[0]];
  renderMetricBox();
  updateMetricTrigger();
}
function renderMetricBox(){
  const pool=getMetricPool();
  const groups=metricGroups(pool);
  const box=document.getElementById('metricBox');
  box.innerHTML='';
  groups.forEach(g=>{
    const gh=document.createElement('div');
    gh.className='tree-group';
    gh.textContent=g.label;
    box.appendChild(gh);
    g.items.forEach(([mk,name])=>{
      const row=document.createElement('div');
      row.className='tree-row metric-row'+(v2SelMets.includes(mk)?' tree-sel':'');
      const cb=document.createElement('input');
      cb.type='checkbox'; cb.className='tree-cb'; cb.checked=v2SelMets.includes(mk);
      cb.onchange=(e)=>{
        e.stopPropagation();
        v2ShowSub=false; // 重新选择指标时收起明细
        if(e.target.checked){ if(!v2SelMets.includes(mk)) v2SelMets.push(mk); }
        else { v2SelMets=v2SelMets.filter(x=>x!==mk); }
        // 按 pool 顺序保持选中顺序（首个=主排序指标）
        v2SelMets=v2SelMets.slice().sort((a,b)=>pool.indexOf(a)-pool.indexOf(b));
        if(v2SelMets.length===0){ v2SelMets=[mk]; cb.checked=true; } // 至少保留一项
        renderMetricBox(); updateMetricTrigger(); renderStore();
      };
      const label=document.createElement('span');
      label.className='tree-label'; label.textContent=name;
      row.appendChild(cb); row.appendChild(label);
      row.onclick=(e)=>{ if(e.target.tagName!=='INPUT') cb.click(); };
      box.appendChild(row);
    });
  });
}
function updateMetricTrigger(){
  const cnt=document.getElementById('metricCount');
  const txt=document.getElementById('metricTriggerTxt');
  cnt.textContent='已选 '+v2SelMets.length+' 项';
  if(v2SelMets.length===0){ txt.textContent='请选择指标'; return; }
  txt.textContent=trigLabel(v2SelMets.map(m=>METRICS[m].name),'请选择指标','项指标');
}
function getFiltered(mets){
  const regs=v2RegTree.getChecked();
  const sups=v2SupTree.getChecked();
  const cities=v2CityTree.getChecked();
  const checked=v2Tree.getChecked();
  return DATA.stores.filter(s=>
    s.status==='营业中' &&
    (regs.length===0||regs.includes(s.region)) &&
    (sups.length===0||sups.includes(s.supervisor)) &&
    (cities.length===0||cities.includes(s.city)) &&
    checked.includes(s.name) &&
    mets.every(m=>s.metrics[m].cur!==null)
  );
}
function storeDetailRows(arr,mets){
  const primary=mets[0];
  const allSub=SUB_OF[primary]||[];
  const canExpand=allSub.length>0;
  const showSub=(canExpand && v2ShowSub);
  const subCols=showSub?allSub.filter(m=>!mets.includes(m)):[];
  let h='<table class="tbl"><thead><tr><th>#</th><th>督导</th><th>城市</th><th>门店</th>';
  mets.forEach((m,mi)=>{
    let thAttr=''; let arrow='';
    if(mi===0 && canExpand){
      thAttr=' style="cursor:pointer" title="点击展开/收起 6 项明细指标" data-v2sub="toggle"';
      arrow=' <span class="sort-acc">'+(showSub?'▾':'▸')+'</span>';
    } else if(mi===0){
      arrow=' <span class="sort-acc">↓</span>';
    }
    h+='<th'+thAttr+'>'+METRICS[m].name+helpIcon(m)+arrow+'</th>';
    if(mi===0 && subCols.length){
      subCols.forEach(s=>h+='<th>'+METRICS[s].name+helpIcon(s)+'</th>');
    }
  });
  h+='</tr></thead><tbody>';
  arr.forEach((s,idx)=>{
    h+='<tr><td>'+String(idx+1).padStart(2,'0')+'</td><td class="txt">'+s.supervisor+'</td><td class="txt">'+s.city+'</td><td class="txt">'+s.name+'</td>';
    mets.forEach((m,mi)=>{
      const cur=s.metrics[m].cur;
      const warn=isWarn(m,cur)?' class="warn"':'';
      h+='<td'+warn+'><span class="num">'+fmt(m,cur)+'</span><br>'+dtext(m,s.metrics[m].delta)+'</td>';
      if(mi===0 && subCols.length){
        subCols.forEach(su=>{const w=isWarn(su,s.metrics[su].cur)?' class="warn"':'';h+='<td'+w+'><span class="num">'+fmt(su,s.metrics[su].cur)+'</span><br>'+dtext(su,s.metrics[su].delta)+'</td>';});
      }
    });
    h+='</tr>';
  });
  return h+'</tbody></table>';
}
function v2ToggleSub(){ v2ShowSub=!v2ShowSub; renderStore(); }
function renderStore(){
  if(v2SelMets.length===0){
    document.getElementById('storeView').innerHTML='<div style="color:var(--sub);padding:10px 0">请在「指标」下拉中至少勾选一个指标。</div>';
    return;
  }
  const mk=v2SelMets[0];
  if(!SUB_OF[mk]) v2ShowSub=false;
  const filtered=getFiltered(v2SelMets);
  if(filtered.length===0){
    document.getElementById('storeView').innerHTML='<div style="color:var(--sub);padding:10px 0">当前筛选条件下无匹配门店，请调整筛选或至少勾选一家门店。</div>';
    return;
  }
  document.getElementById('storeView').innerHTML=storeDetailRows(filtered,v2SelMets);
}

// ---- 视图3 ----
function fillV3Sups(){
  const regs=v3RegTree.getChecked();
  const sups=[...new Set(DATA.supervisor_summary.filter(s=>regs.length===0||regs.includes(s.region)).map(s=>s.name))].sort();
  v3SupTree.rebuild(sups.map(x=>({value:x,label:x})));
}
// 预警判定（视图1 KPI 卡、视图2 门店明细、视图3 督导表 / 门店明细共用）：返回该单元格是否未达标
// 注意：pct 类指标底层存的是小数（0.92=92%），阈值需用小数：90%=0.9、0.3%=0.003
// ① 5 分制”绝对分“（评分 / 商品质量分 / 服务体验分 / 满意度）：低于 4.5（满分 5 分的 90% 线）
// ② 排名折算类得分（复购率指标得分 / 食品安全负反馈率 / 消息回复率得分 / 服务负反馈率）：
//     这些分由平台按名次区间折算（0.1 分递减），分布天然偏低（同期中位数 3.8~4.4），绝对分数线会把大多数门店染红，
//     因此改用相对线：低于同期同渠道组合分布的后 10% 分位（P10）
// ③ 商责取消率：高于 0.3%（0.003）
const WARN_ABS45=['mt_score','mt_quality','mt_service','sg_score','sg_quality','sg_service','mt_goods_sat','mt_pack_sat','sg_taste_sat','sg_pack_sat'];
const WARN_RANK=['mt_repeat_score','mt_food_safe','mt_reply_score','mt_service_fb','sg_repeat_score','sg_food_safe','sg_reply_score','sg_service_fb'];
const WARN_RANK_PCT=0.10;   // 排名折算类的预警线：同组合后 10%
let _warnThr={};
function rankWarnThr(mk){
  const key=CUR_PERIOD+'|'+mk;
  if(Object.prototype.hasOwnProperty.call(_warnThr,key)) return _warnThr[key];
  const vals=DATA.stores.filter(s=>s.status==='营业中'&&s.metrics[mk]&&s.metrics[mk].cur!==null).map(s=>s.metrics[mk].cur).sort((a,b)=>a-b);
  let t=null;
  if(vals.length) t=vals[Math.max(0,Math.ceil(WARN_RANK_PCT*vals.length)-1)];
  _warnThr[key]=t;
  return t;
}
function isWarn(mk,cur){
  if(cur===null || cur===undefined) return false;
  if(mk==='sg_cancel') return cur>0.003;
  if(WARN_ABS45.indexOf(mk)>=0) return cur<4.5;
  if(WARN_RANK.indexOf(mk)>=0){ const t=rankWarnThr(mk); return t!==null && cur<=t; }
  return false;
}

function renderSup(){
  const regs=v3RegTree.getChecked();
  const supsSel=v3SupTree.getChecked();
  let sups=DATA.supervisor_summary.filter(s=>(regs.length===0||regs.includes(s.region)) && (supsSel.length===0||supsSel.includes(s.name)));
  const lastMt=V3_MT_ORDER.map(mk=>METRICS[mk].ch==='渠道A').lastIndexOf(true);
  let html='<div style="overflow-x:auto"><table class="tbl"><thead>'+
    '<tr><th rowspan="2">督导</th><th rowspan="2">区域</th><th colspan="'+V3_MT_ORDER.length+'" class="group-mt">渠道A</th><th colspan="'+V3_SG_ORDER.length+'" class="group-sg">渠道B</th></tr>'+
    '<tr>';
  V3_MT_ORDER.forEach((mk,i)=>{html+='<th class="mt-col'+(i===lastMt?' mt-last':'')+'">'+V3_MT_HEADERS[i]+helpIcon(mk)+'</th>';});
  V3_SG_ORDER.forEach((mk,i)=>{html+='<th class="sg-col">'+V3_SG_HEADERS[i]+helpIcon(mk)+'</th>';});
  html+='</tr></thead><tbody>';
  sups.forEach(s=>{
    html+='<tr><td class="txt"><b>'+s.name+'</b></td><td class="txt">'+s.region+'</td>';
    V3_MT_ORDER.forEach((mk,i)=>{const mm=s.metrics[mk];const cls=[isWarn(mk,mm.cur)?'warn':'',i===lastMt?'mt-last':''].filter(Boolean).join(' ');html+='<td'+(cls?' class="'+cls+'"':'')+'><span class="num">'+fmt(mk,mm.cur)+'</span><br>'+dtext(mk,mm.delta)+'</td>';});
    V3_SG_ORDER.forEach(mk=>{const mm=s.metrics[mk];const w=isWarn(mk,mm.cur)?' warn':'';html+='<td'+(w?' class="'+w.trim()+'"':'')+'><span class="num">'+fmt(mk,mm.cur)+'</span><br>'+dtext(mk,mm.delta)+'</td>';});
    html+='</tr>';
  });
  html+='</tbody></table></div>';
  document.getElementById('supTable').innerHTML=html;
  // 门店明细表（选中督导后展示其下属门店，受门店树筛选控制）
  const stPanel=document.getElementById('supStoreTable');
  if(supsSel.length===0){ stPanel.style.display='none'; stPanel.innerHTML=''; return; }
  const checked=v3Tree.getChecked();
  let stores=DATA.stores.filter(s=>supsSel.includes(s.supervisor) && s.status==='营业中' && checked.includes(s.name));
  if(stores.length===0){ stPanel.style.display='block'; stPanel.innerHTML='<div style="color:var(--sub);padding:10px 0">所选督导下未勾选门店，请在「门店」下拉中勾选</div>'; return; }
  let sh='<h3>'+supsSel.join('、')+' · 门店明细（'+stores.length+' 家）</h3><div style="overflow-x:auto"><table class="tbl"><thead>'+
    '<tr><th rowspan="2">门店</th><th colspan="'+V3_MT_ORDER.length+'" class="group-mt">渠道A</th><th colspan="'+V3_SG_ORDER.length+'" class="group-sg">渠道B</th></tr>'+
    '<tr>';
  const lastMtS=V3_MT_ORDER.map(mk=>METRICS[mk].ch==='渠道A').lastIndexOf(true);
  V3_MT_ORDER.forEach((mk,i)=>sh+='<th class="mt-col'+(i===lastMtS?' mt-last':'')+'">'+V3_MT_HEADERS[i]+helpIcon(mk)+'</th>');
  V3_SG_ORDER.forEach((mk,i)=>sh+='<th class="sg-col">'+V3_SG_HEADERS[i]+helpIcon(mk)+'</th>');
  sh+='</tr></thead><tbody>';
  stores.forEach(s=>{
    sh+='<tr><td class="txt"><b>'+s.name+'</b></td>';
    V3_MT_ORDER.forEach((mk,i)=>{const mm=s.metrics[mk];const cls=[isWarn(mk,mm.cur)?'warn':'',i===lastMtS?'mt-last':''].filter(Boolean).join(' ');sh+='<td'+(cls?' class="'+cls+'"':'')+'><span class="num">'+fmt(mk,mm.cur)+'</span><br>'+dtext(mk,mm.delta)+'</td>';});
    V3_SG_ORDER.forEach(mk=>{const mm=s.metrics[mk];const w=isWarn(mk,mm.cur)?' warn':'';sh+='<td'+(w?' class="'+w.trim()+'"':'')+'><span class="num">'+fmt(mk,mm.cur)+'</span><br>'+dtext(mk,mm.delta)+'</td>';});
    sh+='</tr>';
  });
  sh+='</tbody></table></div>';
  stPanel.style.display='block';
  stPanel.innerHTML=sh;
}

// ---- init ----
function applyPeriod(){
  const p=document.getElementById('periodSel').value;
  if(!PERIODS[p]||p===CUR_PERIOD) return;
  DATA=PERIODS[p];
  CUR_PERIOD=p;
  try{localStorage.setItem('operations_demo_period',p);}catch(e){}
  document.getElementById('hdrMeta').innerHTML='数据周期：'+DATA.meta.period+'<span class="dot">|</span>上一周期：'+DATA.meta.prevPeriod+'<span class="dot">|</span>营业中门店：'+DATA.meta.openTotal+' 家';
  document.getElementById('ftr').textContent='数据源：'+(DATA.meta.dataSource||'合成演示数据')+'（区域汇总 / 督导维度 / 门店维度）　·　固定种子可复现';
  b3RegTree.rebuild(REGION_OPTS,REGION_OPTS.length?[REGION_OPTS[0].value]:[]); b3CityTree.rebuild();
  v2RegTree.rebuild(REGION_OPTS,[]); v2PlatTree.rebuild(PLATFORM_OPTS,[]); v2SupTree.rebuild([],[]); fillSups(); v2CityTree.rebuild();
  v3RegTree.rebuild(REGION_OPTS,[]); v3SupTree.rebuild([],[]); fillV3Sups();
  fillMetrics();
  v1RegionIdx=0;
  renderRegion(); renderBottom3();
  v2Tree.build(); v2Tree.render(); renderStore();
  v3Tree.build(); v3Tree.render(); renderSup();
}

function init(){
  document.getElementById('hdrMeta').innerHTML='数据周期：'+DATA.meta.period+'<span class="dot">|</span>上一周期：'+DATA.meta.prevPeriod+'<span class="dot">|</span>营业中门店：'+DATA.meta.openTotal+' 家';
  document.getElementById('ftr').textContent='数据源：'+(DATA.meta.dataSource||'合成演示数据')+'（区域汇总 / 督导维度 / 门店维度）　·　固定种子可复现';
  // 数据周期切换
  const periodSel=document.getElementById('periodSel');
  periodSel.innerHTML=PERIOD_ORDER.map(function(p){
    return opt(p, PERIODS[p].meta.period);
  }).join('');
  periodSel.value=CUR_PERIOD;
  periodSel.onchange=applyPeriod;
  // tabs
  document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{
    document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.sec').forEach(x=>x.classList.remove('active'));
    b.classList.add('active'); document.getElementById(b.dataset.v).classList.add('active');
  });
  // 视图1 区域 / 城市 多选
  b3RegTree.rebuild(REGION_OPTS,REGION_OPTS.length?[REGION_OPTS[0].value]:[]);
  b3CityTree.rebuild();
  document.getElementById('b3regionTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('b3regionPanel'));b3RegTree.toggle();};
  document.getElementById('b3regionCheckAll').onclick=()=>b3RegTree.checkAll();
  document.getElementById('b3regionClear').onclick=()=>b3RegTree.clear();
  const b3rp=document.getElementById('b3regionPanel'); if(b3rp) b3rp.onclick=(e)=>e.stopPropagation();
  document.getElementById('b3cityTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('b3cityPanel'));b3CityTree.toggle();};
  document.getElementById('b3cityCheckAll').onclick=()=>b3CityTree.checkAll();
  document.getElementById('b3cityClear').onclick=()=>b3CityTree.clear();
  const b3cp=document.getElementById('b3cityPanel'); if(b3cp) b3cp.onclick=(e)=>e.stopPropagation();
  // 视图2 区域 / 督导 / 平台 / 城市 多选
  v2RegTree.rebuild(REGION_OPTS,[]);
  v2PlatTree.rebuild(PLATFORM_OPTS,[]);
  v2SupTree.rebuild([],[]);
  fillSups();
  v2CityTree.rebuild();
  document.getElementById('v2regionTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('v2regionPanel'));v2RegTree.toggle();};
  document.getElementById('v2regionCheckAll').onclick=()=>v2RegTree.checkAll();
  document.getElementById('v2regionClear').onclick=()=>v2RegTree.clear();
  const v2rp=document.getElementById('v2regionPanel'); if(v2rp) v2rp.onclick=(e)=>e.stopPropagation();
  document.getElementById('v2supTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('v2supPanel'));v2SupTree.toggle();};
  document.getElementById('v2supCheckAll').onclick=()=>v2SupTree.checkAll();
  document.getElementById('v2supClear').onclick=()=>v2SupTree.clear();
  const v2sp=document.getElementById('v2supPanel'); if(v2sp) v2sp.onclick=(e)=>e.stopPropagation();
  document.getElementById('v2platformTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('v2platformPanel'));v2PlatTree.toggle();};
  document.getElementById('v2platformCheckAll').onclick=()=>v2PlatTree.checkAll();
  document.getElementById('v2platformClear').onclick=()=>v2PlatTree.clear();
  const v2pp=document.getElementById('v2platformPanel'); if(v2pp) v2pp.onclick=(e)=>e.stopPropagation();
  document.getElementById('v2cityTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('v2cityPanel'));v2CityTree.toggle();};
  document.getElementById('v2cityCheckAll').onclick=()=>v2CityTree.checkAll();
  document.getElementById('v2cityClear').onclick=()=>v2CityTree.clear();
  const v2cp=document.getElementById('v2cityPanel'); if(v2cp) v2cp.onclick=(e)=>e.stopPropagation();
  // 视图2 指标多选面板
  document.getElementById('metricTrigger').onclick=(e)=>{e.stopPropagation();
    const mp=document.getElementById('metricPanel');
    closeTreePanelsExcept(mp);
    mp.classList.toggle('open');
  };
  const metricPanel=document.getElementById('metricPanel');
  if(metricPanel) metricPanel.onclick=(e)=>e.stopPropagation();
  document.getElementById('metricAll').onclick=()=>{
    const pool=getMetricPool();
    v2ShowSub=false;
    v2SelMets=pool.slice().sort((a,b)=>pool.indexOf(a)-pool.indexOf(b));
    renderMetricBox(); updateMetricTrigger(); renderStore();
  };
  document.getElementById('metricClear').onclick=()=>{
    v2ShowSub=false;
    v2SelMets=[];
    renderMetricBox(); updateMetricTrigger(); renderStore();
  };
  // 视图2 门店树
  document.getElementById('treeSearch').oninput=(e)=>v2Tree.onSearch(e.target.value);
  document.getElementById('treeExpand').onclick=()=>v2Tree.expandAll();
  document.getElementById('treeCollapse').onclick=()=>v2Tree.collapseAll();
  document.getElementById('treeCheckAll').onclick=()=>v2Tree.checkAll();
  document.getElementById('treeClear').onclick=()=>v2Tree.clearAll();
  document.getElementById('treeTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('treePanel'));v2Tree.toggle();};
  const tp=document.getElementById('treePanel'); if(tp) tp.onclick=(e)=>e.stopPropagation();
  if(document.addEventListener) document.addEventListener('click', closeTreeOutside);
  // 视图2 表头点击展开/收起二级指标（事件委托，兼容动态表格）
  document.addEventListener('click', function(e){
    const th=e.target.closest('th[data-v2sub="toggle"]');
    if(th) v2ToggleSub();
  });
  // 视图3
  v3RegTree.rebuild(REGION_OPTS,[]);
  v3SupTree.rebuild([],[]);
  fillV3Sups();
  document.getElementById('v3regionTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('v3regionPanel'));v3RegTree.toggle();};
  document.getElementById('v3regionCheckAll').onclick=()=>v3RegTree.checkAll();
  document.getElementById('v3regionClear').onclick=()=>v3RegTree.clear();
  const v3rp=document.getElementById('v3regionPanel'); if(v3rp) v3rp.onclick=(e)=>e.stopPropagation();
  document.getElementById('v3supTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('v3supPanel'));v3SupTree.toggle();};
  document.getElementById('v3supCheckAll').onclick=()=>v3SupTree.checkAll();
  document.getElementById('v3supClear').onclick=()=>v3SupTree.clear();
  const v3sp=document.getElementById('v3supPanel'); if(v3sp) v3sp.onclick=(e)=>e.stopPropagation();
  document.getElementById('v3treeSearch').oninput=(e)=>v3Tree.onSearch(e.target.value);
  document.getElementById('v3treeExpand').onclick=()=>v3Tree.expandAll();
  document.getElementById('v3treeCollapse').onclick=()=>v3Tree.collapseAll();
  document.getElementById('v3treeCheckAll').onclick=()=>v3Tree.checkAll();
  document.getElementById('v3treeClear').onclick=()=>v3Tree.clearAll();
  document.getElementById('v3treeTrigger').onclick=(e)=>{e.stopPropagation();closeTreePanelsExcept(document.getElementById('v3treePanel'));v3Tree.toggle();};
  const v3tp=document.getElementById('v3treePanel'); if(v3tp) v3tp.onclick=(e)=>e.stopPropagation();
  // first render
  renderRegion(); renderBottom3(); fillSups(); fillMetrics(); v2Tree.build(); v2Tree.render(); renderStore(); fillV3Sups(); v3Tree.build(); v3Tree.render(); renderSup();
}
init();
</script>
<script>
// ---- 本地实时自动刷新（仅 localhost 服务时生效）----
(function(){
  if(!(location.hostname==='localhost'||location.hostname==='127.0.0.1'))return;
  var lastV=null;
  function loop(){
    fetch('/api/reload?v='+(lastV==null?0:lastV),{cache:'no-store'}).then(function(r){
      return r.ok?r.json():null;
    }).then(function(d){
      if(d){
        if(lastV===null){lastV=d.v;}
        else if(d.v>lastV){location.reload();return;}
      }
      setTimeout(loop,1500);
    }).catch(function(){setTimeout(loop,1500);});
  }
  setTimeout(loop,1500);
})();
</script>
</body>
</html>'''


if __name__ == "__main__":
    main()
