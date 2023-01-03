---
title: Contributing to the Docs
weight: 40
---

Crossplane documentation lives in two repositories:

* Crossplane documentation source is in the [Crossplane
repository](https://github.com/crossplane/crossplane) `/docs` directory. 

* The Crossplane docs website is in the
  [docs](https://github.com/crossplane/docs)
repository.

Use `crossplane/crossplane` for documentation contributions.  
Use `crossplane/docs` for local development or updates involving
HTML, CSS or Hugo.


## Local development
Build the Crossplane documentation site locally for development and
testing. 

### Clone the Crossplane repository
Clone the [Crossplane
repository](https://github.com/crossplane/crossplane) with

```command
git clone https://github.com/crossplane/crossplane.git
```

<!-- vale off -->
<!-- ignore Make -->
### Install Make
<!-- vale on -->
{{< tabs >}}

{{< tab "MacOS" >}}
Install `make` with [Homebrew](https://formulae.brew.sh/formula/make).

```command
brew install make
```
{{< /tab >}}

{{<tab "Linux" >}}
Most Linux distributions include `make` by default. For more information on
`make` for Linux, visit the [GNU make
website](https://www.gnu.org/software/make/).

{{< /tab >}}

{{<tab "Windows" >}}
The Crossplane build system doesn't support Windows.
{{< /tab >}}

{{< /tabs >}}

### Build the Crossplane documentation
From the `crossplane` folder run

```command
make docs.run
```

Hugo builds the website and launch a local web server on
[http://localhost:1313](http://localhost:1313).

Any changes made are instantly reflected on the local web server. You
don't need to restart Hugo.

### Contribute to a specific version
In the [crossplane/crossplane](https://github.com/crossplane/crossplane)
each active release has a `/docs` folder in a branch called
`release-<version>`. For example, v1.10 docs are in the branch
[release-1.10](https://github.com/crossplane/crossplane/tree/release-1.10).

To contribute to a specific release submit a pull-request to the
`release-<version>` or `master` branch.

The next Crossplane release uses `master` as the starting documentation.

## Adding new content

To create new content create a new markdown file in the appropriate location. 

To create a new section, create a new directory and an `_index.md` file in the
root. 

### Types of content
Crossplane documentation has three content sections:
* The [Developer Guide]({{<ref "/contribute/_index.md">}}) with details on how to
  contribute to the Crossplane project or Crossplane documentation.
* The [Knowledge Base]({{<ref "/knowledge-base" >}}) is for content related to
  Crossplane integrations, in-depth articles or how-to guides. 
* [User documentation]({{<ref "/master" >}}) are for generic documentation,
  commonly version-specific. 

#### User documentation vs knowledge base articles
User documentation includes both _conceptual_ and _procedural_ instructions.

_Conceptual_ content describes the background and theory behind the technology.
Conceptual documents are helpful to explain the "why" of the technology.

An example of _Conceptual_ content would be describing the role
of a Crossplane Provider.

_Procedural_ content is the step-by-step instructions to do something.
Procedural content details the "how" of a piece of technology.

An example of a _Procedural_ document would be a step-by-step Crossplane installation guide.

User documentation is more narrowly focused on a single piece or
related pieces of technology. For example, installing a Provider and creating a
ProviderConfig.

Knowledge base articles are more "free-form" and can describe multiple pieces of
technology or provide more opinionated examples.

{{< hint "tip" >}}
Not sure if the content would be better as a knowledge base article or user
document? Ask in the `#documentation` channel of the [Crossplane Slack](https://slack.crossplane.io/).
{{< /hint >}}

### Front matter
Each page contains metadata called [front matter](https://gohugo.io/content-management/front-matter/). Each page requires front matter to render.

```yaml
---
title: "A New Page"
weight: 610
---
```

`title` defines the name of the page.
`weight` determines the ordering of the page in the table of contents. Lower
weight pages come before higher weights in the table of contents. The value of
`weight` is otherwise arbitrary. 

### Headings
Use standard markdown for headings (`#`). The top level heading, a single hash
(`#`) is for the page title. All content headings should be two hashes (`##`) or more.

### Hiding pages
To hide a page from the left-hand navigation use `tocHidden: true` in the front
matter of the page. The docs website skips pages with `tocHidden:true` when
building the menu.