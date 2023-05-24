---
title: Managed Resources
weight: 102
---

A _managed resource_ (`MR`) represents an external service in a Provider. When
asking a Provider to create an external resource, the Provider creates a managed resource
inside the Kubernetes cluster. Every external service managed by Crossplane maps
to a managed resource. 

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
deletes the external resource as well. If the `deletionPolicy` is `orphan` 

#### Options
* `deletionPolicy: delete` - Delete the external resource when deleting the managed resource. _Default value_
* `deletionPolicy: orphan` - Leave the external resource when deleting the managed resource. 

<!-- vale off -->
### forProvider
<!-- vale on -->

The {{<hover label="forProvider" line="4">}}spec.forProvider{{</hover>}} of a managed resource maps to the parameters of the
external resource. 

For example, when creating an AWS EC2 instance the Provider supports defining the 
AWS {{<hover label="forProvider" line="5">}}region{{</hover>}} and the VM size,
called the {{<hover label="forProvider" line="6">}}instanceType{{</hover>}}.

```yaml {label="forProvider"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
spec:
  forProvider:
    region: us-west-1
    instanceType: t2.micro
```

{{< hint "note" >}}
The Provider defines the settings and their valid values. Providers also define
the required values in the `forProvider` definition.

Refer to the documentation for your specific Provider for details. 
{{< /hint >}}


<!-- vale off -->
### managementPolicy
<!-- vale on --> 

<!-- vale off -->
### providerConfigRef
<!-- vale on -->

The `providerConfigRef` on a managed resource tells the Provider which
[ProviderConfig]({{<ref "../concepts/providers#provider-configuration">}}) to
use when creating the managed resource.  

A ProviderConfig commonly defines the authentication to use when communicating to
the Provider.

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

<!-- vale off -->
### writeConnectionSecretToRef
<!-- vale on --> 

A Managed Resource (MR) is Crossplane's representation of a resource in an
external system - most commonly a cloud provider. Managed Resources are
opinionated, Crossplane Resource Model ([XRM]({{<ref "../concepts/terminology">}})) compliant Kubernetes
Custom Resources that are installed by a Crossplane [provider]({{<ref "providers" >}}).

For example, `RDSInstance` in the AWS Provider corresponds to an actual RDS
Instance in AWS. There is a one-to-one relationship and the changes on managed
resources are reflected directly on the corresponding resource in the provider.
Similarly, the `Database` types in the SQL provider represent a PostgreSQL or
MySQL database.

Managed Resources are the building blocks of Crossplane. They're designed to be
_composed_ into higher level, opinionated Custom Resources that Crossplane calls
Composite Resources or XRs - not used directly. See the
[Composition]({{<ref "composition" >}}) documentation for more information.

## Syntax

Crossplane API conventions extend the Kubernetes API conventions for the schema
of Crossplane managed resources. Following is an example of a managed resource:

{{< tabs >}}
{{< tab "AWS" >}}

The AWS provider supports provisioning an [RDS][rds] instance via the `RDSInstance`
managed resource it adds to Crossplane.

```yaml
apiVersion: database.aws.crossplane.io/v1beta1
kind: RDSInstance
metadata:
  name: rdspostgresql
spec:
  forProvider:
    region: us-east-1
    dbInstanceClass: db.t2.small
    masterUsername: masteruser
    allocatedStorage: 20
    engine: postgres
    engineVersion: "12"
    skipFinalSnapshotBeforeDeletion: true
  writeConnectionSecretToRef:
    namespace: crossplane-system
    name: aws-rdspostgresql-conn
```

```console
kubectl apply -f https://raw.githubusercontent.com/crossplane/crossplane/release-1.10/docs/snippets/provision/aws.yaml
```

Creating the above instance will cause Crossplane to provision an RDS instance
on AWS. You can view the progress with the following command:

```console
kubectl get rdsinstance rdspostgresql
```

When provisioning is complete, you should see `READY: True` in the output. You
can take a look at its connection secret that is referenced under
`spec.writeConnectionSecretToRef`:

```console
kubectl describe secret aws-rdspostgresql-conn -n crossplane-system
```

You can then delete the `RDSInstance`:

```console
kubectl delete rdsinstance rdspostgresql
```

{{< /tab >}}
{{< tab "GCP" >}}

The GCP provider supports provisioning a [CloudSQL][cloudsql] instance with the
`CloudSQLInstance` managed resource it adds to Crossplane.

```yaml
apiVersion: database.gcp.crossplane.io/v1beta1
kind: CloudSQLInstance
metadata:
  name: cloudsqlpostgresql
spec:
  forProvider:
    databaseVersion: POSTGRES_12
    region: us-central1
    settings:
      tier: db-custom-1-3840
      dataDiskType: PD_SSD
      dataDiskSizeGb: 10
  writeConnectionSecretToRef:
    namespace: crossplane-system
    name: cloudsqlpostgresql-conn
```

```console
kubectl apply -f https://raw.githubusercontent.com/crossplane/crossplane/release-1.10/docs/snippets/provision/gcp.yaml
```

