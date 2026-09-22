# Security

## Reporting a vulnerability

Please report security issues privately via GitHub: open a draft advisory
from the [Security tab](https://github.com/pipeboard-co/meta-ads-mcp/security/advisories/new)
("Report a vulnerability"). Do not file public issues for unpatched
vulnerabilities.

## Advisories

### GHSA-45gf-fjxp-cjpq — Server-Side Request Forgery (SSRF) in `upload_ad_image` via unrestricted `image_url` fetch

- **Severity:** High (CVSS 3.1 8.3 — `AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L`)
- **Affected versions:** `<= 1.0.114` when run with `--transport streamable-http`.
- **Fixed in:** `1.0.115`
- **Affected configurations:** Self-hosted deployments that expose the
  streamable-HTTP port on a reachable network interface, especially when
  co-located with internal services or a cloud metadata endpoint. The hosted
  MCP at `*.mcp.pipeboard.co` binds the Python process to localhost behind an
  authenticating proxy, so it was not reachable by unauthenticated callers; the
  fix is still applied there as defense-in-depth.

**What went wrong.** `upload_ad_image` (and the image-viewing tools) passed a
caller-supplied URL straight to an HTTP client (`download_image` /
`try_multiple_download_methods`) with `follow_redirects=True` and no scheme,
host, or IP validation. A caller could supply `http://127.0.0.1/...`, an RFC
1918 address, or `http://169.254.169.254/` (cloud instance metadata) and make
the server issue outbound requests to those targets. On the streamable-HTTP
transport the image fetch ran before Meta credential validation, so any
non-empty bearer token reached the sink.

**Fix.**
1. A new `validate_public_url()` guard restricts fetches to `http`/`https`
   URLs whose host resolves only to public addresses. Private, loopback,
   link-local (incl. `169.254.169.254`), reserved, multicast, and unspecified
   addresses are rejected; IPv4-mapped IPv6 addresses are unwrapped first.
2. An httpx request event hook re-validates every redirect hop, so a public URL
   cannot redirect into a private/internal address.

**Action for operators.**
- Upgrade to `1.0.115` or later.
- If you exposed an earlier version on a reachable interface, review outbound
  request and access logs for unexpected internal fetches, and ensure the cloud
  metadata service is hardened (e.g. IMDSv2 / metadata not reachable from the
  app process).

### GHSA-9gw6-46qc-99vr — Unauthenticated HTTP MCP tool execution leaks operator Meta access token

- **Severity:** Critical (CVSS 3.1 9.1 — `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`)
- **Affected versions:** `<= 1.0.108` when run with `--transport streamable-http`
  and a `META_ACCESS_TOKEN` environment variable.
- **Fixed in:** `1.0.109`
- **Affected configurations:** Self-hosted deployments that expose the
  streamable-HTTP port on a reachable network interface. The hosted MCP at
  `*.mcp.pipeboard.co` was not affected — it sits behind an authenticating
  proxy and the Python process is bound to localhost.

**What went wrong.** `AuthInjectionMiddleware.dispatch()` logged a warning when
a request arrived with no `Authorization: Bearer` / `X-PIPEBOARD-API-TOKEN`
header and then forwarded the request to the tool handler anyway. Tool handlers
fall back to `META_ACCESS_TOKEN` when no per-request token is set, so any
network-reachable caller could invoke any MCP tool as the operator. When the
downstream Graph API call returned a 4xx, `make_api_request()` serialized
`e.request.url` — including `access_token` as a query parameter — verbatim into
the JSON-RPC error payload, exposing the long-lived operator credential.

**Fix.**
1. `AuthInjectionMiddleware` now returns `401 Unauthorized` with
   `WWW-Authenticate: Bearer` when neither token header is present.
2. `make_api_request()` redacts `access_token` and `appsecret_proof` from any
   URLs returned in error payloads (`_redact_url` helper).

**Action for operators.**
- Upgrade to `1.0.109` or later.
- HTTP clients must send `Authorization: Bearer <meta-access-token>` (or the
  legacy `X-PIPEBOARD-API-TOKEN` header) on every request. The
  `META_ACCESS_TOKEN` env var is no longer used as an implicit fallback for
  HTTP transport.
- If you exposed an earlier version to an untrusted network, rotate the Meta
  access token (`https://developers.facebook.com/tools/debug/accesstoken/`)
  and review Graph API access logs for unexpected calls.

### GHSA-2v2f-mvfg-ph56 — `X-Pipeboard-Token` header bypasses auth and reuses operator Meta access token

- **Severity:** High (CVSS 3.1 7.4 — `AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`)
- **Affected versions:** `<= 1.0.113` when run with `--transport streamable-http`
  and a `META_ACCESS_TOKEN` environment variable.
- **Fixed in:** `1.0.115`
- **Affected configurations:** Self-hosted deployments that expose the
  streamable-HTTP port on a reachable network interface with `META_ACCESS_TOKEN`
  set. The hosted MCP at `*.mcp.pipeboard.co` was not affected — it does not set
  `META_ACCESS_TOKEN` and binds the Python process to localhost behind an
  authenticating proxy.

**What went wrong.** This is a follow-up to GHSA-9gw6-46qc-99vr. After that fix,
`AuthInjectionMiddleware` rejected a request only when *both* a primary token and
a supplementary token were absent. `X-Pipeboard-Token` is a supplementary service
token (used only for the duplication callback) and is read into the supplementary
slot, so a request carrying `X-Pipeboard-Token` alone — with any arbitrary value —
satisfied the guard and passed through. No request auth context was set, so tool
handlers fell back to the operator's `META_ACCESS_TOKEN`, letting a
network-reachable caller act as the operator.

**Fix.** `AuthInjectionMiddleware` now requires a primary access-token credential
(`Authorization: Bearer`, `X-META-ACCESS-TOKEN`, or `X-PIPEBOARD-API-TOKEN`) and
returns `401 Unauthorized` otherwise. `X-Pipeboard-Token` is treated as a
supplementary token only and cannot, on its own, admit a request.

**Action for operators.**
- Upgrade to `1.0.115` or later.
- If you exposed an earlier version on a reachable network with
  `META_ACCESS_TOKEN` set, rotate the Meta access token
  (`https://developers.facebook.com/tools/debug/accesstoken/`) and review Graph
  API access logs for unexpected calls.

### GHSA-8353-5qhw-8hfw — Unauthenticated HTTP MCP tool execution under `--sse-response` (auth middleware installed on the unserved app)

- **Severity:** Critical (CVSS 3.1 9.1 — `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`)
- **Affected versions:** `<= 1.0.118` when run with
  `--transport streamable-http --sse-response` and a `META_ACCESS_TOKEN`
  environment variable, on a network-reachable interface.
- **Fixed in:** `1.0.119`
- **Affected configurations:** Self-hosted deployments that pass
  `--sse-response` and expose the streamable-HTTP port on a reachable network
  interface with `META_ACCESS_TOKEN` set. The **default JSON response mode is
  not affected**. The hosted MCP at `*.mcp.pipeboard.co` was not affected — it
  runs in the default JSON mode, does not set `META_ACCESS_TOKEN`, and binds the
  Python process to localhost behind an authenticating proxy.

**What went wrong.** This is a third instance of the class fixed in
GHSA-9gw6-46qc-99vr and GHSA-2v2f-mvfg-ph56. Those fixes hardened the HTTP auth
middleware's request handling, but under `--sse-response` the middleware was not
attached to the Starlette app that the streamable-http transport actually
serves. As a result the served endpoint carried no auth gate in that
configuration, so requests could reach tool handlers and fall back to the
operator's `META_ACCESS_TOKEN`. The default JSON response mode was unaffected.

**Fix.** The HTTP auth middleware is now attached to the served app
unconditionally (independent of the response-format setting), with the SSE app
covered as well for defense-in-depth. Regression tests assert the served app
rejects unauthenticated requests in both JSON and `--sse-response` modes.

**Action for operators.**
- Upgrade to `1.0.119` or later.
- If you exposed an earlier version with `--transport streamable-http
  --sse-response` and `META_ACCESS_TOKEN` set on a reachable network, rotate the
  Meta access token (`https://developers.facebook.com/tools/debug/accesstoken/`)
  and review Graph API access logs for unexpected calls.
- Credited to zx (Jace) — GitHub [@manus-use](https://github.com/manus-use).

### GHSA-6v2r-2m4r-768m — Reflected XSS in the local OAuth callback server error page

- **Severity:** Medium
- **Affected versions:** `<= 1.0.120` when the local OAuth login flow is used
  (the callback server listens on `127.0.0.1:8080-8089`).
- **Fixed in:** `1.0.121`
- **Affected configurations:** Anyone completing an interactive OAuth login on
  a desktop where a browser can reach `localhost` during the 180-second
  authorization window. The hosted MCP at `*.mcp.pipeboard.co` does not run the
  local callback server.

**What went wrong.** The callback server interpolated the `error` query
parameter straight into its HTML error page, so a page open in the user's
browser could navigate to the callback URL with script in `error` and execute
it on the `localhost` origin. The server also exposed an unauthenticated
`/token` endpoint that returned the stored OAuth authorization code to any
same-origin page — the escalation target for the XSS above.

**Fix.**
1. The `error` value is HTML-escaped (and truncated) before being reflected.
2. Every callback response now carries `Content-Security-Policy: default-src
   'none'`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
   `Referrer-Policy: no-referrer` and `Cache-Control: no-store`; the success
   page's inline script runs under a per-response nonce.
3. The unreferenced `/token` endpoint was removed.

**Action for operators.**
- Upgrade to `1.0.121` or later.
- If you completed an OAuth login on a machine where an untrusted page may have
  been open, reconnect the Meta account so a fresh token is issued.
- Credited to zx — GitHub [@manus-pi](https://github.com/manus-pi).
