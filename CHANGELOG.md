## 6 mei 2026 - upstream sync 1.0.70 -> 1.0.97

- Sync met upstream pipeboard-co/meta-ads-mcp 1.0.70 -> 1.0.97 (@herriaan)
- Bumped `mcp[cli]` van 1.12.2 -> >=1.23.0 in pyproject.toml en requirements.txt; resolves CVE-2025-66416 (@herriaan)
- Upstream pinned `actions/checkout@v6.0.2` en `actions/setup-python@v6.2.0` (Node 24 runtime), waardoor onze eigen Node 22 GHA fix uit PR#1 niet meer relevant is (@herriaan)
- Geen merge conflicts; clean fast-forward + dependency bump (@herriaan)
