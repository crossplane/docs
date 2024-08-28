---
title: Composite Resources
weight: 50
description: "Composite resources, an XR or XRs, represent a collection of related cloud resources."
---

A composite resource represents a set of managed resources as a single
Kubernetes object. Crossplane creates composite resources when users access a
custom API, defined in the CompositeResourceDefinition. 

{{<hint "tip" >}}
Composite resources are a _composite_ of managed resources.  
A _Composition_ defines how to _compose_ the managed resources together.
{{< /hint >}}

{{<expand "Confused about Compositions, XRDs, XRs and Claims?" >}}
Crossplane has four core components that users commonly mix up:

* [Compositions]({{<ref "./compositions">}}) - A template to define how to create resources.
* [Composite Resource Definition]({{<ref "./composite-resource-definitions">}})
  (`XRD`) - A custom API specification. 
* Composite Resource (`XR`) - This page. Created by
  using the custom API defined in a Composite Resource Definition. XRs use the
  Composition template to create new managed resources. 
* [Claims]({{<ref "./claims" >}}) (`XRC`) - Like a Composite Resource, but
  with namespace scoping. 
{{</expand >}}

## Creating composite resources

Creating composite resources requires a 
[Composition]({{<ref "./compositions">}}) and a 
[CompositeResourceDefinition]({{<ref "./composite-resource-definitions">}}) 
(`XRD`).  
The Composition defines the set of resources to create.  
The XRD defines the custom API users call to request the set of resources.

![Diagram of the relationship of Crossplane components](/media/composition-how-it-works.svg)

XRDs define the API used to create a composite resource.  
For example, 
this {{<hover label="xrd1" line="2">}}CompositeResourceDefinition{{</hover>}}
creates a custom API endpoint 
{{<hover label="xrd1" line="4">}}xmydatabases.example.org{{</hover>}}.

```yaml {label="xrd1",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata: 
  name: xmydatabases.example.org
spec:
  group: example.org
  names:
    kind: xMyDatabase
    plural: xmydatabases
  # Removed for brevity
```

When a user calls the custom API, 
{{<hover label="xrd1" line="4">}}xmydatabases.example.org{{</hover>}}, 
Crossplane chooses the Composition to use based on the Composition's 
{{<hover label="typeref" line="6">}}compositeTypeRef{{</hover>}}

```yaml {label="typeref",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: my-composition
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: xMyDatabase
  # Removed for brevity
```

The Composition
{{<hover label="typeref" line="6">}}compositeTypeRef{{</hover>}} matches the 
XRD {{<hover label="xrd1" line="6">}}group{{</hover>}} and 
{{<hover label="xrd1" line="9">}}kind{{</hover>}}.

Crossplane creates the resources defined in the matching Composition and
represents them as a single `composite` resource. 

```shell{copy-lines="1"}
kubectl get composite
NAME                    SYNCED   READY   COMPOSITION         AGE
my-composite-resource   True     True    my-composition      4s
```

### Naming external resources
By default, managed resources created by a composite resource have the name of
the composite resource, followed by a random suffix.

<!-- vale Google.FirstPerson = NO -->
<!-- vale Crossplane.Spelling = NO -->
For example, a composite resource named "my-composite-resource" creates external
resources named "my-composite-resource-fqvkw." 
<!-- vale Google.FirstPerson = YES -->
<!-- vale Crossplane.Spelling = YES  -->

Resource names can be deterministic by applying an 
{{<hover label="annotation" line="5">}}annotation{{</hover>}} to the composite
resource. 

```yaml {label="annotation",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
  annotations: 
    crossplane.io/external-name: my-custom-name
# Removed for brevity
```

Inside the Composition, use a 
{{<hover label="comp" line="10">}}patch{{</hover>}}
to apply the external-name to the resources. 

The {{<hover label="comp" line="11">}}fromFieldPath{{</hover>}} patch copies the
{{<hover label="comp" line="11">}}metadata.annotations{{</hover>}} field from
the composite resource to the 
{{<hover label="comp" line="12">}}metadata.annotations{{</hover>}} inside the
managed resource. 

{{<hint "note" >}}
If a managed resource has the `crossplane.io/external-name` annotation
Crossplane uses the annotation value to name the external resource.
{{</hint >}}

```yaml {label="comp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: my-composition
spec:
  resources:
    - name: database
      base:
        # Removed for brevity
      patches:
      - fromFieldPath: metadata.annotations
        toFieldPath: metadata.annotations
```

For more information on patching resources refer to the [Patch and Transform]({{<ref "./patch-and-transform">}}) documentation. 

### Composition selection

Select a specific Composition for a composite resource to use with 
{{<hover label="compref" line="6">}}compositionRef{{</hover>}}

