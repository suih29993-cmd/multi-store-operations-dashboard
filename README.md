# Multi-store Operations Dashboard

**Live demo:** [https://multi-store-operations-dashboard.pages.dev/](https://multi-store-operations-dashboard.pages.dev/)

[![dashboard-ci](https://github.com/suih29993-cmd/multi-store-operations-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/suih29993-cmd/multi-store-operations-dashboard/actions/workflows/ci.yml)

`Python 3.11+` · `Synthetic data` · `No third-party frontend libraries`

An offline, self-contained operations dashboard for multi-store performance analysis. The public demo keeps the original three-view dashboard layout and interaction model while replacing all business data with deterministic synthetic records.

> **Data notice:** every store, city, supervisor, score and rate in this repository is fictional and generated from a fixed seed. No production dataset, internal report, customer record or company account is required. The numbers are not real business results.

![Desktop dashboard preview](docs/screenshots/dashboard-desktop.png)

<details>
<summary>Mobile preview</summary>

<p align="center">
  <img src="docs/screenshots/dashboard-mobile.png" width="360" alt="Mobile dashboard preview">
</p>
</details>

Screenshots use the committed synthetic dataset.

## Restored dashboard experience

The page follows the original dashboard structure rather than a redesigned template:

- Three views: region overview, supervisor view and store-wide ranking.
- Seven region KPI cards with period-over-period deltas.
- Nine Bottom-5 comparisons with region and city multi-select filters.
- Province/city/store tree filters, channel filters, metric multi-select and expandable sub-metrics.
- Period switcher, metric help tooltips, warning highlights and store drill-down.
- Responsive desktop/tablet/mobile layout without a front-end framework.
- Self-contained HTML: no remote font, script, analytics request or API client.

## Data and analytics

- Three synthetic reporting periods, 60 stores per period, two regions, six cities and eight supervisors.
- Store-level metric derivation for quality score, service score and composite score.
- Region, city and supervisor aggregations calculated from the synthetic store rows.
- Period deltas and threshold highlighting derived from the same validated payload.
- Explicit synthetic labels in the page footer and all documentation.

The CSV source fields use generic `channel_a_*` / `channel_b_*` names. `generate_html.py` maps them to the original UI's metric contract at build time; the browser receives only the transformed synthetic payload.

## Project structure

| File | Purpose |
| --- | --- |
| `scripts/generate_demo_inputs.py` | Deterministic synthetic CSV generator. |
| `build_data.py` | Schema checks, numeric validation, metric derivation, aggregation and `data.json` output. |
| `generate_html.py` | Maps the synthetic payload to the restored original UI contract and renders `dashboard.html`. |
| `dashboard.html` | Self-contained build artifact with inline CSS, JavaScript and synthetic data. |
| `server.py` | Local-only preview server and health endpoint. |
| `tests/test_dashboard.py` | Data-contract and UI-contract tests. |

## Quick start

```powershell
python scripts/generate_demo_inputs.py
python build_data.py
python generate_html.py
python server.py
```

Open `http://127.0.0.1:8000` if the browser does not open automatically. You can also open the included `dashboard.html` directly because the page is self-contained.

The generator is deterministic. Re-running the commands reproduces the same synthetic stores and metrics without any external file or account.

## Validation

```powershell
python scripts/generate_demo_inputs.py
python build_data.py --check
python -m unittest discover -s tests -v
python generate_html.py
python scripts/prepare_static.py
```

## Data model

Each store record contains:

- Fictional identity: `Store_A001` / `Store_B001`, region, province, city, supervisor and store type.
- Two synthetic channel snapshots with satisfaction, repeat, reply, food-safety and cancellation indicators.
- Current value, previous value and period delta for every metric.

Regional, city and supervisor summaries use unweighted arithmetic means of the store-level values. This keeps the demo easy to audit; a production implementation would normally choose weightings explicitly.

## Design and privacy boundaries

- The original page structure, CSS tokens, component hierarchy, responsive rules and interaction behavior are retained.
- Brand text, logo and channel names are neutral placeholders; no company image asset is included.
- The synthetic data generator creates new values from a fixed seed rather than perturbing production records.
- No internal hostname, local path, webhook, token, password or company account is referenced.
- The page makes no external request and the local server binds to `127.0.0.1`.

## Scope and limitations

This repository demonstrates an analytics and visualization workflow, not a production data platform. It does not include authentication, multi-tenant access control, a production database or vendor integrations. The warning thresholds are illustrative examples, not confidential operating rules. All displayed values are synthetic and must not be presented as business performance.

## Deployment

Run `python scripts/prepare_static.py` to assemble a minimal `public/` directory containing only the self-contained dashboard, security headers and `robots.txt`. Cloudflare Pages direct upload is the recommended public demo path; Netlify is a documented fallback. See `docs/DEPLOYMENT.md` for exact steps. No credentials are required for the demo.
