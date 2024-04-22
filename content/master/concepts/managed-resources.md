---
title: Managed Resources
weight: 10
description: "Managed resources are the Crossplane representation of external provider resources"
---

A _managed resource_ (`MR`) represents an external service in a Provider. When
users create a new managed resource, the Provider reacts by creating an external 
resource inside the Provider's environment. Every external service managed by 
Crossplane maps to a managed resource. 

{{< hint "note" >}}
Crossplane calls the object inside Kubernetes a _managed resource_ and the
external object inside the Provider an _external resource_.
{{< /hint >}}

Examples of managed resources include:
* Amazon AWS EC2 [`Instance`](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/resources/ec2.aws.upbound.io/Instance/v1beta1)
* Google Cloud GKE [`Cluster`](https://marketplace.upbound.io/providers/upbound/provider-gcp/latest/resources/container.gcp.upbound.io/Cluster/v1beta1)
* Microsoft Azure PostgreSQL [`Database`](https://marketplace.upbound.io/providers/upbound/provider-azure/latest/resources/dbforpostgresql.azure.upbound.io/Database/v1beta1)

{{< hint "tip" >}}

You can create individual managed resources, but Crossplane recommends using
[Compositions]({{<ref "./compositions" >}}) and Claims to create
managed resources.
{{< /hint >}}

## Managed resource fields

The Provider defines the group, kind and version of a managed resource. The
Provider also define the available settings of a managed resource.

### Group, kind and version
Each managed resource is a unique API endpoint with their own
group, kind and version. 

For example the [Upbound AWS Provider](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/)
defines the {{<hover label="gkv" line="2">}}Instance{{</hover>}} kind from the
group {{<hover label="gkv" line="1">}}ec2.aws.upbound.io{{</hover>}}

```yaml {label="gkv",copy-lines="none"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
```

<!-- vale off -->
### deletionPolicy
<!-- vale on --> 

A managed resource's `deletionPolicy` tells the Provider what to do after
deleting the managed resource. If the `deletionPolicy` is `Delete` the Provider
deletes the external resource as well. If the `deletionPolicy` is `orphan` the
Provider deletes the managed resource but doesn't delete the external resource.

#### Options
* `deletionPolicy: Delete` - **Default** - Delete the external resource when deleting the managed resource.
* `deletionPolicy: Orphan` - Leave the external resource when deleting the managed resource.

#### Interaction with management policies

The [management policy](#managementpolicies) takes precedence over the
`deletionPolicy` when:
<!-- vale write-good.Passive = NO -->
- The related management policy alpha feature is enabled.
<!-- vale write-good.Passive = YES -->
- The resource configures a management policy other than the default value.

See the table below for more details.

{{< table "table table-sm table-hover">}}
| managementPolicies          | deletionPolicy   | result  |
|-----------------------------|------------------|---------|
| "*" (default)               | Delete (default) | Delete  |
| "*" (default)               | Orphan           | Orphan  |
| contains "Delete"           | Delete (default) | Delete  |
| contains "Delete"           | Orphan           | Delete  |
| doesn't contain "Delete"   | Delete (default) | Orphan  |
| doesn't contain "Delete"   | Orphan           | Orphan  |
{{< /table >}}

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
required and optional values in the `forProvider` definition.

Refer to the documentation of your specific Provider for details. 
{{< /hint >}}


```yaml {label="forProvider",copy-lines="none"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
# Removed for brevity
spec:
  forProvider:
    region: us-west-1
    instanceType: t2.micro
```

{{< hint "important">}}
Crossplane considers the `forProvider` field of a managed resource 
the "source of truth" for external resources. Crossplane overrides any changes 
made to an external resource outside of Crossplane. If a user makes a change 
inside a Provider's web console, Crossplane reverts that change back to what's
configured in the `forProvider` setting. 
{{< /hint >}}

#### Referencing other resources

Some fields in a managed resource may depend on values from other managed
resources. For example a VM may need the name of a virtual network to use. 

Managed resources can reference other managed resources by external name, name
reference or selector. 

##### Matching by external name

When matching a resource by name Crossplane looks for the name of the external
resource in the Provider. 

For example, a AWS VPC object named `my-test-vpc` has the external name
`vpc-01353cfe93950a8ff`.

```shell {copy-lines="1"
kubectl get vpc
NAME            READY   SYNCED   EXTERNAL-NAME           AGE
my-test-vpc     True    True     vpc-01353cfe93950a8ff   49m
```

To match the VPC by name, use the external name. For example, creating a Subnet
managed resource attached to this VPC.

```yaml {copy-lines="none"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
spec:
  forProvider:
    # Removed for brevity
    vpcId: vpc-01353cfe93950a8ff
```      

##### Matching by name reference

To match a resource based on the name of the managed resource and not the
external resource name inside the Provider, use a `nameRef`.

For example, a AWS VPC object named `my-test-vpc` has the external name
`vpc-01353cfe93950a8ff`.

```shell {copy-lines="1"}
kubectl get vpc
NAME            READY   SYNCED   EXTERNAL-NAME           AGE
my-test-vpc     True    True     vpc-01353cfe93950a8ff   49m
```

To match the VPC by name reference, use the managed resource name. For example,
creating a Subnet managed resource attached to this VPC.

```yaml {copy-lines="none"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
spec:
  forProvider:
    # Removed for brevity
    vpcIdRef: 
      name: my-test-vpc
```      


##### Matching by selector

Matching by selector is the most flexible matching method. 

{{<hint "note" >}}

The [Compositions]({{<ref "./compositions">}}) section covers the 
`matchControllerRef` selector.
{{</hint >}}

Use `matchLabels` to match the labels applied to a resource. For example, this
Subnet resource only matches VPC resources with the label 
`my-label: label-value`.

```yaml {copy-lines="none"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
spec:
  forProvider:
    # Removed for brevity
    vpcIdSelector: 
      matchLabels:
        my-label: label-value
```


#### Immutable fields

Some providers don't support changing the fields of some managed resources after
creation. For example, you can't change the `region` of an Amazon AWS
`RDSInstance`. These fields are _immutable fields_. Amazon requires you delete 
and recreate the resource.

Crossplane allows you to edit the immutable field of a managed resource, but
doesn't apply the change. Crossplane never deletes a resource based on a
`forProvider` change. 

{{<hint "note" >}}
<!-- vale write-good.Passive = NO -->
Crossplane behaves differently than other tools like Terraform. Terraform
deletes and recreates a resource to change an immutable field. Crossplane only
deletes an external resource if their corresponding managed 
resource object is deleted from Kubernetes and the `deletionPolicy` is 
`Delete`.
<!-- vale write-good.Passive = YES -->
{{< /hint >}}

#### Late initialization

Crossplane treats the managed resource as the source of truth by default;
it expects to have all values under `spec.forProvider` including the
optional ones. If not provided, Crossplane populates the empty fields with
the values assigned by the provider. For example, consider fields such as
`region` and `availabilityZone`. You might specify only the region and let the
cloud provider choose the availability zone. In this case, if the provider
assigns an availability zone, Crossplane uses that value to populate the
`spec.forProvider.availabilityZone` field.

{{<hint "note" >}}
<!-- vale write-good.Passive = NO -->
With [managementPolicies]({{<ref "./managed-resources#managementpolicies" >}}),
this behavior can be turned off by not including the `LateInitialize` policy in
the `managementPolicies` list.
<!-- vale write-good.Passive = YES -->
{{< /hint >}}

<!-- vale off -->
### initProvider
<!-- vale on -->

{{<hint "important" >}}
The managed resource `initProvider` option is a beta feature related to
[managementPolicies]({{<ref "./managed-resources#managementpolicies" >}}).

{{< /hint >}}

The
{{<hover label="initProvider" line="7">}}initProvider{{</hover>}} defines
settings Crossplane applies only when creating a new managed resource.  
Crossplane ignores settings defined in the
{{<hover label="initProvider" line="7">}}initProvider{{</hover>}}
field that change after creation.

{{<hint "note" >}}
Settings in `forProvider` are always enforced by Crossplane. Crossplane reverts
any changes to a `forProvider` field in the external resource.

Settings in `initProvider` aren't enforced by Crossplane. Crossplane ignores any
changes to a `initProvider` field in the external resource.
{{</hint >}}

Using `initProvider` is useful for setting initial values that a Provider may
automatically change, like an auto scaling group.

For example, creating a
{{<hover label="initProvider" line="2">}}NodeGroup{{</hover>}}
with an initial
{{<hover label="initProvider" line="9">}}desiredSize{{</hover>}}.  
Crossplane doesn't change the
{{<hover label="initProvider" line="9">}}desiredSize{{</hover>}}
setting back when an autoscaler scales the Node Group external resource.

{{< hint "tip" >}}
Crossplane recommends configuring
{{<hover label="initProvider" line="6">}}managementPolicies{{</hover>}} without
`LateInitialize` to avoid conflicts with `initProvider` settings.
{{< /hint >}}

```yaml {label="initProvider",copy-lines="none"}
apiVersion: eks.aws.upbound.io/v1beta1
kind: NodeGroup
metadata:
  name: sample-eks-ng
spec:
  managementPolicies: ["Observe", "Create", "Update", "Delete"]
  initProvider:
    scalingConfig:
      - desiredSize: 1
  forProvider:
    region: us-west-1
    scalingConfig:
      - maxSize: 4
        minSize: 1
```

<!-- vale off -->
### managementPolicies
<!-- vale on --> 

{{<hint "note" >}}
The managed resource `managementPolicies` option is a beta feature. Crossplane enables
beta features by default. 

The Provider determines support for management policies.  
Refer to the Provider's documentation to see if the Provider supports
management policies.
{{< /hint >}}

Crossplane
{{<hover label="managementPol1" line="4">}}managementPolicies{{</hover>}}
determine which actions Crossplane can take on a
managed resource and its corresponding external resource.  
Apply one or more
{{<hover label="managementPol1" line="4">}}managementPolicies{{</hover>}}
to a managed resource to determine what permissions
Crossplane has over the resource.

For example, give Crossplane permission to create and delete an external resource,
but not make any changes, set the policies to
{{<hover label="managementPol1" line="4">}}["Create", "Delete", "Observe"]{{</hover>}}.

```yaml {label="managementPol1"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
spec:
  managementPolicies: ["Create", "Delete", "Observe"]
  forProvider:
    # Removed for brevity
```

The default policy grants Crossplane full control over the resources.  
Defining the `managementPolicies` field with an empty array [pauses](#paused)
the resource.

{{<hint "important" >}}
The Provider determines support for management policies.  
Refer to the Provider's documentation to see if the Provider supports
management policies.
{{< /hint >}}

Crossplane supports the following policies:
{{<table "table table-sm table-hover">}}
| Policy | Description |
| --- | --- |
| `*` | _Default policy_. Crossplane has full control over a resource. |
| `Create` | If the external resource doesn't exist, Crossplane creates it based on the managed resource settings. |
| `Delete` | Crossplane can delete the external resource when deleting the managed resource. |
| `LateInitialize` | Crossplane initializes some external resource settings not defined in the `spec.forProvider` of the managed resource. See [the late initialization]({{<ref "./managed-resources#late-initialization" >}}) section for more details. |
| `Observe` | Crossplane only observes the resource and doesn't make any changes. Used for [observe only resources]({{<ref "../guides/import-existing-resources#import-resources-automatically">}}). |
| `Update` | Crossplane changes the external resource when changing the managed resource. |
{{</table >}}

The following is a list of common policy combinations:
{{<table "table table-sm table-hover table-striped-columns" >}}
| Create | Delete | LateInitialize | Observe | Update | Description |
| :---:  | :---:  | :---:          | :---:   | :---:  | ---         |
| {{<check>}}      | {{<check>}}      | {{<check>}}              | {{<check>}}       | {{<check>}}      | _Default policy_. Crossplane has full control over the resource.                                                                                                     |
| {{<check>}}      | {{<check>}}      | {{<check>}}              | {{<check>}}       |        | After creation any changes made to the managed resource aren't passed to the external resource. Useful for immutable external resources. |
| {{<check>}}      | {{<check>}}      |                | {{<check>}}       | {{<check>}}      | Prevent Crossplane from managing any settings not defined in the managed resource. Useful for immutable fields in an external resource. |
| {{<check>}}      | {{<check>}}      |                | {{<check>}}       |        | Crossplane doesn't import any settings from the external resource and doesn't push changes to the managed resource. Crossplane recreates the external resource if it's deleted. |
| {{<check>}}      |        | {{<check>}}              | {{<check>}}       | {{<check>}}      | Crossplane doesn't delete the external resource when deleting the managed resource. |
| {{<check>}}      |        | {{<check>}}              | {{<check>}}       |        | Crossplane doesn't delete the external resource when deleting the managed resource. Crossplane doesn't apply changes to the external resource after creation. |
| {{<check>}}      |        |                | {{<check>}}       | {{<check>}}      | Crossplane doesn't delete the external resource when deleting the managed resource. Crossplane doesn't import any settings from the external resource. |
| {{<check>}}      |        |                | {{<check>}}       |        | Crossplane creates the external resource but doesn't apply any changes to the external resource or managed resource. Crossplane can't delete the resource. |
|        |        |                | {{<check>}}       |        | Crossplane only observes a resource. Used for [observe only resources]({{<ref "../guides/import-existing-resources#import-resources-automatically">}}). |
|        |        |                |         |        | No policy set. An alternative method for [pausing](#paused) a resource.                                                                                              |
{{< /table >}}

<!-- vale off -->
### providerConfigRef
<!-- vale on -->

The `providerConfigRef` on a managed resource tells the Provider which
[ProviderConfig]({{<ref "./providers#provider-configuration">}}) to
use when creating the managed resource.  

Use a ProviderConfig to define the authentication method to use when 
communicating to the Provider.

{{< hint "important" >}}
If `providerConfigRef` isn't applied, Providers use the ProviderConfig named `default`.
{{< /hint >}}

For example, a managed resource references a ProviderConfig named 
{{<hover label="pcref" line="6">}}user-keys{{</hover>}}.

This matches the {{<hover label="pc" line="4">}}name{{</hover>}} of a ProviderConfig.

```yaml {label="pcref",copy-lines="none"}}
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
Each managed resource can reference different ProviderConfigs. This allows
different managed resources to authenticate with different credentials to the
same Provider. 
{{< /hint >}}

<!-- vale off -->
### providerRef
<!-- vale on --> 

<!-- vale Crossplane.Spelling = NO -->
Crossplane deprecated the `providerRef` field in `crossplane-runtime` 
[v0.10.0](https://github.com/crossplane/crossplane-runtime/releases/tag/v0.10.0). 
Managed resources using `providerRef`must use [`providerConfigRef`](#providerconfigref).
<!-- vale Crossplane.Spelling = YES -->

<!-- vale off -->
### writeConnectionSecretToRef
<!-- vale on --> 

When a Provider creates a managed resource it may generate resource-specific
details, like usernames, passwords or connection details like an IP address. 

Crossplane stores these details in a Kubernetes Secret object specified by the
`writeConnectionSecretToRef` values. 

For example, when creating an AWS RDS database instance with the Crossplane 
[community AWS provider](https://marketplace.upbound.io/providers/crossplane-contrib/provider-aws/v0.40.0) 
generates an endpoint, password, port and username data. The Provider saves
these variables in the Kubernetes secret 
{{<hover label="secretname" line="9" >}}rds-secret{{</hover>}}, referenced by
the 
{{<hover label="secretname" line="9" >}}writeConnectionSecretToRef{{</hover>}}
field. 

```yaml {label="secretname",copy-lines="none"}
apiVersion: database.aws.crossplane.io/v1beta1
kind: RDSInstance
metadata:
  name: my-rds-instance
spec:
  forProvider:
  # Removed for brevity
  writeConnectionSecretToRef:
    name: rds-secret
```

Viewing the Secret object shows the saved fields.

```yaml {copy-lines="1"}
kubectl describe secret rds-secret
Name:         rds-secret
# Removed for brevity
Data
====
port:      4 bytes
username:  10 bytes
endpoint:  54 bytes
password:  27 bytes
```

{{<hint "important" >}}
The Provider determines the data written to the Secret object. Refer to the
specific Provider documentation for the generated Secret data.
{{< /hint >}}

<!-- vale off -->
### publishConnectionDetailsTo
<!-- vale on --> 

The `publishConnectionDetailsTo` field expands on 
[`writeConnectionSecretToRef`](#writeconnectionsecrettoref) supporting storing
managed resource information as a Kubernetes Secret object or in an external
secrets store like [HashiCorp Vault](https://www.vaultproject.io/).

Using `publishConnectionDetailsTo` requires enabling Crossplane 
External Secrets Stores (ESS). Enable ESS inside a Provider with a
[DeploymentRuntimeConfig]({{<ref "providers#runtime-configuration" >}}) and
in Crossplane with the `--enable-external-secret-stores` argument.

{{< hint "note" >}}
Not all Providers support `publishConnectionDetailsTo`. Check your Provider
documentation for details.
{{< /hint >}}

#### Publish secrets to Kubernetes

To publish the data generated by a managed resource as a Kubernetes Secret
object provide a 
{{<hover label="k8secret" line="7">}}publishConnectionDetailsTo.name{{< /hover >}} 

```yaml {label="k8secret",copy-lines="none"}
apiVersion: rds.aws.upbound.io/v1beta1
kind: Instance
spec:
  forProvider:
  # Removed for brevity
  publishConnectionDetailsTo:
    name: rds-kubernetes-secret
```

Crossplane can apply labels and annotations to the Kubernetes secret as well
using 
{{<hover label="k8label" line="8">}}publishConnectionDetailsTo.metadata{{</hover>}}.

```yaml {label="k8label",copy-lines="none"}
apiVersion: rds.aws.upbound.io/v1beta1
kind: Instance
spec:
  forProvider:
  # Removed for brevity
  publishConnectionDetailsTo:
    name: rds-kubernetes-secret
    metadata:
      labels:
        label-tag: label-value
      annotations:
        annotation-tag: annotation-value
```

#### Publish secrets to an external secrets store

Publishing secrets data to an external secret store like 
[HashiCorp Vault](https://www.vaultproject.io/) relies on a 
{{<hover label="configref" line="8">}}publishConnectionDetailsTo.configRef{{</hover>}}. 

The 
{{<hover label="configref" line="9">}}configRef.name{{</hover>}} references a 
{{<hover label="storeconfig" line="4">}}StoreConfig{{</hover>}}
object. 

```yaml {label="configref",copy-lines="none"}
apiVersion: rds.aws.upbound.io/v1beta1
kind: Instance
spec:
  forProvider:
  # Removed for brevity
  publishConnectionDetailsTo:
    name: rds-kubernetes-secret
    configRef: 
      name: my-vault-storeconfig
```

```yaml {label="storeconfig",copy-lines="none"}
apiVersion: secrets.crossplane.io/v1alpha1
kind: StoreConfig
metadata:
  name: my-vault-storeconfig
# Removed for brevity
```

{{<hint "tip" >}}
Read the 
[Vault as an External Secrets Store]({{<ref "../guides/vault-as-secret-store">}})
guide for details on using StoreConfig objects.
{{< /hint >}}

## Annotations

Crossplane applies a standard set of Kubernetes `annotations` to managed
resources.

{{<table "table table-sm">}}
| Annotation | Definition | 
| --- | --- | 
| `crossplane.io/external-name` | The name of the managed resource inside the Provider. |
| `crossplane.io/external-create-pending` | The timestamp of when Crossplane began creating the managed resource. | 
| `crossplane.io/external-create-succeeded` | The timestamp of when the Provider successfully created the managed resource. | 
| `crossplane.io/external-create-failed` | The timestamp of when the Provider failed to create the managed resource. | 
| `crossplane.io/paused` | Indicates Crossplane isn't reconciling this resource. Read the [Pause Annotation](#paused) for more details. |
| `crossplane.io/composition-resource-name` | For managed resource created by a Composition, this is the Composition's `resources.name` value. | 
{{</table >}}

### Naming external resources
By default Providers give external resources the same name as the Kubernetes
object.

For example, a managed resource named 
{{<hover label="external-name" line="4">}}my-rds-instance{{</hover >}} has
the name `my-rds-instance` as an external resource inside the Provider's
environment. 

```yaml {label="external-name",copy-lines="none"}
apiVersion: database.aws.crossplane.io/v1beta1
kind: RDSInstance
metadata:
  name: my-rds-instance
```

```shell
kubectl get rdsinstance
NAME                 READY   SYNCED   EXTERNAL-NAME        AGE
my-rds-instance      True    True     my-rds-instance      11m
```

Managed resource created with a `crossplane.io/external-name` 
annotation already provided use the annotation value as the external
resource name.

For example, the Provider creates managed resource named 
{{< hover label="custom-name" line="6">}}my-rds-instance{{</hover>}} but uses
the name {{<hover label="custom-name" line="5">}}my-custom-name{{</hover >}}
for the external resource inside AWS.

```yaml {label="custom-name",copy-lines="none"}
apiVersion: database.aws.crossplane.io/v1beta1
kind: RDSInstance
metadata:
  name: my-rds-instance  
  annotations: 
    crossplane.io/external-name: my-custom-name
```

```shell {copy-lines="1"}
kubectl get rdsinstance
NAME                 READY   SYNCED   EXTERNAL-NAME        AGE
my-rds-instance      True    True     my-custom-name       11m
```

### Creation annotations

When an external system like AWS generates nondeterministic resource names it's
possible for a provider to create a resource but not record that it did. When
this happens the provider can't manage the resource.

{{<hint "tip">}}
Crossplane calls resources that a provider creates but doesn't manage _leaked
resources_.
{{</hint>}}

Providers set three creation annotations to avoid and detect leaked resources:

* {{<hover label="creation" line="8">}}crossplane.io/external-create-pending{{</hover>}} -
  The last time the provider was about to create the resource.
* {{<hover label="creation" line="9">}}crossplane.io/external-create-succeeded{{</hover>}} -
  The last time the provider successfully created the resource.
* `crossplane.io/external-create-failed` - The last time the provider failed to
  create the resource.

Use `kubectl get` to view the annotations on a managed resource. For example, an
AWS VPC resource:

```yaml {label="creation" copy-lines="2-9"}
$ kubectl get -o yaml vpc my-vpc
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPC
metadata:
  name: my-vpc
  annotations:
    crossplane.io/external-name: vpc-1234567890abcdef0
    crossplane.io/external-create-pending: "2023-12-18T21:48:06Z"
    crossplane.io/external-create-succeeded: "2023-12-18T21:48:40Z"
```

A provider uses the
{{<hover label="creation" line="7">}}crossplane.io/external-name{{</hover>}}
annotation to lookup a managed resource in an external system.

The provider looks up the resource in the external system to determine if it
exists, and if it matches the managed resource's desired state. If the provider
can't find the resource, it creates it.

Some external systems don't let a provider specify a resource's name when the
provider creates it. Instead the external system generates an nondeterministic
name and returns it to the provider.

When the external system generates the resource's name, the provider attempts to
save it to the managed resource's `crossplane.io/external-name` annotation. If
it doesn't, it _leaks_ the resource.

A provider can't guarantee that it can save the annotation. The provider could
restart or lose network connectivity between creating the resource and saving
the annotation.

A provider can detect that it might have leaked a resource. If the provider
thinks it might have leaked a resource, it stops reconciling it until you tell
the provider it's safe to proceed.

{{<hint "important">}}
Anytime an external system generates a resource's name there is a risk the
provider could leak the resource.

The safest thing for a provider to do when it detects that it might have leaked
a resource is to stop and wait for human intervention.

This ensures the provider doesn't create duplicates of the leaked resource.
Duplicate resources can be costly and dangerous.
{{</hint>}}

When a provider thinks it might have leaked a resource it creates a `cannot
determine creation result` event associated with the managed resource. Use
`kubectl describe` to see the event.

```shell {copy-lines="1"}
kubectl describe queue my-sqs-queue

# Removed for brevity

Events:
  Type     Reason                           Age                 From                                 Message
  ----     ------                           ----                ----                                 -------
  Warning  CannotInitializeManagedResource  29m (x19 over 19h)  managed/queue.sqs.aws.crossplane.io  cannot determine creation result - remove the crossplane.io/external-create-pending annotation if it is safe to proceed
```

Providers use the creation annotations to detect that they might have leaked a
resource.

Each time a provider reconciles a managed resource it checks the resource's
creation annotations. If the provider sees a create pending time that's more
recent than the most recent create succeeded or create failed time, it knows
that it might have leaked a resource.

{{<hint "note">}}
Providers don't remove the creation annotations. They use the timestamps to
determine which is most recent. It's normal for a managed resource to have
several creation annotations.
{{</hint>}}

The provider knows it might have leaked a resource because it updates all the
resource's annotations at the same time. If the provider couldn't update the
creation annotations after it created the resource, it also couldn't update the
`crossplane.io/external-name` annotation.

{{<hint "tip">}}
If a resource has a `cannot determine creation result` error, inspect the
external system.

Use the timestamp from the `crossplane.io/external-create-pending` annotation to
determine when the provider might have leaked a resource. Look for resources
created around this time.

If you find a leaked resource, and it's safe to do so, delete it from the
external system.

Remove the `crossplane.io/external-create-pending` annotation from the managed
resource after you're sure no leaked resource exists. This tells the provider to
resume reconciliation of and recreate the managed resource.
{{</hint>}}

Providers also use the creation annotations to avoid leaking resources.

When a provider writes the `crossplane.io/external-create-pending` annotation it
knows it's reconciling the latest version of the managed resource. The write
would fail if the provider was reconciling an old version of the managed
resource.

If the provider reconciled an old version with an outdated
`crossplane.io/external-name` annotation it could mistakenly determine that the
resource didn't exist. The provider would create a new resource, and leak the
existing one.

Some external systems have a delay between when a provider creates a resource
and when the system reports that it exists. The provider uses the most recent
create succeeded time to account for this delay.

If the provider didn't account for the delay, it could mistakenly determine
that the resource didn't exist. The provider would create a new resource, and
leak the existing one.

### Paused
Manually applying the `crossplane.io/paused` annotation causes the Provider to
stop reconciling the managed resource. 

Pausing a resource is useful when modifying Providers or preventing
race-conditions when editing Kubernetes objects.

Apply a {{<hover label="pause" line="6">}}crossplane.io/paused: "true"{{</hover>}}
annotation to a managed resource to pause reconciliation. 

{{< hint "note" >}}
Only the value `"true"` pauses reconciliation.
{{< /hint >}}

```yaml {label="pause"}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
metadata:
  name: my-rds-instance
  annotations:
    crossplane.io/paused: "true"
spec:
  forProvider:
    region: us-west-1
    instanceType: t2.micro
```

Remove the annotation to resume reconciliation.

{{<hint "important">}}
Kubernetes and Crossplane can't delete resources with a `paused` annotation,
even with `kubectl delete`. 

Read 
[Crossplane discussion #4839](https://github.com/crossplane/crossplane/issues/4839) 
for more details.
{{< /hint >}}

## Finalizers
Crossplane applies a 
[Finalizer](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)
on managed resources to control their deletion. 

{{< hint "note" >}}
Kubernetes can't delete objects with Finalizers.
{{</hint >}}

When Crossplane deletes a managed resource the Provider begins deleting the
external resource, but the managed resource remains until the external 
resource is fully deleted.

When the external resource is fully deleted Crossplane removes the Finalizer and
deletes the managed resource object.

## Conditions

Crossplane has a standard set of `Conditions` for a managed 
resource. View the `Conditions` of a managed resource with 
`kubectl describe <managed_resource>`


{{<hint "note" >}}
Providers may define their own custom `Conditions`. 
{{</hint >}}


### Available
`Reason: Available` indicates the Provider created the managed resource and it's
ready for use. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  Ready
  Status:                True
  Reason:                Available
```
### Creating

`Reason: Creating` indicates the Provider is attempting to create the managed
resource. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  Ready
  Status:                False
  Reason:                Creating
```

### Deleting
`Reason: Deleting` indicates the Provider is attempting to delete the managed
resource. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  Ready
  Status:                False
  Reason:                Deleting
```

<!-- vale off -->
### ReconcilePaused
<!-- vale on -->
`Reason: ReconcilePaused` indicates the managed resource has a [Pause](#paused)
annotation 

```yaml {copy-lines="none"}
Conditions:
  Type:                  Synced
  Status:                False
  Reason:                ReconcilePaused
```

<!-- vale off -->
### ReconcileError
<!-- vale on -->
`Reason: ReconcileError` indicates Crossplane encountered an error while
reconciling the managed resource. The `Message:` value of the `Condition` helps
identify the Crossplane error. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  Synced
  Status:                False
  Reason:                ReconcileError
```

<!-- vale off -->
### ReconcileSuccess
<!-- vale on -->
`Reason: ReconcileSuccess` indicates the Provider created and is monitoring the 
managed resource.

```yaml {copy-lines="none"}
Conditions:
  Type:                  Synced
  Status:                True
  Reason:                ReconcileSuccess
```

### Unavailable
`Reason: Unavailable` indicates Crossplane expects the managed resource to be 
available, but the Provider reports the resource is unhealthy.

```yaml {copy-lines="none"}
Conditions:
  Type:                  Ready
  Status:                False
  Reason:                Unavailable
```

### Unknown
`Reason: Unknown` indicates the Provider has an unexpected error with the
managed resource. The `conditions.message` provides more information on what
went wrong. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  Unknown
  Status:                False
  Reason:                Unknown
```


### Upjet Provider conditions
[Upjet](https://github.com/upbound/upjet), the open source tool to generate
Crossplane Providers, also has a set of standard `Conditions`.


<!-- vale off -->
#### AsyncOperation
<!-- vale on -->

Some resources may take more than a minute to create. Upjet based providers can 
complete their Kubernetes command before creating the managed resource by using 
an asynchronous operation. 


##### Finished 
The `Reason: Finished` indicates the asynchronous operation completed
successfully. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  AsyncOperation
  Status:                True
  Reason:                Finished
```


##### Ongoing

`Reason: Ongoing` indicates the managed resource operation is still in progress. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  AsyncOperation
  Status:                True
  Reason:                Ongoing
```

<!-- vale off -->
#### LastAsyncOperation
<!-- vale on -->

The Upjet `Type: LastAsyncOperation` captures the previous asynchronous
operation status as either `Success` or a failure `Reason`. 

<!-- vale off -->
##### ApplyFailure
<!-- vale on -->

`Reason: ApplyFailure` indicates the Provider failed to apply a setting to the
managed resource. The `conditions.message` provides more information on what
went wrong. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  LastAsyncOperation
  Status:                False
  Reason:                ApplyFailure
```

<!-- vale off -->
##### DestroyFailure
<!-- vale on -->

`Reason: DestroyFailure` indicates the Provider failed to delete the managed
resource. The `conditions.message` provides more information on what
went wrong. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  LastAsyncOperation
  Status:                False
  Reason:                DestroyFailure
```

##### Success
`Reason: Success` indicates the Provider successfully created the managed
resource asynchronously. 

```yaml {copy-lines="none"}
Conditions:
  Type:                  LastAsyncOperation
  Status:                True
  Reason:                Success
```
