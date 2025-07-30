# Release Process

This repository uses GitHub Actions to automatically publish releases to PyPI. Here's how it works:

## Automated Publishing

### Setup Status

✅ **Trusted Publishing Configured**: The repository is already set up with PyPI trusted publishing using the `release` environment.

### Creating a Release

1. **Update the version** in both files:
   
   In `pyproject.toml`:
   ```toml
   version = "0.3.8"  # Increment as needed
   ```
   
   In `meta_ads_mcp/__init__.py`:
   ```python
   __version__ = "0.3.8"  # Must match pyproject.toml
   ```

2. **Commit and push** the version changes:
   ```bash
   git add pyproject.toml meta_ads_mcp/__init__.py
   git commit -m "Bump version to 0.3.8"
   git push origin main
   ```

3. **Wait for build tests to pass** (optional):
   ```bash
   # Check the latest test workflow run
   gh run list --workflow=test.yml --limit 1
   
   # Get the run ID and wait for completion
   RUN_ID=$(gh run list --workflow=test.yml --limit 1 --json databaseId --jq '.[0].databaseId')
   gh run watch $RUN_ID
   ```
   Note: This only tests package building and installation, not the actual pytest tests.

4. **Create a GitHub release**:
   ```bash
   gh release create 0.3.8 --title "0.3.8" --generate-notes
   ```
   This command will:
   - Create a release with the specified version (no "v" prefix)
   - Auto-generate release notes from commits
   - Automatically trigger the GitHub Action for PyPI publishing

5. **Automatic deployment**:
   - The GitHub Action will automatically trigger
   - It will build the package and publish to PyPI
   - Check the "Actions" tab to monitor progress

## Workflows

### `publish.yml`
- **Triggers**: When a GitHub release is published, or manual workflow dispatch
- **Purpose**: Builds and publishes the package to PyPI
- **Security**: Uses trusted publishing with OIDC tokens (no API keys needed)

### `test.yml`
- **Triggers**: On pushes and pull requests to main/master
- **Purpose**: Tests package building and installation across Python versions
- **Matrix**: Tests Python 3.10, 3.11, and 3.12
- **Note**: Does not run pytest tests, only validates package structure

## Manual Deployment

If you need to deploy manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (requires API token or configured credentials)
python -m twine upload dist/*
```

## Version Management

- Follow semantic versioning (SemVer): `MAJOR.MINOR.PATCH`
- **Important**: Update version in BOTH `pyproject.toml` and `meta_ads_mcp/__init__.py`
- The git tag should match the version (e.g., `v0.3.8` for version `0.3.8`)
- Keep versions synchronized between the two files

## Security Notes

- Trusted publishing is preferred over API tokens
- Uses GitHub's OIDC tokens for secure authentication to PyPI
- Only maintainers should be able to create releases
- All builds run in isolated GitHub-hosted runners 