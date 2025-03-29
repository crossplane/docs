---
title: Composite Resource Definitions
weight: 20
description: "Composite Resource Definitions or XRDs define custom API schemas"
---

Composite resource definitions (`XRDs`) define the schema for a custom API.  
Users create composite resources (`XRs`) using the API schema defined by an
`XRD`.


{{<hint "note">}}
Read the [composite resources]({{<ref "./composite-resources">}}) page for more
information about composite resources.
{{</hint>}}


{{<expand "Confused about Compositions, XRDs, and XRs?" >}}
Crossplane has four core components that users commonly mix up:

* [Compositions]({{<ref "./compositions" >}}) - A template to define how to create resources.
* Composite Resource Definition (`XRD`) - This page. A custom API specification. 
* [Composite Resource]({{<ref "./composite-resources">}}) (`XR`) - Created by
  using the custom API defined in a Composite Resource Definition. XRs use the
  Composition template to create new managed resources. 
{{</expand >}}

Crossplane XRDs are like 
[Kubernetes custom resource definitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/). 
XRDs require fewer fields and add options related to Crossplane, like connection
secrets. 

## Creating a CompositeResourceDefinition

Creating a CompositeResourceDefinition consists of:
* [Defining a custom API group](#xrd-groups).
* [Defining a custom API name](#xrd-names).
* [Defining a custom API schema and version](#xrd-versions).
  
Optionally, CompositeResourceDefinitions also support:
* [Defining connection secrets](#manage-connection-secrets).
* [Setting composite resource defaults](#set-composite-resource-defaults).
 
Composite resource definitions (`XRDs`) create new API endpoints inside a
Kubernetes cluster. 

Creating a new API requires defining an API 
{{<hover label="xrd1" line="6">}}group{{</hover>}},
{{<hover label="xrd1" line="7">}}name{{</hover>}} and
{{<hover label="xrd1" line="10">}}version{{</hover>}}. 

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
  versions:
  - name: v1alpha1
  # Removed for brevity
```

After applying an XRD, Crossplane creates a new Kubernetes custom resource
definition matching the defined API.

For example, the XRD 
{{<hover label="xrd1" line="4">}}xmydatabases.example.org{{</hover >}} 
creates a custom resource definition 
{{<hover label="kubeapi" line="2">}}xmydatabases.example.org{{</hover >}}.  

```shell {label="kubeapi",copy-lines="3"}
kubectl api-resources
NAME                              SHORTNAMES   APIVERSION          NAMESPACED   KIND
xmydatabases.example.org                       v1alpha1            true         xmydatabases
# Removed for brevity
```

{{<hint "warning">}}
You can't change the XRD
{{<hover label="xrd1" line="6">}}group{{</hover>}} or
{{<hover label="xrd1" line="7">}}names{{</hover>}}.  
You must delete and
recreate the XRD to change the 
{{<hover label="xrd1" line="6">}}group{{</hover>}} or
{{<hover label="xrd1" line="7">}}names{{</hover>}}.
{{</hint >}}

### XRD groups

Groups define a collection of related API endpoints. The `group` can be any
value, but common convention is to map to a fully qualified domain name.

<!-- vale write-good.Weasel = NO -->
Many XRDs may use the same `group` to create a logical collection of APIs.  
<!-- vale write-good.Weasel = YES -->
For example a `database` group may have a `relational` and `nosql` kinds. 

### XRD names

The `names` field defines how to refer to this specific XRD.  
The required name fields are: 

* `kind` - the `kind` value to use when calling this API. The kind is
  [UpperCamelCased](https://kubernetes.io/docs/contribute/style/style-guide/#use-upper-camel-case-for-api-objects).
  Crossplane recommends starting XRD `kinds` with an `X` to show 
  it's a custom Crossplane API definition. 
* `plural` - the plural name used for the API URL. The plural name must be
  lowercase. 

{{<hint "important" >}}
The XRD 
{{<hover label="xrdName" line="4">}}metadata.name{{</hover>}} must be 
{{<hover label="xrdName" line="9">}}plural{{</hover>}} name, `.` (dot character),
{{<hover label="xrdName" line="6">}}group{{</hover>}}.

For example, {{<hover label="xrdName"
line="4">}}xmydatabases.example.org{{</hover>}} matches the {{<hover
label="xrdName" line="9">}}plural{{</hover>}} name
{{<hover label="xrdName" line="9">}}xmydatabases{{</hover>}}, `.` 
{{<hover label="xrdName" line="6">}}group{{</hover>}} name, 
{{<hover label="xrdName" line="6">}}example.org{{</hover>}}.

```yaml {label="xrdName",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata: 
  name: xmydatabases.example.org
spec:
  group: example.org
  names:
    kind: XMyDatabase
    plural: xmydatabases
    # Removed for brevity
```
{{</hint >}}

### XRD versions

<!-- vale gitlab.SentenceLength = NO -->
The XRD `version` is like the 
[API versioning used by Kubernetes](https://kubernetes.io/docs/reference/using-api/#api-versioning).
The version shows how mature or stable the API is and increments when changing,
adding or removing fields in the API.
<!-- vale gitlab.SentenceLength = YES -->

Crossplane doesn't require specific versions or a specific version naming 
convention, but following 
[Kubernetes API versioning guidelines](https://kubernetes.io/docs/reference/using-api/#api-versioning)
is strongly recommended. 

* `v1alpha1` - A new API that may change at any time.
* `v1beta1` - An existing API that's considered stable. Breaking changes are
  strongly discouraged.
* `v1` - A stable API that doesn't have breaking changes. 

#### Define a schema

<!-- vale write-good.Passive = NO -->
<!-- vale write-good.TooWordy = NO -->
The `schema` defines the names
of the parameters, the data types of the parameters and which parameters are
required or optional. 
<!-- vale write-good.Passive = YES -->
<!-- vale write-good.TooWordy = YES -->

{{<hint "note" >}}
All `schemas` follow the Kubernetes custom resource definition 
[OpenAPIv3 structural schema](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#specifying-a-structural-schema). 
{{< /hint >}}

Each 
{{<hover label="schema" line="11">}}version{{</hover>}} of the API has a unique 
{{<hover label="schema" line="12">}}schema{{</hover>}}. 

All XRD {{<hover label="schema" line="12">}}schemas{{</hover>}} validate against
the {{<hover label="schema" line="13">}}openAPIV3Schema{{</hover>}}. The schema
is an OpenAPI 
{{<hover label="schema" line="14">}}object{{</hover>}} with the 
{{<hover label="schema" line="15">}}properties{{</hover>}} of a 
{{<hover label="schema" line="16">}}spec{{</hover>}}
{{<hover label="schema" line="17">}}object{{</hover>}}.

Inside the {{<hover label="schema" line="18">}}spec.properties{{</hover>}} is the custom
API definition.

In this example, the key {{<hover label="schema" line="19">}}region{{</hover>}}
is a {{<hover label="schema" line="20">}}string{{</hover>}}.

```yaml {label="schema",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: xDatabase
    plural: xdatabases
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string
    # Removed for brevity
```

A composite resource using this API references the 
{{<hover label="xr" line="1">}}group/version{{</hover>}} and 
{{<hover label="xr" line="2">}}kind{{</hover>}}. The 
{{<hover label="xr" line="5">}}spec{{</hover>}} has the 
{{<hover label="xr" line="6">}}region{{</hover>}} key with a string value. 

```yaml {label="xr"}
apiVersion: custom-api.example.org/v1alpha1
kind: xDatabase
metadata:
  name: my-composite-resource
spec: 
  region: "US"
```


{{<hint "tip" >}}
The custom API defined inside the 
{{<hover label="schema" line="18">}}spec.properties{{</hover>}} is an OpenAPIv3
specification. The 
[data models page](https://swagger.io/docs/specification/data-models/) of 
the Swagger documentation provides a list of examples using data types and input
restrictions. 

The Kubernetes documentation lists 
[the set of special restrictions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation)
on what your OpenAPIv3 custom API can use.
{{< /hint >}}

{{<hint "important" >}}

Changing or expanding the XRD schema requires restarting the [Crossplane pod]({{<ref "../guides/pods#crossplane-pod">}}) to take effect.
{{< /hint >}}

##### Required fields

By default all fields in a schema are optional. Define a parameter as required
with the 
{{< hover label="required" line="25">}}required{{</hover>}} attribute. 

In this example the XRD requires 
{{< hover label="required" line="19">}}region{{</hover>}} and 
{{< hover label="required" line="21">}}size{{</hover>}} but
{{< hover label="required" line="23">}}name{{</hover>}} is optional. 
```yaml {label="required",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: xDatabase
    plural: xdatabases
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string 
              size:
                type: string  
              name:
                type: string  
            required: 
              - region 
              - size
    # Removed for brevity
```

According to the OpenAPIv3 specification, the `required` field is per-object. If
a schema contains multiple objects the schema may need multiple `required`
fields.

This XRD defines two objects:
 1. the top-level {{<hover label="required2" line="7">}}spec{{</hover>}} object
 2. a second {{<hover label="required2" line="14">}}location{{</hover>}} object

The {{<hover label="required2" line="7">}}spec{{</hover>}} object 
{{<hover label="required2" line="23">}}requires{{</hover>}} the 
{{<hover label="required2" line="10">}}size{{</hover>}} and 
{{<hover label="required2" line="14">}}location{{</hover>}} but 
{{<hover label="required2" line="12">}}name{{</hover>}} is optional.

Inside the required {{<hover label="required2" line="14">}}location{{</hover>}} 
object,
{{<hover label="required2" line="17">}}country{{</hover>}} is 
{{<hover label="required2" line="21">}}required{{</hover>}} and
{{<hover label="required2" line="19">}}zone{{</hover>}} is optional.

```yaml {copy-lines="none",label="required2"}
# Removed for brevity
- name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              size:
                type: string  
              name:
                type: string 
              location:
                type: object
                properties:
                  country: 
                    type: string 
                  zone:
                    type: string
                required:
                  - country
            required:  
              - size
              - location
```

The Swagger "[Describing Parameters](https://swagger.io/docs/specification/describing-parameters/)"
documentation has more examples. 

##### Crossplane reserved fields

Crossplane doesn't allow the following fields in a schema:
* Any field under the object `spec.crossplane`
* Any field under the object `status.crossplane`
* `status.conditions`

Crossplane ignores any fields matching the reserved fields.

#### Serve and reference a schema

To use a schema it must be
{{<hover label="served" line="12" >}}served: true{{</hover >}}
and 
{{<hover label="served" line="13" >}}referenceable: true{{</hover>}}.

```yaml {label="served"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: xDatabase
    plural: xdatabases
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string            
```

Composite resources can use any schema version set as 
{{<hover label="served" line="12" >}}served: true{{</hover >}}.  
Kubernetes rejects any composite resource using a schema version set as `served:
false`.

{{< hint "tip" >}}
Setting a schema version as `served:false` causes errors for users using an older
schema. This can be an effective way to identify and upgrade users before
deleting the older schema version. 
{{< /hint >}}

The {{<hover label="served" line="13" >}}referenceable: true{{</hover>}}
field indicates which version of the schema Compositions use. Only one
version can be `referenceable`. 

{{< hint "note" >}}
Changing which version is `referenceable:true` requires [updating the `compositeTypeRef.apiVersion`]({{<ref "./compositions#enable-composite-resources" >}}) 
of any Compositions referencing that XRD.
{{< /hint >}}


#### Multiple schema versions

{{<hint "warning" >}}
Crossplane supports defining multiple `versions`, but the schema of each version
can't change any existing fields, also called "making a breaking change."

Breaking schema changes between versions requires the use of [conversion webhooks](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/#webhook-conversion).

New versions may define new optional parameters, but new required fields are
a "breaking change."

<!-- vale Crossplane.Spelling = NO -->
<!-- ignore to allow for CRDs -->
<!-- don't add to the spelling exceptions to catch when it's used instead of XRD -->
Crossplane XRDs use Kubernetes custom resource definitions for versioning. 
Read the Kubernetes documentation on 
[versions in CustomResourceDefinitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/)
for more background on versions and breaking changes. 
<!-- vale Crossplane.Spelling = YES -->

Crossplane recommends implementing breaking schema changes as brand new XRDs.
{{< /hint >}}

For XRDs, to create a new version of an API add a new 
{{<hover label="ver" line="21">}}name{{</hover>}} in the
{{<hover label="ver" line="10">}}versions{{</hover>}}
list. 

For example, this XRD version 
{{<hover label="ver" line="11">}}v1alpha1{{</hover>}} only has the field 
{{<hover label="ver" line="19">}}region{{</hover>}}.

A second version, 
{{<hover label="ver" line="21">}}v1{{</hover>}} expands the API to have both 
{{<hover label="ver" line="29">}}region{{</hover>}} and 
{{<hover label="ver" line="31">}}size{{</hover>}}.

```yaml {label="ver",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: xDatabase
    plural: xdatabases
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string  
  - name: v1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              region:
                type: string 
              size:
                type: string            
```

{{<hint "important" >}}

Changing or expanding the XRD schema requires restarting the [Crossplane pod]({{<ref "../guides/pods#crossplane-pod">}}) to take effect.
{{< /hint >}}

### Set composite resource defaults
XRDs can set default parameters for composite resources.

<!-- vale off -->
#### defaultCompositionRef
<!-- vale on -->
It's possible for multiple [Compositions]({{<ref "./compositions">}}) to
reference the same XRD. If more than one Composition references the same XRD,
the composite resource must select which Composition to use. 

An XRD can define the default Composition to use with the
`defaultCompositionRef` value. 

Set a
{{<hover label="defaultComp" line="6">}}defaultCompositionRef{{</hover>}} 
to set the default Composition.

```yaml {label="defaultComp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  defaultCompositionRef: 
    name: myComposition
  group: custom-api.example.org
  names:
  # Removed for brevity
  versions:
  # Removed for brevity
```

<!-- vale off -->
#### defaultCompositionUpdatePolicy
<!-- vale on -->

Changes to a Composition generate a new Composition revision. By default all
composite resources use the updated Composition revision. 

Set the XRD `defaultCompositionUpdatePolicy` to `Manual` to prevent composite
resources from automatically using the new revision. 

The default value is `defaultCompositionUpdatePolicy: Automatic`.

Set {{<hover label="compRev" line="6">}}defaultCompositionUpdatePolicy: Manual{{</hover>}}
to set the default Composition update policy for composite resources and using
this XRD.

```yaml {label="compRev",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  defaultCompositionUpdatePolicy: Manual
  group: custom-api.example.org
  names:
  # Removed for brevity
  versions:
  # Removed for brevity
```

<!-- vale off -->
#### enforcedCompositionRef
<!-- vale on -->
To require all composite resources to use a specific Composition use the
`enforcedCompositionRef` setting in the XRD.

For example, to require all composite resources using this XRD to use the
Composition 
{{<hover label="enforceComp" line="6">}}myComposition{{</hover>}} 
set 
{{<hover label="enforceComp" line="6">}}enforcedCompositionRef.name: myComposition{{</hover>}}.

```yaml {label="defaultComp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  enforcedCompositionRef: 
    name: myComposition
  group: custom-api.example.org
  names:
  # Removed for brevity
  versions:
  # Removed for brevity
```

## Verify a CompositeResourceDefinition

Verify an XRD with `kubectl get compositeresourcedefinition` or the short form, 
{{<hover label="getxrd" line="1">}}kubectl get xrd{{</hover>}}.

```yaml {label="getxrd",copy-lines="1"}
kubectl get xrd                                
NAME                                ESTABLISHED   OFFERED   AGE
xdatabases.custom-api.example.org   True          True      22m
```

The `ESTABLISHED` field indicates Crossplane installed the Kubernetes custom
resource definition for this XRD.

### XRD conditions
Crossplane uses a standard set of `Conditions` for XRDs.  
View the conditions of a XRD under their `Status` with 
`kubectl describe xrd`. 

```yaml {copy-lines="none"}
kubectl describe xrd
Name:         xpostgresqlinstances.database.starter.org
API Version:  apiextensions.crossplane.io/v1
Kind:         CompositeResourceDefinition
# Removed for brevity
Status:
  Conditions:
    Reason:                WatchingCompositeResource
    Status:                True
    Type:                  Established
# Removed for brevity
```

<!-- vale off -->
#### WatchingCompositeResource
<!-- vale on -->
`Reason: WatchingCompositeResource` indicates Crossplane defined the new
Kubernetes custom resource definitions related to the composite resource and is 
watching for the creation of new composite resources. 

```yaml
Type: Established
Status: True
Reason: WatchingCompositeResource
```

<!-- vale off -->
#### TerminatingCompositeResource
<!-- vale on -->
`Reason: TerminatingCompositeResource` indicates Crossplane is deleting the
custom resource definitions related to the composite resource and is 
terminating the composite resource controller.

```yaml
Type: Established
Status: False
Reason: TerminatingCompositeResource
```
