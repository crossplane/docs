# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

This is the repository for the [Crossplane documentation](https://docs.crossplane.io).
The documentation site is built using [Hugo](https://gohugo.io/) and hosted on
Netlify. The site provides comprehensive documentation for Crossplane, a cloud
native control plane framework.

## Development Commands

### Local Development
- `hugo server` - Start local development server on http://localhost:1313
- `hugo server --minify` - Start server with minified output
- `hugo --minify` - Build static site with minified output

### Prerequisites
- Hugo Extended version (required for SCSS/CSS processing)
- Node.js and npm (for PostCSS processing)
- Git (for content management)
- Vale (for style linting)

### Nix Development Environment
For Nix users, a `shell.nix` file is provided with all necessary dependencies:

```bash
nix-shell  # Enter development environment with Hugo, Vale, Node.js, and utilities
```

The Nix shell includes:
- Hugo (extended version)
- Vale prose linter
- Node.js 20 with npm
- HTML validation tools
- Image processing utilities (ImageMagick)
- JSON/YAML processing tools (jq, yq)

### Building and Deployment
- Site automatically builds on Netlify using `netlify_build.sh`
- Uses Hugo version 0.119.0 (specified in netlify.toml)
- Production URL: https://docs.crossplane.io/
- Preview deployments available for PRs

## Repository Structure

### Content Organization
- `content/` - All documentation content organized by version
  - `v1.18/`, `v1.19/`, `v1.20/` - Version-specific documentation
  - `master/` - Next release documentation
  - `v2.0-preview/` - Preview documentation for v2.0
  - `contribute/` - Contributing guidelines and style guides
- `static/` - Static assets (images, icons, etc.)
- `themes/geekboot/` - Custom Hugo theme based on Geekdoc and Bootstrap
- `utils/` - Development utilities (Vale style checking, webpack config)

### Key Configuration Files
- `config.yaml` - Hugo site configuration
- `netlify.toml` - Netlify build and deployment configuration
- `netlify_build.sh` - Custom build script for version management
- `package.json` - PostCSS dependencies for CSS optimization

## Documentation Architecture

### Version Management
- Each Crossplane version has its own content directory
- Latest version (currently 1.20) is copied to `/latest` during build
- Version dropdown menu allows switching between versions
- Automatic redirects for EOL versions

### Content Types
- **Getting Started** - Installation and basic usage guides
- **Concepts** - Core Crossplane concepts and architecture
- **Guides** - How-to guides and advanced usage patterns
- **API Reference** - CRD documentation generated from YAML
- **CLI Reference** - Command reference documentation

### Hugo Features Used
- Custom shortcodes for enhanced functionality (tabs, hints, code highlighting)
- Front matter for metadata (version, weight, state, descriptions)
- Table of contents generation
- Syntax highlighting with line numbers
- Image optimization and processing
- RSS feeds for sections

## Writing Guidelines

### Style Guide Essentials
- Use active voice, avoid passive voice
- Present tense, avoid "will"
- Sentence-case headings
- Wrap lines at 80 characters
- Spell out numbers less than 10
- Use contractions (don't, can't, isn't)
- No Oxford commas
- U.S. English spelling and grammar
- Capitalize "Crossplane" and "Kubernetes" (never "k8s")

### Content Structure
- Each page requires front matter with `title` and `weight`
- Use `state: alpha` or `state: beta` for feature lifecycle
- Include `alphaVersion` and `betaVersion` for feature tracking
- Use descriptive link text, avoid "click here"
- Order brand names alphabetically (AWS, Azure, GCP)

### Code and Technical Content
- Use inline code style (backticks) for files, directories, paths
- Use angle brackets for placeholders (`<placeholder_name>`)
- Kubernetes objects: use UpperCamelCase for Kinds, kebab-case for names
- Use hover shortcodes to relate explanations to code examples

## Development Workflow

### Contributing Process
1. Clone the repository: `git clone https://github.com/crossplane/docs.git`
2. Set up development environment:
   - **With Nix**: Run `nix-shell` to enter development environment
   - **Without Nix**: Install Hugo Extended, Vale, and Node.js manually
3. Run `hugo server` for local development
4. Make changes to appropriate version directory in `/content`
5. Test locally at http://localhost:1313
6. Run `vale content/` to check style compliance
7. Submit PR for review

### Content Management
- Create new content as markdown files in appropriate version directories
- Use `_index.md` for section landing pages
- Include proper front matter for all pages
- Test with Vale linter for style compliance
- Images should be optimized and placed in appropriate directories

### Quality Assurance
- Vale linter enforces style guide compliance
- HTML validation with htmltest
- Automated Netlify preview deployments for all PRs
- Manual review process for content accuracy

## Build System Details

### Hugo Configuration
- Uses custom "geekboot" theme (based on Geekdoc + Bootstrap)
- Goldmark renderer with unsafe HTML enabled
- Syntax highlighting with line numbers and anchor links
- Module mounts for content and asset processing
- Table of contents generation (levels 1-9)

### CSS and Assets
- PostCSS with PurgeCSS for optimization
- Custom SCSS in theme directory
- Responsive design with Bootstrap framework
- Font loading for Avenir and Consolas
- Icon system with SVG assets

### Netlify Integration
- Environment-specific base URLs
- Automatic redirects for moved/deprecated content
- Build optimization with writeStats for PurgeCSS
- Deploy preview URLs for testing

## Common Tasks

### Adding New Documentation
1. Create markdown file in appropriate version directory
2. Add front matter with title, weight, and optional state
3. Follow style guide for writing
4. Add to multiple versions if needed
5. Test locally with Hugo server

### Version Management
- Copy content between version directories as needed
- Update version references in netlify_build.sh
- Ensure redirects are configured for moved content
- Test version switching functionality

### Style and Linting
- Run Vale linter: `vale content/`
- Check for style guide compliance
- Validate HTML structure
- Ensure proper image optimization

## Important Files

- `config.yaml` - Hugo site configuration and parameters
- `netlify_build.sh` - Build script with version management logic
- `shell.nix` - Nix development environment with all dependencies
- `content/contribute/` - Comprehensive contributing guidelines
- `themes/geekboot/layouts/` - Hugo templates and partials
- `utils/vale/` - Vale style checking configuration

## Vale Linting Guidelines

**CRITICAL: The documentation uses Vale for strict style enforcement. ALL errors and warnings MUST be fixed before merging. Writing Vale-compliant content from the start saves significant time - fixing linting issues after writing is much more time-consuming than avoiding them initially.**

Here are common issues to avoid:

### Common Vale Errors

**Spelling Issues:**
- **API field names**: Put in backticks (`lastScheduleTime`) rather than adding to dictionaries
- **Technical terms**: Add Crossplane-specific terms to `utils/vale/styles/Crossplane/crossplane-words.txt`
- **General tech terms**: Add to `utils/vale/styles/Crossplane/allowed-jargon.txt` 
- **Hyphenated terms**: Add to `utils/vale/styles/Crossplane/spelling-exceptions.txt`
- **Resource kinds**: When referring to Kubernetes resource kinds (Operation, CronOperation), these are correct - use Vale disable comments for false positives

### Common Vale Warnings

**Headings:**
- Use sentence-case, not title-case: "How operations work" not "How Operations Work" 
- Exception: Technical terms like CronOperation in headings need disable comments
- Use `<!-- vale Google.Headings = NO -->` around technical headings

**Word Choice Issues:**
- **Weasel words**: Avoid "many", "various", "numerous" → use "several", "multiple", "some"
- **Too wordy**: "terminate" → "stop", "monitor" → "check" (unless monitoring is the correct technical term)
- **Future tense**: "won't start" → "don't start", avoid "will" → use present tense

**Passive Voice:**
- "Operations are designed for" → "Operations focus on"
- "may be terminated" → "may stop"
- "being watched" → "under watch"
- "is needed" → "you need"

**Other Issues:**
- **Ordinal numbers**: "1st" → "first" 
- **Adverbs**: Remove "gracefully", "correctly", "properly", "repeatedly"
- **Contractions**: Use "can't" instead of "cannot"

### Vale Disable Comments

Use disable comments for legitimate technical terms that trigger false positives:

```markdown
<!-- vale Google.Headings = NO -->
### CronOperation
<!-- vale Google.Headings = YES -->

<!-- vale write-good.TooWordy = NO -->
Monitor resource usage carefully.
<!-- vale write-good.TooWordy = YES -->
```

### Dictionary Management

- **`crossplane-words.txt`**: Crossplane-specific terms only (CronOperation, XRD, etc.)
- **`allowed-jargon.txt`**: General technical terms (kubectl, ConfigMap, etc.)
- **`spelling-exceptions.txt`**: Hyphenated terms (day-two, self-signed, etc.)
- Keep all dictionaries sorted alphabetically

### Testing Vale

**ALWAYS run Vale before considering documentation complete:**

```bash
# Check only warnings and errors (ignore suggestions)
vale --minAlertLevel=warning content/

# Get structured output for analysis
vale --output=JSON content/ | jq '.[][] | select(.Severity == "warning")'
```

**Remember: Writing documentation that follows these guidelines from the start is much faster than writing first and fixing Vale issues later. The time investment in learning these patterns pays off immediately.**

## Session Management

- **Pre-Compaction Analysis**: Before compacting chat history, provide a
  structured session summary including:
  - Documentation updates made and their impact
  - Important learnings about Hugo, documentation patterns, or writing guidelines
  - Potential updates to CLAUDE.md based on new documentation features or workflows
  - Any recurring style or technical issues encountered