{{<hint "important">}}
The selected Composition must allow the composite resource to use it with a
`compositeTypeRef`. Read more about the `compositeTypeRef` field in the
[Enabling Composite Resources]({{<ref "./compositions#enabling-composite-resources">}})
section of the Composition documentation. 
{{< /hint >}}

```yaml {label="compref",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
spec:
  compositionRef:
    name: my-other-composition
  # Removed for brevity
```

A composite resource can also select a Composition based on labels instead of 
the exact name with a
{{<hover label="complabel" line="6">}}compositionSelector{{</hover>}}.

Inside the {{<hover label="complabel" line="7">}}matchLabels{{</hover>}} section
provide one or more Composition labels to match.

```yaml {label="complabel",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
spec:
  compositionSelector:
    matchLabels:
      environment: production
  # Removed for brevity
```

### Composition revision policy

Crossplane tracks changes to Compositions as 
[Composition revisions]({{<ref "composition-revisions">}}) . 

A composite resource can use
a {{<hover label="comprev" line="6">}}compositionUpdatePolicy{{</hover>}} to
manually or automatically reference newer Composition revisions.

The default 
{{<hover label="comprev" line="6">}}compositionUpdatePolicy{{</hover>}} is 
"Automatic." Composite resources automatically use the latest Composition
revision. 

Change the policy to 
{{<hover label="comprev" line="6">}}Manual{{</hover>}} to prevent composite
resources from automatically upgrading.

```yaml {label="comprev",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
spec:
  compositionUpdatePolicy: Manual
  # Removed for brevity
```

### Composition revision selection

Crossplane records changes to Compositions as 
[Composition revisions]({{<ref "composition-revisions">}}).    
A composite resource can
select a specific Composition revision.


Use {{<hover label="comprevref" line="6">}}compositionRevisionRef{{</hover>}} to
select a specific Composition revision by name.

For example, to select a specific Composition revision use the name of the
desired Composition revision. 

```yaml {label="comprevref",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
spec:
  compositionUpdatePolicy: Manual
  compositionRevisionRef:
    name: my-composition-b5aa1eb
  # Removed for brevity
```

{{<hint "note" >}}
Find the Composition revision name from 
{{<hover label="getcomprev" line="1">}}kubectl get compositionrevision{{</hover>}}

```shell {label="getcomprev",copy-lines="1"}
kubectl get compositionrevision
NAME                         REVISION   XR-KIND        XR-APIVERSION            AGE
my-composition-5c976ad       1          xmydatabases   example.org/v1alpha1     65m
my-composition-b5aa1eb       2          xmydatabases   example.org/v1alpha1     64m
```
{{< /hint >}}

A Composite resource can also select Composition revisions based on labels
instead of the exact name with a 
{{<hover label="comprevsel" line="6">}}compositionRevisionSelector{{</hover>}}.

Inside the {{<hover label="comprevsel" line="7">}}matchLabels{{</hover>}} 
section provide one or more Composition revision labels to match.


```yaml {label="comprevsel",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
spec:
  compositionRevisionSelector:
    matchLabels:
      channel: dev
  # Removed for brevity
```

### Manage connection secrets 

When a composite resource creates resources, Crossplane provides any
[connection secrets]({{<ref "./managed-resources#writeconnectionsecrettoref">}})
to the composite resource.

{{<hint "important" >}}

A resource may only access connection secrets allowed by the XRD. By
default XRDs provide access to all connection secrets generated by managed
resources.  
Read more about [managing connection secrets]({{<ref "./composite-resource-definitions#manage-connection-secrets">}})
in the XRD documentation.
{{< /hint >}}

Use 
{{<hover label="writesecret" line="6">}}writeConnectionSecretToRef{{</hover>}} 
to specify where the composite resource writes their connection secrets to. 

For example, this composite resource saves the connection secrets in a 
Kubernetes secret object named
{{<hover label="writesecret" line="7">}}my-secret{{</hover>}} in the namespace 
{{<hover label="writesecret" line="8">}}crossplane-system{{</hover>}}.

```yaml {label="writesecret",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
spec:
  writeConnectionSecretToRef:
    name: my-secret
    namespace: crossplane-system
  # Removed for brevity
```

Composite resources can write connection secrets to an 
[external secret store]({{<ref "../guides/vault-as-secret-store">}}),
like HashiCorp Vault. 

{{<hint "important" >}}
External secret stores are an alpha feature. Alpha features aren't enabled by
default. 
{{< /hint >}}

Use the {{<hover label="publishsecret"
line="6">}}publishConnectionDetailsTo{{</hover>}} field to save connection
secrets to an external secrets store.

