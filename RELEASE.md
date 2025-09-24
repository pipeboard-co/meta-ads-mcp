# Release Process

This repository uses GitHub Actions to automatically publish releases to PyPI. Here's the optimized release process:

## 🚀 Quick Release (Recommended)

### Prerequisites
- ✅ **Trusted Publishing Configured**: Repository uses PyPI trusted publishing with OIDC tokens
- ✅ **GitHub CLI installed**: `gh` command available for streamlined releases
- ✅ **Clean working directory**: No uncommitted changes

### Optimal Release Process

1. **Update version in three files** (use consistent versioning):
   
   ```bash
   # Update pyproject.toml
   sed -i '' 's/version = "0.7.7"/version = "0.7.8"/' pyproject.toml
   
   # Update __init__.py  
   sed -i '' 's/__version__ = "0.7.7"/__version__ = "0.7.8"/' meta_ads_mcp/__init__.py

   # Update server.json (both top-level and package versions)
   sed -i '' 's/"version": "0.7.7"/"version": "0.7.8"/g' server.json
   ```
   
  Or manually edit:
  - `pyproject.toml`: `version = "0.7.8"`
  - `meta_ads_mcp/__init__.py`: `__version__ = "0.7.8"`
  - `server.json`: set `"version": "0.7.8"` and package `"version": "0.7.8"`

2. **Commit and push version changes**:
   ```bash
   git add pyproject.toml meta_ads_mcp/__init__.py server.json
   git commit -m "Bump version to 0.7.8"
   git push origin main
   ```

3. **Create GitHub release** (triggers automatic PyPI publishing):
   ```bash
   # Use bash wrapper if gh has issues in Cursor
   bash -c "gh release create 0.7.8 --title '0.7.8' --generate-notes"
   ```

4. **Verify release** (optional):
   ```bash
   # Check GitHub release
   curl -s "https://api.github.com/repos/pipeboard-co/meta-ads-mcp/releases/latest" | grep -E '"tag_name"|"name"'
   
   # Check PyPI availability (wait 2-3 minutes)
   curl -s "https://pypi.org/pypi/meta-ads-mcp/json" | grep -E '"version"|"0.7.8"'
   ```

## 📋 Detailed Release Process

### Version Management Best Practices

- **Semantic Versioning**: Follow `MAJOR.MINOR.PATCH` (e.g., 0.7.8)
- **Synchronized Files**: Always update BOTH version files
- **Commit Convention**: Use `"Bump version to X.Y.Z"` format
- **Release Tag**: GitHub release tag matches version (no "v" prefix)

### Pre-Release Checklist

```bash
# 1. Ensure clean working directory
git status

# 2. Run tests locally (optional but recommended)
uv run python -m pytest tests/ -v

# 3. Check current version
grep -E 'version =|__version__|"version":' pyproject.toml meta_ads_mcp/__init__.py server.json
```

### Release Commands (One-liner)

```bash
# Complete release in one sequence
VERSION="0.7.8" && \
sed -i '' "s/version = \"0.7.7\"/version = \"$VERSION\"/" pyproject.toml && \
sed -i '' "s/__version__ = \"0.7.7\"/__version__ = \"$VERSION\"/" meta_ads_mcp/__init__.py && \
sed -i '' "s/\"version\": \"0.7.7\"/\"version\": \"$VERSION\"/g" server.json && \
git add pyproject.toml meta_ads_mcp/__init__.py server.json && \
git commit -m "Bump version to $VERSION" && \
git push origin main && \
bash -c "gh release create $VERSION --title '$VERSION' --generate-notes"
```

## 🔄 Workflows

### `publish.yml` (Automatic)
- **Trigger**: GitHub release creation
- **Purpose**: Build and publish to PyPI
- **Security**: OIDC tokens (no API keys)
- **Status**: ✅ Fully automated

### `test.yml` (Validation)
- **Trigger**: Push to main/master
- **Purpose**: Package structure validation
- **Matrix**: Python 3.10, 3.11, 3.12
- **Note**: Build tests only, not pytest

## 🛠️ Troubleshooting

### Common Issues

1. **gh command issues in Cursor**:
   ```bash
   # Use bash wrapper
   bash -c "gh release create 0.7.8 --title '0.7.8' --generate-notes"
   ```

2. **Version mismatch**:
   ```bash
   # Verify all three files have the same version
   grep -E 'version =|__version__|"version":' pyproject.toml meta_ads_mcp/__init__.py server.json
   ```

3. **PyPI not updated**:
   ```bash
   # Check if package is available (wait 2-3 minutes)
   curl -s "https://pypi.org/pypi/meta-ads-mcp/json" | grep '"version"'
   ```

### Manual Deployment (Fallback)

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (requires API token)
python -m twine upload dist/*
```

## 📊 Release Verification

### GitHub Release
- ✅ Release created with correct tag
- ✅ Auto-generated notes from commits
- ✅ Actions tab shows successful workflow

### PyPI Package
- ✅ Package available for installation
- ✅ Correct version displayed
- ✅ All dependencies listed

### Installation Test
```bash
# Test new version installation
pip install meta-ads-mcp==0.7.8
# or
uvx meta-ads-mcp@0.7.8
```

## 🔒 Security Notes

- **Trusted Publishing**: Uses GitHub OIDC tokens (no API keys needed)
- **Isolated Builds**: All builds run in GitHub-hosted runners
- **Access Control**: Only maintainers can create releases
- **Audit Trail**: All releases tracked in GitHub Actions

## 📈 Release Metrics

Track successful releases:
- **GitHub Releases**: https://github.com/pipeboard-co/meta-ads-mcp/releases
- **PyPI Package**: https://pypi.org/project/meta-ads-mcp/
- **Actions History**: https://github.com/pipeboard-co/meta-ads-mcp/actions 