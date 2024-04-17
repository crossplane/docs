---
title: Using Vale
weight: 11
description: "Install and configure Vale for the Crossplane docs"
hideFromLanding: true
---

Crossplane relies on [Vale](https://github.com/errata-ai/vale) to enforce the style guide.

Crossplane's Vale style definitions are in the
[`utils/vale`](https://github.com/crossplane/docs/tree/master/utils/vale) 
directory.

{{< hint "important" >}}
The Crossplane community is updating existing content to pass Vale. Until the
community completes the project Vale errors are only enforced for new or changed
content. The community approves PRs with Vale errors in unmodified document sections.
{{< /hint >}}

## Install Vale

Follow the directions on the Vale website to 
[install the Vale binary](https://vale.sh/docs/vale-cli/installation/).
<!-- vale off -->
Crossplane CI uses [Vale v2.22.0](https://github.com/errata-ai/vale/releases/tag/v2.22.0) or later.
<!-- vale on -->
## Run Vale

Run Vale on all documentation from the command-line with

```shell
vale --config="utils/vale/.vale.ini" content/
```

To run Vale on a single file use

```shell
vale --config="utils/vale/.vale.ini" content/contribute/writing-style-guide.md
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
* [Crossplane](https://github.com/crossplane/docs/tree/master/utils/vale/styles/Crossplane) - spelling exceptions for Kubernetes and Crossplane related words. 
* [write-good](https://github.com/errata-ai/write-good) - for higher quality writing.

{{<hint "warning" >}}
Crossplane maintainers consider Vale warnings the same as errors. 

Error levels aren't changed to make Vale style maintenance easier.
{{< /hint >}}

### Spelling errors and exceptions

Spelling exceptions are in `utils/vale/styles/Crossplane`. 
* `allowed-jargon.txt` - technical terms allowed in the docs
* `brands.txt` - brand and product names
* `crossplane-words.txt` - words specific to Crossplane
* `provider-words.txt` - words related to Providers and Provider resources
* `spelling-exceptions.txt` - English words that are incorrectly flagged as errors

If Vale considers a word incorrect add an
exception to one of the text files along with your pull request. 

<!-- vale off -->
Because of how Vale parses words the following are errors:
 * Hugo shortcodes without a space between the quote and angle bracket.  
  For example `{{</* expand "Reference Composition"*/>}}`
 * Markdown links containing a line break.
 * Hugo `{{</* ref */>}}` links containing a line break. 
 * Markdown link styling outside of the square brackets.  
 For example `_[error]_` is an error. Use `[_works_]` instead. 
 <!-- vale on -->
### Ignore Vale rules

Vale can turn off specific rules or all rules inside a doc.

All ignored rules must include a justification for why they're ignored.

After the ignored content turn the rules back on. 

{{<hint "important" >}}
Vale ignores rules not turned back on for the rest of the document.
{{< /hint >}}

#### Sentence length

<!-- vale Google.WordList = NO -->
Vale counts words in a link URL in the `gitlab.SentenceLength` check. 
<!-- vale Google.WordList = YES -->

Aim for 25 to 30 word sentences. If a URL triggers a Vale error wrap the sentence
in a rule disabling the rule. 

```html
<!-- vale gitlab.SentenceLength = NO -->
The XRD `version` is like the 
[API versioning used by Kubernetes](https://kubernetes.io/docs/reference/using-api/#api-versioning).
The version shows how mature or stable the API is and increments when changing,
adding or removing fields in the API.
<!-- vale gitlab.SentenceLength = YES -->
```

### Ignore all rules

Use `<!-- vale off -->` to ignore all Vale rules and `<!-- vale on -->` to turn
Vale back on.

For example, 

```plaintext
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
```plaintext
<!-- vale Microsoft.Contractions = NO -->
<!-- turn off contractions for the example -->
Do not turn off rules without good reasons.
<!-- vale Microsoft.Contractions = YES -->
```

{{<hint "important" >}}
Vale requires capitalization for `YES` and `NO` and a space around `=`.
{{</hint >}}

## Vale settings

The Vale configuration for the repository is in
[utils/vale/vale.ini](https://github.com/crossplane/docs/blob/master/utils/vale/.vale.ini).

{{< hint "note" >}}
The `vale.ini` file is a Vale configuration file. Read the Vale documentation 
for more information about the `vale.ini` file. 
{{< /hint >}}

Some imported Vale styles don't apply or duplicate other rules. Disable
individual rules inside the `vale.ini` file.

For example Google and Microsoft rules both cover the use of first person words 
like `I`. The docs `vale.ini` disables the
[Microsoft rule](https://github.com/crossplane/docs/blob/3e9e10671c32e368f5381d83e406e16bc38c93bc/utils/vale/.vale.ini#L42) 
to prevent duplicate errors.