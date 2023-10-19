---
title: Additional Styling Features
weight: 60
description: "Add style and visuals to the docs"
---

The following is a list of Crossplane documentation customizations that expand
traditional Markdown. Most of these are custom 
[Hugo Shortcodes](https://gohugo.io/templates/shortcode-templates/).

{{< hint "note" >}}
If you're having trouble with the Hugo shortcodes, ask for help in the
`#documentation` channel of the 
[Crossplane Slack](https://slack.crossplane.io/).
{{< /hint >}}

## Markdown
Crossplane documentation uses Hugo to render Markdown to
HTML. Hugo supports [Commonmark](https://commonmark.org/) and 
[GitHub Flavored Markdown](https://github.github.com/gfm/) through the
[Goldmark](https://github.com/yuin/goldmark/) parser.

{{< hint "note" >}}
Commonmark and `GFM` are extensions to the 
[standard Markdown](https://www.markdownguide.org/) language.
{{< /hint >}}

The docs support standard Markdown for images, links and tables, Crossplane
recommend using the custom shortcodes to provide a better experience for readers.

* [Images]({{< ref "#images">}})
* [Links]({{< ref "#links">}})
* [Tables]({{< ref "#tables" >}})

## Hide long outputs
Some outputs may be verbose or only relevant for
a small audience. Use the `expand` shortcode to hide blocks of text by default.

{{<expand "A large XRD" >}}
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.org
spec:
  group: database.example.org
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
  claimNames:
    kind: PostgreSQLInstance
    plural: postgresqlinstances
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              parameters:
                type: object
                properties:
                  storageGB:
                    type: integer
                required:
                - storageGB
            required:
            - parameters
```
{{< /expand >}}

The `expand` shortcode can have a title, the default is "Expand."
````yaml
{{</* expand "A large XRD" */>}}
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xpostgresqlinstances.database.example.org
```
{{</* /expand */>}}
````

The `expand` shortcode requires opening and closing tags. Unclosed tags causes
Hugo to fail.

## Hints and alert boxes
Hint and alert boxes provide call-outs to important information to the reader. Crossplane docs support four different hint box styles.

{{< hint "note" >}}
Notes are useful for calling out optional information.
{{< /hint >}}

{{< hint "tip" >}}
Use tips to provide context or a best practice.
{{< /hint >}}

{{< hint "important" >}}
Important hints are for drawing extra attention to something. 
{{< /hint >}}

{{< hint "warning" >}}
Use warning boxes to alert users of things that may cause outages, lose data or
are irreversible changes.
{{< /hint >}}


Create a hint by using a shortcode in your markdown file:
```html
{{</* hint "note" */>}}
Your box content. This hint box is a note.
{{</* /hint */>}}
```

Use `note`, `tip`, `important`, or `warning` as the `hint` value.

The `hint` shortcode requires opening and closing tags. Unclosed tags causes
Hugo to fail.

## Images
All images are in `/content/media`.  
Crossplane supports standard [Markdown image
syntax](https://www.markdownguide.org/basic-syntax/#images-1) but using the
`img` shortcode is strongly recommended.

Images using the shortcode are automatically converted to `webp` image format,
compressed and use responsive image sizing. 

{{<hint "note">}}
The `img` shortcode doesn't support `.svg` files.
{{< /hint >}}

The shortcode requires a `src`, an
`alt` text and an optional `size`.  

The `src` is relative to `/content`.

The `size` can be one of:
* `xtiny` - Resizes the image to 150px.
* `tiny` - Resizes the image to 320px.
* `small` - Resizes the image to 600px.
* `medium` - Resizes the image to 1200px.
* `large` - Resizes the image to 1800px.

By default the image isn't resized.

An example of using the `img` shortcode:
```html
{{</* img src="/media/banner.png" alt="Crossplane Popsicle Truck" size="small" */>}}
```

Which generates this responsive image (change your browser size to see it change):
{{<img src="/media/banner.png" alt="Crossplane Popsicle Truck" size="small" >}}

## Links
Crossplane docs support standard [Markdown
links](https://www.markdownguide.org/basic-syntax/#links) but Crossplane prefers link shortcodes
for links between docs pages. Using shortcodes prevents incorrect link creation
and notifies which links to change after moving a page.

### Between docs pages
For links between pages use a standard Markdown link in the form:

<!-- vale off -->
`[Link text](link)`
<!-- vale on -->

Crossplane recommends using the [Hugo ref shortcode](https://gohugo.io/content-management/shortcodes/#ref-and-relref)
with the path of the file relative to `/content` for the link location.

For example, to link to the `master` release index page use
<!-- vale off -->
```markdown
[master branch documentation]({{</* ref "master/_index.md" */>}})
```
<!-- vale on -->

<!-- [master branch documentation]({{<ref "master/_index.md" >}}) -->

The `ref` value is of the markdown file, including `.md` extension.

If the `ref` value points to a page that doesn't exist, Hugo fails to start. 

### Linking to external sites
Minimize linking to external sites. When linking to any page outside of
`crossplane.io` use standard [markdown link
syntax](https://www.markdownguide.org/basic-syntax/#links) without using the
`ref` shortcode.

For example, 
```markdown
[Go to Upbound](http://upbound.io)
```

## Tables
The docs support 
[extended markdown tables](https://www.markdownguide.org/extended-syntax/#tables)
but the styling isn't optimized.

| Title | A Column | Another Column |
| ---- | ---- | ---- | 
| Content | more content | even more content | 
| A Row | more of the row | another column in the row | 
<br />

Wrap a markdown table in the `{{</* table */>}}` shortcode to provide styling.

{{< hint "important" >}}
The `table` shortcode requires a closing `/table` tag.
{{< /hint >}}

```markdown
{{</* table */>}}
| Title | A Column | Another Column |
| ---- | ---- | ---- | 
| Content | more content | even more content | 
| A Row | more of the row | another column in the row | 
{{</* /table */>}}
```

{{< table >}}
| Title | A Column | Another Column |
| ---- | ---- | ---- | 
| Content | more content | even more content | 
| A Row | more of the row | another column in the row | 
{{< /table >}}

[Bootstrap](https://getbootstrap.com/docs/5.2/content/tables/) provides styling
for the `table` shortcode. The docs support all Bootstrap table classes passed
to the shortcode. 

### Striped tables
<!-- vale off -->
To create a table with 
[striped rows](https://getbootstrap.com/docs/5.2/content/tables/#striped-rows):


```markdown
{{</* table "table table-striped" */>}}
| Title | A Column | Another Column |
| ---- | ---- | ---- | 
| Content | more content | even more content | 
| A Row | more of the row | another column in the row | 
{{</* /table */>}}
```
<!-- vale on -->

{{< table "table table-striped">}}
| Title | A Column | Another Column |
| ---- | ---- | ---- | 
| Content | more content | even more content | 
| A Row | more of the row | another column in the row | 
{{< /table >}}

### Compact tables
For more compact tables use `table table-sm`
```markdown
{{</* table "table table-striped" */>}}
| Title | A Column | Another Column |
| ---- | ---- | ---- | 
| Content | more content | even more content | 
| A Row | more of the row | another column in the row | 
{{</* /table */>}}
```

{{< table "table table-sm">}}
| Title | A Column | Another Column |
| ---- | ---- | ---- | 
| Content | more content | even more content | 
| A Row | more of the row | another column in the row | 
{{< /table >}}

## Tabs
Use tabs to present information about a single topic with multiple exclusive
options. For example, creating a resource via command-line or GUI. 

To create a tab set, first create a `tabs` shortcode and use multiple `tab`
shortcodes inside for each tab.

```html
{{</* tabs */>}}

{{</* tab "First tab title" */>}}
An example tab. Place anything inside a tab.
{{</* /tab */>}}

{{</* tab "Second tab title" */>}}
A second example tab. 
{{</* /tab */>}}

{{</* /tabs */>}}
```

This code block renders the following tabs
{{< tabs >}}

{{< tab "First tab title" >}}
An example tab. Place anything inside a tab.
{{< /tab >}}

{{< tab "Second tab title" >}}
A second example tab. 
{{< /tab >}}

{{< /tabs >}}

Both `tab` and `tabs` require opening and closing tags. Unclosed tags causes
Hugo to fail.

## Shortcodes