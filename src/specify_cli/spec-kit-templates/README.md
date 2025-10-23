# Spec Kit Templates Directory

This directory contains local template zip files for offline project initialization.

## Purpose

When running `specify init`, the CLI searches this directory for template files matching the pattern:
```
spec-kit-template-{agent}-{script}-v{version}.zip
```

For example:
- `spec-kit-template-claude-sh-v1.0.0.zip`
- `spec-kit-template-copilot-ps-v1.2.3.zip`

## Template Discovery Order

The CLI searches for templates in this order:

1. **Installation directory** (this directory): `src/specify_cli/spec-kit-templates/`
2. **GitHub releases**: Downloads from the latest release if no local template found

## Using Local Templates

### For Development

During development, place template zip files in this directory to test changes without publishing to GitHub:

```bash
# Generate release packages
./.github/workflows/scripts/create-release-packages.sh v1.0.0

# Copy specific template to installation directory
cp .genreleases/spec-kit-template-claude-sh-v1.0.0.zip \
   src/specify_cli/spec-kit-templates/
```

### For Offline Environments

For corporate environments or offline usage:

1. Download template files from [GitHub Releases](https://github.com/github/spec-kit/releases)
2. Place them in this directory
3. The CLI will use these local templates instead of attempting GitHub downloads

## Version Selection

If multiple versions of the same template exist, the CLI automatically selects the latest version based on semantic versioning.

Example:
```
spec-kit-template-claude-sh-v1.0.0.zip  <- ignored
spec-kit-template-claude-sh-v1.2.3.zip  <- selected (latest)
spec-kit-template-claude-sh-v1.1.5.zip  <- ignored
```

## Template Persistence

Local templates in this directory are **never deleted** by the CLI, unlike GitHub-downloaded templates which are cleaned up after extraction.
