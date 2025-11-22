#!/bin/bash
# utils/vale/scripts/add-term.sh
#
# Interactive script to add terms to Vale vocabulary

set -e

VOCAB_DIR="utils/vale/styles/config/vocabularies/Crossplane"
ACCEPT_FILE="$VOCAB_DIR/accept.txt"

echo "=== Add Term to Vale Vocabulary ==="
echo ""

# Prompt for term
read -p "Enter term to add: " TERM

# Check if already exists
if grep -Fxq "$TERM" "$ACCEPT_FILE"; then
    echo "⚠️  Term '$TERM' already exists in vocabulary"
    exit 0
fi

# Prompt for category
echo ""
echo "Select category:"
echo "1) Crossplane terminology"
echo "2) Kubernetes terms"
echo "3) Cloud provider brands"
echo "4) Cloud-native acronyms"
echo "5) Technical jargon"
echo "6) Spelling exceptions"
read -p "Category (1-6): " CATEGORY

# Add term and sort
echo "$TERM" >> "$ACCEPT_FILE"
sort -o "$ACCEPT_FILE" "$ACCEPT_FILE"

echo "✅ Added '$TERM' to vocabulary"
echo ""
echo "Next steps:"
echo "1. Test: vale --config=utils/vale/.vale.ini content/"
echo "2. Commit: git add $ACCEPT_FILE"
echo "3. Document reason in commit message"
