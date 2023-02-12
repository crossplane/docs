---
title: Using Vale
weight: 11
description: "Install and configure Vale for the Crossplane docs"
hideFromLanding: true
---

Crossplane relies on [Vale](https://github.com/errata-ai/vale) to enforce the style guide.

Crossplane's Vale style definitions are in the
[utils/vale](https://github.com/crossplane/docs/tree/master/utils/vale) 
directory.

## Install Vale

Follow the directions on the Vale website to 
[install the Vale binary](https://vale.sh/docs/vale-cli/installation/).

Crossplane CI uses [Vale v2.22.0](https://github.com/errata-ai/vale/releases/tag/v2.22.0) or later.

## Run Vale

Run Vale on all documentation from the command-line with

```shell
vale --config="utils/vale/.vale.ini"` content/
```

To run Vale on a single file use

```shell
vale --config="utils/vale/.vale.ini"` content/contribute/writing-style-guide.md
```

{{<hint "tip" >}}
VSCode has a [Vale plugin](https://github.com/errata-ai/vale-vscode). VSCode
runs the Vale checks when saving a markdown file.
{{</hint >}}

## Vale styles

Crossplane uses the following Vale styles:
* [Alex](https://github.com/errata-ai/alex) - for insensitive, inconsiderate writing.
* [GitLab](https://gitlab.com/gitlab-org/gitlab/-/tree/master/doc/.vale/gitlab)
  - for the [GitLab documentation style guide](https://docs.gitlab.com/ee/development/documentation/styleguide/).
* [Google](https://github.com/errata-ai/google) - for the [Google developer documentation style guide](https://developers.google.com/style).
* [Microsoft](https://github.com/errata-ai/Microsoft) - for the [Microsoft style guide](https://learn.microsoft.com/en-us/style-guide/welcome/).
* [proselint](https://github.com/errata-ai/proselint) - for higher quality writing.
* [Upbound](https://github.com/upbound/vale/tree/main/styles/Upbound) - for
  customized terms and preventing corporate jargon.
* [write-good](https://github.com/errata-ai/write-good) - for higher quality writing.

### Ignore Vale rules

Vale can turn off specific rules or all rules inside a doc.

All ignored rules must include a justification for why they're ignored.

After the ignored content turn the rules back on. 

{{<hint "important" >}}
Vale ignores rules not turned back on for the rest of the document.
{{< /hint >}}

### Ignore all rules

Use `<!-- vale off -->` to ignore all Vale rules and `<!-- vale on -->` to turn
Vale back on.

For example, 

```text
<!-- vale off -->
<!-- turn off vale checking for this example -->
The following example will use passive voice and lowercase crossplane. Do not do this.
<!-- vale on -->
```

### Ignore specific rules

Ignore a specific rule with `<!-- vale <rule name> = NO -->` and turn the rule
back on with `<!-- vale <rule name> = YES -->`.

<!-- vale Microsoft.Contractions = NO -->
<!-- turn off contractions for the example -->
Do not turn off rules without good reasons.
<!-- vale Microsoft.Contractions = YES -->

For example,
```text
<!-- vale Microsoft.Contractions = NO -->
<!-- turn off contractions for the example -->
Do not turn off rules without good reasons.
<!-- vale Microsoft.Contractions = YES -->
```

{{<hint "important" >}}
Vale requires capitalization for `YES` and `NO` and a space around `=`.
{{</hint >}}