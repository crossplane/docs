---
title: Docs Infrastructure
weight: 600
description: "Learn how the docs and our tools are built"
---

The Crossplane document website is in a unique [website GitHub
repository](https://github.com/crossplane/docs).

Crossplane uses [Hugo](https://gohugo.io/), a static site generator. Hugo
influences the directory structure of the website repository.

The `/content` directory is the root directory for all documentation content.

The `/themes/geekboot` directory is the root directory for all website related
files, like HTML templates, shortcodes and global media files.

The `/utils/` directory is for JavaScript source code and files unrelated to
Hugo used in the website.

The `/themes/geekboot/assets` folder contains all (S)CSS and compiled JavaScript
for the website.

## CSS
Crossplane documentation uses [Bootstrap
5.2](https://getbootstrap.com/docs/5.2/getting-started/introduction/).
Unmodified Bootstrap SCSS files are in
`/themes/geekboot/assets/scss/bootstrap/`. Any docs-specific overrides are in
per-element SCSS files located one directory higher in
`/themes/geekboot/assets/scss/`.

{{<hint "important" >}}
Don't edit the original Bootstrap stylesheets. It makes the ability to
upgrade to future Bootstrap versions difficult or impossible.
{{< /hint >}}

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
`/themes/geekboot/assets/scss/light-mode.scss`.

{{<hint "note" >}}
When creating new styles rely on variables for any color function, even if both
themes share the color.
{{< /hint >}}

### SCSS compilation
Hugo compiles the SCSS to CSS. Local development doesn't require SCSS installed.

For local development (when using `hugo server`) Hugo compiles SCSS without
any optimizations.

For production (publishing on Netlify or using `hugo server
--environment production`) Hugo compiles SCSS and optimizes the CSS with
[PostCSS](https://postcss.org/). The PostCSS configuration is in
`/postcss.config.js`. The optimizations includes:
* [postcss-lightningcss](https://github.com/onigoetz/postcss-lightningcss) - for
  building, minimizing and generating a source map.
* [PurgeCSS](https://purgecss.com/plugins/postcss.html) - removes unused styles
  to reduce the CSS file size. 
* [postcss-sort-media-queries](https://github.com/yunusga/postcss-sort-media-queries)- 
to organize and reduce CSS media queries to remove duplicate and unused
    CSS.

Optimizing CSS locally with PostCSS requires installing extra packages.
* [Sass](https://sass-lang.com/install)
* [NPM](https://www.npmjs.com/)
* NPM packages defined in `/package.json` with `npm install`.


## JavaScript
A goal of the documentation website is to use as little JavaScript as possible. Unless
the script provides a significant improvement in performance, capability or user
experience. 

To make local development there are no run-time dependencies for
JavaScript. 

Runtime JavaScript is in `/themes/geekboot/assets/js/`. [Webpack](https://webpack.js.org/)
has bundled, minified and compressed the JavaScript.

The source JavaScript is in `/utils/webpack/src/js` and
requires [Webpack](https://webpack.js.org/) to bundle and optimize the code.

* `colorMode.js` provides the ability to change the light/dark mode color theme.
* `tabDeepAnchor.js` rewrites anchor links inside tabs to open a tab and present
  the anchor. 
* `globalScripts.js` is the point of entry for Webpack to determine all
  dependencies. This bundles [instant.page](https://instant.page/) and
  [Bootstrap's
  JavaScript](https://getbootstrap.com/docs/5.2/getting-started/javascript/).
  
### Bootstrap JavaScript builder
The entire [Bootstrap JavaScript
source](https://github.com/twbs/bootstrap/tree/main/js/src) is in
`/utils/webpack/src/js/bootstrap`. 

Adding a new Bootstrap feature requires importing it in `globalScripts.js`. 

By importing only the necessary Bootstrap JavaScript features, reduces the
bundle size.
## Annotated website tree
Expand the tab below to see an annotated `tree` output of the website repository.

{{<expand >}}
```shell
tree .
├── content                     # Root for all page content
│   ├── contribute
│   ├── knowledge-base
│   ├── master
│   ├── v1.12
│   ├── v1.11
│   └── v1.10
├── themes                      # Entry point for theme-specific designs
│   └── geekboot
│       ├── assets              # JS and stylesheets
│       │   ├── js              # Bundled and optmized Javascript
│       │   └── scss            # Bootstrap SCSS overrides
│       │       └── bootstrap   # Bootstrap original SCSS files
│       ├── data
│       ├── layouts             # HTML layouts and shortcodes
│       │   ├── _default        # HTML layouts for page types
│       │   │   └── _markup     # Hugo render hooks
│       │   ├── partials        # HTML Template elements
│       │   │   ├── icons
│       │   │   └── utils
│       │   └── shortcodes      # Shortcode features
│       └── static              # Static files across the theme.
│           ├── fonts           # Font files
│           └── img             # Global images
└── utils                       # Files unrelated to Hugo
    └── vale                    # Files related to our Vale validation rules
    └── webpack                 # Files managed or related to webpack
        └── src
            └── js
                └── bootstrap/          # Original Bootstrap JavaScript
                └── colorMode.js        # Color theme switcher
                └── customClipboard.js  # Defines where to put a clipboard icon and what to copy
                └── globalScripts.js    # The collection of things to load on all pages
                └── hoverHighlight.js   # Enables hover to highlight
                └── slackNotify.js      # Tooltip to prompt user to join the community Slack
                └── tabDeepAnchor.js    # Enable anchors inside tabs
```
{{</expand>}}