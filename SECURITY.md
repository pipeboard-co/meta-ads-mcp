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
