# Deployment Notes

## Build locally

```powershell
python scripts/generate_demo_inputs.py
python build_data.py
python generate_html.py
```

The resulting `dashboard.html` contains CSS, JavaScript and data in one file.

## Netlify

The repository includes `netlify.toml` with a Python build command. Connect a repository and let Netlify run the build. The public directory is generated at build time.

## Cloudflare Pages / Workers

- Build command: `python build_data.py && python generate_html.py`
- Build output directory: `public`
- Copy `dashboard.html` to `public/index.html` during the build.

`wrangler.jsonc` is a generic static-assets example. Replace the project name with your own before deploying.

## Security checklist before publishing

1. Confirm every file in the repository is synthetic or otherwise cleared for public distribution.
2. Keep private source data, credentials, browser profiles and logs outside the repository.
3. Verify Git history as well as the current working tree.
4. Do not add vendor keys to frontend code or static assets.