```yaml {label="publishsecret",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
spec:
  publishConnectionDetailsTo:
    name: my-external-secret-store
  # Removed for brevity
```

Read the [External Secrets Store]({{<ref "../guides/vault-as-secret-store">}}) documentation for more information on using
external secret stores. 

For more information on connection secrets read the [Connection Secrets knowledge base article]({{<ref "connection-details">}}).

### Pausing composite resources

<!-- vale Google.WordList = NO -->
Crossplane supports pausing composite resources. A paused composite resource
doesn't check or make changes on its external resources.
<!-- vale Google.WordList = YES -->

To pause a composite resource apply the 
{{<hover label="pause" line="4">}}crossplane.io/paused{{</hover>}} annotation. 

```yaml {label="pause",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: xMyDatabase
metadata:
  name: my-composite-resource
  annotations:
    crossplane.io/paused: "true"
spec:
  # Removed for brevity
```

## Verify composite resources
Use 
{{<hover label="getcomposite" line="1">}}kubectl get composite{{</hover>}}
to view all the composite resources Crossplane created.

```shell{copy-lines="1",label="getcomposite"}
kubectl get composite
NAME                    SYNCED   READY   COMPOSITION         AGE
my-composite-resource   True     True    my-composition      4s
```

Use `kubectl get` for the specific custom API endpoint to view
only those resources.

```shell {copy-lines="1"}
kubectl get xMyDatabase.example.org
NAME                    SYNCED   READY   COMPOSITION        AGE
my-composite-resource   True     True    my-composition     12m
```

Use 
{{<hover label="desccomposite" line="1">}}kubectl describe composite{{</hover>}}
to view the linked 
{{<hover label="desccomposite" line="16">}}Composition Ref{{</hover>}},
and unique managed resources created in the
{{<hover label="desccomposite" line="22">}}Resource Refs{{</hover>}}.


```yaml {copy-lines="1",label="desccomposite"}
kubectl describe composite my-composite-resource
Name:         my-composite-resource
API Version:  example.org/v1alpha1
Kind:         xMyDatabase
Spec:
  Composition Ref:
    Name:  my-composition
  Composition Revision Ref:
    Name:                     my-composition-cf2d3a7
  Composition Update Policy:  Automatic
  Resource Refs:
    API Version:  s3.aws.upbound.io/v1beta1
    Kind:         Bucket
    Name:         my-composite-resource-fmrks
    API Version:  dynamodb.aws.upbound.io/v1beta1
    Kind:         Table
    Name:         my-composite-resource-wnr9t
# Removed for brevity
```

### Composite resource conditions

The conditions of composite resources match the conditions of their managed 
resources. 

Read the 
[conditions section]({{<ref "./managed-resources#conditions">}}) of the
managed resources documentation for details.

## Composite resource labels

Crossplane adds labels to composite resources to show their relationship to
other Crossplane components.

### Composite label
Crossplane adds the 
{{<hover label="complabel" line="4">}} crossplane.io/composite{{</hover>}} label
to all composite resources. The label matches the name of the composite.
Crossplane applies the composite label to any managed resource created by a
composite, creating a reference between the managed resource and owning
composite resource. 

```shell {label="claimname",copy-lines="1"}
kubectl describe xmydatabase.example.org/my-claimed-database-x9rx9
Name:         my-claimed-database2-x9rx9
Namespace:
Labels:       crossplane.io/composite=my-claimed-database-x9rx9
```

### Claim name label
Crossplane adds the 
{{<hover label="claimname" line="4">}}crossplane.io/claim-name{{</hover>}}
label to composite resources created from a Claim. The label indicates the name
of the Claim linked to this composite resource. 

```shell {label="claimname",copy-lines="1"}
kubectl describe xmydatabase.example.org/my-claimed-database-x9rx9
Name:         my-claimed-database2-x9rx9
Namespace:
Labels:       crossplane.io/claim-name=my-claimed-database
```

Composite resources created directly, without using a Claim, don't have a
{{<hover label="claimname" line="4">}}crossplane.io/claim-name{{</hover>}} 
label. 

### Claim namespace label
Crossplane adds the 
{{<hover label="claimname" line="4">}}crossplane.io/claim-namespace{{</hover>}}
label to composite resources created from a Claim. The label indicates the 
namespace of the Claim linked to this composite resource. 

```shell {label="claimname",copy-lines="1"}
kubectl describe xmydatabase.example.org/my-claimed-database-x9rx9
Name:         my-claimed-database2-x9rx9
Namespace:
Labels:       crossplane.io/claim-namespace=default
```

Composite resources created directly, without using a Claim, don't have a
{{<hover label="claimname" line="4">}}crossplane.io/claim-namespace{{</hover>}} 
label. 