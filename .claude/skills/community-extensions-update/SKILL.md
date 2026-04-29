---
name: community-extensions-update
description: Use when the user asks to refresh, update, or sync the Crossplane Community Extension Projects page (content/master/learn/community-extension-projects.md) with the current state of the crossplane-contrib GitHub organization. Fetches live repo data, reconciles adds/removes against the page, categorizes new entries, and writes the updated page.
---

# Update the Community Extension Projects page

The community extension projects page lists every public, non-archived repo under the `crossplane-contrib` GitHub org, grouped into categories. The list drifts out of date as repos are added, archived, or renamed. This skill reconciles the page against the live org state.

Target file: `content/master/learn/community-extension-projects.md`
Data source script: `scripts/discover-community-extensions.sh`

## Procedure

### 1. Fetch the live repo list

Run the script and capture its JSON output:

```bash
./scripts/discover-community-extensions.sh > /tmp/contrib-repos.json
```

Each entry has `name`, `url`, `description`, `topics`, and `fork`. The list is already sorted by `name` and only contains public, non-archived repos.

### 2. Compute the diff against the current page

Extract the names currently listed on the page and compare to the API output:

```bash
grep -oE '\[([a-z0-9-]+)\]\(https://github.com/crossplane-contrib/' \
  content/master/learn/community-extension-projects.md \
  | sed 's/\[//; s/\](.*//' | sort -u > /tmp/contrib-from-page.txt

jq -r '.[].name' /tmp/contrib-repos.json | sort > /tmp/contrib-from-api.txt

# To add (in API but not on page):
comm -23 /tmp/contrib-from-api.txt /tmp/contrib-from-page.txt

# To remove (on page but not in API — archived, renamed, deleted):
comm -13 /tmp/contrib-from-api.txt /tmp/contrib-from-page.txt
```

Show both lists to the user before editing so they can sanity-check, especially the removals.

### 3. Categorize new entries

The page has these sections, in this order:

- **Providers** — repos that expose external APIs as Crossplane managed resources
- **Functions** — composition functions
- **Configurations** — opinionated configuration packages
- **Tools and utilities** — CLIs, GitHub Actions, libraries, plugins
- **Dashboard** — UIs for visualizing/operating Crossplane

Apply these heuristics in order:

| Pattern | Category |
| --- | --- |
| name starts with `provider-` | Providers |
| name contains `provider` (e.g. `crossplane-provider-*`) | Providers |
| name starts with `function-` | Functions |
| name starts with `configuration-` | Configurations |
| description/topics indicate a UI or dashboard | Dashboard |
| anything else | **ask the user** before placing |

Do **not** silently default ambiguous entries to "Tools and utilities". When the heuristics don't give a confident answer, ask the user — citing the repo's description and topics — and let them pick the section. Examples of historically ambiguous entries: `crossview` (Dashboard, not Tools), `xprin` (testing framework → Tools), repos with empty/null descriptions.

### 4. Determine removals

Removals come from the "in page only" diff. These are repos that have been archived, renamed, or deleted upstream. Confirm removals with the user before deleting — a renamed repo should be replaced (e.g., `provider-cloudflare` → `provider-upjet-cloudflare`), not just dropped.

### 5. Rewrite the section bodies

For each affected section:

- Alphabetize the full list using the **target-based** sort defined below.
- Format each line as `- [{{name}}](https://github.com/crossplane-contrib/{{name}})`.
- Keep the section's surrounding `<!-- vale off -->` / `<!-- vale on -->` comments intact.
- Keep the section header (e.g., `## Providers`) and the blank line after it intact.

#### Alphabetization rule

Repos are sorted by **target** — the part of the name that identifies what the extension is *for*, not by the full repo name. Qualifiers like `upjet-`, `jet-`, and `crossplane-` aren't part of the target.

To compute the target, strip the longest matching prefix from the repo name:

| Section | Strip these prefixes (longest match wins) |
| --- | --- |
| Providers | `crossplane-provider-`, `provider-upjet-`, `provider-jet-`, `provider-` |
| Functions | `function-` |
| Configurations | `configuration-` |
| Tools and utilities | none — sort by full name |
| Dashboard | none — sort by full name |

