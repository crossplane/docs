---
title: Providers
weight: 101
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
Kubernetes API endpoint. These endpoints are 
[_Managed Resources_]({{<ref "managed-resources" >}}).
<!-- vale write-good.Passive = YES -->

{{< hint "note" >}}
Instructions on building your own Provider are outside of the scope of this
document. Read the Crossplane contributing [Provider Development
Guide](https://github.com/crossplane/crossplane/blob/master/contributing/guide-provider-development.md)
for more information.
{{< /hint >}}

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

{{< hint "tip" >}}
Providers are Crossplane Packages. Read more about Packages in the
[Packages documentation]({{<ref "packages" >}}).
{{< /hint >}}

By default, the Provider pod installs in the same namespace as Crossplane
(`crossplane-system`).

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

### Install from a private repository

Installing a Provider from a private package repository requires a
Kubernetes secret object. The Provider uses the secret with the
{{<hover label="pps" line="7" >}}packagePullSecrets{{</hover>}} option. 

```yaml {label="pps"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: private-provider
spec:
  package: private-repo.example.org/providers/my-provider
  packagePullSecrets:
    - name: my-secret
```

{{< hint "note" >}}
The Kubernetes secret object the Provider uses must be in the same namespace as
the Crossplane pod.
{{< /hint >}}

## Upgrade a Provider

To upgrade an existing Provider edit the installed Provider Package by either
applying a new Provider manifest or with `kubectl edit providers`.

Update the version number in the Provider's `spec.package` and apply the change. 
Crossplane installs the new image and creates a new `ProviderRevision`.

## Remove a Provider

Remove a Provider by deleting the Provider object with `kubectl delete
provider`. 

{{< hint "warning" >}}
Removing a Provider without first removing the Provider's managed resources 
may abandon the resources. The external resources aren't deleted.

If you remove the Provider first, you must manually delete external resources 
through your cloud provider. Managed resources must be manually deleted by 
removing their finalizers. 

For more information on deleting abandoned resources read the [Crossplane
troubleshooting guide]({{<ref "/knowledge-base/guides/troubleshoot#deleting-when-a-resource-hangs" >}}). 
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
  running inside the Kubernetes cluster. For example, Pod `toleration`. 
* _Provider configurations_ that change settings used when communicating with
  an external provider. For example, cloud provider authentication. 

{{<hint "important" >}}
Apply `ControllerConfig` objects to Providers.  

Apply `ProviderConfig` objects to managed resources.
{{< /hint >}}

### Controller configuration 
{{< hint "important" >}}
The Crossplane community deprecated the `ControllerConfig` type in v1.11.
Applying a Controller configuration generates a deprecation warning. 

Controller configurations are still supported until there is a replacement type
in a future Crossplane version.
{{< /hint >}}

Applying a Crossplane `ControllerConfig` to a Provider changes the settings of
the Provider's pod. The
[Crossplane ControllerConfig schema](https://doc.crds.dev/github.com/crossplane/crossplane/pkg.crossplane.io/ControllerConfig/v1alpha1) 
defines the supported set of ControllerConfig settings. 

The most common use-case for ControllerConfigs are providing `args` to a
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

