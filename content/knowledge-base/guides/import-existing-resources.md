---
title: Import Existing Resources
weight: 200
---

If you have resources that are already provisioned in a Provider,
you can import them as managed resources and let Crossplane manage them. 

Crossplane can import resources either [manually]({{<ref
"#import-resources-manually">}}) or [automatically]({{<ref
"#import-resources-automatically">}}).


## Import resources manually

Crossplane can discover and import existing Provider resources by matching the
`external-name` annotation in a managed resource. 

To import an existing external resource in a Provider, create a new managed
resource with a `metadata.annotations.crossplane.io/external-name` value. Set
the `external-name` to the name of the resource in the Provider.

Leave the `spec.forProvider` field empty. Crossplane imports the settings and
applies them to the managed resource. 

For example, to import an existing GCP Network named `my-existing-network`,
create a new managed resource and use the 
{{<hover label="annotation" line="5">}}my-existing-network{{</hover>}} in the
annotation. 

```yaml {label="annotation"}
apiVersion: compute.gcp.crossplane.io/v1beta1
kind: Network
metadata:
  annotations:
    crossplane.io/external-name: my-existing-network
```



## Import resources automatically 


What
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