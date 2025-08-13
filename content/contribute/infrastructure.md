---
title: Docs Infrastructure
weight: 600
description: "Learn how the docs and our tools are built"
---

The Crossplane document website is in a standalone
[GitHub repository](https://github.com/crossplane/docs) separate from Crossplane
core.

The Crossplane docs tools consist of:
* [Netlify](https://netlify.com/) - web hosting and DNS provided by the CNCF.
* [Hugo](https://gohugo.io/) - to compile markdown to static HTML.
* [Bootstrap](https://getbootstrap.com/docs/5.2/) - for pre-built CSS options.
* [PostCSS](https://postcss.org/) - for CSS optimization.
* [Webpack](https://webpack.js.org/) - for Javascript optimization.


## Netlify

Builds for production deploys and PR previews are automatically done by Netlify.

{{< hint "note" >}}
The CNCF controls Netlify access.
{{< /hint >}}

Settings for Netlify are inside
[`netlify.toml`](https://github.com/crossplane/docs/blob/master/netlify.toml).

Settings inside the `netlify.toml` file override any settings in the Netlify web
interface.

The
[`build`](https://github.com/crossplane/docs/blob/3e9e10671c32e368f5381d83e406e16bc38c93bc/netlify.toml#L1)
directive defines what Netlify does to build the site.

The
[`HUGO_VERSION`](https://github.com/crossplane/docs/blob/3e9e10671c32e368f5381d83e406e16bc38c93bc/netlify.toml#L7)
settings defines which version of Hugo Netlify uses.

The
[`redirects`](https://github.com/crossplane/docs/blob/3e9e10671c32e368f5381d83e406e16bc38c93bc/netlify.toml#L9)
are server side HTTP redirects for moved pages.

The [Netlify documentation](https://docs.netlify.com/configure-builds/file-based-configuration/)
has more information about configuring `netlify.toml`.

Netlify automatically detects the
[`package.json`](https://github.com/crossplane/docs/blob/master/package.json)
file and loads the listed NodeJS dependencies.

<!-- vale off -->
### netlify_build.sh
<!-- vale on -->

During a build Netlify runs the Bash script
[`netlify_build.sh`](https://github.com/crossplane/docs/blob/master/netlify_build.sh).

The script creates a new docs section called `latest` and copies the defined
`LATEST_VER` to `/latest`.

Next the script enables `writeStats` in the Hugo configuration file.

Then, using the Netlify `$CONTEXT`
[environmental variable](https://docs.netlify.com/configure-builds/environment-variables/#build-metadata)
Hugo runs, defining the [`BaseURL`](https://gohugo.io/methods/site/baseurl/) to
use for generating internal links.

## Hugo
Crossplane uses [Hugo](https://gohugo.io/), a static site generator.

Hugo combines HTML templates, markdown content and generates static HTML
content.

{{<hint "note" >}}
The Hugo web server is only used for local development. Crossplane documentation
uses Netlify for hosting.

Hugo only acts as an HTML compiler.
{{< /hint >}}

Hugo influences the directory structure of the repository.

The `/content` directory is the root directory for all documentation content.

The `/themes/geekboot` directory is the root directory for all website related
files, like HTML templates, shortcodes and global media files.

The `/utils/` directory is for JavaScript source code and files unrelated to
Hugo used in the website.

<!-- vale Google.Headings = NO -->
## CSS
<!-- vale Google.Headings = YES -->

Crossplane documentation uses [Bootstrap 5.2](https://getbootstrap.com/docs/5.2/getting-started/introduction/).

Bootstrap provides multiple prebuilt styles and features making CSS easier.

The docs import _all_ Bootstrap SCSS files and rely on Hugo and PostCSS to
optimize the compiled CSS file.

The unmodified Bootstrap SCSS files are in
`/themes/geekboot/assets/scss/bootstrap/`.

Any docs-specific overrides are in per-element SCSS files located one directory
higher in `/themes/geekboot/assets/scss/`.

{{<hint "important" >}}
Don't edit the original Bootstrap stylesheets. It makes the ability to
upgrade to future Bootstrap versions difficult or impossible.
{{< /hint >}}

The file `/themes/geekboot/assets/scss/docs.scss` defines all the stylesheets
Hugo loads and compiles. Add any new styles to the `docs.scss` file to include
them.

### Color themes
Crossplane docs support a light and dark color theme that's applied via CSS
variables.

<!-- vale off -->
<!-- allowing passive voice to isolate the file path -->
Universal and default variables are defined in
`/themes/geekboot/assets/scss/_variables.scss`.
<!-- vale on -->

Provide theme specific color overrides in
`/themes/geekboot/assets/scss/light-mode.scss` or
`/themes/geekboot/assets/scss/dark-mode.scss`.

{{<hint "note" >}}
When creating new styles, use variables for any colors, even if both
themes share the color.
{{< /hint >}}

<!-- vale Google.Headings = NO -->
### SCSS compilation
<!-- vale Google.Headings = YES -->

Hugo compiles the SCSS to CSS. Local development doesn't require SCSS installed.

For local development (when using `hugo server`) Hugo compiles SCSS without
any optimizations.

In production, when publishing on Netlify or using
`hugo server --environment production`, Hugo compiles SCSS and optimizes the
CSS with [PostCSS](https://postcss.org/).


The PostCSS configuration is in `/postcss.config.js`.

The optimizations includes:
* [postcss-lightningcss](https://github.com/onigoetz/postcss-lightningcss) - for
  building, minimizing and generating a source map.
* [PurgeCSS](https://purgecss.com/plugins/postcss.html) - removes unused styles
  to reduce the CSS file size.
* [postcss-sort-media-queries](https://github.com/yunusga/postcss-sort-media-queries)-
to organize the output CSS for another small performance boost.

#### How optimization works

Crossplane runs a
[different Hugo CSS command](https://github.com/crossplane/docs/blob/3e9e10671c32e368f5381d83e406e16bc38c93bc/themes/geekboot/layouts/partials/stylesheet-dynamic.html#L4)
if it's in local development or production.

Hugo is in "production" when using `hugo` to only build HTML or with
`hugo server --environment production`.

{{<hint "important" >}}
Running Hugo in `production` mode requires the Hugo _extended_ version to
support PostCSS.

Standard Hugo fails to build the documentation.
{{< /hint >}}

<!-- vale Crossplane.Spelling = NO -->
<!-- unoptimized -->
PurgeCSS relies on a JSON file of every HTML tag and CSS class used across the
website and only preserves the matching CSS styles. The resulting file is around
20x smaller than unoptimized CSS.
<!-- vale Crossplane.Spelling = YES -->

Hugo generates the JSON file with the `buildStats` (or `writeStats`)
[configuration setting](https://gohugo.io/getting-started/configuration/#configure-build)
enabled.

{{<hint "important" >}}
Some tags or classes are dynamically created or not always enabled, like light
or dark mode.

Exclude these style sheets from CSS optimization with the
`purgecss start ignore` comment.

For example, the Crossplane documentation ignores the `color-modes` style sheet.

```css
/* purgecss start ignore */
@import "color-modes";
/* purgecss end ignore */
```
{{< /hint >}}

The Crossplane documentation only enables this flag during Netlify builds.
Manually update the `config.yaml` file to enable local optimization.

Optimizing CSS locally with PostCSS requires installing extra packages.
* [Sass](https://sass-lang.com/install)
* [NPM](https://www.npmjs.com/)
* NPM packages defined in `/package.json` with `npm install`.

## JavaScript
A goal of the documentation website is to use as little JavaScript as possible.
Unless the script provides a significant improvement in performance, capability
or user experience.

Local development has no run-time JavaScript dependencies. To prevent
dependencies, making JavaScript changes requires compiling and committing to git.

The source JavaScript is in `/utils/webpack/src/js` and
requires [Webpack](https://webpack.js.org/) to bundle and optimize the code.

Webpack places the compiled JavaScript in `/themes/geekboot/assets/js/` and
updates `/themes/geekboot/data/assets.json` to tell Hugo the new compiled
JavaScript filename.

{{< hint "important" >}}
The JavaScript source in `/utils/webpack/src`, newly compiled JavaScript in
`/themes/geekboot/assets/js` and updated `/themes/geekboot/data/assets.json`
must be in git for production and preview deploys to use the changed JavaScript.
{{< /hint >}}

### JavaScript files
* `bootstrap/` is the entire Bootstrap JavaScript library.
* `colorMode.js` provides the ability to change the light and dark mode color
  theme.
* `customClipboard.js` supports the `copy-lines` code box function.
* `globalScripts.js` is the point of entry for Webpack to determine all
  dependencies. This bundles [instant.page](https://instant.page/) and
  [Bootstrap's JavaScript](https://getbootstrap.com/docs/5.2/getting-started/javascript/).
* `hoverHighlight.js` provides dynamic "hover to highlight" function.
* `slackNotify.js` creates the "Join Crossplane Slack" bubble on the home page.
* `tabDeepAnchor.js` rewrites anchor links inside tabs to open a tab and present
  the anchor.

The `globalScripts.js` file is the entry point for Webpack. Any JavaScript
modules or scripts must be in `globalScripts.js` to get compiled.

#### Building JavaScript

Requirements:
* [NodeJS](https://nodejs.org/en/download) v20.1.2 or later.
* [NPM CLI](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

From the `/utils/webpack` director use `npm` to install the NodeJS dependencies.

```shell
cd utils/webpack
npm install
```

Building JavaScript has two options:
1. `npm run dev`
2. `npm run prod`

Using the `dev` argument doesn't optimize the JavaScript, simplifying
debugging.

Using the `prod` argument optimizes the JavaScript but makes debugging more
difficult.

{{<hint "important" >}}
Always use `npm run prod` to build the compiled JavaScript to use on the
Crossplane documentation site.
{{< /hint >}}

```shell
npm run prod

> prod
> webpack --mode=production

assets by status 80.9 KiB [cached] 1 asset
asset ../../data/assets.json 158 bytes [compared for emit]
orphan modules 180 KiB [orphan] 81 modules
runtime modules 670 bytes 3 modules
cacheable modules 223 KiB
  modules by path ./src/js/*.js 186 KiB
    ./src/js/globalScripts.js + 81 modules 181 KiB [built] [code generated]
    ./src/js/colorMode.js 2.69 KiB [built] [code generated]
    ./src/js/tabDeepAnchor.js 2.31 KiB [built] [code generated]
  modules by path ./node_modules/ 37.6 KiB
    ./node_modules/instant.page/instantpage.js 11.4 KiB [built] [code generated]
    ./node_modules/clipboard/dist/clipboard.js 26.2 KiB [built] [code generated]
webpack 5.89.0 compiled successfully in 1248 ms
```

## Search

[Algolia](https://www.algolia.com/) provides search functionality through their
[DocSearch](https://docsearch.algolia.com/) program.

{{< hint note >}}
Crossplane docs don't use the Netlify Algolia plugin and relies on the
[Algolia Crawler](https://www.algolia.com/doc/tools/crawler/getting-started/overview/) to
discover new content and changes.
{{< /hint >}}

## Sitemap and robots

Hugo generates the `robots.txt`
[automatically](https://gohugo.io/templates/robots/).

For search engine discovery Crossplane uses a `sitemap.xml` file generated from
the [`sitemap.xml` template](https://github.com/crossplane/docs/blob/master/themes/geekboot/layouts/_default/sitemap.xml).

## Link checking

Crossplane checks links with Hugo and
[`htmltest`](https://github.com/wjdp/htmltest).

Hugo builds fail for any broken links in a Hugo `ref` shortcode.

To catch markdown links `htmltest` crawls rendered HTML and validates all
internal links.

On Monday a
[GitHub Action](https://github.com/crossplane/docs/blob/master/.github/workflows/weekly-link-checker.yml)
runs to validate external links with `htmltest`.

The configuration for `htmltest` is in
[`/utils/htmlstest`](https://github.com/crossplane/docs/blob/master/utils/htmltest/.htmltest.yml).


## Annotated website tree
Expand the tab below to see an annotated `tree` output of the website repository.

{{<expand >}}
```shell
├── config.yaml    # Hugo configuration file
├── content        # Root for all page content
│   ├── contribute
│   ├── master
│   ├── media      # Images used in docs pages
│   ├── v1.13
│   ├── v1.14
│   └── v1.15
├── hugo_stats.json   # Generated by Hugo writeStats for PurgeCSS
├── netlify.toml      # Netlify configuration
├── netlify_build.sh  # Custom build script for Netlify
├── package-lock.json # NodeJS dependency version lock
├── package.json      # NodeJS dependencies
├── postcss.config.js # PostCSS configuration
├── static            # Legacy docs site images
├── themes
│   └── geekboot      # The Hugo theme used by Crossplane
│       ├── LICENSE-bootstrap
│       ├── LICENSE-geekdoc
│       ├── assets
│       │   ├── js    # Compiled JavaScript
│       │   └── scss  # Sytlesheets
│       │       └── bootstrap # Unmodified Bootstrap 5.2 SCSS
│       ├── data      # Hugo mapping for JavaScript files. Autogenerated.
│       ├── layouts   # HTML template pages
│       │   ├── 404.html  # 404 page template
│       │   ├── _default
│       │   │   ├── _markup/ # Templates for rendering specific style components
│       │   │   ├── baseof.html        # Entrypoint template for all pages
│       │   │   ├── list.html          # List type pages, see partials/single-list.html
│       │   │   ├── redirect.html      # Provides HTML redirect functions
│       │   │   ├── section.rss.xml    # RSS feed template
│       │   │   ├── single.html        # Single type pages, see partials/single-list.html
│       │   │   └── sitemap.xml        # Sitemap template
│       │   ├── partials  # Template includes
│       │   │   ├── analytics.html  # Analytics and trackers
│       │   │   ├── crds.html       # Entrypoint for API documentation
│       │   │   ├── docs-navbar.html  # Top header links
│       │   │   ├── docs-sidebar.html # left-side navigation menu
│       │   │   ├── favicons.html     # Favicons
│       │   │   ├── feature-state-alert.html  # Alert box for alpha/beta features
│       │   │   ├── footer.html       # Footer copyright and links
│       │   │   ├── ga-tag.html       # Google Analytics
│       │   │   ├── google-analytics.html # Notice for GA release version
│       │   │   ├── header.html       # <head></head> content
│       │   │   ├── icons             # Icons from fontawesome and Crossplane specific
│       │   │   ├── icons.html        # SVG includes common enough to be on every page
│       │   │   ├── left-nav.html     # Left-hand navigation
│       │   │   ├── master-version-alert.html   # Alert box for the master version
│       │   │   ├── mermaid.html      # Styling and JavaScript for mermaid diagrams
│       │   │   ├── meta-common.html  # <meta> tags used on all pages
│       │   │   ├── old-version-alert.html  # Alert box for versions that aren't the latest
│       │   │   ├── preview-version-alert.html  # Alert box for preview versions
│       │   │   ├── redirect.html     # HTML meta redirect
│       │   │   ├── release-notes.html  # Release note summary page generator
│       │   │   ├── scripts.html      # Global JavaScript includes
│       │   │   ├── search-button.html  # Algolia search button
│       │   │   ├── sidebar           # Static links in the left-side nav
│       │   │   ├── single-list.html  # Template used by all single and list type pages
│       │   │   ├── skippy.html       # Shift the page when the target is an anchor link
│       │   │   ├── social.html       # Social media data includes
│       │   │   ├── stylesheet-cached.html  # Static CSS that never changes
│       │   │   ├── stylesheet-dynamic.html # Dynamic CSS that may change between pages
│       │   │   ├── toc.html          # Table of contents modifications
│       │   │   ├── utils             # Utils imported from Geekdoc theme
│       │   │   └── version-dropdown-menu.html  # Version dropdown menu
│       │   └── shortcodes
│       │       ├── check.html        # Produce and style a Checkmark
│       │       ├── editCode.html     # Code box with editable field
│       │       ├── expand.html       # Expand button
│       │       ├── getCRDs.html      # Generate API pages
│       │       ├── hint.html         # Hint boxes
│       │       ├── hover.html        # Hover to highlight
│       │       ├── img.html          # Image optimizer
│       │       ├── include.html      # Include an external file
│       │       ├── markdown.html     # Run content through the markdown engine again
│       │       ├── param.html        # Import from Bootstrap theme
│       │       ├── partial.html      # Import from Bootstrap theme
│       │       ├── placeholder.html  # Import from Bootstrap theme
│       │       ├── propertylist.html # Import from Bootstrap theme
│       │       ├── tab.html          # Individual Tab. Related to tabs.html
│       │       ├── table.html        # Apply bootstrap styles to markdown tables
│       │       ├── tabs.html         # Tab builder, related to tab.html
│       │       ├── url.html          # Create a download link to a file. Used by the APIs
│       │       └── year.html         # Print the current year
│       └── static       # Static global image files
└── utils   # Scripts and tools related to the docs
    ├── htmltest  # htmltest link checker
    ├── vale      # Vale linter
    │   └── styles
    │       ├── Crossplane  # Crossplane spelling exceptions
    │       ├── Google      # Google's Vale rules
    │       ├── Microsoft   # Microsoft's Vale rules
    │       ├── alex        # Write inclusive language
    │       ├── gitlab      # Gitlab's Vale rules
    │       ├── proselint   # Write better
    │       └── write-good  # Write better
    └── webpack   # JavaScript tools
        ├── package-lock.json # NodeJS dependency version lock
        ├── package.json      # NodeJS dependencies
        ├── src
        │   └── js
        │       ├── bootstrap/          # Unmodified Bootstrap JavaScript
        │       ├── colorMode.js        # Color mode switcher
        │       ├── customClipboard.js  # Custom copy-to-clipboard tool
        │       ├── globalScripts.js    # Point of entry for all scripts compiled by Webpack
        │       ├── hoverHighlight.js   # Hover to highlight
        │       ├── slackNotify.js      # "Join Crossplane Slack" bubble
        │       └── tabDeepAnchor.js    # Link inside a tab
        └── webpack.config.js
```
{{</expand>}}