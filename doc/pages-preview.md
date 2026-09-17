# Previewing the web interface on GitHub Pages

This describes tooling that exists only on this fork. It is kept out of
[`DEVELOPMENT.md`](../DEVELOPMENT.md) deliberately: that file is maintained upstream, so editing it
would create a merge conflict on every sync. A new file never conflicts.

The canonical deployment of the web interface is Netlify (see [`web/netlify.toml`](../web/netlify.toml)),
which publishes deploy previews for upstream pull requests. A fork cannot use that, so this
publishes an equivalent static preview to GitHub Pages. Only the frontend is published: GitHub
Pages serves static files, so the preview talks to the already-deployed sandbox API rather than to
a locally running backend.

## Per-pull-request previews

Every pull request gets its own preview. The [`preview.yml`](../.github/workflows/preview.yml)
workflow builds `web/` and hands the result to
[`pr-preview-action`](https://github.com/rossjrw/pr-preview-action), which commits it to the
`gh-pages` branch under `pr-preview/pr-<number>/`, comments on the pull request with the link, and
deletes the directory when the pull request is closed. Each preview is therefore served from its
own subpath, and the build uses a matching base path:

```
VITE_BASE_PATH: /<repo>/pr-preview/pr-<number>/
```

The workflow does not run on `dandi/dandi-archive`.

## Enabling it on a fork

Set Settings → Pages → Source to "Deploy from a branch", and select the `gh-pages` branch (the
workflow creates that branch on its first run). This step cannot be automated: the workflow's token
can push to the branch, but configuring Pages requires admin rights it does not have.

## Branch layout

The preview workflow lives on the `master-preview` branch, not on `master`. `master` is kept
identical to `dandi/dandi-archive` so that contributions upstream can be branched from it without
carrying the preview commits. Pull requests must therefore target `master-preview` for a preview to
be built.

## Previewing locally

Because Pages serves a project site from a subpath and has no SPA rewrite rule, the deployed site
differs from `npm run dev` in ways worth checking before pushing. To reproduce it locally:

```
./scripts/pages_preview.py
```

This builds the app with the appropriate base path, adds the `404.html` fallback that lets
`vue-router` resolve deep links, and serves the result the way Pages does, at
http://localhost:8080/dandi-archive/. Pass `--base` to serve from a different subpath — for
instance `--base /dandi-archive/pr-preview/pr-42/` to match exactly where a given pull request's
preview is deployed — and `--no-build` to re-serve an existing build. The API the preview uses can
be overridden by exporting `VITE_APP_DANDI_API_ROOT` (and the other `VITE_APP_*` variables) before
running it.

## Limitations

- Logging in does not work from a Pages origin, since that origin is not a registered OAuth
  redirect URI for the sandbox deployment. The preview is for anonymous browsing of the UI.
- Netlify's redirect rules, plugins and per-context environments have no equivalent here; the
  preview reproduces the static build and nothing else.
