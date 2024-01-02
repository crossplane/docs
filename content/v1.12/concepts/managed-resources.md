---
title: Managed Resources
weight: 102
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
[Compositions]({{<ref "../concepts/composition" >}}) and Claims to create
managed resources.
{{< /hint >}}

## Managed resource fields

The Provider defines the group, kind and version of a managed resource. The
Provider also define the available settings of a managed resource.

### Group, kind and version
Each managed resource is a unique API endpoint with their own
group, kind and version. 

For example the [Upbound AWS
Provider](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/)
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
deleting the managed resource. If the `deletionPolicy` is `delete` the Provider
deletes the external resource as well. If the `deletionPolicy` is `orphan` the
Provider deletes the managed resource but doesn't delete the external resource.

#### Options
* `deletionPolicy: Delete` - **Default** - Delete the external resource when deleting the managed resource.
* `deletionPolicy: Orphan` - Leave the external resource when deleting the managed resource. 

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

Providers add any settings not manually set to the `forProvider` field of the 
created managed resource object.
Use `kubectl describe <managed_resource>` to view the applied values. 
 
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
The [Composition]({{<ref "composition">}}) section covers the 
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
`delete`.
<!-- vale write-good.Passive = YES -->
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

For example, a managed resource references a ProviderConfig named 
{{<hover label="pcref" line="6">}}user-keys{{</hover>}}.

This matches the {{<hover label="pc" line="4">}}name{{</hover>}} of a ProviderConfig.

```yaml {label="pcref",copy-lines="none"}}
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Instance
spec:
  forProvider:
    # Removed for brevity
  providerConfigRef:
    name: user-keys
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

Crossplane deprecated the `providerRef` field in `crossplane-runtime` 
[v0.10.0](https://github.com/crossplane/crossplane-runtime/releases/tag/v0.10.0). 
Managed resources using `providerRef`must use [`providerConfigRef`](#providerconfigref).


<!-- vale off -->
### writeConnectionSecretToRef
<!-- vale on --> 

When a Provider creates a managed resource it may generate resource-specific
details, like usernames, passwords or connection details like an IP address. 

Crossplane stores these details in a Kubernetes Secret object specified by the
`writeConnectionSecretToRef` values. 

For example, when creating an AWS RDS database instance with the Crossplane 
[community AWS
provider](https://marketplace.upbound.io/providers/crossplane-contrib/provider-aws/v0.40.0) 
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
[ControllerConfig]({{<ref "providers#controller-configuration" >}}) and
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
[Vault as an External Secrets Store]({{<ref "knowledge-base/integrations/vault-as-secret-store">}})
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
    crossplane.io/external-name: my-custom-namee
```

```shell {copy-lines="1"}
kubectl get rdsinstance
NAME                 READY   SYNCED   EXTERNAL-NAME        AGE
my-rds-instance      True    True     my-custom-name       11m
```

### Creation annotations

Providers create new managed resources with the
`crossplane.io/external-create-pending` annotation.

The Provider applies the `crossplane.io/external-create-succeeded` or
`crossplane.io/external-create-failed` annotation after making the external API
call and receiving a response. 

{{<hint "note" >}}
If a Provider restarts before creating the `succeed` or `fail` annotations the
Provider can't reconcile the managed resource. 

Read Crossplane [issue
#3037](https://github.com/crossplane/crossplane/issues/3037#issuecomment-1110142427)
for more details 
{{< /hint >}}


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
