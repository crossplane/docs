---
title: Upgrade Crossplane
weight: 200
---

The recommended upgrade method for an existing Crossplane install is to use
[Helm](http://helm.io).

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
{{< /hint >}}

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

For example, in v1.15.0 Crossplane changed the default image registry from 
`index.docker.io` to `xpkg.upbound.io`. Upgrading Crossplane from a version
before v1.15.0 updates the default package registry. 

Override new defaults by 
[customizing the Helm chart]({{<ref "install#customize-the-crossplane-helm-chart" >}}) 
with the upgrade command.

For example, to maintain the original image registry use 
```shell 
helm upgrade crossplane --namespace crossplane-system crossplane-stable/crossplane `--set 'args={"--registry=index.docker.io"}'
```
