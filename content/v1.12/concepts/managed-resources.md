---
title: Managed Resources
weight: 102
---

A _managed resource_ (`MR`) represents an external service in a Provider. When
asking a Provider to create an external resource, the Provider creates a managed 
resource inside the Kubernetes cluster. Every external service managed by 
Crossplane maps to a managed resource. 

{{< hint "note" >}}
Crossplane calls the object inside Kubernetes a _managed resource_ and the
external object inside the Provider an _external resource_.
{{< /hint >}}

Examples of managed resources include:
* Amazon AWS EC2 [`Instance`](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/resources/ec2.aws.upbound.io/Instance/v1beta1)
* Google Cloud GKE [`Cluster`](https://marketplace.upbound.io/providers/upbound/provider-gcp/latest/resources/container.gcp.upbound.io/Cluster/v1beta1)
* Microsoft Azure Postgre [`Database`](https://marketplace.upbound.io/providers/upbound/provider-azure/latest/resources/dbforpostgresql.azure.upbound.io/Database/v1beta1)

{{< hint "tip" >}}

You can create individual managed resources, but Crossplane recommends using
[Compositions]({{<ref "../concepts/composition" >}}) and Claims to create
managed resources.
{{< /hint >}}

## Managed resource fields

The Provider defines the group, Kind and version of a managed resource. The
Provider also define the available settings of a managed resource.

### Group, kind and version
Each managed resource is a unique API endpoint with their own
group, Kind and version. 

For example the [Upbound AWS
Provider](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/)
defines the {{<hover label="gkv" line="2">}}Instance{{</hover>}} Kind from the
group {{<hover label="gkv" line="1">}}ec2.aws.upbound.io{{</hover>}}

```yaml {label="gkv"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
```

<!-- vale off -->
### deletionPolicy
<!-- vale on --> 

A managed resource's `deletionPolicy` tells the Provider what to do after
deleting the managed resource. If the `deletionPolicy` is `delete` the Provider
deletes the external resource as well. If the `deletionPolicy` is `orphan` the
Provider deletes the managed resource but doesn't delete the remote resource.

#### Options
* `deletionPolicy: delete` - **Default** - Delete the external resource when deleting the managed resource.
* `deletionPolicy: orphan` - Leave the external resource when deleting the managed resource. 

<!-- vale off -->
### forProvider
<!-- vale on -->

The {{<hover label="forProvider" line="4">}}spec.forProvider{{</hover>}} of a 
managed resource maps to the parameters of the external resource. 

For example, when creating an AWS EC2 instance, the Provider supports defining 
the AWS {{<hover label="forProvider" line="5">}}region{{</hover>}} and the VM 
size, called the 
{{<hover label="forProvider" line="6">}}instanceType{{</hover>}}.

{{< hint "note" >}}
The Provider defines the settings and their valid values. Providers also define
the required values in the `forProvider` definition.

Refer to the documentation of your specific Provider for details. 
{{< /hint >}}


```yaml {label="forProvider"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
spec:
  forProvider:
    region: us-west-1
    instanceType: t2.micro
```

{{< hint "important">}}
Crossplane considers the `forProvider` field of a managed resource 
the "source of truth." Crossplane overrides any changes made to a managed
resource outside of Crossplane. If a user makes a change inside a
Provider's web console, Crossplane reverts that change back to what's
configured in the `forProvider` setting. 
{{< /hint >}}

<!-- vale off -->
### managementPolicy
<!-- vale on --> 

{{<hint "important" >}}
The managed resource `managementPolicy` option is an alpha feature. 

Enable the `managementPolicy` in a provider with `--enable-management-policies` 
in a 
[ControllerConfig]({{<ref "../concepts/providers#controller-configuration" >}}).
{{< /hint >}}

A `managementPolicy` determines if Crossplane can make changes to managed
resources. The `ObserveOnly` policy imports existing external resources not 
originally created by Crossplane.  
This allows new managed resources to reference 
the `ObserveOnly` resource, for example, a shared database or network. 
The `ObserveOnly` policy can also place existing resources under the control of
Crossplane.  

{{< hint "tip" >}}
Read the [Import Existing Resources]({{<ref
"/knowledge-base/guides/import-existing-resources" >}}) guide for more
information on using the `managementPolicy` to import existing resources.
{{< /hint >}}

#### Options
* `managementPolicy: FullControl` - **Default** - Crossplane can create, change
  and delete the managed resource. 
* `managementPolicy: ObserveOnly` - Crossplane only imports the details of the
  external resource, but doesn't make any changes to the managed resource. 


<!-- vale off -->
### providerConfigRef
<!-- vale on -->

The `providerConfigRef` on a managed resource tells the Provider which
[ProviderConfig]({{<ref "../concepts/providers#provider-configuration">}}) to
use when creating the managed resource.  

Use a ProviderConfig to define the authentication method to use when 
communicating to the Provider.

{{< hint "important" >}}
If `providerConfigRef` isn't applied, Providers use the ProviderConfig named `default`.
{{< /hint >}}

For example, a managed resource references a ProviderConfig named {{<hover label="pcref"
line="6">}}user-keys{{</hover>}}.

This matches the {{<hover label="pc" line="4">}}name{{</hover>}} of a ProviderConfig.

```yaml {label="pcref"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
spec:
  forProvider:
    # Removed for brevity
  providerConfigRef: user-keys
```

```yaml {label="pc"}
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: user-keys
# Removed for brevity
```

{{< hint "tip" >}}
Different managed resources can reference different ProviderConfigs. This allows
different managed resources to authenticate with different credentials with the
same Provider. 
{{< /hint >}}

<!-- vale off -->
### providerRef
<!-- vale on --> 

Crossplane deprecated the `providerRef` field in `crossplane-runtime` 
[v0.10.0](https://github.com/crossplane/crossplane-runtime/releases/tag/v0.10.0). 
Managed resources using `providerRef`must use `providerConfigRef`.

<!-- vale off -->
### publishConnectionDetailsTo
<!-- vale on --> 

When a Provider creates a managed resource it may generate resource-specific
details, like usernames, passwords or connection details like an IP address. 

Crossplane stores these details in a Kubernetes Secret object



<!-- vale off -->
### writeConnectionSecretToRef
<!-- vale on --> 

{{< hint "important" >}}
The Crossplane community recommends using `publishConnectionDetailsTo` over
`writeConnectionSecretToRef`.
{{< /hint >}}


`writeConnectionSecretToRef`: A reference to the secret that you want this
  managed resource to write its connection secret that you'd be able to mount to
  your pods in the same namespace. For `RDSInstance`, this secret would contain
  `endpoint`, `username` and `password`.

## Annotations

## Status fields

<!-- vale off -->
### atProvider
<!-- vale on -->
https://github.com/crossplane/docs/issues/272


When provisioning is complete, you should see `READY: True` in the output. You
can take a look at its connection secret that is referenced under
`spec.writeConnectionSecretToRef`:

### Versioning

Crossplane closely follows the [Kubernetes API versioning
conventions][api-versioning] for the CRDs that it deploys. In short, for
`vXbeta` and `vX` versions, you can expect that either automatic migration or
instructions for manual migration will be provided when a new version of that
CRD schema is released.

In practice, we suggest the following guidelines to provider developers:
* Every new kind has to be introduced as `v1alpha1` with no exception.
* Breaking changes require a version change, i.e. `v1alpha1` needs to become
  `v1alpha2`.
  * Alpha resources don't require automatic conversions or manual instructions
    but it's recommended that manual instructions are provided.
  * Beta resources require at least manual instructions but it's recommended
    that conversion webhooks are used so that users can upgrade without any
    hands-on operation.
  * Stable resources require conversion webhooks.
* As long as the developer feels comfortable with the guarantees above, they can
  bump the version to beta or stable given that the CRD shape adheres to the
  Crossplane Resource Model (XRM) specifications for managed resources
  [here][managed-api-patterns].
* It's suggested that the bump from Alpha to Beta or from Beta to Stable happen
  after a bake period which includes at least one release.

### Grouping

In general, managed resources are high fidelity resources meaning they will
provide parameters and behaviors that are provided by the external resource API.
This applies to grouping of resources, too. For example, `Queue` appears under
`sqs` API group in AWS,so, its `APIVersion` and `Kind` look like the following:

```yaml
apiVersion: sqs.aws.crossplane.io/v1beta1
kind: Queue
```

#### Connection Details

Some Crossplane resources support writing connection details - things like URLs,
usernames, endpoints, and passwords to a Kubernetes `Secret`. You can specify
the secret to write by setting the `spec.writeConnectionSecretToRef` field. Note
that while all managed resources have a `writeConnectionSecretToRef` field, not
all managed resources actually have connection details to write - many will
write an empty `Secret`.

> Which managed resources have connection details and what connection details
> they have is currently undocumented. This is tracked in [this
> issue][issue-1143].

#### Immutable Properties

There are configuration parameters in external resources that cloud providers do
not allow to be changed. For example, in AWS, you cannot change the region of an
`RDSInstance`.

Some infrastructure tools such as Terraform delete and recreate the resource to
accommodate those changes but Crossplane does not take that route. Unless the
managed resource is deleted and its `deletionPolicy` is `Delete`, its controller
never deletes the external resource in the provider.

> Kubernetes does not yet support immutable fields for custom resources. This
> means Crossplane will allow immutable fields to be changed, but will not
> actually make the desired change. This is tracked in [this issue][issue-727].

#### Pausing Reconciliations
If a managed resource being reconciled by the [managed reconciler], has the
`crossplane.io/paused` annotation with its value set to `true` as in the
following example, then further reconciliations are paused on that resource
after emitting an event with the type `Synced`, the status `False`,
and the reason `ReconcilePaused`:
```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPC
metadata:
  name: paused-vpc
  annotations:
    crossplane.io/paused: "true"
...
```
Reconciliations on the managed resource will resume once the 
`crossplane.io/paused` annotation is removed or its value is set
to anything other than `true`.

### External Name

By default the name of the managed resource is used as the name of the external
cloud resource that will show up in your cloud console. To specify a different
external name, Crossplane has a special annotation to represent the name of the
external resource. For example, I would like to have a `CloudSQLInstance` with
an external name that is different than its managed resource name:

```yaml
apiVersion: database.gcp.crossplane.io/v1beta1
kind: CloudSQLInstance
metadata:
  name: foodb
  annotations:
    crossplane.io/external-name: my-special-db
spec:
  ...
```

When you create this managed resource, you will see that the name of
`CloudSQLInstance` in GCP console will be `my-special-db`.

If the annotation is not given, Crossplane will fill it with the name of the
managed resource by default. In cases where provider doesn't allow you to name
the resource, like AWS VPC, the controller creates the resource and sets
external annotation to be the name that the cloud provider chose. So, you would
see something like `vpc-28dsnh3` as the value of `crossplane.io/external-name`
annotation of your AWS `VPC` resource even if you added your own custom external
name during creation.

### Late Initialization

For some of the optional fields, users rely on the default that the cloud
provider chooses for them. Since Crossplane treats the managed resource as the
source of the truth, values of those fields need to exist in `spec` of the
managed resource. So, in each reconciliation, Crossplane will fill the value of
a field that is left empty by the user but is assigned a value by the provider.
For example, there could be two fields like `region` and `availabilityZone` and
you might want to give only `region` and leave the availability zone to be
chosen by the cloud provider. In that case, if the provider assigns an
availability zone, Crossplane gets that value and fills `availabilityZone`. Note
that if the field is already filled, the controller won't override its value.

### Deletion

When a deletion request is made for a managed resource, its controller starts
the deletion process immediately. However, the managed resource is kept in the
Kubernetes API (via a finalizer) until the controller confirms the external
resource in the cloud is gone. So you can be sure that if the managed resource
is deleted, then the external cloud resource is also deleted. Any errors that
happen during deletion will be added to the `status` of the managed resource, so
you can troubleshoot any issues.

## Dependencies

In many cases, an external resource refers to another one for a specific
configuration. For example, you could want your Azure Kubernetes cluster in a
specific Virtual Network. External resources have specific fields for these
relations, however, they usually require the information to be supplied in
different formats. In Azure MySQL, you might be required to enter only the name
of the Virtual Network while in Azure Kubernetes, it could be required to enter
a string in a specific format that includes other information such as resource
group name.

In Crossplane, users have 3 fields to refer to another resource. Here is an
example from Azure MySQL managed resource referring to an Azure Resource Group:

```yaml
spec:
  forProvider:
    resourceGroupName: foo-res-group
    resourceGroupNameRef:
      name: resourcegroup
    resourceGroupNameSelector:
      matchLabels:
        app: prod
```

In this example, the user provided only a set of labels to select a
`ResourceGroup` managed resource that already exists in the cluster via
`resourceGroupNameSelector`. Then after a specific `ResourceGroup` is selected,
`resourceGroupNameRef` is filled with the name of that `ResourceGroup` managed
resource. Then in the last step, Crossplane fills the actual `resourceGroupName`
field with whatever format Azure accepts it. Once a dependency is resolved, the
controller never changes it.

Users are able to specify any of these three fields:

- Selector to select via labels
- Reference to point to a determined managed resource
- Actual value that will be submitted to the provider

It's important to note that in case a reference exists, the managed resource
does not create the external resource until the referenced object is ready. In
this example, creation call of Azure MySQL Server will not be made until
referenced `ResourceGroup` has its `status.condition` named `Ready` to be true.


## Backup and Restore

Crossplane adheres to Kubernetes conventions as much as possible and one of the
advantages we gain is backup & restore ability with tools that work with native
Kubernetes types, like [Velero][velero].

If you'd like to backup and restore manually, you can simply export them and
save YAMLs in your file system. When you reload them, as we've discovered in
import section, their `crossplane.io/external-name` annotation and required
fields are there and those are enough to import a resource. The tool you're
using needs to store `annotations` and `spec` fields, which most tools do
including Velero.

[rds]: https://aws.amazon.com/rds/
[cloudsql]: https://cloud.google.com/sql
[api-versioning]: https://kubernetes.io/docs/reference/using-api/#api-versioning#api-versioning
[velero]: https://velero.io/
[issue-727]: https://github.com/crossplane/crossplane/issues/727
[issue-1143]: https://github.com/crossplane/crossplane/issues/1143
[managed-api-patterns]: https://github.com/crossplane/crossplane/blob/release-1.10/design/one-pager-managed-resource-api-design.md
[managed reconciler]: https://github.com/crossplane/crossplane-runtime/blob/84e629b9589852df1322ff1eae4c6e7639cf6e99/pkg/reconciler/managed/reconciler.go#L637
[management policies]: #management-policies