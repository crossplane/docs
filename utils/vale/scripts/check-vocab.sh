#!/bin/bash
# utils/vale/scripts/check-vocab.sh
#
# Vale Vocabulary Maintenance Script
# Checks for duplicates, sorting issues, and overlaps between vocabulary and rule exceptions

set -e

VOCAB_DIR="utils/vale/styles/config/vocabularies/Crossplane"
ACCEPT_FILE="$VOCAB_DIR/accept.txt"

echo "=== Vale Vocabulary Maintenance ==="
echo ""

# Check for duplicates within accept.txt
echo "1. Checking for duplicates in accept.txt..."
DUPES=$(sort "$ACCEPT_FILE" | uniq -d)
if [ -n "$DUPES" ]; then
    echo "⚠️  Found duplicates:"
    echo "$DUPES"
else
    echo "✅ No duplicates found"
fi
echo ""

# Check for unsorted entries
echo "2. Checking if accept.txt is sorted..."
if diff <(sort "$ACCEPT_FILE") "$ACCEPT_FILE" > /dev/null; then
    echo "✅ File is sorted"
else
    echo "⚠️  File is not sorted. Run: sort -o $ACCEPT_FILE $ACCEPT_FILE"
fi
echo ""

# Find terms that might be in rule exceptions
echo "3. Checking for terms in both accept.txt and rule exceptions..."
RULES_DIR="utils/vale/styles/Crossplane"
for rule in "$RULES_DIR"/*.yml; do
    RULE_NAME=$(basename "$rule")
    # Extract exception lists from YAML files (lines starting with "  - ")
    OVERLAPS=$(grep -h "^  - " "$rule" 2>/dev/null | sed 's/^  - //' | comm -12 - <(sort "$ACCEPT_FILE") || true)
    if [ -n "$OVERLAPS" ]; then
        echo "⚠️  $RULE_NAME has overlapping exceptions:"
        echo "$OVERLAPS" | head -5
        echo ""
    fi
done

echo "4. Statistics"
echo "   Total terms in accept.txt: $(wc -l < "$ACCEPT_FILE")"
echo "   Unique terms: $(sort -u "$ACCEPT_FILE" | wc -l)"
echo ""

echo "✅ Vocabulary check complete"
