# Vale Configuration for Crossplane Documentation

## Overview

This directory contains Vale linting configuration for Crossplane documentation. Vale enforces the [Crossplane Writing Style Guide](https://docs.crossplane.io/contribute/writing-style-guide/) and provides automated prose linting for pull requests.

**Current Vale Version:** 3.13.0

## Table of Contents

- [Structure](#structure)
- [Vocabulary Management](#vocabulary-management)
- [Rule Development](#rule-development)
- [Base Styles](#base-styles)
- [Testing](#testing)
- [Disabling Rules](#disabling-rules)
- [Common Issues](#common-issues)
- [Maintenance](#maintenance)
- [CI/CD Integration](#cicd-integration)
- [Resources](#resources)

## Structure

```
utils/vale/
├── .vale.ini                    # Main configuration (includes Packages directive)
├── README.md                    # This file
├── scripts/                     # Maintenance utilities
│   ├── check-vocab.sh          # Vocabulary health checks
│   └── add-term.sh             # Interactive term addition
└── styles/
    ├── .gitignore              # Excludes package-managed styles from git
    ├── alex/                   # Package-managed (downloaded by vale sync)
    ├── proselint/              # Package-managed (downloaded by vale sync)
    ├── write-good/             # Package-managed (downloaded by vale sync)
    ├── config/
    │   └── vocabularies/
    │       └── Crossplane/
    │           └── accept.txt   # Accepted terminology (418 terms)
    └── Crossplane/              # Custom Crossplane rules
        ├── Acronyms.yml        # Acronym usage (85 exceptions)
        ├── ComplexWords.yml    # Simplified word preferences
        ├── CorporateSpeak.yml  # Avoid marketing jargon
        ├── ReadingLevel.yml    # Target grade level 12.5
        └── Spelling.yml        # Spelling check (uses Vocab)
```

## Vocabulary Management

### accept.txt Hierarchy

The consolidated vocabulary file (`accept.txt`) contains 418 unique terms organized by category:

1. **Crossplane terminology** - XRD, MRD, MRAP, CompositeResourceDefinition, etc.
2. **Kubernetes terms** - Pod, ConfigMap, ClusterRole, CronJob, etc.
3. **Cloud provider brands** - AWS, Azure, GCP, DigitalOcean, etc.
4. **Cloud-native acronyms** - RBAC, OIDC, OCI, gRPC, etc.
5. **Technical jargon** - API, CLI, SDK, webhook, etc.
6. **Spelling exceptions** - Hyphenated terms, brand-specific capitalization

### When to Add Terms

| Term Type | Where to Add | Example |
|-----------|--------------|---------|
| Crossplane API objects | accept.txt | CompositeResourceDefinition, ProviderConfig |
| Cloud provider terms | accept.txt | EC2, GKE, CloudSQL, S3 |
| Common acronyms | Acronyms.yml exceptions | API, CLI, RBAC (if needing special handling) |
| Corporate speak to avoid | CorporateSpeak.yml tokens | synergy, leverage, circle back |

### What NOT to Add

- Common English words (Vale's default dictionary handles these)
- Terms that should be rewritten (e.g., "utilize" → "use")
- Project-specific abbreviations not in the style guide
- Temporary code names or internal project names

### Adding Terms

**Using the helper script:**
```bash
make vale-add-term
```

**Manual process:**
1. Add term to `accept.txt` in alphabetical order
2. Test: `vale --config=./utils/vale/.vale.ini content/`
3. Commit with justification in commit message

## Rule Development

### Custom Crossplane Rules

#### Acronyms.yml
Checks acronym usage and requires definitions on first use. Contains 85 exceptions for common technical acronyms.

```yaml
extends: conditional
message: "'%s' has no definition."
level: suggestion
scope: text
```

**Exception philosophy:** Include acronyms that are:
- Standard in Kubernetes/cloud-native ecosystem (RBAC, CRD, YAML)
- Widely known to target audience (API, CLI, HTTP, URL)
- Official product names (AWS, GCP, Azure)

#### ComplexWords.yml
Suggests simpler alternatives for complex or wordy expressions.

```yaml
extends: substitution
message: "Consider using '%s' instead of '%s'."
level: suggestion
```

**Based on Microsoft.ComplexWords** but excludes technical terms appropriate for Crossplane documentation (e.g., "provide," "aggregate," "implement").

#### CorporateSpeak.yml
Flags marketing jargon and corporate buzzwords.

```yaml
extends: existence
message: "Avoid using '%s'."
level: error
```

**Philosophy:** Technical documentation should be precise, not promotional.

#### ReadingLevel.yml
Targets Flesch-Kincaid grade level of 12.5 or lower.

```yaml
extends: readability
message: "The grade level is %s. Aim for 12.5 or lower..."
level: suggestion
```

**Rationale:** Technical audience (developers, platform engineers) comfortable with moderate complexity.

#### Spelling.yml
Uses Vale's Vocab feature to check spelling against `accept.txt`.

```yaml
extends: spelling
message: 'Spelling check: "%s"?'
level: error
```

**Note:** Vale's built-in spelling (Vale.Spelling) is disabled in favor of this custom rule.

### Base Styles

#### Package Management

Vale 3.x supports automatic package management for style guides. The following styles are **automatically downloaded** via `vale sync`:

- **alex** - Inclusive language checking
- **proselint** - Writing quality checks
- **write-good** - Readability improvements

These package-managed styles are excluded from git (see `styles/.gitignore`) and must be downloaded before first use:

```bash
vale --config="./utils/vale/.vale.ini" sync
```

**CI automatically runs `vale sync`** before linting, so no manual setup is needed for GitHub Actions.

#### Currently Active (5 styles)

**alex** (10 rules, all enabled) - Package-managed
- Inclusive language checking
- Gender-neutral language
- Minimal overhead, well-aligned with style guide

**Crossplane** (5 rules, all enabled) - Custom
- Custom rules specific to Crossplane documentation
- Primary enforcement of Crossplane Writing Style Guide
- Maintained in this repository

**proselint** (38 rules, mostly enabled) - Package-managed
- Writing quality checks
- Well-suited for technical documentation

**Vale** (built-in, 1 rule disabled)
- Vale.Spelling disabled (using Crossplane.Spelling instead)
- Vale.Terms enabled (auto-generated from Vocab feature)

**write-good** (10 rules, 1 disabled) - Package-managed
- Readability improvements
- Lightweight, effective
- E-Prime disabled (too pedantic for technical docs)

### Rule Naming Convention

- `Crossplane/RuleName.yml` - Custom rules specific to Crossplane
- Match upstream naming when overriding (e.g., `ComplexWords`, `Acronyms`)
- Use descriptive names for new rules (e.g., `CorporateSpeak`, `ReadingLevel`)

### Creating Custom Rules

1. **Extend upstream rules when possible:**
   ```yaml
   extends: substitution
   message: "Consider using '%s' instead of '%s'."
   link: 'https://docs.crossplane.io/contribute/writing-style-guide/'
   ```

2. **Document rationale in comments:**
   ```yaml
   # - 'provide' (technical standard: provide credentials)
   # - 'aggregate' (technical term: Kubernetes ClusterRole aggregation)
   ```

3. **Test thoroughly before committing:**
   ```bash
   # Test specific file
   vale --config=./utils/vale/.vale.ini content/master/path/to/file.md

   # Compare to baseline
   diff <(vale --config=./utils/vale/.vale.ini content/) baseline.txt
   ```

## Testing

### First-Time Setup

Before running Vale for the first time, download the package-managed styles:

```bash
vale --config="./utils/vale/.vale.ini" sync
```

This downloads alex, proselint, and write-good styles from the Vale package hub. The command is idempotent and can be run anytime to update packages.

**Note:** GitHub Actions automatically runs `vale sync` before linting, so no manual setup is needed for CI.

### Local Testing

```bash
# Test specific file
vale --config="./utils/vale/.vale.ini" content/master/path/to/file.md

# Test all changed files (what CI does)
vale --config="./utils/vale/.vale.ini" $(git diff --name-only master...HEAD | grep "^content/")

# Test all documentation
vale --config="./utils/vale/.vale.ini" content/

# Use Makefile shortcuts
make vale-test           # Test all content
make vale-test-changed   # Test only changed files
```

### Validation

```bash
# List active rules and configuration
vale ls-config

# Check vocabulary health
make vale-check

# Show Vale version
vale --version

# Debug specific file
vale --config="./utils/vale/.vale.ini" --debug content/master/_index.md
```

### Makefile Commands

```makefile
make vale-check          # Run vocabulary maintenance checks
make vale-add-term       # Interactively add a term to vocabulary
make vale-test           # Test all documentation with Vale
make vale-test-changed   # Test only changed files (what CI does)
```

## Disabling Rules

### In Configuration

Disable rules in `.vale.ini` when they conflict with Crossplane style:

```ini
# Disable Vale's built-in spelling - using custom Crossplane.Spelling instead
Vale.Spelling = NO

# Vale.Terms is enabled - Vocab feature auto-generates this rule for term consistency
# (No need to explicitly enable - it's enabled by default when Vocab is configured)

# Disable E-Prime (avoid "to be" verbs) - too pedantic for technical docs
write-good.E-Prime = NO
```

**Always document why a rule is disabled in comments.**

### In Content

Use Vale comments sparingly and always with justification:

**Disable all rules:**
```markdown
<!-- vale off -->
Content to ignore (e.g., API examples with special formatting)
<!-- vale on -->
```

**Disable specific rule:**
```markdown
<!-- vale Microsoft.Contractions = NO -->
Do not use contractions in this specific section.
<!-- vale Microsoft.Contractions = YES -->
```

**Important:**
- Vale requires capitalization for `YES` and `NO`
- Requires space around `=` (e.g., `= NO`, not `=NO`)
- Always re-enable rules after disabled content
- Document why the rule is disabled in a comment

### Exception Hierarchy

When a term triggers false positives:

1. **Check if it's a spelling issue** → Add to `accept.txt`
2. **Check if it's an acronym needing special handling** → Add to `Acronyms.yml` exceptions
3. **Check if it's a word substitution issue** → Update `ComplexWords.yml`
4. **Last resort** → Use inline Vale comments in content

## Common Issues

### Vale Errors with Hugo Shortcodes

Hugo shortcodes can trigger false positives. Ensure proper spacing:

```markdown
<!-- Incorrect: No space between quote and angle bracket -->
{{< expand "Title"*/>}}

<!-- Correct: Space before closing angle bracket -->
{{< expand "Title" */>}}
```

### Markdown Link Styling

```markdown
<!-- Incorrect: Styling outside brackets -->
_[error]_

<!-- Correct: Styling inside brackets -->
[_error_]
```

### Line Breaks in Links

Avoid line breaks in markdown links and Hugo ref shortcodes:

```markdown
<!-- Incorrect -->
[Link text]({{< ref "master/
  path/to/page.md" >}})

<!-- Correct -->
[Link text]({{< ref "master/path/to/page.md" >}})
```

### Passive Voice Warnings

Vale flags passive voice heavily (Google.Passive and Microsoft.Passive both trigger).

**Strategy:**
- Technical documentation sometimes needs passive voice (e.g., "is managed by Kubernetes")
- Review each case: can it be rewritten in active voice without losing clarity?
- If passive voice is clearer or more accurate for the context, it's acceptable

## Maintenance

### Vocabulary Maintenance

**Check vocabulary health:**
```bash
make vale-check
```

This checks for:
- Duplicate entries
- Unsorted entries
- Terms in both accept.txt and rule exceptions
- Statistics on vocabulary size

**Add new terms:**
```bash
make vale-add-term
```

Interactive prompt guides you through:
1. Enter the term
2. Select category
3. Automatic sorting
4. Testing guidance

### Updating Package-Managed Styles

Package-managed styles (alex, proselint, write-good) can be updated to their latest versions:

```bash
vale --config="./utils/vale/.vale.ini" sync
```

This downloads the latest versions from the Vale package hub. Review changes before committing to ensure compatibility.

### Updating Rules

1. Make changes to rule files in `styles/Crossplane/`
2. Run full test suite: `make vale-test`
3. Compare results to baseline: `diff current.txt baseline.txt`
4. Document changes in commit message
5. Update this README if behavior changes

### Adding New Base Styles

**Not recommended.** Current configuration already includes 7 base styles with 66 total rules.

If absolutely necessary:
1. Evaluate overlap with existing rules
2. Test on all documentation to understand impact
3. Document why the new style is needed
4. Add explicit disables for conflicting rules
5. Update this README with rationale

## CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/vale.yml`

**Workflow steps:**
1. Checkout repository
2. Get changed files in `content/**`
3. Run Vale on changed files using `errata-ai/vale-action@reviewdog`
   - Automatically downloads and caches Vale binary
   - Automatically syncs package-managed styles
   - Posts inline PR comments for any warnings

**Benefits:**
- Inline PR comments show Vale warnings directly on changed lines
- Automatic package syncing (no manual `vale sync` needed)
- Automatic binary caching (faster than manual installation)
- Official `errata-ai/vale-action@reviewdog` maintained by Vale team

**Testing workflow locally:**
```bash
# Same command CI uses
vale --config="./utils/vale/.vale.ini" $(git diff --name-only master...HEAD | grep "^content/")
```

### Vale Action Configuration

```yaml
- name: Run Vale on changed files
  uses: errata-ai/vale-action@reviewdog
  with:
    version: 3.13.0
    files: ${{ steps.changed-files.outputs.all_changed_files }}
    reporter: github-pr-review
    fail_on_error: true
    filter_mode: nofilter
    vale_flags: '--config=./utils/vale/.vale.ini'
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Configuration notes:**
- `reporter: github-pr-review` - Inline comments on PR
- `fail_on_error: true` - Warnings treated as errors
- `filter_mode: nofilter` - Show all issues, not just diff context

## Troubleshooting

### Vale reports errors on correct content

1. **Check if it's a Crossplane term:** Add to `accept.txt`
2. **Check if it's a false positive:** File an issue with example
3. **Check if rule is appropriate:** Consider disabling in `.vale.ini`

### Vale crashes or fails to run

1. **Check Vale version:** `vale --version` (should be 3.13.0+)
2. **Validate config:** `vale ls-config`
3. **Check for syntax errors in rule files:** YAML parsing errors
4. **Check file permissions:** Vale needs read access to all style files

### CI passes locally but fails in GitHub Actions

1. **Check Vale version:** CI uses version from workflow file
2. **Check changed files:** CI only tests changed content files
3. **Check configuration path:** Must use `--config=./utils/vale/.vale.ini`
4. **Review workflow logs:** Look for config validation errors

### Vocabulary terms not being recognized

1. **Check spelling:** `accept.txt` is case-sensitive by default (but Vocab feature handles this)
2. **Check sorting:** Run `make vale-check` to verify file is sorted
3. **Check Vocab configuration:** `.vale.ini` should have `Vocab = Crossplane`
4. **Test with specific file:** `vale --config=./utils/vale/.vale.ini --debug file.md`

## Resources

### Vale Documentation

- [Vale Documentation](https://vale.sh/docs/) - Official Vale docs
- [Vale Vocab Feature](https://vale.sh/docs/topics/vocab/) - Vocabulary management
- [Vale Package Hub](https://vale.sh/hub/) - Downloadable style packages
- [Vale GitHub Action](https://github.com/errata-ai/vale-action) - CI integration

### Crossplane Documentation

- [Crossplane Writing Style Guide](https://docs.crossplane.io/contribute/writing-style-guide/)
- [Crossplane Contributing Guide](https://docs.crossplane.io/contribute/)
- [Hugo Documentation](https://gohugo.io/documentation/) - Static site generator

### Style Guides

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
- [alex Inclusive Language](https://alexjs.com/)

---

**Last Updated:** November 2025
**Maintained by:** Crossplane Documentation Team
**Questions?** File an issue or ask in #docs channel
