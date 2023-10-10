---
title: Providers
weight: 5
description: "Providers connect Crossplane to external APIs"
---

Providers enable Crossplane to provision infrastructure on an
external service. Providers create new Kubernetes APIs and map them to external
APIs.

Providers are responsible for all aspects of connecting to non-Kubernetes
resources. This includes authentication, making external API calls and
providing
[Kubernetes Controller](https://kubernetes.io/docs/concepts/architecture/controller/)
logic for any external resources.

Examples of providers include:

* [Provider AWS](https://github.com/upbound/provider-aws)
* [Provider Azure](https://github.com/upbound/provider-azure)
* [Provider GCP](https://github.com/upbound/provider-gcp)
* [Provider Kubernetes](https://github.com/crossplane-contrib/provider-kubernetes)

{{< hint "tip" >}}
Find more providers in the [Upbound Marketplace](https://marketplace.upbound.io).
{{< /hint >}}

<!-- vale write-good.Passive = NO -->
<!-- "are Managed" isn't passive in this context -->
Providers define every external resource they can create in Kubernetes as a
Kubernetes API endpoint.  
These endpoints are
[_Managed Resources_]({{<ref "managed-resources" >}}).
<!-- vale write-good.Passive = YES -->


## Install a Provider

Installing a provider creates a Provider pod that's responsible for installing
the Provider's APIs into the Kubernetes cluster. Providers constantly watch the
state of the desired managed resources and create any external resources that
are missing.

Install a Provider with a Crossplane
{{<hover label="install" line="2">}}Provider{{</hover >}} object setting the
{{<hover label="install" line="6">}}spec.package{{</hover >}} value to the
location of the provider package.

For example, to install the
[AWS Community Provider](https://github.com/crossplane-contrib/provider-aws),

```yaml {label="install"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.39.0
```

By default, the Provider pod installs in the same namespace as Crossplane
(`crossplane-system`).

{{<hint "note" >}}
Providers are part of the 
{{<hover label="install" line="1">}}pkg.crossplane.io{{</hover>}} group.  

The {{<hover label="meta-pkg" line="1">}}meta.pkg.crossplane.io{{</hover>}}
group is for creating Provider packages. 

Instructions on building Providers are outside of the scope of this
document.  
Read the Crossplane contributing 
[Provider Development Guide](https://github.com/crossplane/crossplane/blob/master/contributing/guide-provider-development.md)
for more information.

For information on the specification of Provider packages read the 
[Crossplane Provider Package specification](https://github.com/crossplane/crossplane/blob/master/contributing/specifications/xpkg.md#provider-package-requirements).

```yaml {label="meta-pkg"}
apiVersion: meta.pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
# Removed for brevity
```
{{</hint >}}

### Install with Helm

Crossplane supports installing Providers during an initial Crossplane
installation with the Crossplane Helm chart.

Use the
{{<hover label="helm" line="5" >}}--set provider.packages{{</hover >}}
argument with `helm install`.

For example, to install the AWS Community Provider,

```shell {label="helm"}
helm install crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace \
--set provider.packages='{xpkg.upbound.io/crossplane-contrib/provider-aws:v0.39.0}'
```

### Install offline

Crossplane installs packages from a local package cache. By
default the Crossplane package cache is an 
[emptyDir volume](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir). 

Configure Crossplane to use a 
[PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
to use a storage location containing the Provider image. Read more about
configuring the Crossplane Pod settings in the 
[Crossplane install documentation]({{<ref "../software/install#customize-the-crossplane-helm-chart">}}).

Provide the name of the Provider's `.xpkg` file and set 
{{<hover label="offline" line="7">}}packagePullPolicy: Never{{</hover>}}.

For example, to install a locally downloaded version of Provider AWS set the 
{{<hover label="offline" line="6">}}package{{</hover>}} to the local filename
and set the Provider's 
{{<hover label="offline" line="7">}}packagePullPolicy: Never{{</hover>}}.

```yaml {label="offline"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: offline-provider-aws
spec:
  package: provider-aws
  packagePullPolicy: Never
```

### Installation options

Providers support multiple configuration options to change installation related
settings. 

#### Provider pull policy

Use a {{<hover label="pullpolicy" line="6">}}packagePullPolicy{{</hover>}} to
define when Crossplane should download the Provider package to the local
Crossplane package cache.

The `packagePullPolicy` options are: 
* `IfNotPresent` - (**default**) Only download the package if it isn't in the cache.
* `Always` - Check for new packages every minute and download any matching
  package that isn't in the cache.
* `Never` - Never download the package. Packages are only installed from the
  local package cache. 

{{<hint "tip" >}}
The Crossplane 
{{<hover label="pullpolicy" line="6">}}packagePullPolicy{{</hover>}} works
like the Kubernetes container image 
[image pull policy](https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy).  

Crossplane supports the use of tags and package digest hashes like
Kubernetes images. 
{{< /hint >}}

For example, to `Always` download a given Provider package use the 
{{<hover label="pullpolicy" line="6">}}packagePullPolicy: Always{{</hover>}}
configuration. 

```yaml {label="pullpolicy",copy-lines="6"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  packagePullPolicy: Always
# Removed for brevity
```

#### Upgrade policy

Crossplane automatically upgrades a Provider the to the latest version available
in the package cache. 

Control the Provider upgrade behavior with a
{{<hover label="revision" line="6">}}revisionActivationPolicy{{</hover>}}.

The {{<hover label="revision" line="6">}}revisionActivationPolicy{{</hover>}} 
options are:
* `Automatic` - (**default**) Automatically use the latest Provider version
  available in the cache. 
* `Manual` - Require the current Provider in use to be manually set. 

For example, to change the upgrade behavior to require manual upgrades, set 
{{<hover label="revision" line="6">}}revisionActivationPolicy: Manual{{</hover>}}.

```yaml {label="revision"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  revisionActivationPolicy: Manual
# Removed for brevity
```

{{<hint "important" >}}
Crossplane only upgrades a Provider if a newer version is in the package cache.   
By default the Crossplane [`packagePullPolicy`](#provider-pull-policy) doesn't
download new Provider versions, even if they're available.
{{< /hint >}}

Read the [Provider upgrade](#upgrade-a-provider) section for
more information on the use of package revisions.

#### Package revision history limit

When Crossplane installs a different version of the same Provider package 
Crossplane creates a new _revision_. 

By default Crossplane maintains one _Inactive_ revision. 

{{<hint "note" >}}
Read the [Provider upgrade](#upgrade-a-provider) section for
more information on the use of package revisions.
{{< /hint >}}

Change the number of revisions Crossplane maintains with a Provider Package 
{{<hover label="revHistoryLimit" line="6">}}revisionHistoryLimit{{</hover>}}. 

The {{<hover label="revHistoryLimit" line="6">}}revisionHistoryLimit{{</hover>}}
field is an integer.  
The default value is `1`.  
Disable storing revisions by setting 
{{<hover label="revHistoryLimit" line="6">}}revisionHistoryLimit{{</hover>}} to `0`.

For example, to change the default setting and store 10 revisions use 
{{<hover label="revHistoryLimit" line="6">}}revisionHistoryLimit: 10{{</hover>}}.

```yaml {label="revHistoryLimit"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  revisionHistoryLimit: 10
# Removed for brevity
```

#### Install a provider from a private registry

Like Kubernetes uses `imagePullSecrets` to 
[install images from private registries](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/), 
Crossplane uses `packagePullSecrets` to install Provider packages from a private
registry. 

Use {{<hover label="pps" line="6">}}packagePullSecrets{{</hover>}} to provide a
Kubernetes secret to use for authentication when downloading a Provider package. 

{{<hint "important" >}}
The Kubernetes secret must be in the same namespace as Crossplane.
{{</hint >}}

The {{<hover label="pps" line="6">}}packagePullSecrets{{</hover>}} is a list of
secrets.

For example, to use the secret named
{{<hover label="pps" line="6">}}example-secret{{</hover>}} configure a 
{{<hover label="pps" line="6">}}packagePullSecrets{{</hover>}}.

```yaml {label="pps"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  packagePullSecrets: 
    - name: example-secret
# Removed for brevity
```

{{<hint "note" >}}
Configured `packagePullSecrets` aren't passed to any Provider package
dependencies. 
{{< /hint >}}

#### Ignore dependencies

By default Crossplane installs any [dependencies](#manage-dependencies) listed
in a Provider package. 

Crossplane can ignore a Provider package's dependencies with 
{{<hover label="pkgDep" line="6" >}}skipDependencyResolution{{</hover>}}.

For example, to disable dependency resolution configure 
{{<hover label="pkgDep" line="6" >}}skipDependencyResolution: true{{</hover>}}.

```yaml {label="pkgDep"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  skipDependencyResolution: true
# Removed for brevity
```

#### Ignore Crossplane version requirements

A Provider package may require a specific or minimum Crossplane version before
installing. By default, Crossplane doesn't install a Provider if the Crossplane
version doesn't meet the required version. 

Crossplane can ignore the required version with 
{{<hover label="xpVer" line="6">}}ignoreCrossplaneConstraints{{</hover>}}.

For example, to install a Provider package into an unsupported Crossplane
version, configure 
{{<hover label="xpVer" line="6">}}ignoreCrossplaneConstraints: true{{</hover>}}.

```yaml {label="xpVer"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  ignoreCrossplaneConstraints: true
# Removed for brevity
```

### Manage dependencies

Providers packages may include dependencies on other packages including
Configurations or other Providers. 

If Crossplane can't meet the dependencies of a Provider package the Provider
reports `HEALTHY` as `False`. 

For example, this installation of the Upbound AWS reference platform is
`HEALTHY: False`.

```shell {copy-lines="1"}
kubectl get providers
NAME              INSTALLED   HEALTHY   PACKAGE                                           AGE
provider-aws-s3   True        False     xpkg.upbound.io/upbound/provider-aws-s3:v0.41.0   12s
```

To see more information on why the Provider isn't `HEALTHY` use 
{{<hover label="depend" line="1">}}kubectl describe providerrevisions{{</hover>}}.

```yaml {copy-lines="1",label="depend"}
kubectl describe providerrevisions
Name:         provider-aws-s3-92206523fff4
API Version:  pkg.crossplane.io/v1
Kind:         ProviderRevision
Spec:
  Desired State:                  Active
  Image:                          xpkg.upbound.io/upbound/provider-aws-s3:v0.41.0
  Revision:                       1
Status:
  Conditions:
    Last Transition Time:  2023-10-10T21:06:39Z
    Reason:                UnhealthyPackageRevision
    Status:                False
    Type:                  Healthy
  Controller Ref:
    Name:
Events:
  Type     Reason             Age                From                                         Message
  ----     ------             ----               ----                                         -------
  Warning  LintPackage        41s (x3 over 47s)  packages/providerrevision.pkg.crossplane.io  incompatible Crossplane version: package is not compatible with Crossplane version (v1.10.0)
```

The {{<hover label="depend" line="17">}}Events{{</hover>}} show a 
{{<hover label="depend" line="20">}}Warning{{</hover>}} with a message that the
current version of Crossplane doesn't meet the Configuration package 
requirements.

## Upgrade a Provider

To upgrade an existing Provider edit the installed Provider Package by either
applying a new Provider manifest or with `kubectl edit providers`.

Update the version number in the Provider's `spec.package` and apply the change.
Crossplane installs the new image and creates a new `ProviderRevision`.

The `ProviderRevision` allows Crossplane to store deprecated Provider CRDs
without removing them until you decide.

View the `ProviderRevisions` with 
{{<hover label="getPR" line="1">}}kubectl get providerrevisions{{</hover>}}

```shell {label="getPR",copy-lines="1"}
kubectl get providerrevisions
NAME                                       HEALTHY   REVISION   IMAGE                                                    STATE      DEP-FOUND   DEP-INSTALLED   AGE
provider-aws-s3-dbc7f981d81f               True      1          xpkg.upbound.io/upbound/provider-aws-s3:v0.37.0          Active     1           1               10d
provider-nop-552a394a8acc                  True      2          xpkg.upbound.io/crossplane-contrib/provider-nop:v0.3.0   Active                                 11d
provider-nop-7e62d2a1a709                  True      1          xpkg.upbound.io/crossplane-contrib/provider-nop:v0.2.0   Inactive                               13d
upbound-provider-family-aws-710d8cfe9f53   True      1          xpkg.upbound.io/upbound/provider-family-aws:v0.40.0      Active                                 10d
```

By default Crossplane keeps a single 
{{<hover label="getPR" line="5">}}Inactive{{</hover>}} Provider.

Read the [revision history limit](#package-revision-history-limit) section to
change the default value. 

Only a single revision of a Provider is 
{{<hover label="getPR" line="4">}}Active{{</hover>}} at a time.

## Remove a Provider

Remove a Provider by deleting the Provider object with 
`kubectl delete provider`.

{{< hint "warning" >}}
Removing a Provider without first removing the Provider's managed resources
may abandon the resources. The external resources aren't deleted.

If you remove the Provider first, you must manually delete external resources
through your cloud provider. Managed resources must be manually deleted by
removing their finalizers.

For more information on deleting abandoned resources read the [Crossplane troubleshooting guide]({{<ref "/knowledge-base/guides/troubleshoot#deleting-when-a-resource-hangs" >}}).
{{< /hint >}}

## Verify a Provider

Providers install their own APIs representing the managed resources they support.
Providers may also create Deployments, Service Accounts or RBAC configuration.

View the status of a Provider with

`kubectl get providers`

During the install a Provider report `INSTALLED` as `True` and `HEALTHY` as
`Unknown`.

```shell {copy-lines="1"}
kubectl get providers
NAME                              INSTALLED   HEALTHY   PACKAGE                                                   AGE
crossplane-contrib-provider-aws   True        Unknown   xpkg.upbound.io/crossplane-contrib/provider-aws:v0.39.0   63s
```

After the Provider install completes and it's ready for use the `HEALTHY` status
reports `True`.

```shell {copy-lines="1"}
kubectl get providers
NAME                              INSTALLED   HEALTHY   PACKAGE                                                   AGE
crossplane-contrib-provider-aws   True        True      xpkg.upbound.io/crossplane-contrib/provider-aws:v0.39.0   88s
```

{{<hint "important" >}}
Some Providers install hundreds of Kubernetes Custom Resource Definitions (`CRDs`).
This can create significant strain on undersized API Servers, impacting Provider
install times.

The Crossplane community has more
[details on scaling CRDs](https://github.com/crossplane/crossplane/blob/master/design/one-pager-crd-scaling.md).
{{< /hint >}}

### Provider conditions

Crossplane uses a standard set of `Conditions` for Providers.  
View the conditions of a provider under their `Status` with
`kubectl describe provider`.

```yaml
kubectl describe provider
Name:         my-provider
API Version:  pkg.crossplane.io/v1
Kind:         Provider
# Removed for brevity
Status:
  Conditions:
    Reason:      HealthyPackageRevision
    Status:      True
    Type:        Healthy
    Reason:      ActivePackageRevision
    Status:      True
    Type:        Installed
# Removed for brevity
```

#### Types

Provider `Conditions` support two `Types`:

* `Type: Installed` - the Provider package installed but isn't ready for use.
* `Type: Healthy` - The Provider package is ready to use.

#### Reasons

Each `Reason` relates to a specific `Type` and `Status`. Crossplane uses the
following `Reasons` for Provider `Conditions`.

<!-- vale Google.Headings = NO -->
##### InactivePackageRevision

`Reason: InactivePackageRevision` indicates the Provider Package is using an
inactive Provider Package Revision.

<!-- vale Google.Headings = YES -->
```yaml
Type: Installed
Status: False
Reason: InactivePackageRevision
```

<!-- vale Google.Headings = NO -->
##### ActivePackageRevision
<!-- vale Google.Headings = YES -->
The Provider Package is the current Package Revision, but Crossplane hasn't
finished installing the Package Revision yet.

{{< hint "tip" >}}
Providers stuck in this state are because of a problem with Package Revisions.

Use `kubectl describe providerrevisions` for more details.
{{< /hint >}}

```yaml
Type: Installed
Status: True
Reason: ActivePackageRevision
```

<!-- vale Google.Headings = NO -->
##### HealthyPackageRevision

The Provider is fully installed and ready to use.

{{<hint "tip" >}}
`Reason: HealthyPackageRevision` is the normal state of a working Provider.
{{< /hint >}}

<!-- vale Google.Headings = YES -->
```yaml
Type: Healthy
Status: True
Reason: HealthyPackageRevision
```

<!-- vale Google.Headings = NO -->
##### UnhealthyPackageRevision
<!-- vale Google.Headings = YES -->

There was an error installing the Provider Package Revision, preventing
Crossplane from installing the Provider Package.

{{<hint "tip" >}}
Use `kubectl describe providerrevisions` for more details on why the Package
Revision failed.
{{< /hint >}}

```yaml
Type: Healthy
Status: False
Reason: UnhealthyPackageRevision
```
<!-- vale Google.Headings = NO -->
##### UnknownPackageRevisionHealth
<!-- vale Google.Headings = YES -->

The status of the Provider Package Revision is `Unknown`. The Provider Package
Revision may be installing or has an issue.

{{<hint "tip" >}}
Use `kubectl describe providerrevisions` for more details on why the Package
Revision failed.
{{< /hint >}}

```yaml
Type: Healthy
Status: Unknown
Reason: UnknownPackageRevisionHealth
```

## Configure a Provider

Providers have two different types of configurations:

* _Controller configurations_ that change the settings of the Provider pod
  running inside the Kubernetes cluster. For example, setting a `toleration` on
  the Provider pod.

* _Provider configurations_ that change settings used when communicating with
  an external provider. For example, cloud provider authentication.

{{<hint "important" >}}
Apply `ControllerConfig` objects to Providers.  

Apply `ProviderConfig` objects to managed resources.
{{< /hint >}}

### Controller configuration

{{< hint "important" >}}
The Crossplane community deprecated the `ControllerConfig` type in v1.11 to
announce that there are no further enhancements.
Applying a Controller configuration generates a deprecation warning.
<!-- vale Crossplane.Spelling = NO -->
<!-- vale gitlab.SubstitutionWarning = NO -->
<!-- allow runtime config -->
Controller configurations are still supported until there is a replacement type
in a future Crossplane version. You can read more about the design of the
[Package Runtime Config](https://github.com/crossplane/crossplane/blob/master/design/one-pager-package-runtime-config.md)
which is a future replacement.
<!-- vale Crossplane.Spelling = YES -->
<!-- vale gitlab.SubstitutionWarning = YES -->
{{< /hint >}}

Applying a Crossplane `ControllerConfig` to a Provider changes the settings of
the Provider's pod. The
[Crossplane ControllerConfig schema](https://doc.crds.dev/github.com/crossplane/crossplane/pkg.crossplane.io/ControllerConfig/v1alpha1)
defines the supported set of ControllerConfig settings.

The most common use case for ControllerConfigs are providing `args` to a
Provider's pod enabling optional services. For example, enabling
[external secret stores](https://docs.crossplane.io/knowledge-base/integrations/vault-as-secret-store/#enable-external-secret-stores-in-the-provider)
for a Provider.

Each Provider determines their supported set of `args`.

### Provider configuration

The `ProviderConfig` determines settings the Provider uses communicating to the
external provider. Each Provider determines available settings of their
`ProviderConfig`.

<!-- vale write-good.Weasel = NO -->
<!-- allow "usually" -->
Provider authentication is usually configured with a `ProviderConfig`. For
example, to use basic key-pair authentication with Provider AWS a
{{<hover label="providerconfig" line="2" >}}ProviderConfig{{</hover >}}
{{<hover label="providerconfig" line="5" >}}spec{{</hover >}}
defines the
{{<hover label="providerconfig" line="6" >}}credentials{{</hover >}} and that
the Provider pod should look in the Kubernetes
{{<hover label="providerconfig" line="7" >}}Secrets{{</hover >}} objects and use
the key named
{{<hover label="providerconfig" line="10" >}}aws-creds{{</hover >}}.
<!-- vale write-good.Weasel = YES -->
```yaml {label="providerconfig"}
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: aws-provider
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-creds
      key: creds
```

{{< hint "important" >}}
Authentication configuration may be different across Providers.

Read the documentation on a specific Provider for instructions on configuring
authentication for that Provider.
{{< /hint >}}

<!-- vale write-good.TooWordy = NO -->
<!-- allow multiple -->
ProviderConfig objects apply to individual Managed Resources. A single
Provider can authenticate with multiple users or accounts through
ProviderConfigs.
<!-- vale write-good.TooWordy = YES -->

Each account's credentials tie to a unique ProviderConfig. When creating a
managed resource, attach the desired ProviderConfig.

For example, two AWS ProviderConfigs, named
{{<hover label="user" line="4">}}user-keys{{</hover >}} and
{{<hover label="admin" line="4">}}admin-keys{{</hover >}}
use different Kubernetes secrets.

```yaml {label="user"}
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: user-keys
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: my-key
      key: secret-key
```

```yaml {label="admin"}
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: admin-keys
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: admin-key
      key: admin-secret-key
```

Apply the ProviderConfig when creating a managed resource.

This creates an AWS {{<hover label="user-bucket" line="2" >}}Bucket{{< /hover >}}
resource using the
{{<hover label="user-bucket" line="9" >}}user-keys{{< /hover >}} ProviderConfig.

```yaml {label="user-bucket"}
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: user-bucket
spec:
  forProvider:
    region: us-east-2
  providerConfigRef:
    name: user-keys
```

This creates a second {{<hover label="admin-bucket" line="2" >}}Bucket{{< /hover >}}
resource using the
{{<hover label="admin-bucket" line="9" >}}admin-keys{{< /hover >}} ProviderConfig.

```yaml {label="admin-bucket"}
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: user-bucket
spec:
  forProvider:
    region: us-east-2
  providerConfigRef:
    name: admin-keys
```
