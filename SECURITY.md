# Security

## Reporting a vulnerability

Please report security issues privately via GitHub: open a draft advisory
from the [Security tab](https://github.com/pipeboard-co/meta-ads-mcp/security/advisories/new)
("Report a vulnerability"). Do not file public issues for unpatched
vulnerabilities.

## Advisories

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
