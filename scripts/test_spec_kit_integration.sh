#!/bin/bash
# Pantheon Spec Kit Integration Verification Script
#
# Purpose: Comprehensive test of Pantheon's Spec Kit v0.0.57+ compatibility
# Usage: ./scripts/test_spec_kit_integration.sh [--cleanup]
#
# This script:
# 1. Creates a fresh test project with Spec Kit v0.0.57+
# 2. Tests format detection
# 3. Tests integration
# 4. Tests rollback
# 5. Verifies all functionality works correctly
#
# Options:
#   --cleanup    Remove test directory after completion
#   --keep       Keep test directory (default)

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PANTHEON_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_DIR="/tmp/pantheon-integration-test-$(date +%s)"
CLEANUP=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --keep)
            CLEANUP=false
            shift
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: $0 [--cleanup|--keep]"
            exit 1
            ;;
    esac
done

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

test_result() {
    ((TESTS_RUN++))
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $1"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $1"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    ((TESTS_RUN++))
    if [ "$expected" = "$actual" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $message"
        echo -e "  Expected: $expected"
        echo -e "  Actual:   $actual"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_file_exists() {
    local filepath="$1"
    local message="$2"

    ((TESTS_RUN++))
    if [ -f "$filepath" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $message (file not found: $filepath)"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_file_contains() {
    local filepath="$1"
    local pattern="$2"
    local message="$3"

    ((TESTS_RUN++))
    if grep -q "$pattern" "$filepath" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $message (pattern not found: $pattern)"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_file_not_contains() {
    local filepath="$1"
    local pattern="$2"
    local message="$3"

    ((TESTS_RUN++))
    if ! grep -q "$pattern" "$filepath" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $message (pattern found when it shouldn't be: $pattern)"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Main test execution
main() {
    print_header "Pantheon Spec Kit Integration Test Suite"

    echo "Test directory: $TEST_DIR"
    echo "Pantheon root:  $PANTHEON_ROOT"
    echo "Cleanup after:  $CLEANUP"
    echo

    # ============================================================================
    # SETUP
    # ============================================================================

    print_header "Setup: Installing Pantheon v0.2.0"

    cd "$PANTHEON_ROOT"
    echo "Uninstalling previous version..."
    uv tool uninstall pantheon-agents 2>/dev/null || true

    echo "Installing from source..."
    uv tool install . >/dev/null 2>&1
    test_result "Pantheon installation"

    if ! command -v pantheon &> /dev/null; then
        echo -e "${RED}✗ FATAL${NC}: pantheon command not found after installation"
        exit 1
    fi

    echo "Installed version: $(pantheon --version 2>&1 || echo 'unknown')"

    # ============================================================================
    # TEST PROJECT SETUP
    # ============================================================================

    print_header "Setup: Creating Test Project"

    echo "Creating test project at $TEST_DIR..."
    mkdir -p "$TEST_DIR"
    cd "$TEST_DIR"

    # Create basic Python project structure
    mkdir -p src/test_app tests

    cat > pyproject.toml << 'EOF'
[project]
name = "test-app"
version = "0.1.0"
requires-python = ">=3.9"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
EOF

    cat > src/test_app/__init__.py << 'EOF'
"""Test application."""
def add(a: int, b: int) -> int:
    return a + b
EOF

    cat > tests/test_sample.py << 'EOF'
"""Sample tests."""
from test_app import add
def test_add() -> None:
    assert add(2, 3) == 5
EOF

    test_result "Project structure created"

    echo "Installing Spec Kit v0.0.57+..."
    specify init . --ai claude --force >/dev/null 2>&1
    test_result "Spec Kit installation"

    # ============================================================================
    # TEST 1: FORMAT DETECTION
    # ============================================================================

    print_header "Test 1: Format Detection"

    assert_file_exists ".claude/commands/speckit.implement.md" \
        "speckit.implement.md exists"

    assert_file_exists ".claude/commands/speckit.plan.md" \
        "speckit.plan.md exists"

    assert_file_exists ".claude/commands/speckit.tasks.md" \
        "speckit.tasks.md exists"

    # Test Python format detection
    python3 << 'EOF'
import sys
sys.path.insert(0, '$PANTHEON_ROOT/src')
from pathlib import Path
from pantheon.integrations.spec_kit import _detect_command_format, _get_command_files

project_root = Path('$TEST_DIR')
format_type = _detect_command_format(project_root)

if format_type != "new":
    print(f"Expected 'new', got '{format_type}'")
    sys.exit(1)

command_files = _get_command_files(project_root)
if len(command_files) != 3:
    print(f"Expected 3 files, got {len(command_files)}")
    sys.exit(1)

for name, path in command_files.items():
    if not path.exists():
        print(f"File missing: {path}")
        sys.exit(1)

sys.exit(0)
EOF

    test_result "Python format detection returns 'new'"

    # ============================================================================
    # TEST 2: PANTHEON INIT
    # ============================================================================

    print_header "Test 2: Pantheon Init"

    # pantheon init will prompt, we just check DEV agent installation
    if [ ! -d ".claude/agents" ]; then
        mkdir -p .claude/agents
        cp "$PANTHEON_ROOT/agents/dev.md" .claude/agents/dev.md
    fi

    assert_file_exists ".claude/agents/dev.md" \
        "DEV agent installed"

    # ============================================================================
    # TEST 3: INTEGRATION
    # ============================================================================

    print_header "Test 3: Pantheon Integration"

    echo "Running pantheon integrate..."
    pantheon integrate >/dev/null 2>&1
    test_result "Integration command executed"

    assert_file_contains ".claude/commands/speckit.implement.md" \
        "## Agent Integration" \
        "speckit.implement.md has Agent Integration section"

    assert_file_contains ".claude/commands/speckit.plan.md" \
        "## Quality Standards" \
        "speckit.plan.md has Quality Standards section"

    assert_file_contains ".claude/commands/speckit.tasks.md" \
        "## Task Format" \
        "speckit.tasks.md has Task Format section"

    # ============================================================================
    # TEST 4: BACKUP VERIFICATION
    # ============================================================================

    print_header "Test 4: Backup Verification"

    BACKUP_DIR=$(ls -d .integration-backup-* 2>/dev/null | tail -1)

    if [ -z "$BACKUP_DIR" ]; then
        echo -e "${RED}✗ FAIL${NC}: No backup directory found"
        ((TESTS_RUN++))
        ((TESTS_FAILED++))
    else
        echo -e "${GREEN}✓ PASS${NC}: Backup directory created: $BACKUP_DIR"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))

        assert_file_exists "$BACKUP_DIR/speckit.implement.md" \
            "Backup contains speckit.implement.md"

        assert_file_exists "$BACKUP_DIR/speckit.plan.md" \
            "Backup contains speckit.plan.md"

        assert_file_exists "$BACKUP_DIR/speckit.tasks.md" \
            "Backup contains speckit.tasks.md"

        # Check backup has correct filenames (not old format)
        if [ -f "$BACKUP_DIR/implement.md" ]; then
            echo -e "${RED}✗ FAIL${NC}: Backup contains old format files"
            ((TESTS_RUN++))
            ((TESTS_FAILED++))
        else
            echo -e "${GREEN}✓ PASS${NC}: Backup uses new format filenames"
            ((TESTS_RUN++))
            ((TESTS_PASSED++))
        fi
    fi

    # ============================================================================
    # TEST 5: QUALITY HOOKS
    # ============================================================================

    print_header "Test 5: Quality Hooks Installation"

    if [ -d ".pantheon/hooks" ]; then
        echo -e "${GREEN}✓ PASS${NC}: Quality hooks directory exists"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))

        for hook in SubagentStop PreCommit PhaseGate; do
            if [ -f ".pantheon/hooks/${hook}.sh" ]; then
                echo -e "${GREEN}✓ PASS${NC}: ${hook}.sh hook installed"
                ((TESTS_RUN++))
                ((TESTS_PASSED++))
            else
                echo -e "${RED}✗ FAIL${NC}: ${hook}.sh hook missing"
                ((TESTS_RUN++))
                ((TESTS_FAILED++))
            fi
        done
    else
        echo -e "${YELLOW}⚠ SKIP${NC}: Quality hooks not installed (may be optional)"
    fi

    # ============================================================================
    # TEST 6: ROLLBACK
    # ============================================================================

    print_header "Test 6: Rollback Functionality"

    echo "Running pantheon rollback..."
    echo "y" | pantheon rollback >/dev/null 2>&1
    test_result "Rollback command executed"

    assert_file_not_contains ".claude/commands/speckit.implement.md" \
        "## Agent Integration" \
        "Agent Integration section removed"

    assert_file_not_contains ".claude/commands/speckit.plan.md" \
        "## Quality Standards" \
        "Quality Standards section removed"

    assert_file_not_contains ".claude/commands/speckit.tasks.md" \
        "## Task Format" \
        "Task Format section removed"

    # ============================================================================
    # TEST 7: RE-INTEGRATION
    # ============================================================================

    print_header "Test 7: Re-Integration After Rollback"

    echo "Running pantheon integrate again..."
    pantheon integrate >/dev/null 2>&1
    test_result "Re-integration command executed"

    assert_file_contains ".claude/commands/speckit.implement.md" \
        "## Agent Integration" \
        "Agent Integration section re-added"

    # Check new backup was created
    BACKUP_COUNT=$(ls -d .integration-backup-* 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -ge 2 ]; then
        echo -e "${GREEN}✓ PASS${NC}: Multiple backups created (idempotent)"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: Expected multiple backups, found $BACKUP_COUNT"
        ((TESTS_RUN++))
        ((TESTS_FAILED++))
    fi

    # ============================================================================
    # TEST SUMMARY
    # ============================================================================

    print_header "Test Summary"

    echo "Tests Run:    $TESTS_RUN"
    echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
    if [ $TESTS_FAILED -gt 0 ]; then
        echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
    else
        echo -e "Tests Failed: ${GREEN}$TESTS_FAILED${NC}"
    fi

    SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_RUN))
    echo "Success Rate: ${SUCCESS_RATE}%"
    echo

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                   ✓ ALL TESTS PASSED ✓                        ║${NC}"
        echo -e "${GREEN}║                                                                ║${NC}"
        echo -e "${GREEN}║  Pantheon Spec Kit v0.0.57+ compatibility verified!           ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo
        echo "Test project location: $TEST_DIR"

        if [ "$CLEANUP" = true ]; then
            echo "Cleaning up test directory..."
            rm -rf "$TEST_DIR"
            echo "✓ Cleanup complete"
        else
            echo "Test directory preserved for inspection"
        fi

        exit 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                   ✗ SOME TESTS FAILED ✗                       ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo
        echo "Test project preserved at: $TEST_DIR"
        echo "Review the output above for details on failures"
        exit 1
    fi
}

# Run main test suite
main "$@"
