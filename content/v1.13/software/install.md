---
title: Install Crossplane
weight: 100
---

Crossplane installs into an existing Kubernetes cluster, creating the
`Crossplane` pod, enabling the installation of Crossplane _Provider_ resources.

{{< hint type="tip" >}}
If you don't have a Kubernetes cluster create one locally with [Kind](https://kind.sigs.k8s.io/).
{{< /hint >}}

## Prerequisites
* An actively [supported Kubernetes version](https://kubernetes.io/releases/patch-releases/#support-period)
* [Helm](https://helm.sh/docs/intro/install/) version `v3.2.0` or later

## Install Crossplane

Install Crossplane using the Crossplane published _Helm chart_. 

### Add the Crossplane Helm repository

Add the Crossplane repository with the `helm repo add` command.

```shell
helm repo add crossplane-stable https://charts.crossplane.io/stable
```

Update the
local Helm chart cache with `helm repo update`.
```shell
helm repo update
```

### Install the Crossplane Helm chart

Install the Crossplane Helm chart with `helm install`.

{{< hint "tip" >}}
View the changes Crossplane makes to your cluster with the 
`helm install --dry-run --debug` options. Helm shows what configurations it
applies without making changes to the Kubernetes cluster.
{{< /hint >}}

Crossplane creates and installs into the `crossplane-system` namespace.

```shell
helm install crossplane \
--namespace crossplane-system \
--create-namespace crossplane-stable/crossplane 
```

View the installed Crossplane pods with `kubectl get pods -n crossplane-system`.

```shell {copy-lines="1"}
kubectl get pods -n crossplane-system
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-6d67f8cd9d-g2gjw                1/1     Running   0          26m
crossplane-rbac-manager-86d9b5cf9f-2vc4s   1/1     Running   0          26m
```

{{< hint "tip" >}}
Install a specific version of Crossplane with the `--version <version>` option. For example, to install version `1.10.0`:

```shell
helm install crossplane \
--namespace crossplane-system \
--create-namespace crossplane-stable/crossplane \
--version 1.10.0
```
{{< /hint >}}


## Installed deployments
Crossplane creates two Kubernetes _deployments_ in the `crossplane-system`
namespace to deploy the Crossplane pods. 

```shell {copy-lines="1"}
kubectl get deployments -n crossplane-system
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
crossplane                1/1     1            1           8m13s
crossplane-rbac-manager   1/1     1            1           8m13s
```

### Crossplane deployment
The Crossplane deployment starts with the `crossplane-init container`. The
`init` container installs the Crossplane _Custom Resource Definitions_ into the
Kubernetes cluster. 

After the `init` container finishes, the `crossplane` pod manages two Kubernetes
controllers. 
* The _Package Manager controller_ installs the
provider and configuration packages.
* The _Composition controller_ installs and manages the
Crossplane _Composite Resource Definitions_, _Compositions_ and _Claims_.

### Crossplane-rbac-manager deployment
The `crossplane-rbac-manager` creates and manages Kubernetes _ClusterRoles_ for
installed Crossplane _Provider_ and their _Custom Resource Definitions_.

The 
[Crossplane RBAC Manger design document](https://github.com/crossplane/crossplane/blob/master/design/design-doc-rbac-manager.md) 
has more information on the installed _ClusterRoles_.

## Installation options

### Customize the Crossplane Helm chart
Crossplane supports customizations at install time by configuring the Helm
chart.

Apply customizations with the command line or with a Helm _values_ file. 

<!-- vale gitlab.Substitutions = NO -->
<!-- allow lowercase yaml -->
{{<expand "All Crossplane customization options" >}}
{{< table "table table-hover table-striped table-sm">}}
| Parameter | Description | Default |
| --- | --- | --- |
| `affinity` | Add `affinities` to the Crossplane pod deployment. | `{}` |
| `args` | Add custom arguments to the Crossplane pod. | `[]` |
| `configuration.packages` | A list of Configuration packages to install. | `[]` |
| `customAnnotations` | Add custom `annotations` to the Crossplane pod deployment. | `{}` |
| `customLabels` | Add custom `labels` to the Crossplane pod deployment. | `{}` |
| `deploymentStrategy` | The deployment strategy for the Crossplane and RBAC Manager pods. | `"RollingUpdate"` |
| `extraEnvVarsCrossplane` | Add custom environmental variables to the Crossplane pod deployment. Replaces any `.` in a variable name with `_`. For example, `SAMPLE.KEY=value1` becomes `SAMPLE_KEY=value1`. | `{}` |
| `extraEnvVarsRBACManager` | Add custom environmental variables to the RBAC Manager pod deployment. Replaces any `.` in a variable name with `_`. For example, `SAMPLE.KEY=value1` becomes `SAMPLE_KEY=value1`. | `{}` |
| `extraVolumeMountsCrossplane` | Add custom `volumeMounts` to the Crossplane pod. | `{}` |
| `extraVolumesCrossplane` | Add custom `volumes` to the Crossplane pod. | `{}` |
| `hostNetwork` | Enable `hostNetwork` for the Crossplane deployment. Caution: enabling `hostNetwork`` grants the Crossplane Pod access to the host network namespace. | `false` |
| `image.pullPolicy` | The image pull policy used for Crossplane and RBAC Manager pods. | `"IfNotPresent"` |
| `image.repository` | Repository for the Crossplane pod image. | `"crossplane/crossplane"` |
| `image.tag` | The Crossplane image tag. Defaults to the value of `appVersion` in Chart.yaml. | `""` |
| `imagePullSecrets` | The imagePullSecret names to add to the Crossplane ServiceAccount. | `{}` |
| `leaderElection` | Enable [leader election](https://docs.crossplane.io/latest/concepts/pods/#leader-election) for the Crossplane pod. | `true` |
| `metrics.enabled` | Enable Prometheus path, port and scrape annotations and expose port 8080 for both the Crossplane and RBAC Manager pods. | `false` |
| `nodeSelector` | Add `nodeSelectors` to the Crossplane pod deployment. | `{}` |
| `packageCache.configMap` | The name of a ConfigMap to use as the package cache. Disables the default package cache `emptyDir` Volume. | `""` |
| `packageCache.medium` | Set to `Memory` to hold the package cache in a RAM-backed file system. Useful for Crossplane development. | `""` |
| `packageCache.pvc` | The name of a PersistentVolumeClaim to use as the package cache. Disables the default package cache `emptyDir` Volume. | `""` |
| `packageCache.sizeLimit` | The size limit for the package cache. If medium is `Memory` the `sizeLimit` can't exceed Node memory. | `"20Mi"` |
| `podSecurityContextCrossplane` | Add a custom `securityContext` to the Crossplane pod. | `{}` |
| `podSecurityContextRBACManager` | Add a custom `securityContext` to the RBAC Manager pod. | `{}` |
| `priorityClassName` | The PriorityClass name to apply to the Crossplane and RBAC Manager pods. | `""` |
| `provider.packages` | A list of Provider packages to install. | `[]` |
| `rbacManager.affinity` | Add `affinities` to the RBAC Manager pod deployment. | `{}` |
| `rbacManager.args` | Add custom arguments to the RBAC Manager pod. | `[]` |
| `rbacManager.deploy` | Deploy the RBAC Manager pod and its required roles. | `true` |
| `rbacManager.leaderElection` | Enable [leader election](https://docs.crossplane.io/latest/concepts/pods/#leader-election) for the RBAC Manager pod. | `true` |
| `rbacManager.managementPolicy` | Defines the Roles and ClusterRoles the RBAC Manager creates and manages. - A policy of `Basic` creates and binds Roles only for the Crossplane ServiceAccount, Provider ServiceAccounts and creates Crossplane ClusterRoles. - A policy of `All` includes all the `Basic` settings and also creates Crossplane Roles in all namespaces. - Read the Crossplane docs for more information on the [RBAC Roles and ClusterRoles](https://docs.crossplane.io/latest/concepts/pods/#crossplane-clusterroles) | `"Basic"` |
| `rbacManager.nodeSelector` | Add `nodeSelectors` to the RBAC Manager pod deployment. | `{}` |
| `rbacManager.replicas` | The number of RBAC Manager pod `replicas` to deploy. | `1` |
| `rbacManager.skipAggregatedClusterRoles` | Don't install aggregated Crossplane ClusterRoles. | `false` |
| `rbacManager.tolerations` | Add `tolerations` to the RBAC Manager pod deployment. | `[]` |
| `registryCaBundleConfig.key` | The ConfigMap key containing a custom CA bundle to enable fetching packages from registries with unknown or untrusted certificates. | `""` |
| `registryCaBundleConfig.name` | The ConfigMap name containing a custom CA bundle to enable fetching packages from registries with unknown or untrusted certificates. | `""` |
| `replicas` | The number of Crossplane pod `replicas` to deploy. | `1` |
| `resourcesCrossplane.limits.cpu` | CPU resource limits for the Crossplane pod. | `"100m"` |
| `resourcesCrossplane.limits.memory` | Memory resource limits for the Crossplane pod. | `"512Mi"` |
| `resourcesCrossplane.requests.cpu` | CPU resource requests for the Crossplane pod. | `"100m"` |
| `resourcesCrossplane.requests.memory` | Memory resource requests for the Crossplane pod. | `"256Mi"` |
| `resourcesRBACManager.limits.cpu` | CPU resource limits for the RBAC Manager pod. | `"100m"` |
| `resourcesRBACManager.limits.memory` | Memory resource limits for the RBAC Manager pod. | `"512Mi"` |
| `resourcesRBACManager.requests.cpu` | CPU resource requests for the RBAC Manager pod. | `"100m"` |
| `resourcesRBACManager.requests.memory` | Memory resource requests for the RBAC Manager pod. | `"256Mi"` |
| `securityContextCrossplane.allowPrivilegeEscalation` | Enable `allowPrivilegeEscalation` for the Crossplane pod. | `false` |
| `securityContextCrossplane.readOnlyRootFilesystem` | Set the Crossplane pod root file system as read-only. | `true` |
| `securityContextCrossplane.runAsGroup` | The group ID used by the Crossplane pod. | `65532` |
| `securityContextCrossplane.runAsUser` | The user ID used by the Crossplane pod. | `65532` |
| `securityContextRBACManager.allowPrivilegeEscalation` | Enable `allowPrivilegeEscalation` for the RBAC Manager pod. | `false` |
| `securityContextRBACManager.readOnlyRootFilesystem` | Set the RBAC Manager pod root file system as read-only. | `true` |
| `securityContextRBACManager.runAsGroup` | The group ID used by the RBAC Manager pod. | `65532` |
| `securityContextRBACManager.runAsUser` | The user ID used by the RBAC Manager pod. | `65532` |
| `serviceAccount.customAnnotations` | Add custom `annotations` to the Crossplane ServiceAccount. | `{}` |
| `tolerations` | Add `tolerations` to the Crossplane pod deployment. | `[]` |
| `webhooks.enabled` | Enable webhooks for Crossplane and installed Provider packages. | `true` |
| `xfn.args` | Add custom arguments to the Composite functions runner container. | `[]` |
| `xfn.cache.configMap` | The name of a ConfigMap to use as the Composite function runner package cache. Disables the default Composite function runner package cache `emptyDir` Volume. | `""` |
| `xfn.cache.medium` | Set to `Memory` to hold the Composite function runner package cache in a RAM-backed file system. Useful for Crossplane development. | `""` |
| `xfn.cache.pvc` | The name of a PersistentVolumeClaim to use as the Composite function runner package cache. Disables the default Composite function runner package cache `emptyDir` Volume. | `""` |
| `xfn.cache.sizeLimit` | The size limit for the Composite function runner package cache. If medium is `Memory` the `sizeLimit` can't exceed Node memory. | `"1Gi"` |
| `xfn.enabled` | Enable the alpha Composition functions (`xfn`) sidecar container. Also requires Crossplane `args` value `--enable-composition-functions` set. | `false` |
| `xfn.extraEnvVars` | Add custom environmental variables to the Composite function runner container. Replaces any `.` in a variable name with `_`. For example, `SAMPLE.KEY=value1` becomes `SAMPLE_KEY=value1`. | `{}` |
| `xfn.image.pullPolicy` | Composite function runner container image pull policy. | `"IfNotPresent"` |
| `xfn.image.repository` | Composite function runner container image. | `"crossplane/xfn"` |
| `xfn.image.tag` | Composite function runner container image tag. Defaults to the value of `appVersion` in Chart.yaml. | `""` |
| `xfn.resources.limits.cpu` | CPU resource limits for the Composite function runner container. | `"2000m"` |
| `xfn.resources.limits.memory` | Memory resource limits for the Composite function runner container. | `"2Gi"` |
| `xfn.resources.requests.cpu` | CPU resource requests for the Composite function runner container. | `"1000m"` |
| `xfn.resources.requests.memory` | Memory resource requests for the Composite function runner container. | `"1Gi"` |
| `xfn.securityContext.allowPrivilegeEscalation` | Enable `allowPrivilegeEscalation` for the Composite function runner container. | `false` |
| `xfn.securityContext.capabilities.add` | Set Linux capabilities for the Composite function runner container. The default values allow the container to create an unprivileged user namespace for running Composite function containers. | `["SETUID","SETGID"]` |
| `xfn.securityContext.readOnlyRootFilesystem` | Set the Composite function runner container root file system as read-only. | `true` |
| `xfn.securityContext.runAsGroup` | The group ID used by the Composite function runner container. | `65532` |
| `xfn.securityContext.runAsUser` | The user ID used by the Composite function runner container. | `65532` |
| `xfn.securityContext.seccompProfile.type` | Apply a `seccompProfile` to the Composite function runner container. The default value allows the Composite function runner container permissions to use the `unshare` syscall. | `"Unconfined"` |
{{< /table >}}
{{< /expand >}}
<!-- vale gitlab.Substitutions = YES -->

#### Command line customization

Apply custom settings at the command line with 
`helm install crossplane --set <setting>=<value>`.

For example, to change the image pull policy:

```shell
helm install crossplane \
--namespace crossplane-system \
--create-namespace \
crossplane-stable/crossplane \
--set image.pullPolicy=Always
```

Helm supports comma-seperated arguments.

For example, to change the image pull policy and number of replicas:

```shell
helm install crossplane \
--namespace crossplane-system \
--create-namespace \
crossplane-stable/crossplane \
--set image.pullPolicy=Always,replicas=2
```

#### Helm values file

Apply custom settings in a Helm _values_ file with
`helm install crossplane -f <filename>`.

A YAML file defines the customized settings. 

For example, to change the image pull policy and number of replicas:

Create a YAML with the customized settings.

```yaml
replicas: 2

image:
  pullPolicy: Always
```

Apply the file with `helm install`:

```shell
helm install crossplane \
--namespace crossplane-system \
--create-namespace \
crossplane-stable/crossplane \
-f settings.yaml
```

#### Feature flags

Crossplane introduces new features behind feature flags. By default
alpha features are off. Crossplane enables beta features by default. To enable a 
feature flag, set the `args` value in the Helm chart. Available feature flags
can be directly found by running `crossplane core start --help`, or by looking 
at the table below.

{{< expand "Feature flags" >}}
{{< table caption="Feature flags" >}}
| Status | Flag | Description |
| --- | --- | --- |
| Beta | `--enable-composition-revisions` |Enable support for CompositionRevisions |
| Alpha | `--enable-composition-functions` | Enable support for Composition Functions. |
| Alpha | `--enable-composition-webhook-schema-validation` | Enable Composition validation using schemas. |
| Alpha | `--enable-environment-configs` | Enable support for EnvironmentConfigs. |
| Alpha | `--enable-external-secret-stores` | Enable support for External Secret Stores. |
{{< /table >}}
{{< /expand >}}

Set these flags either in the `values.yaml` file or at install time using the
`--set` flag, for example: `--set
args='{"--enable-composition-functions","--enable-composition-webhook-schema-validation"}'`.

### Install pre-release Crossplane versions
Install a pre-release versions of Crossplane from the `master` Crossplane Helm channel.

Versions in the `master` channel are under active development and may be unstable.

{{< hint "warning" >}}
Don't use Crossplane `master` releases in production. Only use `stable` channel.  
Only use `master` for testing and development.
{{< /hint >}}


#### Add the Crossplane master Helm repository

Add the Crossplane repository with the `helm repo add` command.

```shell
helm repo add crossplane-master https://charts.crossplane.io/master/
```

Update the
local Helm chart cache with `helm repo update`.
```shell
helm repo update
```

#### Install the Crossplane master Helm chart

Install the Crossplane `master` Helm chart with `helm install`.

{{< hint "tip" >}}
View the changes Crossplane makes to your cluster with the 
`helm install --dry-run --debug` options. Helm shows what configurations it
applies without making changes to the Kubernetes cluster.
{{< /hint >}}

Crossplane creates and installs into the `crossplane-system` namespace.

```shell
helm install crossplane \
--namespace crossplane-system \
--create-namespace crossplane-master/crossplane \
--devel 
```

## Crossplane distributions
Third-party vendors may maintain their own Crossplane distributions. Vendor
supported distribution may have features or tooling that isn't in the
Community Crossplane distribution. 

The CNCF certified third-party distributions as 
"[conformant](https://github.com/cncf/crossplane-conformance)" with the 
Community Crossplane distribution.

### Vendors
Below are vendors providing conformant Crossplane distributions. 

#### Upbound
Upbound, the founders of Crossplane, maintains a free and open source 
distribution of Crossplane called 
[Universal Crossplane](https://www.upbound.io/products/universal-crossplane)
(`UXP`). 

Find information on UXP in the 
[Upbound UXP documentation](https://docs.upbound.io/uxp/install/).
