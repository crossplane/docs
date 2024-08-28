---
title: Usages
weight: 95
state: alpha
alphaVersion: "1.14"
description: "Usage defines a usage relationship for Managed Resources or Composites"
---

A `Usage` is a Crossplane resource that defines a usage relationship for a 
Managed Resource or a Composite Resource. Two main use cases for the Usages are
as follows:

1. Protecting a resource from accidental deletion.
2. Deletion ordering by ensuring that a resource isn't deleted before the 
   deletion of its dependent resources.

See the section [Usage for Deletion Protection](#usage-for-deletion-protection) for the
first use case and the section [Usage for Deletion Ordering](#usage-for-deletion-ordering)
for the second one.

## Enable usages
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
## Create a usage
<!-- vale Google.Headings = YES -->

<!-- vale write-good.Passive = NO -->
A {{<hover label="protect" line="2">}}Usage{{</hover>}}
{{<hover label="protect" line="5">}}spec{{</hover>}} has a mandatory
{{<hover label="protect" line="6">}}of{{</hover>}} field for defining the resource
in use or protected. The 
{{<hover label="protect" line="11">}}reason{{</hover>}} field defines the reason
for protection and the {{<hover label="order" line="11">}}by{{</hover>}} field
defines the using resource. Both fields are optional, but at least one of them
must be provided.
<!-- vale write-good.Passive = YES -->

{{<hint "important" >}}
<!-- vale write-good.Passive = NO -->
Usage relationships can be defined between `Managed Resources` and `Composites`.
<!-- vale write-good.TooWordy = NO -->
However, a `Composite` as the using resource (`spec.by`) would be ineffective
unless the `compositeDeletePolicy` `Foreground` is used because it wouldn't block
deletion of its child resources before its own deletion with the default deletion
policy `Background`.
<!-- vale write-good.TooWordy = YES -->
<!-- vale write-good.Passive = YES -->
{{< /hint >}}

### Usage for deletion protection

The following example prevents the deletion of the 
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

### Usage for deletion ordering

The following example prevents the deletion of
{{<hover label="order" line="10">}}my-cluster{{</hover>}} resource by rejecting
any deletion request before the deletion of 
{{<hover label="order" line="15">}}my-prometheus-chart{{</hover>}} resource.

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

### Using selectors with usages

Usages can use {{<hover label="selectors" line="9">}}selectors{{</hover>}}
to define the resource in use or the using one.
This enables using {{<hover label="selectors" line="12">}}labels{{</hover>}} or
{{<hover label="selectors" line="10">}}matching controller references{{</hover>}}
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

After the `Usage` controller resolves the selectors, it persists the resource
name in the 
{{<hover label="selectors-resolved" line="10">}}resourceRef.name{{</hover>}}
field. The following example shows the `Usage` resource after the resolution of
selectors.

{{<hint "important" >}}
<!-- vale write-good.Passive = NO -->
The selectors are resolved only once. If there are more than one matches, a
random resource is selected from the list of matched resources.
<!-- vale write-good.Passive = YES -->
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

### Replay blocked deletion attempt

By default, the deletion of a `Usage` resource doesn't trigger the deletion of
the resource in use even if there were deletion attempts blocked by the `Usage`.
Replaying the blocked deletion is possible by setting the
{{<hover label="replay" line="6">}}replayDeletion{{</hover>}} field to `true`.

```yaml {label="replay"}
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: Usage
metadata:
  name: release-uses-cluster
spec:
  replayDeletion: true
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

{{<hint "tip" >}}

Replay deletion is useful when the used resource is part of a composition.
This configuration radically decreases time for the deletion of the used
resource, hence the composite owning it, by replaying the deletion of the
used resource right after the using resource disappears instead of waiting
for the long exponential backoff durations of the Kubernetes garbage collector.
{{< /hint >}}

## Usage in a Composition

A typical use case for Usages is to define a deletion ordering between the
resources in a Composition. The Usages support
[matching controller reference]({{<ref "./compositions#match-a-controller-reference" >}})
in selectors to ensures that the matching resource is in the same composite
resource in the same way as [cross-resource referencing]({{<ref "./compositions#cross-resource-references" >}}).

The following example shows a Composition that defines a deletion ordering
between a `Cluster` and a `Release` resource. The `Usage` blocks deletion of
the `Cluster` resource until the `Release` resource is successfully deleted.

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
          replayDeletion: true
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

{{<hint "tip" >}}

<!-- vale write-good.Passive = NO -->
When there are multiple resources of same type in a Composition, the
{{<hover label="composition" line="18">}}Usage{{</hover>}} resource must
uniquely identify the resource in use or the using one. This could be
accomplished by using extra labels and combining
{{<hover label="composition" line="24">}}matchControllerRef{{</hover>}}
with a `matchLabels` selector. Another alternative is patching `resourceRef.name`
directly with the help of `ToCompositeFieldPath` and `FromCompositeFieldPath`
or `ToEnvironmentFieldPath` and `FromEnvironmentFieldPath` type patches. 
<!-- vale write-good.Passive = YES -->
{{< /hint >}}