---
title: Code Styling Guide
weight: 20
description: "How to style code outputs in the docs"
---

To optimize readability and comprehension Crossplane has developed guidelines
for source code used in documentation.


## Use fenced code blocks
Use Markdown [fenced code
blocks](https://www.markdownguide.org/extended-syntax/#fenced-code-blocks) with
three backticks (` ``` `) for
all command examples and outputs.

````markdown
```
this is a code block
```
````

Only use a single backtick (`` ` ``) for commands used in a sentence. 

For example, the command `kubectl apply` is inside a sentence. 

## Use language hints for proper highlighting
Hugo attempts to determine the language and apply proper styling, but it's
not always optimized for readability. 

For example, this YAML output isn't automatically detected.
```
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.org
```

All code blocks must include a language definition on the same line as the backticks.
````yaml
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.org
```
````

Find a [full list of supported languages](https://github.com/alecthomas/chroma/#supported-languages) in the Chroma documentation.

{{< hint "important" >}}
The language definition should optimize for display and not technical correctness.
{{< /hint >}}

For example, this uses the `shell` language hint.

```shell
cat test.yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```

Using the `yaml` language hint provides improved readability. 
```yaml
cat test.yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```

## Code line highlighting
Crossplane docs provide two methods of code highlighting: static and dynamic highlighting.

### Static line highlighting
Static highlighting is an "always on" highlight of a line in a code box.
```yaml {hl_lines="1-3"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```

Apply a `{hl_lines=<line number>}` to a code fence.
````yaml
```yaml {hl_lines=1}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```
````

To highlight continuous blocks use a range in quotes `{hl_lines="1-4"}`.
For multiple lines, including blocks, create an array of values in square brackets. `{hl_lines=[1,2,"4-6"]}`.

More information on static highlighting is available in the [Hugo syntax highlighting documentation](https://gohugo.io/content-management/syntax-highlighting/).

### Dynamic line highlighting
Dynamic highlighting only highlights a specific line when a read hovers over a specific word outside of the code block.
This highlighting style is useful to draw attention to a line of code when explaining a command or argument.

For example hover over the word {{<hover label="example1" line="2" >}}kind{{</hover>}} to highlight a line in the YAML file. 
```yaml {label=example1}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```

First, apply the {{<hover label="example" line="1" >}}{label=name}{{</hover >}} to the code fence.


{{<hint "tip">}}
Don't use quotes around the `label` name.
{{< /hint >}}


````yaml {label=example}
```yaml {label=example}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```
````

Next, use the `hover` shortcode around the word that triggers the highlighting. Provide the matching `label` name and `line` number to highlight

```html
{{</* hover label="example" line="2" */>}}commmand{{</* /hover */>}}
```

{{<hint "note" >}}
Hovering triggers a highlight to any code block with the label. Duplicate labels highlight all matching code boxes.
{{< /hint >}} 

## Custom code box copy button
Code boxes automatically have a "copy to clipboard" button that copies the entire contents of the code box. 

Customize the lines the button copies with a `{copy-lines="<start line>-<end line>"}` label on the code block.

For example, to copy lines from 2 to 5 inclusive and not copy the code fence in this example:

````yaml {copy-lines="2-5"}
```yaml {copy-lines="2-5"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```
````

Copying a single line is also supported without using the ending line number. For example to copy only line 3 use `{copy-lines="3"}`.

{{<hint "important" >}}
The line number range must be in quotations.
{{< /hint >}}

Combining copying and highlighting in a single comma-seperated annotation. 
````yaml {copy-lines="2-5", hl_lines="2-3"}
```yaml {copy-lines="2-5", hl_lines="2-3"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: aProvider
```
````