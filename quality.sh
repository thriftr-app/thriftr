#!/usr/bin/env bash
if [ "$1" = "clean" ]; then
  echo "🧹 Cleaning quality reports..."
  rm -rf quality_reports
  echo "✅ Clean complete"
fi

OUT_DIR="quality_reports"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

RUFF_OUT="$OUT_DIR/ruff_$TIMESTAMP.txt"
RADON_CC_OUT="$OUT_DIR/radon_cc_$TIMESTAMP.txt"
RADON_MI_OUT="$OUT_DIR/radon_mi_$TIMESTAMP.txt"
SUMMARY="$OUT_DIR/summary_$TIMESTAMP.txt"

mkdir -p "$OUT_DIR"

# Failure flags
RUFF_FAILED=0
RADON_CC_FAILED=0
RADON_MI_FAILED=0

echo "➡️  Running code quality checks..."
echo "➡️  Output directory: $OUT_DIR"

# -------------------------
# Ruff
# -------------------------
echo "➡️  Running ruff..."
if ! ruff check backend > "$RUFF_OUT" 2>&1; then
  echo "❌ Ruff reported issues"
  RUFF_FAILED=1
fi

# -------------------------
# Radon – Cyclomatic Complexity
# -------------------------
echo "➡️  Running radon (cyclomatic complexity)..."
if ! radon cc backend -s -a > "$RADON_CC_OUT" 2>&1; then
  echo "❌ Radon CC failed"
  RADON_CC_FAILED=1
fi

# -------------------------
# Radon – Maintainability Index
# -------------------------
echo "➡️  Running radon (maintainability index)..."
if ! radon mi backend -s > "$RADON_MI_OUT" 2>&1; then
  echo "❌ Radon MI failed"
  RADON_MI_FAILED=1
fi

# -------------------------
# Summary
# -------------------------
echo "➡️  Writing summary..."

{
  echo "===== CODE QUALITY SUMMARY ====="
  echo "Timestamp: $TIMESTAMP"
  echo
  echo "Ruff:              $([ $RUFF_FAILED -eq 0 ] && echo OK || echo ISSUES FOUND)"
  echo "Radon CC:          $([ $RADON_CC_FAILED -eq 0 ] && echo OK || echo FAILED)"
  echo "Radon MI:          $([ $RADON_MI_FAILED -eq 0 ] && echo OK || echo FAILED)"
  echo
  echo "===== RUFF OUTPUT ====="
  cat "$RUFF_OUT"
  echo
  echo "===== RADON CC OUTPUT ====="
  cat "$RADON_CC_OUT"
  echo
  echo "===== RADON MI OUTPUT ====="
  cat "$RADON_MI_OUT"
} > "$SUMMARY"

echo "➡️  Summary written to: $SUMMARY"

# -------------------------
# Final exit code
# -------------------------
if [ $RUFF_FAILED -ne 0 ] || [ $RADON_CC_FAILED -ne 0 ] || [ $RADON_MI_FAILED -ne 0 ]; then
  echo "❌ One or more quality checks failed"
  exit 1
fi

echo "✅ All quality checks passed"
exit 0

