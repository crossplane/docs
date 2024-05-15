---
title: Import Existing Resources
weight: 200
---

If you have resources that are already provisioned in a Provider,
you can import them as managed resources and let Crossplane manage them.
A managed resource's [`managementPolicies`]({{<ref "/v1.16/concepts/managed-resources#managementpolicies">}})
field enables importing external resources into Crossplane.

Crossplane can import resources either [manually]({{<ref "#import-resources-manually">}})
or [automatically]({{<ref "#import-resources-automatically">}}).

## Import resources manually

Crossplane can discover and import existing Provider resources by matching the
`crossplane.io/external-name` annotation in a managed resource.

To import an existing external resource in a Provider, create a new managed
resource with the `crossplane.io/external-name` annotation. Set the annotation
value to the name of the resource in the Provider.

For example, to import an existing GCP Network named
{{<hover label="annotation" line="5">}}my-existing-network{{</hover>}},
create a new managed resource and use the
{{<hover label="annotation" line="5">}}my-existing-network{{</hover>}} in the
annotation.

```yaml {label="annotation",copy-lines="none"}
apiVersion: compute.gcp.crossplane.io/v1beta1
kind: Network
metadata:
  annotations:
    crossplane.io/external-name: my-existing-network
```

The {{<hover label="name" line="5">}}metadata.name{{</hover>}}
field can be anything you want. For example,
{{<hover label="name" line="5">}}imported-network{{</hover>}}.

{{< hint "note" >}}
This name is the
name of the Kubernetes object. It's not related to the resource name inside the
Provider.
{{< /hint >}}

```yaml {label="name",copy-lines="none"}
apiVersion: compute.gcp.crossplane.io/v1beta1
kind: Network
metadata:
  name: imported-network
  annotations:
    crossplane.io/external-name: my-existing-network
```

Leave the
{{<hover label="fp" line="8">}}spec.forProvider{{</hover>}} field empty.
Crossplane imports the settings and automatically applies them to the managed
resource.

{{< hint "important" >}}
If the managed resource has _required_ fields in the
{{<hover label="fp" line="8">}}spec.forProvider{{</hover>}} you must add it to
the `forProvider` field.

The values of those fields must match what's inside the Provider or Crossplane
overwrites the existing values.
{{< /hint >}}

```yaml {label="fp",copy-lines="all"}
apiVersion: compute.gcp.crossplane.io/v1beta1
kind: Network
metadata:
  name: imported-network
  annotations:
    crossplane.io/external-name: my-existing-network
spec:
  forProvider: {}
```


Crossplane now controls and manages this imported resource. Any changes to the
managed resource `spec` changes the external resource.

## Import resources automatically

Automatically import external resources with an `Observe` [management policy]({{<ref "/v1.16/concepts/managed-resources#managementpolicies">}}).

Crossplane imports observe only resources but never changes or deletes the
resources.

{{<hint "important" >}}
The managed resource `managementPolicies` option is a beta feature.

The Provider determines support for management policies.
Refer to the Provider's documentation to see if the Provider supports
management policies.
{{< /hint >}}

<!-- vale off -->
### Apply the Observe management policy
<!-- vale on -->

Create a new managed resource matching the
{{<hover label="oo-policy" line="1">}}apiVersion{{</hover>}} and
{{<hover label="oo-policy" line="2">}}kind{{</hover>}} of the resource
to import and add
{{<hover label="oo-policy" line="4">}}managementPolicies: ["Observe"]{{</hover>}} to the
{{<hover label="oo-policy" line="3">}}spec{{</hover>}}

For example, to import a GCP SQL DatabaseInstance, create a new resource with
the {{<hover label="oo-policy" line="4">}}managementPolicies: ["Observe"]{{</hover>}}
set.
```yaml {label="oo-policy",copy-lines="none"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
spec:
  managementPolicies: ["Observe"]
```

### Add the external-name annotation
Add the {{<hover label="oo-ex-name" line="5">}}crossplane.io/external-name{{</hover>}}
annotation for the resource. This name must match the name inside the Provider.

