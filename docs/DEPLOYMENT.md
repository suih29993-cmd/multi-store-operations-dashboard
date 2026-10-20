# Deployment Notes

## Public artifact

`dashboard.html` is a self-contained static page: CSS, JavaScript and the synthetic
payload are all inline. Visitors do not need Python, an account or a backend API.

Rebuild and assemble the publishable directory:

```powershell
python scripts/generate_demo_inputs.py
python build_data.py --check
python build_data.py
python generate_html.py
python scripts/prepare_static.py
```

`scripts/prepare_static.py` writes only these files:

- `public/index.html`
- `public/_headers`
- `public/robots.txt`

The script refuses to publish an unresolved data placeholder, a missing
synthetic-data marker, private local path markers, or unexpected files already
present in `public/`. It does not copy `demo_input/`, `data.json`, tests,
screenshots, Python code, Git metadata or any private backup.

Preview the exact artifact locally:

```powershell
cd public
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`.

## Current public deployment

- Pages project: `multi-store-operations-dashboard`
- Production URL: https://multi-store-operations-dashboard.pages.dev/
- Artifact: the generated `public/` build of the committed synthetic dataset
- Deployment mode: direct upload; no Git integration, account email, token or secret is stored in the repository

The production URL was verified with browser automation for the three views, seven KPI cards, nine Bottom-5 rows, filter panels and mobile layout.

## Cloudflare Pages (recommended)

Cloudflare Pages can serve `public/` as a static site without a runtime build.
The free `*.pages.dev` address is public and requires no visitor login.

### Dashboard upload

1. Sign in to the Cloudflare dashboard. This is the only required account step.
2. Open **Workers & Pages**, choose **Create**, then **Pages**, then **Upload assets**.
3. Use the project name `multi-store-operations-dashboard`, or choose another
   available name if that one is already taken.
4. Upload the contents of the local `public/` directory.
5. Deploy and open the generated `https://<project-name>.pages.dev` address.

The `_headers` file is applied by Cloudflare Pages and adds a restrictive CSP,
clickjacking protection, MIME sniffing protection, a no-referrer policy and a
permissions policy. The page itself makes no external requests.

### Wrangler CLI alternative

After signing in and confirming the target account, this command creates or
updates a Pages project:

```powershell
npx wrangler pages deploy public --project-name multi-store-operations-dashboard
```

The first run opens a browser login. This repository does not automate login,
site creation, deployment or domain changes.

## Cloudflare Workers static assets

`wrangler.jsonc` points Worker static assets at `public/`. If you prefer a
Workers URL instead of a Pages URL, deploy after building `public/`:

```powershell
npx wrangler deploy
```

Cloudflare will return a `https://<worker-name>.<account-subdomain>.workers.dev`
address. Cloudflare Pages direct upload remains the simpler option for this
single-page demo and is the recommended default.

## Netlify fallback

The checked-in `netlify.toml` rebuilds the dashboard and runs
`scripts/prepare_static.py`, publishing only `public/`.

- Manual deployment: `npx netlify deploy --prod --dir=public`
- Git deployment: connect the repository in Netlify and let the build command
  run. This requires a repository push and Netlify account authorization.

No Netlify login, site creation or deployment has been performed.

## Security checklist before publishing

1. Confirm every file under `public/` is intended for public distribution.
2. Keep private source data, credentials, browser profiles and logs outside the repository.
3. Verify Git history as well as the current working tree.
4. Confirm the final HTTP response includes the `_headers` security policies.
5. Open the deployed URL in desktop and mobile browsers and check the console,
   filters, multi-select trees, expandable metrics, KPI cards, Bottom-5 and drill-down tables.
