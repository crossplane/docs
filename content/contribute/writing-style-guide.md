---
title: Writing Style Guide
weight: 10
description: "Guidelines on how to write high quality docs"
---

The most important points of the style guide include:

<!-- vale off -->
* Avoid [passive voice](https://www.grammarly.com/blog/passive-voice/). 
  * Active voice writing is stronger and direct. Active voice simplifies doc translations.
* Use [sentence-case headings](https://apastyle.apa.org/style-grammar-guidelines/capitalization/sentence-case).
  * Sentence case creates more casual and approachable writing.
* Wrap lines at 80 characters.
  * Line wrapping improves review feedback.
* Use [present tense](https://www.grammarly.com/blog/simple-present/) and avoid "will."
  * Docs cover actions happening now and the results in real time.
* Spell out numbers less than 10, except for percentages, time and versions.
  * Numbers in sentences are more difficult to read.
* Capitalize "Crossplane" and "Kubernetes."
  * Crossplane and Kubernetes are proper nouns. Don't use `k8s`.
* Spell out the first use of an acronym unless it's common to new Crossplane
users. When in doubt, spell it out first.
  * Avoid assuming the reader already knows the background.
* Don't use [cliches](https://www.topcreativewritingcourses.com/blog/common-cliches-in-writing-and-how-to-avoid-them).
  * Cliches make writing sound unprofessional and aren't internationally inclusive. 
* Use contractions for phrases like "do not," "cannot," "is not" and related terms.
  * It's easy to miss "not" in "do not." It's hard to misunderstand "don't."
* Don't use Latin terms (i.e., e.g., etc.).
  * These terms are more difficult for non-Latin language speakers to
    understand. 
* Avoid [gerund](https://owl.purdue.edu/owl/general_writing/mechanics/gerunds_participles_and_infinitives/index.html) headings (-ing words).
  * Gerunds make headings less direct. 
* Try and limit sentences to 25 words or fewer.
  * Longer sentences are more difficult to read. Shorter sentences are better
    for search engine optimization.
* [Be descriptive in link text](https://usability.yale.edu/web-accessibility/articles/links#link-text). Don't use "click here" or "read more".
  * Describe link text improves accessibility for screen readers.
* Order brand names alphabetically. For example, AWS, Azure, GCP.
  * Ordered names removes the appearance of preference.
* Don't use "easy," "simple," or "obvious".
  * It's condescending to the reader.
* No Oxford commas.
  * A subjective style choice. No commas before "and" or "or."
* U.S. English spelling and grammar.
<!-- vale on -->

Crossplane relies on [Vale](https://github.com/errata-ai/vale) to enforce the
complete style guide. 

Read more about [using Vale with the Crossplane documentation]({{<ref "Vale" >}}).

## Italics

Use _italics_ to introduce or draw attention term. 

Use italics on the same term sparingly.


## Inline code styles

Use inline code styles, single ticks (`` ` ``) for files directories or paths. 

Use the `{{</* hover */>}}` shortcode to relate command explanations to larger examples. 

## Placeholders

Use angle brackets (`< >`) for placeholders. Use a short, descriptive name
inside the brackets. Use underscores between words to simplify selections.

For example, to creating AWS credentials prompts for the key and secret key. 

```ini {copy-lines="all"}
[default]
aws_access_key_id = <aws_access_key>
aws_secret_access_key = <aws_secret_key>
```
## Styling Kubernetes objects

### Kinds

Kinds should be upper camel case. Capitalize each word, without separators. 

<!-- vale Google.FirstPerson = NO -->
<!-- ignore "My" -->
For example the 
{{<hover label="kind" line="4" >}}kind: MyComputeResource{{< /hover >}} 
capitalizes "My," "Compute" and "Resource" with no spaces or dashes.
<!-- vale Google.FirstPerson = YES -->

```yaml {label="kind"}
spec:
  group: test.example.org
  names:
    kind: MyComputeResource
```

### Names

Object names should use snake case. All words are lowercase with dashes (`-`)
between them.

<!-- vale Google.FirstPerson = NO -->
<!-- ignore "My" -->
For example the 
{{<hover label="kind" line="4" >}}name: my-resource{{< /hover >}} 
uses all lowercase. A dash separates "my" and "resource."
<!-- vale Google.FirstPerson = YES -->

```yaml {label="name"}
apiVersion: test.example.org/v1alpha1
kind: MyComputeResource
metadata:
  name: my-resource
```

### Inline

Kubernetes objects mentioned inline don't require styling unless drawing special
attention. 