Then:

1. **Primary sort**: by target, lexically (case-insensitive ASCII order — `LC_ALL=C` semantics).
2. **Tiebreak (same target)**: shortest full repo name first, i.e., the form closest to the bare target. This puts `provider-aws` before `provider-upjet-aws`, and `provider-newrelic` before `crossplane-provider-newrelic`.

Worked examples (Providers):

- `provider-aws`, `provider-upjet-aws` → both target `aws`. They sort adjacent in the A's, with `provider-aws` first (shorter).
- `crossplane-provider-castai` → target `castai`, sits between `provider-capi` and `provider-civo`.
- `provider-jet-ec`, `provider-upjet-ec` → both target `ec`. Adjacent in the E's, jet- form first (shorter).
- `provider-upjet-cloudflare` → target `cloudflare`, sits between `provider-civo` and `provider-confluent` — **not** down in the U's.
- `provider-upjet-gcp` (target `gcp`) sorts before `provider-gcp-beta` (target `gcp-beta`) because `gcp` < `gcp-beta` lexically. `-beta` is **not** a stripped suffix; it's part of the target.

When in doubt about whether a substring is a qualifier or part of the target, ask the user — don't invent new strip rules.

### 6. Preserve page structure

Do **not** rewrite anything outside the bulleted lists:

- The Hugo front matter (`---` block at the top) stays as-is.
- The intro paragraph and `{{< hint "note" >}}` block stay as-is.
- The `<!-- vale write-good.Passive = NO -->` / `= YES` comments around the hint block stay as-is.
- Section ordering stays as-is: Providers, Functions, Configurations, Tools and utilities, Dashboard.

Prefer `Edit` with the smallest possible old/new strings — one Edit per section that changed — over rewriting the whole file. This keeps the diff reviewable.

### 7. Copy to the latest versioned docs

The latest released docs version tracks `master` for this page. Determine the version from `config.yaml`'s `latest:` key, then copy the freshly edited file over:

```bash
LATEST_VERSION=$(grep -E '^\s+latest:' config.yaml | sed -E 's/.*"([^"]+)".*/\1/')
cp content/master/learn/community-extension-projects.md \
   "content/v${LATEST_VERSION}/learn/community-extension-projects.md"
```

Confirm the destination path exists before copying — if the file isn't already at `content/v${LATEST_VERSION}/learn/community-extension-projects.md`, stop and surface that to the user rather than creating a new file in an unexpected location.

### 8. Verify

After editing and copying:

```bash
# Re-extract names from each page and compare to the API list.
for f in \
  content/master/learn/community-extension-projects.md \
  "content/v${LATEST_VERSION}/learn/community-extension-projects.md"; do
  echo "=== $f ==="
  grep -oE '\[([a-z0-9-]+)\]\(https://github.com/crossplane-contrib/' "$f" \
    | sed 's/\[//; s/\](.*//' | sort -u > /tmp/contrib-from-page-after.txt
  diff /tmp/contrib-from-api.txt /tmp/contrib-from-page-after.txt && echo "OK"
done

# Confirm master and the latest version are byte-identical.
diff content/master/learn/community-extension-projects.md \
     "content/v${LATEST_VERSION}/learn/community-extension-projects.md"
```

A clean diff on each page means it matches the org; a clean diff between the two pages means the copy succeeded. If anything shows up, investigate before claiming done.

### 9. Stop at the file edit

Do not stage, commit, or push. Surface the changed files and the summary of adds/removes/recategorizations to the user; they decide what to do next.

## Notes

- The script requires `gh` (authenticated) and `jq`. If either is missing it fails with a clear message.
- 100+ public repos exist in the org but ~85 are non-archived; expect that range.
- If the script returns zero or wildly off counts, stop and surface the error rather than wiping the page.
- This skill updates two paths: `content/master/learn/community-extension-projects.md` and the matching file under `content/v${LATEST_VERSION}/learn/...` where `${LATEST_VERSION}` comes from `config.yaml`. Older versioned copies (anything other than `master` and the current `latest`) are frozen historical snapshots and should not be touched.
