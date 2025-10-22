# Quickstart: Using Local Template Zips

**Feature**: 001-local-template-zip
**Date**: 2025-10-22
**Audience**: Developers using spec-kit for feature planning

## Overview

This guide shows you how to use local template zip files for offline feature creation instead of downloading templates from GitHub each time.

## Prerequisites

- Spec-kit installed and initialized in your project
- Bash 4.0+ environment (Linux, macOS, WSL)
- `unzip` command available

## Quick Start (5 minutes)

### Step 1: Download Template

Download a template zip file from the spec-kit GitHub releases:

```bash
# Example: Download the claude-sh template v0.0.78
curl -L -o spec-kit-template-claude-sh-v0.0.78.zip \
  https://github.com/spec-kit/templates/releases/download/v0.0.78/template-claude-sh.zip
```

**Naming Convention**: The downloaded file must follow this pattern:
```
spec-kit-template-{arg1}-{arg2}-v{version}.zip
```

Examples:
- `spec-kit-template-claude-sh-v0.0.78.zip` ✅
- `spec-kit-template-claude-py-v0.0.78.zip` ✅
- `my-template.zip` ❌ (wrong pattern)

### Step 2: Place Template in Project

Move the template to your project root (where you run spec-kit commands):

```bash
mv spec-kit-template-claude-sh-v0.0.78.zip /path/to/your/project/
cd /path/to/your/project
```

### Step 3: Configure Template Arguments (Optional)

Create or edit `.specify/config` to specify which template to use:

```bash
# Create config file
mkdir -p .specify
cat > .specify/config <<'EOF'
# Template configuration
TEMPLATE_ARGS="claude sh"
EOF
```

**If you skip this step**: The system will prompt you interactively to select from available templates.

### Step 4: Create a Feature

Run the feature creation command as usual:

```bash
.specify/scripts/bash/create-new-feature.sh "Add user authentication"
```

**What happens**:
1. System reads `.specify/config` for template arguments
2. Finds matching template in current directory
3. Validates zip integrity
4. Extracts template to new feature directory
5. Feature creation completes in <1 second ✨

## Configuration Guide

### Config File Format

Location: `.specify/config`

```bash
# .specify/config - Template configuration

# Required: Template arguments (space-separated)
# Format: "{arg1} {arg2}"
TEMPLATE_ARGS="claude sh"

# Optional: Pin to specific version (defaults to latest)
# TEMPLATE_VERSION="0.0.78"
```

### Finding Template Arguments

Template arguments are embedded in the filename:

```
spec-kit-template-{arg1}-{arg2}-v{version}.zip
                    ^^^^   ^^^^
                    arg1   arg2
```

Examples:
- `spec-kit-template-claude-sh-v0.0.78.zip` → args: `"claude sh"`
- `spec-kit-template-claude-py-v0.0.78.zip` → args: `"claude py"`
- `spec-kit-template-test-js-v1.0.0.zip` → args: `"test js"`

### Multiple Templates

You can keep multiple templates in the same directory:

```bash
ls *.zip
# spec-kit-template-claude-sh-v0.0.78.zip
# spec-kit-template-claude-py-v0.0.78.zip
```

The system will use `TEMPLATE_ARGS` in `.specify/config` to select the right one.

### Version Selection

If you have multiple versions of the same template:

```bash
ls *.zip
# spec-kit-template-claude-sh-v0.0.77.zip
# spec-kit-template-claude-sh-v0.0.78.zip
# spec-kit-template-claude-sh-v0.0.79.zip
```

**Automatic**: System selects the latest version (v0.0.79) by default.

**Manual**: Pin to specific version in config:

```bash
# .specify/config
TEMPLATE_ARGS="claude sh"
TEMPLATE_VERSION="0.0.78"  # Use this version specifically
```

## Interactive Mode

If `.specify/config` doesn't exist or doesn't contain `TEMPLATE_ARGS`, the system prompts you interactively:

```
Multiple templates available. Please select one:
1) spec-kit-template-claude-sh-v0.0.78.zip
2) spec-kit-template-claude-py-v0.0.78.zip
Enter number: 1
```

This is useful for:
- First-time setup
- Switching between templates occasionally
- Testing different templates

## Troubleshooting

### Error: No local template files found

**Problem**: No template zip files in current directory.

**Solution**:
```bash
# Check current directory
ls spec-kit-template-*.zip

# If empty, download a template (see Step 1)
curl -L -o spec-kit-template-claude-sh-v0.0.78.zip \
  https://github.com/spec-kit/templates/releases/download/v0.0.78/template-claude-sh.zip
```

### Error: No template found matching arguments

**Problem**: `.specify/config` specifies args that don't match any available template.

**Example**:
```
Error: No template found matching arguments: claude sh

Available templates:
  - claude-py (version 0.0.78)
  - test-js (version 1.0.0)
```

**Solution**: Either update config to match available template:

```bash
# Update config
echo 'TEMPLATE_ARGS="claude py"' > .specify/config
```

Or download the matching template:

```bash
# Download claude-sh template
curl -L -o spec-kit-template-claude-sh-v0.0.78.zip \
  https://github.com/spec-kit/templates/releases/download/v0.0.78/template-claude-sh.zip
```

### Error: Invalid or corrupted zip file

**Problem**: Template zip file is corrupted or incomplete.

**Solution**:
```bash
# Test zip integrity manually
unzip -t spec-kit-template-claude-sh-v0.0.78.zip

# If corrupted, re-download
rm spec-kit-template-claude-sh-v0.0.78.zip
curl -L -o spec-kit-template-claude-sh-v0.0.78.zip \
  https://github.com/spec-kit/templates/releases/download/v0.0.78/template-claude-sh.zip
```

