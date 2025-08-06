---
title: Install Crossplane
weight: 100
---

Crossplane installs into an existing Kubernetes cluster, creating the
Crossplane pod.

Installing Crossplane enables the installation of Crossplane _Provider_,
_Function_, and _Configuration_ resources.

{{< hint "tip" >}}
If you don't have a Kubernetes cluster create one locally with [Kind](https://kind.sigs.k8s.io/).
{{< /hint >}}

## Prerequisites
* An actively [supported Kubernetes version](https://kubernetes.io/releases/patch-releases/#support-period)
* [Helm](https://helm.sh/docs/intro/install/) version `v3.2.0` or later

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
## Install Crossplane
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

Install Crossplane using the _Helm chart_.


<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
### Add the Crossplane Preview Helm repository
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

Add the Crossplane preview repository with the `helm repo add` command.

```shell
helm repo add crossplane-preview https://charts.crossplane.io/preview
```

Update the
local Helm chart cache with `helm repo update`.
```shell
helm repo update
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
### Install the Crossplane Preview Helm chart
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

Install the Crossplane Preview Helm chart with `helm install`.

{{< hint "tip" >}}
View the changes Crossplane makes to your cluster with the
`helm install --dry-run --debug` options. Helm shows what configurations it
applies without making changes to the Kubernetes cluster.
{{< /hint >}}

Crossplane creates and installs into the `crossplane-system` namespace.

```shell
helm install crossplane \
--namespace crossplane-system \
--create-namespace crossplane-preview/crossplane \
--version v2.0.0-preview.1
```

View the installed Crossplane pods with `kubectl get pods -n crossplane-system`.

```shell {copy-lines="1"}
kubectl get pods -n crossplane-system
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-6d67f8cd9d-g2gjw                1/1     Running   0          26m
crossplane-rbac-manager-86d9b5cf9f-2vc4s   1/1     Running   0          26m
```

## Installation options

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
### Customize the Crossplane Helm chart
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

Crossplane supports customizations at install time by configuring the Helm
chart.

Read [the Helm chart README](https://github.com/crossplane/crossplane/blob/v2/cluster/charts/crossplane/README.md#configuration) 
to learn what customizations are available.

Read [the Helm documentation](https://helm.sh/docs/) to learn how to run Helm
with custom options using `--set` or `values.yaml`.

#### Feature flags

Crossplane introduces new features behind feature flags. By default alpha
features are off. Crossplane enables beta features by default. To enable a
feature flag, set the `args` value in the Helm chart. Available feature flags
can be directly found by running `crossplane core start --help`, or by looking
at the table below.

{{< expand "Feature flags" >}}
{{< table caption="Feature flags" >}}
| Status | Flag | Description |
| --- | --- | --- |
| Beta | `--enable-deployment-runtime-configs` | Enable support for DeploymentRuntimeConfigs. |
| Beta | `--enable-usages` | Enable support for Usages. |
| Alpha | `--enable-realtime-compositions` | Enable support for real time compositions. |
| Alpha | `--enable-dependency-version-upgrades ` | Enable automatic version upgrades of dependencies when updating packages. |
| Alpha | `--enable-signature-verification` | Enable support for package signature verification via ImageConfig API. |
{{< /table >}}
{{< /expand >}}

Set these flags either in the `values.yaml` file or at install time using the
`--set` flag, for example: `--set
args='{"--enable-composition-functions","--enable-composition-webhook-schema-validation"}'`.

#### Change the default package registry

Beginning with Crossplane version 1.20.0 Crossplane uses the [crossplane-contrib](https://github.com/orgs/crossplane-contrib/packages) GitHub Container Registry at `xpkg.crossplane.io` by default for downloading and
installing packages. 

Change the default registry location during the Crossplane install with
`--set args='{"--registry=index.docker.io"}'`.
