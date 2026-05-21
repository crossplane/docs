---
title: Upgrade Crossplane
weight: 400
description: "Upgrade Crossplane to newer versions"
---

The recommended upgrade method for an existing Crossplane install is to use
[Helm](http://helm.io).

<!-- vale write-good.Weasel = NO -->
{{<hint "important" >}}
Always upgrade Crossplane **one minor version at a time**, using the most recent
patch version available for each.

For example, if you are on `v1.18` and want to upgrade to `v2.0`, you should
first upgrade to `v1.19`, then `v1.20`, before finally upgrading to `v2.0`. The
upgrade path in this example looks like `v1.18` → `v1.19` → `v1.20` → `v2.0`.
{{</hint>}}
<!-- vale write-good.Weasel = YES -->

## Prerequisites
* [Helm](https://helm.sh/docs/intro/install/) version `v3.2.0` or later

## Add the Crossplane Helm repository
Verify Helm has the Crossplane repository.

```shell
helm repo add crossplane-stable https://charts.crossplane.io/stable
```

## Update the Helm repository

Update the local Crossplane Helm chart with `helm repo update`.

```shell
helm repo update
```

{{<hint "important" >}}
Upgrading Crossplane without updating the Helm chart installs the last version
available in the locally cached Helm chart.
{{</hint>}}

## Upgrade Crossplane

Upgrade Crossplane with `helm upgrade`, providing the Crossplane namespace.
By default, Crossplane installs into the `crossplane-system`
namespace.

```shell
helm upgrade crossplane --namespace crossplane-system crossplane-stable/crossplane
```

Helm preserves any arguments or flags originally used when installing
Crossplane.

Crossplane uses any new default behaviors unless they're changed in the `helm
upgrade` command.

Override new defaults by
[customizing the Helm chart]({{<ref "../get-started/install#customize-the-crossplane-helm-chart" >}})
with the upgrade command.
