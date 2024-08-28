---
title: Claims
weight: 60
description: "Claims are a way to consume Crossplane resources with namespace scoping"
---

Claims represents a set of managed resources as a single
Kubernetes object, inside a namespace. 

Users create claims when they access the
custom API, defined in the CompositeResourceDefinition. 

{{< hint "tip" >}}

Claims are like [composite resources]({{<ref "./composite-resources">}}). The
difference between Claims and composite resources is Crossplane can create 
Claims in a namespace, while composite resources are cluster scoped.
{{< /hint >}}

{{<expand "Confused about Compositions, XRDs, XRs and Claims?" >}}
Crossplane has four core components that users commonly mix up:

* [Compositions]({{<ref "./compositions">}}) - A template to define how to create resources.
* [Composite Resource Definition]({{<ref "./composite-resource-definitions">}})
  (`XRD`) - A custom API specification. 
* [Composite Resources]({{<ref "./composite-resources">}}) (`XR`) - Created by
  using the custom API defined in a Composite Resource Definition. XRs use the
  Composition template to create new managed resources. 
* Claims (`XRC`) - This page. Like a Composite Resource, but
  with namespace scoping. 
{{</expand >}}

## Creating a Claim

Creating a Claim requires a 
[Composition]({{<ref "./compositions">}}) and a 
[CompositeResourceDefinition]({{<ref "./composite-resource-definitions">}}) 
(`XRD`) already installed.  

{{<hint "note" >}}
The XRD must 
[enable Claims]({{<ref "./composite-resource-definitions#enable-claims">}}).
{{< /hint >}}

The Composition defines the set of resources to create.  
The XRD defines the custom API users call to request the set of resources.

![Diagram of the relationship of Crossplane components](/media/composition-how-it-works.svg)

For example, 
this {{<hover label="xrd1" line="2">}}CompositeResourceDefinition{{</hover>}}
creates a composite resource API endpoint 
{{<hover label="xrd1" line="4">}}xmydatabases.example.org{{</hover>}} and
enables a Claim API endpoint 
{{<hover label="xrd1" line="11">}}database.example.org{{</hover>}}

```yaml {label="xrd1",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata: 
  name: xmydatabases.example.org
spec:
  group: example.org
  names:
    kind: XMyDatabase
    plural: xmydatabases
  claimNames:
    kind: Database
    plural: databases
  # Removed for brevity
```

The Claim uses the XRD's 
{{<hover label="xrd1" line="11">}}kind{{</hover>}} API endpoint to request 
resources.

The Claim's {{<hover label="xrd1" line="1">}}apiVersion{{</hover>}} matches
the XRD {{<hover label="xrd1" line="6">}}group{{</hover>}} and the 
{{<hover label="claim1" line="2">}}kind{{</hover>}} matches the XRD
{{<hover label="xrd1" line="11">}}claimNames.kind{{</hover>}}

```yaml {label="claim1",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: database
metadata:
  name: my-claimed-database
spec:
  # Removed for brevity
```

When a user creates a Claim in a namespace Crossplane also creates a composite
resource.

Use {{<hover label="claimcomp" line="1">}}kubectl describe{{</hover>}} on the 
Claim to view the related composite resource.

The {{<hover label="claimcomp" line="6">}}Resource Ref{{</hover>}} is the
composite resource Crossplane created for this Claim. 

```shell {label="claimcomp",copy-lines="1"}
kubectl describe database.example.org/my-claimed-database
Name:         my-claimed-database
API Version:  example.org/v1alpha1
Kind:         database
Spec:
  Resource Ref:
    API Version:  example.org/v1alpha1
    Kind:         XMyDatabase
    Name:         my-claimed-database-rr4ll
# Removed for brevity.
```

Use {{<hover label="getcomp" line="1">}}kubectl describe{{</hover>}} on the
composite resource to view the 
{{<hover label="getcomp" line="6">}}Claim Ref{{</hover>}} linking the
composite resource to the original Claim.

```shell {label="getcomp",copy-lines="1"}
kubectl describe xmydatabase.example.org/my-claimed-database-rr4ll
Name:         my-claimed-database-rr4ll
API Version:  example.org/v1alpha1
Kind:         XMyDatabase
Spec:
  Claim Ref:
    API Version:  example.org/v1alpha1
    Kind:         database
    Name:         my-claimed-database
    Namespace:    default
```

{{<hint "note" >}}
Crossplane supports directly creating composite resources. Claims allow
namespace scoping and isolation for users consuming the custom APIs. 

If you don't use namespaces in your Kubernetes deployment Claims aren't necessary.
{{< /hint >}}

### Claiming existing composite resources

By default, creating a Claim creates a new composite resource. Claims can also
link to existing composite resources. 

A use case for claiming existing composite resources may be slow to provision
resources. Composite resources can be pre-provisioned and a Claim can
use those resources without waiting for their creation. 

Set the Claim's {{<hover label="resourceref" line="6">}}resourceRef{{</hover>}}
and match the pre-existing composite resource
{{<hover label="resourceref" line="9">}}name{{</hover>}}.

```yaml {label="resourceref",copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: database
metadata:
  name: my-claimed-database
spec:
  resourceRef:
    apiVersion: example.org/v1alpha1
    kind: XMyDatabase
    name: my-pre-created-xr
```

If a Claim specifies a 
{{<hover label="resourceref" line="6">}}resourceRef{{</hover>}} that doesn't
exist, Crossplane doesn't create a composite resource. 

{{<hint "note" >}}
All Claims have a 
{{<hover label="resourceref" line="6">}}resourceRef{{</hover>}}. Manually
defining the 
{{<hover label="resourceref" line="6">}}resourceRef{{</hover>}}
isn't required. Crossplane fills in the
{{<hover label="resourceref" line="6">}}resourceRef{{</hover>}}
with the information from the composite resource created for the Claim.
{{< /hint >}}

## Claim connection secrets

If a Claim expects connection secrets the Claim must define a 
{{<hover label="claimSec" line="6">}}writeConnectionSecretToRef{{</hover>}}
object. 

The 
{{<hover label="claimSec" line="6">}}writeConnectionSecretToRef{{</hover>}}
object defines the name of the Kubernetes secret object where Crossplane saves
the connection details. 

{{<hint "note" >}}
The Crossplane creates the secret object in the same namespace as the Claim.
{{< /hint >}}

For example, to a new secret object named
{{<hover label="claimSec" line="7">}}my-claim-secret{{</hover>}} use 
{{<hover label="claimSec" line="6">}}writeConnectionSecretToRef{{</hover>}} with
the 
{{<hover label="claimSec" line="7">}}name: my-claim-secret{{</hover>}}.
```yaml {label="claimSec"}
apiVersion: example.org/v1alpha1
kind: database
metadata:
  name: my-claimed-database
spec:
  writeConnectionSecretToRef:
    name: my-claim-secret
```

For more information on connection secrets read the [Connection Secrets knowledge base article]({{<ref "connection-details">}}).