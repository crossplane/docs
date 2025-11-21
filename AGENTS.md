# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the Crossplane documentation repository. It's a Hugo-based static site that hosts versioned documentation at https://docs.crossplane.io. The documentation is built with Hugo, styled with Bootstrap, and deployed via Netlify.

## Repository Structure

- **`content/`** - All documentation content organized by version
  - `master/` - Next release documentation (unreleased)
  - `v2.1/`, `v2.0/`, `v1.20/`, etc. - Version-specific documentation
  - `contribute/` - Contributing guide (version-agnostic)
  - `media/` - Shared media assets
- **`themes/geekboot/`** - Hugo theme (based on Geekdoc)
  - `layouts/` - HTML templates
  - `assets/` - SCSS source files
  - `static/` - Static assets
- **`utils/`** - Build and testing utilities
  - `vale/` - Prose linting configuration
  - `htmltest/` - Link validation configuration
  - `webpack/` - JavaScript bundling
- **`config.yaml`** - Hugo configuration
- **`netlify.toml`** - Netlify build and redirect configuration
- **`netlify_build.sh`** - Build script that creates `/latest` from current version

## Development Commands

### Local Development
```bash
# Start Hugo development server (requires Hugo Extended)
hugo server

# Server runs at http://localhost:1313
# Changes auto-reload
```

### Building
```bash
# Standard build (for local testing)
hugo --environment development

# Production build (requires Hugo Extended + writeStats enabled)
# This is what Netlify runs:
bash netlify_build.sh
```

### Testing

#### Prose Linting with Vale
```bash
# Lint specific files
vale --config="./utils/vale/.vale.ini" content/master/path/to/file.md

# Lint all changed files (what CI does)
vale --config="./utils/vale/.vale.ini" $(git diff --name-only master...HEAD | grep "^content/")
```

Vale checks against multiple style guides (alex, Google, Microsoft, proselint, write-good, Crossplane, gitlab).

#### Link Validation
```bash
# Build site first
hugo --environment development

# Run htmltest (requires htmltest binary)
htmltest --conf ./utils/htmltest/.htmltest.yml
```

### Asset Building

#### JavaScript
```bash
cd utils/webpack
npm install
npm run prod  # Production build
npm run dev   # Development build
```

#### CSS
CSS is processed by Hugo + PostCSS during the Hugo build. The build:
1. Compiles Bootstrap SCSS
2. Runs PurgeCSS (removes unused styles using `hugo_stats.json`)
3. Sorts media queries (desktop-first)
4. Minifies with LightningCSS

PostCSS only runs when `build.writeStats: true` is enabled in `config.yaml` (uncommented during Netlify builds).

## Architecture

### Versioning System

Each Crossplane version has its own content directory. The version is set in front matter:

```yaml
---
title: "Page Title"
cascade:
    version: "2.1"
---
```

During Netlify builds, `netlify_build.sh` copies the latest version (currently `v2.1`) to `content/latest/` for search indexing.

The version dropdown links pages by matching titles across versions. Use `matchTitle` in front matter if a page title changes:

```yaml
title: New Title
matchTitle: Original Title
```

### Front Matter Requirements

Every page requires:
```yaml
---
title: "Page Title"
weight: 100  # Controls ordering in navigation (lower = higher)
---
```

Optional fields:
- `description:` - SEO metadata
- `state:` - `alpha` or `beta` for feature state
- `alphaVersion:` / `betaVersion:` - Version tracking
- `tocHidden: true` - Hide from navigation

### Hugo Configuration

- **Theme**: Custom `geekboot` theme (Geekdoc + Bootstrap)
- **Hugo version**: 0.147.3 (defined in `netlify.toml`)
- **Markup**: Goldmark with `unsafe: true` (allows HTML in markdown)
- **Module mounts**: Images and YAML files from `content/` are mounted to `assets/` for compile-time processing

### CRD Documentation

CRD YAML files live in `content/[version]/api/crds/*.yaml` and are processed by Hugo's data pipeline for API reference generation.

## Writing Style Guide

### Core Writing Rules

- **Use active voice** - Avoid passive voice; active writing is stronger and more direct
- **Use sentence-case headings** - More casual and approachable
- **Wrap lines at 80 characters** - Improves review feedback
- **Use present tense** - Avoid "will"; docs cover actions happening now
- **Spell out numbers less than 10** - Except for percentages, time and versions
- **Capitalize "Crossplane" and "Kubernetes"** - Proper nouns; don't use `k8s`
- **Spell out acronyms on first use** - Unless common to new Crossplane users
- **Use contractions** - "don't" instead of "do not" (easier to read)
- **No Latin terms** - Don't use i.e., e.g., etc.
- **Avoid gerund headings** - Don't use -ing words in headings
- **Limit sentences to 25 words or fewer** - Improves readability and SEO
- **Be descriptive in link text** - Don't use "click here" or "read more"
- **Order brand names alphabetically** - AWS, Azure, GCP (removes appearance of preference)
- **Avoid "easy," "simple," or "obvious"** - Can be condescending
- **No Oxford commas** - No commas before "and" or "or"
- **U.S. English spelling** - Always

