---
title: Import Existing Resources
weight: 200
description: "Import existing resources into your control plane for Crossplane to manage"
---

If you have resources that are already provisioned in a Provider,
you can import them as managed resources and let Crossplane manage them.
A managed resource's [`managementPolicies`]({{<ref "../managed-resources/managed-resources#managementpolicies">}})
field enables importing external resources into Crossplane.

## Import resources in observe only mode

Start by importing external resources with an `Observe` [management policy]({{<ref "../managed-resources/managed-resources#managementpolicies">}}).

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
## Control imported observe only resources
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
Manually copy the important `status.atProvider` values to `spec.forProvider`.
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
