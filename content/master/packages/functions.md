---
title: Functions
weight: 100
description: "Functions extend Crossplane with new ways to configure composition"
---

Functions extend Crossplane with new ways to configure
[composition]({{<ref "../composition">}}).

You can use different _composition functions_ to configure what Crossplane does
when someone creates or updates a
[composite resource (XR)]({{<ref "../composition/composite-resources">}}).

{{<hint "important">}}
This page is a work in progress.

Functions are packages, like [Providers]({{<ref "./providers">}}) and
[Configurations]({{<ref "./configurations">}}). Their APIs are similar. You
install and configure them the same way as a provider.

Read the [composition]({{<ref "../composition/compositions">}}) documentation to
learn how to use functions in a composition.
{{</hint>}}

## Install a function

Install a Function with a Crossplane
{{<hover label="install" line="2">}}Function{{</hover >}} object setting the
{{<hover label="install" line="6">}}spec.package{{</hover >}} value to the
location of the function package.

For example, to install the
[patch and transform function](https://github.com/crossplane-contrib/function-patch-and-transform),

```yaml {label="install"}
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: crossplane-contrib-function-patch-and-transform
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.8.2
```

By default, the Function pod installs in the same namespace as Crossplane
(`crossplane-system`).

{{<hint "note" >}}
Functions are part of the
{{<hover label="install" line="1">}}pkg.crossplane.io{{</hover>}} group.

The {{<hover label="meta-pkg" line="1">}}meta.pkg.crossplane.io{{</hover>}}
group is for creating Function packages.

Instructions on building Functions are outside of the scope of this
document.
Read the Crossplane contributing
[Function Development Guide](https://github.com/crossplane/crossplane/blob/main/contributing/guide-provider-development.md)
for more information.

For information on the specification of Function packages read the
[Crossplane Function Package specification](https://github.com/crossplane/crossplane/blob/main/contributing/specifications/xpkg.md#provider-package-requirements).

```yaml {label="meta-pkg"}
apiVersion: meta.pkg.crossplane.io/v1
kind: Function
metadata:
  name: provider-aws
spec:
# Removed for brevity
```
{{</hint >}}

## Functions managed by Crossplane

{{<hint "important">}}
Referencing functions by OCI reference is an alpha feature. Enable it by
setting the `--enable-pipeline-oci-references` feature flag.
{{</hint>}}

A Composition or Operation pipeline step can reference a function package by
digest with the `function` field instead of naming an installed Function with
`functionRef`. Read
[Roll out function changes]({{<ref "../composition/composition-revisions#roll-out-function-changes">}})
to learn why you might want to use this feature.

You don't install these functions yourself. For each digest a pipeline
references, Crossplane creates a `FunctionRevision`. Crossplane groups the
revisions under a Function named after the package repository. For example,
`xpkg.crossplane.io/crossplane-contrib/function-go-templating` becomes
`crossplane-contrib-function-go-templating`, the same name Crossplane uses when
it installs the function as a
[dependency]({{<ref "./configurations#manage-dependencies">}}).

The `CompositionRevisions` and `Operations` that reference a function by OCI
reference own its `FunctionRevision`. The `FunctionRevision` is garbage
collected by Kubernetes when you delete the last `CompositionRevision` or
`Operation` that references it.

### External revisions

For Functions installed by users or as dependencies, Crossplane's package
manager sets one active revision. The revisions created for `function`
references in the `CompositionRevisions` and `Operations` are
different. Controllers outside the package manager manage these "external"
revisions. The package manager pulls the package, runs a function pod for each
one, and records their names in the parent `Function`'s
`status.externalFunctionRefs` field. Multiple external revisions of the same
Function can be active at once and the package manager doesn't determine which
should be active.

A Function that only has external revisions has no `spec.package`. Its
{{<hover label="ext" line="11">}}status.externalRevisionRefs{{</hover>}} lists
its revisions:

```yaml {label="ext",copy-lines="none"}
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: crossplane-contrib-function-go-templating
spec:
  # No package
  # Removed for brevity
status:
  conditions:
  # Removed for brevity
  externalRevisionRefs:
  - name: crossplane-contrib-function-go-templating-91622b9260e8
  - name: crossplane-contrib-function-go-templating-d66b8d13aa14
```

This Function reports `HEALTHY` as `True` only when all its external revisions
are healthy. It has no current revision.

A Function can have both a `spec.package` and external revisions. This happens
when you install a function and also reference it by digest in a pipeline. The
package manager manages the revisions for `spec.package` as usual and lists the
others in `status.externalRevisionRefs`. Pipeline steps that use `functionRef`
call only the revision the package manager manages.

If another package depends on a function that has only external revisions, the
package manager takes over the Function and sets its `spec.package`.
