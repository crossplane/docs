---
title: Crossplane Introduction
weight: 2
---

Crossplane connects your Kubernetes cluster to external,
non-Kubernetes resources, and allows platform teams to build custom Kubernetes
APIs to consume those resources.

Crossplane creates Kubernetes
[Custom Resource Definitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)
(`CRDs`) to represent the external resources as native 
[Kubernetes objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/). 
As native Kubernetes objects, you can use standard commands like `kubectl create`
and `kubectl describe`. The full 
[Kubernetes API](https://kubernetes.io/docs/reference/using-api/) is available
for every Crossplane resource. 

Crossplane also acts as a
[Kubernetes Controller](https://kubernetes.io/docs/concepts/architecture/controller/)
to monitor the state of the external resources and provide state enforcement. If
something modifies or deletes a resource outside of Kubernetes, Crossplane reverses
the change or recreates the deleted resource.

{{<img src="/media/crossplane-intro-diagram.png" alt="Diagram showing a user communicating to Kubernetes. Crossplane connected to Kubernetes and Crossplane communicating with AWS, Azure and GCP" >}}
With Crossplane installed in a Kubernetes cluster, users only communicate with
Kubernetes. Crossplane manages the communication to external resources like AWS,
Azure or Google Cloud.

Crossplane also allows the creation of custom Kubernetes APIs. Platform teams can
combine external resources and simplify or customize the APIs presented to the
platform consumers.

## Crossplane components overview
This table provides a summary of Crossplane components and their roles. 

{{< table "table table-hover table-sm">}}
| Component | Abbreviation | Scope | Summary |
| --- | --- | --- | ---- | 
| [Provider]({{<ref "#Provider">}}) | | cluster | Creates CRDs for an external service. |
| [ProviderConfig]({{<ref "#ProviderConfig">}}) | `PC` | cluster | Applies settings for a Provider. |
| [Managed Resource]({{<ref "#managed-resource">}}) | `MR` | cluster | A provider resource created and managed by Crossplane inside the Kubernetes cluster. | 
| [Composition]({{<ref "#composition">}}) |  | cluster | Creates multiple Managed Resources at once. |
| [Composite Resources]({{<ref "#composite-resources" >}}) | `XR` | cluster | A custom API defined by the platform team, used to access _Compositions_. |
| [Composite Resource Definitions]({{<ref "#composite-resource-definitions" >}}) | `XRD` | cluster | Defines the API schema for a _Composite Resource_ |
| [Claims]({{<ref "#claims" >}}) | `XC` | namespace | Like a _Composite Resource_, but namespace scoped. | 
{{< /table >}}

## The Crossplane Pod
When installed in a Kubernetes cluster Crossplane creates an initial set of
Custom Resource Definitions (`CRDs`) of the core Crossplane components. 

{{< expand "View the initial Crossplane CRDs" >}}
After installing Crossplane use `kubectl get crds` to view the Crossplane
installed CRDs.

```shell
kubectl get crds
NAME                                                     
compositeresourcedefinitions.apiextensions.crossplane.io 
compositionrevisions.apiextensions.crossplane.io         
compositions.apiextensions.crossplane.io                 
configurationrevisions.pkg.crossplane.io                 
configurations.pkg.crossplane.io                         
controllerconfigs.pkg.crossplane.io                      
locks.pkg.crossplane.io                                  
providerrevisions.pkg.crossplane.io                      
providers.pkg.crossplane.io                              
storeconfigs.secrets.crossplane.io                       
```
{{< /expand >}}

The following sections describe the functions of some of these CRDs.

## Providers
A Crossplane _Provider_ creates a second set of CRDs that define how Crossplane
connects to a non-Kubernetes service. Each external service relies on its own
Provider. For example, 
[AWS](https://marketplace.upbound.io/providers/upbound/provider-aws), 
[Azure](https://marketplace.upbound.io/providers/upbound/provider-azure) 
and [GCP](https://marketplace.upbound.io/providers/upbound/provider-gcp)
are different providers for each cloud service.

{{< hint "tip" >}}
Most Providers are for cloud services but Crossplane can use a Provider to
connect to any service with an API.
{{< /hint >}}

For example, an AWS Provider defines Kubernetes CRDs for AWS resources like EC2
compute instances or S3 storage buckets.

The Provider defines the Kubernetes API definition for the external resource.
For example, the 
[Upbound Provider-AWS](https://marketplace.upbound.io/providers/upbound/provider-aws/)
defines a 
[`bucket`](https://marketplace.upbound.io/providers/upbound/provider-aws/v0.25.0/resources/s3.aws.upbound.io/Bucket/v1beta1) 
resource for creating and managing AWS S3 storage buckets. 

Within the `bucket` CRD is a
[`spec.forProvider.region`](https://marketplace.upbound.io/providers/upbound/provider-aws/v0.25.0/resources/s3.aws.upbound.io/Bucket/v1beta1#doc:spec-forProvider-region)
value that defines which AWS region to deploy the bucket in.

The Upbound Marketplace contains a large 
[collection of Crossplane Providers](https://marketplace.upbound.io/providers).

More providers are available in the [Crossplane Contrib repository](https://github.com/crossplane-contrib/).

Providers are cluster scoped and available to all cluster namespaces.

## Provider configurations
Providers also have _ProviderConfigs_. _ProviderConfigs_ configure settings
related to the Provider like authentication or global defaults for the
Provider.

The API endpoints for ProviderConfigs are unique to each Provider.

_ProviderConfigs_ are cluster scoped and available to all cluster namespaces.

## Managed Resources
A Provider's CRDs map to individual _resources_ inside the provider. When
Crossplane creates and monitors a resource it's a _Managed Resource_.

Using a Provider's CRD creates a unique _Managed Resource_. For example,
using the Provider AWS's `bucket` CRD creates a `bucket` _Managed Resource_
inside the Kubernetes cluster. Using the CRD a second time creates a second,
unique, `bucket` _Managed Resource_.

The Crossplane controller provides state enforcement for _Managed Resources_.
Crossplane enforces the settings and existence of _Managed Resources_. This
"Controller Pattern" is like how the Kubernetes 
[kube-controller-manager](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/)
enforces state for pods.

_Managed Resources_ are cluster scoped and available to all cluster namespaces.

## Compositions

_Compositions_ define a collection of Managed Resources and their settings. For
example, a _Composition_ can combine a compute, network and database resource.
This single _Composition_ creates three _Managed Resources_.

_Compositions_ are cluster scoped and available to all cluster namespaces.


## Composite Resources

_Composite Resources_ (`XRs`) are custom Kubernetes APIs defined by Crossplane 
administrators.

Crossplane links _Composite Resources_ to specific _Compositions_. 
A _Composite Resource_ hides or abstracts the _Managed Resources_ configuration 
required in the _Composition_.

For example, a _Composition_ that creates a compute node requires knowledge of a
cloud provider's compute class names like AWS's `m6in.large` or GCP's `e2-standard-2`. A
_Composite Resource_ can provide default or pre-defined values. The
infrastructure consumer may only need to provide a `large` or `small` parameter.
The _Composite Resource_ defines those options and the _Composition_ maps them
to specific settings.

An example _Composite Resource_:
```yaml {label="XR"}
apiVersion: test.example.org/v1alpha1
kind: myComputeInstance
spec:
  size: "large"
```

The {{< hover label="XR" line="4" >}}size{{</ hover >}} is the only parameter
required to create the compute instance. 

An associated _Composition_ maps `size` to the AWS Provider's
[`instanceType`](https://marketplace.upbound.io/providers/upbound/provider-aws/v0.25.0/resources/ec2.aws.upbound.io/Instance/v1beta1#doc:spec-forProvider-instanceType)
value.


{{< hint "note" >}}
[Composite Resource Definitions]({{<ref "#composite-resource-definitions" >}})
discuss the `apiVersion` and `kind` fields.
{{< /hint >}}

_Composite Resources_ are cluster scoped and available to all cluster namespaces.

## Composite Resource Definitions

_Composite Resource Definitions_ (`XRDs`) define the API schema for 
_Composite Resources_.

A _Composite Resource Definition_ defines the `apiVersion` and `kind` as well as
the values of the `spec` for a _Composite Resource_. This defines the fields,
default values and valid inputs.

_Composite Resource Definitions_ are cluster scoped and available to all cluster
namespaces.

## Claims

_Claims_ (`XC`) provide identical capabilities to _Composite Resources_, but
_Claims_ are namespace scoped. 

Using _Claims_ users isolated to a namespace can create and manage resources
without permissions to cluster-wide _Composite Resources_.

The relationship between _Claims_ and _Composite Resources_ is like 
[Kubernetes _Persistent Volume Claims_ and _Persistent Volumes_](https://kubernetes.io/docs/concepts/storage/persistent-volumes/). 

_Claims_ are namespace scoped.