For example, for a GCP database named
{{<hover label="oo-ex-name" line="5">}}my-external-database{{</hover>}}, apply
the
{{<hover label="oo-ex-name" line="5">}}crossplane.io/external-name{{</hover>}}
annotation with the value
{{<hover label="oo-ex-name" line="5">}}my-external-database{{</hover>}}.

```yaml {label="oo-ex-name",copy-lines="none"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  annotations:
    crossplane.io/external-name: my-external-database
spec:
  managementPolicies: ["Observe"]
```

### Create a Kubernetes object name
Create a {{<hover label="oo-name" line="4">}}name{{</hover>}} to use for the
Kubernetes object.

For example, name the Kubernetes object
{{<hover label="oo-name" line="4">}}my-imported-database{{</hover>}}.

```yaml {label="oo-name",copy-lines="none"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  name: my-imported-database
  annotations:
    crossplane.io/external-name: my-external-database
spec:
  managementPolicies: ["Observe"]
```

### Identify a specific external resource
If more than one resource inside the Provider shares the same name, identify the
specific resource with a unique
{{<hover line="9" label="oo-region">}}spec.forProvider{{</hover>}} field.

For example, only import the GCP SQL database in the
{{<hover line="10" label="oo-region">}}us-central1{{</hover>}} region.

```yaml {label="oo-region"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  name: my-imported-database
  annotations:
    crossplane.io/external-name: my-external-database
spec:
  managementPolicies: ["Observe"]
  forProvider:
    region: "us-central1"
```

### Apply the managed resource

Apply the new managed resource. Crossplane syncs the status of the external
resource in the cloud with the newly created managed resource.

### View the discovered resource
Crossplane discovers the managed resource and populates the
{{<hover label="ooPopulated" line="12">}}status.atProvider{{</hover>}}
fields with the values from the external resource.

```yaml {label="ooPopulated",copy-lines="none"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  name: my-imported-database
  annotations:
    crossplane.io/external-name: my-external-database
spec:
  managementPolicies: ["Observe"]
  forProvider:
    region: us-central1
status:
  atProvider:
    connectionName: crossplane-playground:us-central1:my-external-database
    databaseVersion: POSTGRES_14
    deletionProtection: true
    firstIpAddress: 35.184.74.79
    id: my-external-database
    publicIpAddress: 35.184.74.79
    region: us-central1
    # Removed for brevity
    settings:
    - activationPolicy: ALWAYS
      availabilityType: REGIONAL
      diskSize: 100
      # Removed for brevity
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
<!-- vale off -->
## Control imported ObserveOnly resources
<!-- vale on -->

Crossplane can take active control of observe only imported resources by
changing the `managementPolicies` after import.

Change the {{<hover label="fc" line="8">}}managementPolicies{{</hover>}} field
of the managed resource to
{{<hover label="fc" line="8">}}["*"]{{</hover>}}.

Copy any required parameter values from
{{<hover label="fc" line="16">}}status.atProvider{{</hover>}} and provide them
in {{<hover label="fc" line="9">}}spec.forProvider{{</hover>}}.

{{< hint "tip" >}}
Manually copy the important `spec.atProvider` values to `spec.forProvider`.
{{< /hint >}}

```yaml {label="fc"}
apiVersion: sql.gcp.upbound.io/v1beta1
kind: DatabaseInstance
metadata:
  name: my-imported-database
  annotations:
    crossplane.io/external-name: my-external-database
spec:
  managementPolicies: ["*"]
  forProvider:
    databaseVersion: POSTGRES_14
    region: us-central1
    settings:
    - diskSize: 100
      tier: db-custom-4-26624
status:
  atProvider:
    databaseVersion: POSTGRES_14
    region: us-central1
    # Removed for brevity
    settings:
    - diskSize: 100
      tier: db-custom-4-26624
      # Removed for brevity
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

Crossplane now fully manages the imported resource. Crossplane applies any
changes to the managed resource in the Provider's external resource.