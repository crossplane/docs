#!/usr/bin/env bash
#
# Fetch all public, non-archived repositories in the crossplane-contrib GitHub
# organization and emit a JSON array sorted by name. Each entry contains the
# fields the community-extensions-update skill needs to categorize and render
# the list on content/master/learn/community-extension-projects.md.
#
# Output schema:
#   [
#     {
#       "name": "provider-foo",
#       "url": "https://github.com/crossplane-contrib/provider-foo",
#       "description": "...",
#       "topics": ["crossplane", "provider"],
#       "fork": false
#     },
#     ...
#   ]
#
# Requires: gh (authenticated) and jq.

set -euo pipefail

ORG="crossplane-contrib"

for cmd in gh jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "error: $cmd is required but not installed" >&2
    exit 1
  fi
done

# --paginate walks every page; type=public excludes private repos. We then
# filter out archived repos and project the fields we care about.
gh api --paginate "orgs/${ORG}/repos?type=public&per_page=100" \
  | jq -s '
      add
      | map(select(.archived == false))
      | map({
          name: .name,
          url: .html_url,
          description: .description,
          topics: (.topics // []),
          fork: .fork
        })
      | sort_by(.name)
    '
