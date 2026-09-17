#!/usr/bin/env python3
"""Build and locally serve the web app exactly as GitHub Pages would serve it.

GitHub Pages hosts a project site under "https://<user>.github.io/<repo>/", not at
a domain root, and it serves only static files. Two things therefore differ from
`npm run dev`, and both are easy to get wrong without a local preview:

* the app must be built with a base path of "/<repo>/";
* deep links (e.g. "/<repo>/dandiset/000004") are served by Pages' 404 page,
  since there is no server-side rewrite to index.html.

This script reproduces both behaviors so a Pages deployment can be verified
before pushing. The backend is not run: the built app talks to an already-deployed
API (the sandbox instance by default), which is all a frontend-only change needs.
"""

from __future__ import annotations

import argparse
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / 'web'
STAGING_DIR = WEB_DIR / '.pages-preview'

# Mirrors the "deploy-preview" context of web/netlify.toml, so the preview points at
# the sandbox deployment rather than production.
SANDBOX_ENV = {
    'VITE_APP_DANDI_API_ROOT': 'https://api.sandbox.dandiarchive.org/api/',
    'VITE_APP_OAUTH_API_ROOT': 'https://api.sandbox.dandiarchive.org/oauth/',
    'VITE_APP_OAUTH_CLIENT_ID': 'Dk0zosgt1GAAKfN8LT4STJmLJXwMDPbYWYzfNtAl',
    'VITE_APP_DOI_SERVER': 'https://api.test.datacite.org/',
}


class PagesRequestHandler(SimpleHTTPRequestHandler):
    """A static file handler that falls back to 404.html, as GitHub Pages does."""

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if not path.exists() and not self.path.rstrip('/').endswith('.html'):
            # Serve the SPA fallback with Pages' status code, letting the client
            # router resolve the route.
            fallback = Path(self.directory) / self.base_path.strip('/') / '404.html'
            if fallback.is_file():
                body = fallback.read_bytes()
                self.send_response(HTTPStatus.NOT_FOUND)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                return None if self.command == 'HEAD' else _BytesReader(body)
        return super().send_head()

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        sys.stderr.write(f'{self.address_string()} - {format % args}\n')


class _BytesReader:
    """Minimal file-like wrapper so send_head can return an in-memory response."""

    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self, amount: int = -1) -> bytes:
        if amount is None or amount < 0:
            data, self._data = self._data, b''
            return data
        data, self._data = self._data[:amount], self._data[amount:]
        return data

    def close(self) -> None:
        self._data = b''


def build(base_path: str, *, install: bool) -> None:
    env = os.environ.copy()
    # Only fill in API settings the caller has not already provided, so a preview can
    # be pointed at a local or production API by exporting these beforehand.
    for key, value in SANDBOX_ENV.items():
        env.setdefault(key, value)
    env['VITE_BASE_PATH'] = base_path

    npm = shutil.which('npm')
    if npm is None:
        raise SystemExit('npm was not found on PATH; install Node.js to build the app.')

    # The command is a fixed npm invocation resolved from PATH, not user input.
    if install:
        subprocess.run([npm, 'ci'], cwd=WEB_DIR, check=True)  # noqa: S603
    subprocess.run([npm, 'run', 'build'], cwd=WEB_DIR, env=env, check=True)  # noqa: S603


def stage(base_path: str) -> Path:
    """Copy the build into a tree whose layout matches the deployed Pages site."""
    dist = WEB_DIR / 'dist'
    if not dist.is_dir():
        raise SystemExit(f'No build found at {dist}; run without --no-build first.')

    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    target = STAGING_DIR / base_path.strip('/')
    shutil.copytree(dist, target)

    # GitHub Pages has no SPA rewrite rule, so a copy of index.html is served as the
    # 404 page to let vue-router handle deep links.
    shutil.copyfile(target / 'index.html', target / '404.html')
    return STAGING_DIR


def serve(root: Path, base_path: str, port: int) -> None:
    PagesRequestHandler.base_path = base_path  # type: ignore[attr-defined]
    handler = partial(PagesRequestHandler, directory=str(root))

    with ThreadingHTTPServer(('localhost', port), handler) as httpd:
        url = f'http://localhost:{port}{base_path}'
        sys.stderr.write(f'\nServing the Pages preview at {url}\nPress Ctrl+C to stop.\n\n')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.stderr.write('\nStopped.\n')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--base',
        default='/dandi-archive/',
        help="Base path the site is served from; must match the fork's repository "
        'name for a GitHub Pages project site (default: %(default)s)',
    )
    parser.add_argument('--port', type=int, default=8080, help='Port to serve on')
    parser.add_argument('--no-build', action='store_true', help='Reuse the existing web/dist build')
    parser.add_argument('--install', action='store_true', help='Run "npm ci" before building')
    args = parser.parse_args()

    base_path = f'/{args.base.strip("/")}/' if args.base.strip('/') else '/'
    if not args.no_build:
        build(base_path, install=args.install)
    root = stage(base_path)
    serve(root, base_path, args.port)


if __name__ == '__main__':
    main()
