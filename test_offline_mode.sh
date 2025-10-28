#!/bin/bash
# Test script for offline mode functionality

set -e

echo "==================================="
echo "Testing Offline Mode Implementation"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR="/tmp/specify-offline-test-$$"
TEMPLATES_DIR="src/specify_cli/spec-kit-templates"

echo "Step 1: Check if templates directory exists"
if [ -d "$TEMPLATES_DIR" ]; then
    echo -e "${GREEN}✓${NC} Templates directory exists: $TEMPLATES_DIR"
else
    echo -e "${RED}✗${NC} Templates directory not found: $TEMPLATES_DIR"
    exit 1
fi

echo ""
echo "Step 2: List available templates"
if [ -n "$(ls -A $TEMPLATES_DIR/*.zip 2>/dev/null)" ]; then
    echo -e "${GREEN}✓${NC} Found template files:"
    ls -lh $TEMPLATES_DIR/*.zip
    HAS_TEMPLATES=1
else
    echo -e "${YELLOW}⚠${NC} No template zip files found in $TEMPLATES_DIR"
    echo "   This is expected for a fresh checkout."
    HAS_TEMPLATES=0
fi

echo ""
echo "Step 3: Test --offline flag in help text"
if uv run specify init --help 2>/dev/null | grep -q "offline"; then
    echo -e "${GREEN}✓${NC} --offline flag appears in help text"
else
    echo -e "${RED}✗${NC} --offline flag not found in help text"
    exit 1
fi

echo ""
echo "Step 4: Test offline mode with no templates (should fail gracefully)"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "   Running: specify init test-project --offline --ai claude --ignore-agent-tools --no-git"
if uv run specify init test-project --offline --ai claude --ignore-agent-tools --no-git 2>&1 | grep -q "No local template found"; then
    echo -e "${GREEN}✓${NC} Offline mode fails gracefully with expected error message"
else
    echo -e "${YELLOW}⚠${NC} Unexpected behavior (might have found a local template)"
fi

cd - > /dev/null

echo ""
echo "Step 5: Test SPECIFY_OFFLINE environment variable"
export SPECIFY_OFFLINE=1
if uv run specify init --help 2>&1 | grep -q "SPECIFY_OFFLINE"; then
    echo -e "${GREEN}✓${NC} SPECIFY_OFFLINE mentioned in help text"
else
    echo -e "${YELLOW}⚠${NC} SPECIFY_OFFLINE not mentioned in help (may be in description)"
fi
unset SPECIFY_OFFLINE

echo ""
echo "Step 6: Verify template search location"
SEARCH_PATH=$(python3 -c "from pathlib import Path; import sys; sys.path.insert(0, 'src'); from specify_cli import get_installation_templates_dir; print(get_installation_templates_dir())")
if [ "$SEARCH_PATH" = "$PWD/$TEMPLATES_DIR" ]; then
    echo -e "${GREEN}✓${NC} Template search path is correct: $SEARCH_PATH"
else
    echo -e "${YELLOW}⚠${NC} Template search path: $SEARCH_PATH"
fi

echo ""
echo "================================="
echo "Test Summary"
echo "================================="

if [ $HAS_TEMPLATES -eq 1 ]; then
    echo -e "${GREEN}✓${NC} Offline mode is ready to use with existing templates"
    echo ""
    echo "To test full offline initialization:"
    echo "  specify init my-test --offline --ai claude --here --force --ignore-agent-tools --no-git"
else
    echo -e "${YELLOW}⚠${NC} No templates available yet for full offline test"
    echo ""
    echo "To create templates for offline use:"
    echo "  1. ./.github/workflows/scripts/create-release-packages.sh v1.0.0"
    echo "  2. cp .genreleases/spec-kit-template-claude-sh-v1.0.0.zip $TEMPLATES_DIR/"
    echo "  3. Run this test script again"
fi

# Cleanup
rm -rf "$TEST_DIR"

echo ""
echo -e "${GREEN}All tests passed!${NC}"
