---
title: Getting Started
weight: 1
description: "Clone the docs and make a contribution"
---

The Crossplane documentation lives in the 
[docs GitHub repository](https://github.com/crossplane/docs).

## Local development
Clone the documentation and use [Hugo](https://gohugo.io/) to 
build the Crossplane documentation site locally for development and testing. 

### Clone the docs repository
Clone the [Crossplane docs
repository](https://github.com/crossplane/docs) with

```command
git clone https://github.com/crossplane/docs.git
```

### Download Hugo
Download [Hugo](https://github.com/gohugoio/hugo/releases/tag/v0.107.0), the
static site generator Crossplane docs uses.

{{< hint "important" >}}
Download the `hugo_extended` version. The standard Hugo package doesn't support
the Crossplane docs CSS.
{{< /hint >}}

Extract and run Hugo with `hugo server`.

Hugo builds the website and launch a local web server on
<a href="http://localhost:1313" data-proofer-ignore>http://localhost:1313</a>.

Any changes made are instantly reflected on the local web server. You
don't need to restart Hugo.

### Contribute to a specific version
Each Crossplane version is a unique folder inside `/content`. 

{{<hint "note" >}}
The next Crossplane release uses `/content/master` as the starting
documentation.
{{< /hint >}}

Make changes to the files in the associated version folder. To make changes
across more than one version, change the files in each version folder.

## Adding new content

To create new content create a new markdown file in the appropriate location. 

To create a new section, create a new directory and an `_index.md` file in the
root. 

### Types of content
Crossplane documentation has three content sections:


#### User documentation vs knowledge base articles
User documentation includes both _conceptual_ and _procedural_ instructions.

_Conceptual_ content describes the background and theory behind the technology.
Conceptual documents are helpful to explain the "why" of the technology.

An example of _Conceptual_ content would be describing the role
of a Crossplane Provider.

_Procedural_ content is the step-by-step instructions to do something.
Procedural content details the "how" of a piece of technology.

An example of a _Procedural_ document would be a step-by-step Crossplane 
installation guide.

User documentation is more narrowly focused on a single piece or
related pieces of technology. For example, installing a Provider and creating a
ProviderConfig.

Knowledge base articles are more "free-form" and can describe more than one 
piece of technology or provide more opinionated examples.

{{< hint "tip" >}}
Not sure if the content would be better as a knowledge base article or user
document? Ask in the `#documentation` channel of the 
[Crossplane Slack](https://slack.crossplane.io/).
{{< /hint >}}

### Front matter
Each page contains metadata called 
[front matter](https://gohugo.io/content-management/front-matter/). Each page 
requires front matter to render.

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

#### Alpha and beta features
Note features as alpha or beta in the front matter.

For alpha features set `state: alpha` and use `alphaVersion` to provide the 
version that introduced the feature. 

```yaml
---
title: Composition Functions
state: alpha
alphaVersion: "1.11"
---
```

For beta features set `state: beta` and use both `alhpaVersion` and 
`betaVersion` to provide the version that introduced and graudated the feature.

```yaml
---
title: Composition Revisions
state: beta
alphaVersion: "1.4"
betaVersion: "1.11"
---
```

### Headings
Use standard markdown for headings (`#`). The top level heading, a single hash
(`#`) is for the page title. All content headings should be two hashes (`##`) or
more.

### Hiding pages
To hide a page from the left-hand navigation use `tocHidden: true` in the front
matter of the page. The docs website skips pages with `tocHidden:true` when
building the menu.