### Template not in current directory

**Problem**: Template is in a different location.

**Solution**: Template MUST be in the directory where you run the create-new-feature command:

```bash
# Wrong: Template in downloads
~/Downloads/spec-kit-template-claude-sh-v0.0.78.zip
cd ~/my-project
.specify/scripts/bash/create-new-feature.sh "New feature"  # ❌ Won't find it

# Right: Move template to project directory
cd ~/my-project
mv ~/Downloads/spec-kit-template-claude-sh-v0.0.78.zip .
.specify/scripts/bash/create-new-feature.sh "New feature"  # ✅ Works
```

## Advanced Usage

### Switching Templates

To switch between templates temporarily without editing config:

**Option 1**: Remove config to trigger interactive mode:
```bash
mv .specify/config .specify/config.backup
.specify/scripts/bash/create-new-feature.sh "New feature"
# Select from interactive menu
mv .specify/config.backup .specify/config
```

**Option 2**: Edit config before each run:
```bash
# For Python project
echo 'TEMPLATE_ARGS="claude py"' > .specify/config
.specify/scripts/bash/create-new-feature.sh "Python feature"

# For Shell project
echo 'TEMPLATE_ARGS="claude sh"' > .specify/config
.specify/scripts/bash/create-new-feature.sh "Shell feature"
```

### Organizing Templates

Keep templates in a subdirectory and symlink when needed:

```bash
mkdir templates-library
mv spec-kit-template-*.zip templates-library/

# Use specific template
ln -s templates-library/spec-kit-template-claude-sh-v0.0.78.zip .
.specify/scripts/bash/create-new-feature.sh "New feature"
rm spec-kit-template-claude-sh-v0.0.78.zip  # Remove symlink after use
```

### Updating Templates

To update to a newer version:

```bash
# Download new version
curl -L -o spec-kit-template-claude-sh-v0.0.79.zip \
  https://github.com/spec-kit/templates/releases/download/v0.0.79/template-claude-sh.zip

# System will automatically use latest (v0.0.79)
.specify/scripts/bash/create-new-feature.sh "New feature"

# Optional: Remove old version
rm spec-kit-template-claude-sh-v0.0.78.zip
```

### Creating Custom Templates

To create your own template variant:

1. Download and extract existing template:
```bash
unzip spec-kit-template-claude-sh-v0.0.78.zip -d my-template
```

2. Customize template files in `my-template/`

3. Repackage with your own naming:
```bash
cd my-template
zip -r ../spec-kit-template-custom-sh-v1.0.0.zip .
cd ..
rm -rf my-template
```

4. Configure to use custom template:
```bash
echo 'TEMPLATE_ARGS="custom sh"' > .specify/config
```

## Best Practices

### Version Management

1. **Keep latest version only** (for simplicity):
   ```bash
   # Remove old versions after updating
   rm spec-kit-template-claude-sh-v0.0.7[0-8].zip
   ```

2. **Or keep multiple versions** (for rollback):
   ```bash
   # Keep last 3 versions
   ls -t spec-kit-template-claude-sh-*.zip | tail -n +4 | xargs rm
   ```

### Configuration

1. **Commit `.specify/config` to git** (team consistency):
   ```bash
   git add .specify/config
   git commit -m "Configure template for project"
   ```

2. **Add templates to `.gitignore`** (avoid large files in repo):
   ```bash
   echo 'spec-kit-template-*.zip' >> .gitignore
   ```

3. **Document template source** in README:
   ```markdown
   ## Setup
   Download template:
   ```bash
   curl -L -o spec-kit-template-claude-sh-v0.0.78.zip \
     https://github.com/spec-kit/templates/releases/download/v0.0.78/template-claude-sh.zip
   ```
   ```

### Offline Workflow

For completely offline development:

1. Pre-download all needed templates:
   ```bash
   curl -L -o spec-kit-template-claude-sh-v0.0.78.zip ...
   curl -L -o spec-kit-template-claude-py-v0.0.78.zip ...
   ```

2. Verify templates work:
   ```bash
   unzip -t spec-kit-template-*.zip
   ```

3. Configure default:
   ```bash
   echo 'TEMPLATE_ARGS="claude sh"' > .specify/config
   ```

4. Now you can create features without internet! ✅

## Performance

**Before** (GitHub download):
- Network request: 2-8 seconds
- Download: 1-2 seconds
- **Total: 3-10 seconds**

**After** (local template):
- Template search: <10ms
- Version comparison: <5ms
- Zip validation: <50ms
- Extraction: <100ms
- **Total: <1 second** 🚀

**10x faster** for typical use cases!

## Next Steps

- **Automate template updates**: Add a script to check for and download latest templates
- **Template registry**: Maintain a `.specify/templates.json` listing available templates
- **Team sharing**: Share templates via internal artifact repository

## Getting Help

If you encounter issues:

1. Check error message for specific guidance
2. Verify template filename matches pattern exactly
3. Test zip file integrity: `unzip -t <template.zip>`
4. Review this quickstart guide
5. Check `.specify/config` syntax

## Summary

✅ **Download** template zip with correct naming
✅ **Place** in current directory (where you run commands)
✅ **Configure** `.specify/config` with `TEMPLATE_ARGS` (optional)
✅ **Create features** as usual - system uses local template automatically

**Benefits**:
- 🚀 10x faster (sub-second vs 3-10 seconds)
- 🔌 Works offline
- 📌 Version control
- 🔄 Easy template switching