Creating the above instance will cause Crossplane to provision a CloudSQL
instance on GCP. You can view the progress with the following command:

```console
kubectl get cloudsqlinstance cloudsqlpostgresql
```

When provisioning is complete, you should see `READY: True` in the output. You
can take a look at its connection secret that is referenced under
`spec.writeConnectionSecretToRef`:

```console
kubectl describe secret cloudsqlpostgresql-conn -n crossplane-system
```

You can then delete the `CloudSQLInstance`:

```console
kubectl delete cloudsqlinstance cloudsqlpostgresql
```

{{< /tab >}}
{{< tab "Azure" >}}

The Azure provider supports provisioning an [Azure Database for PostgreSQL]
instance with the `PostgreSQLServer` managed resource it adds to Crossplane.

> Note: provisioning an Azure Database for PostgreSQL requires the presence of a
> [Resource Group] in your Azure account. We go ahead and provision a new
> `ResourceGroup` here in case you do not already have a suitable one in your
> account.

```yaml
apiVersion: azure.crossplane.io/v1alpha3
kind: ResourceGroup
metadata:
  name: sqlserverpostgresql-rg
spec:
  location: West US 2
---
apiVersion: database.azure.crossplane.io/v1beta1
kind: PostgreSQLServer
metadata:
  name: sqlserverpostgresql
spec:
  forProvider:
    administratorLogin: myadmin
    resourceGroupNameRef:
      name: sqlserverpostgresql-rg
    location: West US 2
    sslEnforcement: Disabled
    version: "9.6"
    sku:
      tier: GeneralPurpose
      capacity: 2
      family: Gen5
    storageProfile:
      storageMB: 20480
  writeConnectionSecretToRef:
    namespace: crossplane-system
    name: sqlserverpostgresql-conn
```

```console
kubectl apply -f https://raw.githubusercontent.com/crossplane/crossplane/release-1.10/docs/snippets/provision/azure.yaml
```

Creating the above instance will cause Crossplane to provision a PostgreSQL
database instance on Azure. You can view the progress with the following
command:

```console
kubectl get postgresqlserver sqlserverpostgresql
```

When provisioning is complete, you should see `READY: True` in the output. You
can take a look at its connection secret that is referenced under
`spec.writeConnectionSecretToRef`:

```console
kubectl describe secret sqlserverpostgresql-conn -n crossplane-system
```

You can then delete the `PostgreSQLServer`:

```console
kubectl delete postgresqlserver sqlserverpostgresql
kubectl delete resourcegroup sqlserverpostgresql-rg
```

{{< /tab >}}
{{< /tabs >}}

In Kubernetes, `spec` top field represents the desired state of the user.
Crossplane adheres to that and has its own conventions about how the fields
under `spec` should look like.

* `writeConnectionSecretToRef`: A reference to the secret that you want this
  managed resource to write its connection secret that you'd be able to mount to
  your pods in the same namespace. For `RDSInstance`, this secret would contain
  `endpoint`, `username` and `password`.

* `providerConfigRef`: Reference to the `ProviderConfig` resource that will
  provide information regarding authentication of Crossplane to the provider.
  `ProviderConfig` resources refer to `Secret` and potentially contain other
  information regarding authentication. The `providerConfigRef` is defaulted to
  a `ProviderConfig` named `default` if omitted.

* `deletionPolicy`: Enum to specify whether the actual cloud resource should be
  deleted when this managed resource is deleted in Kubernetes API server.
  Possible values are `Delete` (the default) and `Orphan`.

* `managementPolicy`: Enum to specify the level of control Crossplane has over
  the external resource.
  Possible values are `FullControl` (the default) and `ObserveOnly`.
  {{<hint "important">}}
  `managementPolicy` is an experimental feature, see the management policies
  section below for further details.
  {{< /hint >}}

* `forProvider`: While the rest of the fields relate to how Crossplane should
  behave, the fields under `forProvider` are solely used to configure the actual
  external resource. In most of the cases, the field names correspond to the
  what exists in provider's API Reference.

  The objects under `forProvider` field can get huge depending on the provider
  API. For example, GCP `ServiceAccount` has only a few fields while GCP
  `CloudSQLInstance` has over 100 fields that you can configure.

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

## Behavior

As a general rule, managed resource controllers try not to make any decision
that is not specified by the user in the desired state since managed resources
are the lowest level primitives that operate directly on the cloud provider
APIs.

### Continuous Reconciliation

Crossplane providers continuously reconcile the managed resource to achieve the
desired state. The parameters under `spec` are considered the one and only
source of truth for the external resource. This means that if someone changed a
configuration in the UI of the provider, like AWS Console, Crossplane will
change it back to what's given under `spec`.

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

## Management Policies

Crossplane offers a set of management policies that allow you to define the
level of control it has over external resources. You can configure these
policies using the `spec.managementPolicy` field in the managed resource
definition. The available policies include:

- `FullControl (Default)`: With this policy, Crossplane fully manages and
controls the external resource.
- `ObserveOnly`: With the ObserveOnly policy, Crossplane only observes the
external resource without making any changes or deletions.

{{<hint "important" >}}
Management policies are an experimental feature, and the API is
subject to change.
{{< /hint >}}

To use management policies, you must enable them with the
`--enable-management-policies` flag when starting the provider controller.

## Importing Existing Resources

If you have some resources that are already provisioned in the cloud provider,
you can import them as managed resources and let Crossplane manage them. What
you need to do is to enter the name of the external resource as well as the
required fields on the managed resource. For example, let's say I have a GCP
Network provisioned from GCP console and I would like to migrate it to
Crossplane. Here is the YAML that I need to create:

```yaml
apiVersion: compute.gcp.crossplane.io/v1beta1
kind: Network
metadata:
  name: foo-network
  annotations:
    crossplane.io/external-name: existing-network
spec:
  forProvider: {}
  providerConfigRef:
    name: default
```

Crossplane will check whether a GCP Network called `existing-network` exists,
and if it does, then the optional fields under `forProvider` will be filled with
the values that are fetched from the provider.

Note that if a resource has required fields, you must fill those fields or the
creation of the managed resource will be rejected. So, in those cases, you will
need to enter the name of the resource as well as the required fields.

### Alternative Import Procedure: Start with ObserveOnly

Directly importing existing managed resources approach has the following caveats:

1. You must provide all the required fields in the spec of the resource with
correct values even though they're not used for importing the resource. A wrong
value for a required field result in a configuration update which isn't
desired.
2. Any typos in the external name annotation or mistakes in the identifying
arguments, such as the `region`, results in the creation of a new resource
instead of importing the existing one.

Instead of manually creating resources you can import the resource with an
`ObserveOnly` management policy.

Crossplane imports `ObserveOnly` resources but never changes or deletes the
resource.

{{< hint "important" >}}
Management policies including `ObserveOnly` are experimental. They must be
explicitly enabled.
See the management policies section for more details.
{{< /hint >}}

To configure an `ObserveOnly` resource:

1. Create a new resource with an {{<hover label="oo" line="8">}}ObserveOnly{{</hover>}}
   management policy.
  1. With the
     {{<hover label="oo" line="5">}}crossplane.io/external-name{{</hover>}}
     annotation set to the external name of the resource to import.
  1. Only provide the identifying arguments (for example,
     {{<hover label="oo" line="10">}}region{{</hover>}}) in the spec
     of the resource.

```yaml {label="oo"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  annotations:
    crossplane.io/external-name: existing-database-instance
  name: existing-database-instance
spec:
  managementPolicy: ObserveOnly
  forProvider:
    region: "us-central1"
```

Crossplane discovers the managed resource and populates the
{{<hover label="ooPopulated" line="12">}}status.atProvider{{</hover>}}
with the observed state.

```yaml {label="ooPopulated"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  annotations:
    crossplane.io/external-name: existing-database-instance
  name: existing-database-instance
spec:
  managementPolicy: ObserveOnly
  forProvider:
    region: us-central1
status:
  atProvider:
    connectionName: crossplane-playground:us-central1:existing-database-instance
    databaseVersion: POSTGRES_14
    deletionProtection: true
    firstIpAddress: 35.184.74.79
    id: existing-database-instance
    publicIpAddress: 35.184.74.79
    region: us-central1
    <truncated-for-brevity>
    settings:
    - activationPolicy: ALWAYS
      availabilityType: REGIONAL
      diskSize: 100
      <truncated-for-brevity>
      pricingPlan: PER_USE
      tier: db-custom-4-26624
      version: 4
  conditions:
  - lastTransitionTime: "2023-02-22T07:16:51Z"
    reason: Available
    status: "True"
    type: Ready
  - lastTransitionTime: "2023-02-22T07:16:51Z"
    reason: ReconcileSuccess
    status: "True"
    type: Synced
```

To allow Crossplane to control and change the `ObserveOnly` resource, edit the
policy. 

Change the {{<hover label="ooPopulated" line="8">}}ObserveOnly{{</hover>}} field
to {{<hover label="fc" line="8">}}FullControl{{</hover>}}.

Copy any required parameter values from
{{<hover label="fc" line="16">}}status.atProvider{{</hover>}} and provide them
in {{<hover label="fc" line="9">}}spec.forProvider{{</hover>}}.

```yaml {label="fc"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  annotations:
    crossplane.io/external-name: existing-database-instance
  name: existing-database-instance
spec:
  managementPolicy: Full
  forProvider:
    databaseVersion: POSTGRES_14
    region: us-central1
    settings:
    - diskSize: 100
      tier: db-custom-4-26624
status:
  atProvider:
    <truncated-for-brevity>
  conditions:
    - lastTransitionTime: "2023-02-22T07:16:51Z"
      reason: Available
      status: "True"
      type: Ready
    - lastTransitionTime: "2023-02-22T11:16:45Z"
      reason: ReconcileSuccess
      status: "True"
      type: Synced
```

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