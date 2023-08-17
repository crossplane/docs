---
title: Usages
weight: 90
state: alpha
alphaVersion: "1.14"
description: "Usage defines deletion protection for Managed Resources or Composites"
---

A `Usage` is a Crossplane resource that defines deletion protection for a 
Managed Resource or a Composite Resource. There are two main use cases for the
Usages:

1. Protecting a resource from accidental deletion.
2. Deletion ordering, that is, preventing a resource from being deleted before
   the dependent resource deleted.

See the [Usage for Deletion Protection](#usage-for-deletion-protection) for the
first use case and the [Usage for Deletion Ordering](#usage-for-deletion-ordering)
for the second one.

## Enable Usages
Usages are an alpha feature. Alpha features aren't enabled by default.

Enable `Usage` support by 
[changing the Crossplane pod setting]({{<ref "./pods#change-pod-settings">}})
and enabling  
{{<hover label="deployment" line="12">}}--enable-usages{{</hover>}}
argument.

```yaml {label="deployment",copy-lines="12"}
$ kubectl edit deployment crossplane --namespace crossplane-system
apiVersion: apps/v1
kind: Deployment
spec:
# Removed for brevity
  template:
    spec:
      containers:
      - args:
        - core
        - start
        - --enable-usages
```

{{<hint "tip" >}}

The [Crossplane install guide]({{<ref "../software/install#feature-flags">}}) 
describes enabling feature flags like 
{{<hover label="deployment" line="12">}}\-\-enable-usages{{</hover>}}
with Helm.
{{< /hint >}}

<!-- vale Google.Headings = NO -->
## Create a Usage
<!-- vale Google.Headings = YES -->

A {{<hover label="protect" line="2">}}Usage{{</hover>}}
{{<hover label="protect" line="5">}}spec{{</hover>}} has a mandatory
{{<hover label="protect" line="6">}}of{{</hover>}} field for defining the resource
being used or protected. The 
{{<hover label="protect" line="11">}}reason{{</hover>}} field defines the reason
for protection and the {{<hover label="order" line="11">}}by{{</hover>}} field
defines the using resource. Both are optional fields, however, at least one of 
them must be defined.

### Usage for Deletion Protection

The following example will prevent the deletion of the 
{{<hover label="protect" line="10">}}my-database{{</hover>}} resource by rejecting
any deletion request with the
{{<hover label="protect" line="11">}}reason{{</hover>}} defined.

```yaml {label="protect"}
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: Usage
metadata:
  name: protect-production-database
spec:
  of:
    apiVersion: rds.aws.upbound.io/v1beta1
    kind: Instance
    resourceRef:
      name: my-database
  reason: "Production Database - should never be deleted!"
```

### Usage for Deletion Ordering

The following example will prevent the deletion of
{{<hover label="order" line="10">}}my-cluster{{</hover>}} resource by rejecting
any deletion request before 
{{<hover label="order" line="15">}}my-prometheus-chart{{</hover>}} resource is
deleted.

```yaml {label="order"}
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: Usage
metadata:
  name: release-uses-cluster
spec:
  of:
    apiVersion: eks.upbound.io/v1beta1
    kind: Cluster
    resourceRef:
      name: my-cluster
  by:
    apiVersion: helm.crossplane.io/v1beta1
    kind: Release
    resourceRef:
      name: my-prometheus-chart
```

### Using Selectors with Usages

Usages can use {{<hover label="selectors" line="9">}}selectors{{</hover>}}
to define the resource being used or the using one.
This enables using {{<hover label="selectors" line="12">}}labels{{</hover>}} or
{{<hover label="selectors" line="11">}}matching controller references{{</hover>}}
to define resource instead of providing the resource name.

```yaml {label="selectors"}
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: Usage
metadata:
  name: release-uses-cluster
spec:
  of:
    apiVersion: eks.upbound.io/v1beta1
    kind: Cluster
    resourceSelector:
      matchControllerRef: false # default, and could be omitted
      matchLabels:
        foo: bar
  by:
    apiVersion: helm.crossplane.io/v1beta1
    kind: Release
    resourceSelector:
       matchLabels:
          baz: qux
```

Once the selectors are resolved, the `Usage` controller will persist the
resource name in the 
{{<hover label="selectors-resolved" line="10">}}resourceRef.name{{</hover>}}
field. The following example shows the `Usage` resource after the selectors are
resolved.

{{<hint "important" >}}
The selectors are resolved only once and a random resource will be selected from
the list of matched resources if there are more than one matches.
{{< /hint >}}

```yaml {label="selectors-resolved"}
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: Usage
metadata:
  name: release-uses-cluster
spec:
  of:
    apiVersion: eks.upbound.io/v1beta1
    kind: Cluster
    resourceRef:
       name: my-cluster
    resourceSelector:
      matchLabels:
        foo: bar
  by:
    apiVersion: helm.crossplane.io/v1beta1
    kind: Release
    resourceRef:
       name: my-cluster
    resourceSelector:
       matchLabels:
          baz: qux
```

## Usage in a Composition

A typical use case for Usages is to define a deletion ordering between the
resources in a Composition. The Usages support
[matching controller reference]({{<ref "./compositions#matching-a-controller-reference" >}})
in selectors to ensures that the matching resource is in the same composite
resource in the same way as [cross-resource referencing]({{<ref "./compositions#cross-resource-references" >}}).

The following example shows a Composition that defines a deletion ordering
between a `Cluster` and a `Release` resource which will block deletion of the
`Cluster` resource until the `Release` resource is successfully deleted.

```yaml {label="composition"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  resources:
    - name: cluster
      base:
        apiVersion: container.gcp.upbound.io/v1beta1
        kind: Cluster
        # Removed for brevity
    - name: release
      base:
        apiVersion: helm.crossplane.io/v1beta1
        kind: Release
        # Removed for brevity
    - name: release-uses-cluster
      base:
        apiVersion: apiextensions.crossplane.io/v1alpha1
        kind: Usage
        spec:
          of:
            apiVersion: container.gcp.upbound.io/v1beta1
            kind: Cluster
            resourceSelector:
              matchControllerRef: true
          by:
            apiVersion: helm.crossplane.io/v1beta1
            kind: Release
            resourceSelector:
              matchControllerRef: true
```