### Kubernetes Object Naming

- **Kinds**: Upper camel case with no separators (e.g., `MyComputeResource`)
- **Names**: Snake case with dashes (e.g., `my-resource`)
- **Inline references**: No special styling required unless drawing special attention

### Formatting

- **Italics**: Use `_italics_` to introduce or draw attention to a term (use sparingly)
- **Inline code**: Use single backticks (`` ` ``) for files, directories, paths, or commands in sentences
- **Placeholders**: Use angle brackets with underscores between words (e.g., `<aws_access_key>`)

## Code Styling Guide

### Fenced Code Blocks

**Always use fenced code blocks with language hints:**

````markdown
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
```
````

**Never:**
````markdown
```
# code without language hint
```
````

**Supported languages**: See [Chroma documentation](https://github.com/alecthomas/chroma/#supported-languages)

**Important**: Optimize language hints for display, not technical correctness. Use `yaml` instead of `shell` if it improves readability.

### Static Line Highlighting

Highlight specific lines with `{hl_lines=<line number>}`:

````yaml
```yaml {hl_lines=1}
apiVersion: pkg.crossplane.io/v1
kind: Provider
```
````

- Continuous blocks: `{hl_lines="1-4"}`
- Multiple lines/blocks: `{hl_lines=[1,2,"4-6"]}`

### Dynamic Line Highlighting (Hover)

1. Add a label to the code fence:
````yaml
```yaml {label=example}
apiVersion: pkg.crossplane.io/v1
kind: Provider
```
````

2. Use the `hover` shortcode to trigger highlighting:
```html
{{</* hover label="example" line="2" */>}}kind{{</* /hover */>}}
```

**Note**: Don't use quotes around the label name.

### Custom Copy Button

Customize which lines are copied to clipboard:

- Copy specific range: `{copy-lines="2-5"}`
- Copy single line: `{copy-lines="3"}`
- Copy all: `{copy-lines="all"}`
- Disable copy: `{copy-lines="none"}`

**Important**: Line number range must be in quotations.

Combine with highlighting:
````yaml
```yaml {copy-lines="2-5", hl_lines="2-3"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
```
````

### Editable Fields

Make fields editable for readers:

````go
{{</* editCode */>}}
```ini {copy-lines="all"}
[default]
aws_access_key_id = $@<aws_access_key>$@
aws_secret_access_key = $@<aws_secret_key>$@
```
{{</* /editCode */>}}
````

Wrap editable elements in `$@<placeholder>$@`.

## Hugo Shortcodes

### Expand (Collapsible Content)

Hide verbose outputs by default:

```html
{{</* expand "A large XRD" */>}}
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
```
{{</* /expand */>}}
```

**Requires closing tag** - Unclosed tags cause Hugo to fail.

### Hints and Alert Boxes

Four types of hint boxes:

```html
{{</* hint "note" */>}}
Notes are useful for calling out optional information.
{{</* /hint */>}}

{{</* hint "tip" */>}}
Use tips to provide context or a best practice.
{{</* /hint */>}}

{{</* hint "important" */>}}
Important hints are for drawing extra attention to something.
{{</* /hint */>}}

{{</* hint "warning" */>}}
Use warning boxes to alert users of things that may cause outages, lose data or are irreversible changes.
{{</* /hint */>}}
```

**Requires closing tag**.

### Images

**Strongly recommended** to use `img` shortcode instead of standard markdown:

```html
{{</* img src="/media/banner.png" alt="Crossplane Popsicle Truck" size="small" */>}}
```

- Automatically converts to webp format
- Compresses images
- Uses responsive sizing
- **Does not support SVG files**

**Sizes**: `xtiny` (150px), `tiny` (320px), `small` (600px), `medium` (1200px), `large` (1800px)

**Source path**: Relative to `/content`

### Links

**Between docs pages** - Use Hugo `ref` shortcode:

```markdown
[Link text]({{</* ref "master/_index.md" */>}})
```

- Include `.md` extension
- Hugo fails if ref points to non-existent page
- Path relative to `/content`

**External links** - Use standard markdown:

```markdown
[Go to Crossplane](http://crossplane.io)
```

### Tables

Wrap markdown tables in `table` shortcode for proper styling:

```markdown
{{</* table */>}}
| Title | A Column | Another Column |
| ---- | ---- | ---- |
| Content | more content | even more content |
{{</* /table */>}}
```

**Requires closing tag**.

**Striped rows**: `{{</* table "table table-striped" */>}}`
**Compact tables**: `{{</* table "table table-sm" */>}}`

### Tabs

For presenting multiple exclusive options (e.g., CLI vs GUI):

```html
{{</* tabs */>}}

{{</* tab "First tab title" */>}}
Content for first tab
{{</* /tab */>}}

{{</* tab "Second tab title" */>}}
Content for second tab
{{</* /tab */>}}

{{</* /tabs */>}}
```

**Both `tab` and `tabs` require closing tags**.

## Vale Linting

Vale enforces the style guide. **Warnings are treated as errors.**

### Running Vale

```bash
# All documentation
vale --config="utils/vale/.vale.ini" content/

# Single file
vale --config="utils/vale/.vale.ini" content/contribute/writing-style-guide.md

# Changed files only (what CI does)
vale --config="./utils/vale/.vale.ini" $(git diff --name-only main...HEAD | grep "^content/")
```

### Vale Styles Used

- **alex** - Insensitive, inconsiderate writing
- **GitLab** - GitLab documentation style guide
- **Google** - Google developer documentation style guide
- **Microsoft** - Microsoft style guide
- **proselint** - Higher quality writing
- **Crossplane** - Spelling exceptions for Kubernetes/Crossplane terms
- **write-good** - Higher quality writing

### Spelling Exceptions

Add spelling exceptions to `utils/vale/styles/Crossplane/`:
- `allowed-jargon.txt` - Technical terms
- `brands.txt` - Brand and product names
- `crossplane-words.txt` - Crossplane-specific words
- `provider-words.txt` - Provider-related words
- `spelling-exceptions.txt` - English words incorrectly flagged

### Disabling Vale Rules

**Always include justification** and turn rules back on after ignored content.

**Ignore all rules:**
```html
<!-- vale off -->
Content to ignore
<!-- vale on -->
```

**Ignore specific rule:**
```html
<!-- vale Microsoft.Contractions = NO -->
Do not turn off rules without good reasons.
<!-- vale Microsoft.Contractions = YES -->
```

**Important**:
- Vale requires capitalization for `YES` and `NO`
- Requires space around `=`

**Common issues that trigger Vale errors:**
- Hugo shortcodes without space between quote and angle bracket: `{{</* expand "Title"*/>}}`
- Markdown links containing line breaks
- Hugo `{{</* ref */>}}` links containing line breaks
- Markdown link styling outside square brackets: `_[error]_` (use `[_works_]` instead)

## Creating New Content

1. **Create markdown file** in appropriate version directory (e.g., `content/master/`)
2. **Add required front matter**:
   ```yaml
   ---
   title: "Page Title"
   weight: 100  # Lower = higher in navigation
   ---
   ```
3. **Optional front matter**:
   ```yaml
   description: "SEO metadata"
   state: alpha  # or beta
   alphaVersion: "1.11"
   betaVersion: "1.12"
   tocHidden: true  # Hide from navigation
   matchTitle: "Old Title"  # If title changed
   ```
4. **Use `_index.md`** for section landing pages
5. **Reference other pages** with `{{<ref "path/to/page.md">}}`
6. **Headings**: Top level (`#`) is page title; content headings start at `##`

## CI/CD

### GitHub Actions

- **Vale workflow** - Runs on content changes, validates prose style
- **Link checker** - Builds site and validates links with htmltest
- **Weekly link checker** - Scheduled external link validation

### Netlify

- **Production**: Builds from `master` branch → https://docs.crossplane.io
- **Deploy previews**: Automatic for all PRs
- **Branch deploys**: Automatic for non-PR branches

All builds run `netlify_build.sh` which handles version copying and baseURL configuration.

## Important Notes

- **Always use Hugo Extended**: Standard Hugo doesn't support SCSS compilation
- **Version-specific changes**: Must be applied to each version directory separately
- **Master is next release**: Content in `content/master/` represents unreleased documentation
- **Latest version**: Currently `2.1` (set in `netlify_build.sh` and `config.yaml`)
- **No local PostCSS**: PostCSS optimizations only run during Netlify builds unless you manually enable `writeStats` in config.yaml
- **Vale warnings are errors**: All Vale warnings must be resolved before merging
- **80 character line wrapping**: All markdown content should wrap at 80 characters
- **Shortcode closing tags**: All shortcodes with opening tags require closing tags or Hugo will fail to build
