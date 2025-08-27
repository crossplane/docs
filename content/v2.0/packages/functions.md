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

{{< hint "important" >}}
Beginning with Crossplane version 1.20.0 Crossplane uses the [crossplane-contrib](https://github.com/orgs/crossplane-contrib/packages) GitHub Container Registry at `xpkg.crossplane.io` by default for downloading and
installing packages. 

Specify the full domain name with the `package` or change the default Crossplane
registry with the `--registry` flag on the [Crossplane pod]({{<ref "../guides/pods">}})
{{< /hint >}}

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
