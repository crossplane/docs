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

{{<expand "All Crossplane customization options" >}}
{{< table "table table-hover table-striped table-sm">}}
| Parameter | Description | Default |
| --- | --- | --- |
| `affinity` | Enable pod affinity for the Crossplane pods. | `{}` |
| `args` | Optional arguments passed to the Crossplane pods. | `{}` |
| `configuration.packages` | A list of Crossplane _Configuration_ packages to install together with Crossplane. | `[]` |
| `customAnnotations` | Add custom annotations to the Crossplane deployments and pods. | `{}` |
| `customLabels` | Add custom labels to the Crossplane deployments and pods. | `{}` |
| `deploymentStrategy` | The deployment strategy for the Crossplane and RBAC Manager pods. | `RollingUpdate` |
| `extraEnvVarsCrossplane` | List of extra environment variables to set in the Crossplane deployment. **Note**: Helm replaces all dot `.` values with underscores `_` (example: `SAMPLE.KEY=value1` becomes `SAMPLE_KEY=value1`). | `{}` |
| `extraEnvVarsRBACManager` | List of extra environment variables to set in the Crossplane RBAC Manager deployment. **Note**: Helm replaces all dot `.` values with underscores `_` (example: `SAMPLE.KEY=value1` becomes `SAMPLE_KEY=value1`). | `{}` |
| `image.pullPolicy` | Image pull policy used in all Crossplane containers. | `IfNotPresent` |
| `image.repository` | Image repository for the Crossplane pods. | `crossplane/crossplane` |
| `image.tag` | Image tag used to install the Crossplane pod image. | `master` |
| `imagePullSecrets` | Names of image pull secrets to use. | `{}` |
| `leaderElection` | Enable leader election for the Crossplane Manager pods. | `true` |
| `metrics.enabled` | Expose Crossplane and RBAC Manager pod metrics endpoints. | `false` |
| `nodeSelector` | Enable a node selector for the Crossplane pods. | `{}` |
| `packageCache.configMap` | A [Kubernetes `configMap`](https://kubernetes.io/docs/concepts/storage/volumes/#configmap) to define the Crossplane _Configuration_ package cache. Configuring `packageCache.configMap` disables the [Kubernetes `emptyDir`](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir). Crossplane ignores the `packageCache.configMap` when using `packageCache.pvc`. | `""` | 
| `packageCache.medium` | The [Kubernetes `emptyDir`](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) medium used for the Crossplane _Configuration_ package cache. Unused with `packageCache.pvc` or `packageCache.configMap` set. | `""` |
| `packageCache.pvc` | Name of the [Kubernetes `PersistentVolumeClaim`](https://kubernetes.io/docs/concepts/storage/volumes/#persistentvolumeclaim) used for the Crossplane _Configuration_ package cache. The `packageCache.pvc` takes precedence over `packageCache.configMap` and disables the [Kubernetes `emptyDir`](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir).  | `""` |
| `packageCache.sizeLimit` | The size limit of the [Kubernetes `emptyDir`](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) used for the Crossplane _Configuration_ package cache. Unused with `packageCache.pvc` or `packageCache.configMap` set. | `5Mi` |
| `podSecurityContextCrossplane` | Configure a [Kubernetes `securityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for the Crossplane pods. | `{}` |
| `podSecurityContextCrossplane` | Configure a [Kubernetes `securityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) for the Crossplane RBAC Manager pod. | `{}` |
| `priorityClassName` | The priority class name for Crossplane and RBAC Manager pods. | `""` |
| `provider.packages` | A list of Crossplane _Provider_ packages to install together with Crossplane. | `[]` |
| `rbacManager.affinity` | Enable affinity for the Crossplane RBAC Manager pod. | `{}` |
| `rbacManager.deploy` | Deploy the Crossplane RBAC Manager pod and its required roles. | `true` |
| `rbacManager.leaderElection` | Enable the leader election for the Crossplane RBAC Managers pod. | `true` |
| `rbacManager.managementPolicy`| The extent to which the Crossplane RBAC manager manages permissions. Setting `rbacManager.managementPolicy` to `All` the Crossplane RBAC controller manages all Crossplane controller and user roles. Setting `rbacManager.managementPolicy` to `Basic` the Crossplane RBAC controller only manages `crossplane-admin`, `crossplane-edit`, and `crossplane-view` user roles. | `All` |
| `rbacManager.nodeSelector` | Enable a node selector for the Crossplane RBAC Manager pod. | `{}` |
| `rbacManager.replicas` | The number of replicas to run for the Crossplane RBAC Manager pods. | `1` |
| `rbacManager.skipAggregatedClusterRoles` | Don't deploy RBAC aggregated ClusterRoles. | `false` |
| `rbacManager.tolerations` | Enable tolerations for Crossplane RBAC Managers pod. | `[]` |
| `registryCaBundleConfig.key` | Key to use from the _ConfigMap_ containing a CA bundle for fetching from package registries. | `{}` |
| `registryCaBundleConfig.name` | Name of _ConfigMap_ containing a CA bundle for fetching from package registries.  | `{}` |
| `replicas` | The number of replicas to run for the Crossplane pods. | `1` |
| `resourcesCrossplane.limits.cpu` | CPU resource limits for the Crossplane pods. | `100m` |
| `resourcesCrossplane.limits.memory` | Memory resource limits for the Crossplane pods. | `512Mi` |
| `resourcesCrossplane.requests.cpu` | CPU resource requests for the Crossplane pods. | `100m` |
| `resourcesCrossplane.requests.memory` | Memory resource requests for the Crossplane pods. | `256Mi` |
| `resourcesRBACManager.limits.cpu` | CPU resource limits for the Crossplane RBAC Manager pod. | `100m` |
| `resourcesRBACManager.limits.memory` | Memory resource limits for the Crossplane RBAC Manager pod. | `512Mi` |
| `resourcesRBACManager.requests.cpu` | CPU resource requests for the Crossplane RBAC Manager pod. | `100m` |
| `resourcesRBACManager.requests.memory` | Memory resource requests value the Crossplane RBAC Manager pod. | `256Mi` |
| `securityContextCrossplane.allowPrivilegeEscalation` | Allow privilege escalation for the Crossplane pods. | `false` |
| `securityContextCrossplane.readOnlyRootFilesystem` | Set a read only root file system for the Crossplane pods. | `true` |
| `securityContextCrossplane.runAsGroup` | A _run as group_ for the Crossplane pods. | `65532` |
| `securityContextCrossplane.runAsUser` | A _run as user_ for the Crossplane pods. | `65532` |
| `securityContextRBACManager.allowPrivilegeEscalation` | Allow privilege escalation for the Crossplane RBAC Manager pod. | `false` |
| `securityContextRBACManager.readOnlyRootFilesystem` | Set a read only root file system for the Crossplane RBAC Manager pod. | `true` |
| `securityContextRBACManager.runAsGroup` | The _run as group_ for the Crossplane RBAC Manager pod. | `65532` |
| `securityContextRBACManager.runAsUser` | The _run as user_ for the Crossplane RBAC Manager pod. | `65532` |
| `serviceAccount.customAnnotations` | Add custom annotations to the Crossplane service account. | `{}` |
| `tolerations` | Enable tolerations for Crossplane pod. | `[]` |
| `webhooks.enabled` | Enable webhooks for Crossplane as well as packages installed by Crossplane. | `false` |
| `xfn.args` | Optional arguments passed to the _Composite Resource Functions_ sidecar container. | `{}` |
| `xfn.cache.medium` | The [Kubernetes `emptyDir`](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) medium used for the _Composite Resource Functions_ sidecar container cache. Unused with `xfn.cache.pvc` set. | `""` |
| `xfn.cache.pvc` | Name of the [Kubernetes `PersistentVolumeClaim`](https://kubernetes.io/docs/concepts/storage/volumes/#persistentvolumeclaim) used for the _Composite Resource Functions_ sidecar container cache. The `xfn.cache.pvc` disables the _Composite Resource Functions_ [Kubernetes `emptyDir`](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir).  | `""` |
| `xfn.cache.sizeLimit` | The size limit of the [Kubernetes `emptyDir`](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) used for the _Composite Resource Functions_ sidecar container cache. Unused with `xfn.cache.pvc` set. | `1Gi` |
| `xfn.enabled` | Enable Crossplane _Composite Resource Functions_. Enabling _Composite Resource Functions_ also requires `args` set with `--enable-composition-functions`. | `false` |
| `xfn.extraEnvVars` | List of extra environment variables to set in the _Composite Resource Functions_ sidecar container. **Note**: Helm replaces all dot `.` values with underscores `_` (example: `SAMPLE.KEY=value1` becomes `SAMPLE_KEY=value1`). | `{}` |
| `xfn.image.pullPolicy` | Image pull policy used in the _Composite Resource Functions_ sidecar container. | `IfNotPresent` |
| `xfn.image.repository` | Image repository for the _Composite Resource Functions_ sidecar container. | `crossplane/xfn` |
| `xfn.image.tag` | Image tag used to install the _Composite Resource Functions_ sidecar container. | The installed Crossplane version. |
| `xfn.imagePullSecrets` | Names of image pull secrets to use when installing the _Composite Resource Functions_ sidecar container. | `{}` |
| `xfn.limits.cpu` | CPU resource limits for the Crossplane RBAC Manager pod. | `2000m` |
| `xfn.limits.memory` | Memory resource limits for the Crossplane RBAC Manager pod. | `2Gi` |
| `xfn.requests.cpu` | CPU resource requests for the Crossplane RBAC Manager pod. | `1000m` |
| `xfn.requests.memory` | Memory resource requests value the Crossplane RBAC Manager pod. | `1Gi` |
| `xfn.securityContext.allowPrivilegeEscalation` | Allow privilege escalation for the Crossplane RBAC Manager pod. | `false` |
| `xfn.securityContext.readOnlyRootFilesystem` | Set a read only root file system for the Crossplane RBAC Manager pod. | `true` |
| `xfn.securityContext.runAsGroup` | The _run as group_ for the Crossplane RBAC Manager pod. | `65532` |
| `xfn.securityContext.runAsUser` | The _run as user_ for the Crossplane RBAC Manager pod. | `65532` |
{{< /table >}}
{{< /expand >}}

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

Crossplane usually introduces new features behind feature flags. By default
alpha features are off, while beta features are enabled. To enable a feature
flag, set the `args` value in the Helm chart. Available feature flags can be
directly found by running `crossplane core start --help`, or by looking at the
table below.

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
args=["--enable-composition-functions","--enable-composition-webhook-schema-validation"]`.

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




