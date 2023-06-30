---
title: Composite Resource Definitions
weight: 40
---

Composite resource definitions (`XRDs`) define the schema for a custom API.  
Users create composite resources (`XRs`) and Claims (`XCs`) using the API
schema defined by an `XRD`.


{{< hint "note" >}}

Read the [composite resources]({{<ref "./composite-resources">}}) page for more
information about composite resources.

Read the [Claims]({{<ref "./claims">}}) page for more
information about Claims.
{{</hint >}}


{{<expand "Confused about Compositions, XRDs, XRs and Claims?" >}}
Crossplane has four core components that users commonly mix up:

* [Compositions]({{<ref "./compositions" >}}) - A template to define how to create resources.
* Composite Resource Definition (`XRD`) - This page. A custom API specification. 
* [Composite Resource]({{<ref "./composite-resources">}}) (`XR`) - Created by
  using the custom API defined in a Composite Resource Definition. XRs use the
  Composition template to create new managed resources. 
* [Claims]({{<ref "./claims" >}}) (`XRC`) - Like a Composite Resource, but
  with namespace scoping. 
{{</expand >}}

Crossplane XRDs are like 
[Kubernetes custom resource definitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/). 
XRDs require fewer fields and add options related to Crossplane, like Claims and
connection secrets. 

## Creating a CompositeResourceDefinition

Creating a CompositeResourceDefinintion consists of:
* [Defining a custom API group](#xrd-groups).
* [Defining a custom API name](#xrd-names).
* [Defining a custom API schema and version](#xrd-versions).
  
Optionally, CompositeResourceDefinintion also support:
* [Defining a Claim]

 
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
    kind: xMyDatabase
    plural: xmydatabases
  versions:
  - name: v1alpha1
  # Removed for brevity
```

### XRD groups

Groups define a collection of related API endpoints. The `group` can be any
value, but common convention is to map to a fully qualified domain name.

<!-- vale write-good.Weasel = NO -->
Many XRDs may use the same `group` to create a logical collection of APIs. 
<!-- vale write-good.Weasel = YES -->

### XRD names

The `names` field defines how to refer to this specific XRD. The required name 
fields are: 

* `kind` - the `kind` value to use when calling this API. The kind is
  [UpperCamelCased](https://kubernetes.io/docs/contribute/style/style-guide/#use-upper-camel-case-for-api-objects).
  Crossplane recommends starting XRD `kinds` with an `x` to show 
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
    kind: xMyDatabase
    plural: xmydatabases
    # Removed for brevity
```
{{</hint >}}

### XRD versions

The XRD `version` is like the 
[API versioning used by Kubernetes](https://kubernetes.io/docs/reference/using-api/#api-versioning).
The version shows how mature or stable the API is and changes when changing,
adding or removing fields in the API.

Crossplane doesn't require specific versions or a version naming convention, but
following [Kubernetes API versioning guidelines](https://kubernetes.io/docs/reference/using-api/#api-versioning)
is strongly recommended. 

* `v1alpha1` - A new API that's may change at any time.
* `v1beta1` - An existing API that's considered stable. Breaking changes are
  strongly discouraged.
* `v1` - A stable API that doesn't change.

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
[Open APIv3 structural schema](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#specifying-a-structural-schema). 
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

Changing or expanding the XRD schema requires restarting the [Crossplane
pod]({{<ref "./pods#crossplane-pod">}}) to take effect.
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

The Swagger "[Describing
Parameters](https://swagger.io/docs/specification/describing-parameters/)"
documentation has more examples. 

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
schmea. This can be an effective way to identify and upgrade users before
deleting the older schema version. 
{{< /hint >}}

The {{<hover label="served" line="13" >}}referenceable: true{{</hover>}}
field indicates which version of the schema Compositions use. Only one
version can be `referenceable`. 

{{< hint "note" >}}
Changing which version is `referenceable:true` requires [updating the
`compositeTypeRef.apiVersion`]({{<ref
"./compositions#enabling-composite-resources" >}}) 
of any Compositions referencing that XRD.
{{< /hint >}}


#### Multiple schema versions

{{<hint "warning" >}}
Crossplane supports defining multiple `versions`, but the schema of each version
can't change any existing fields, also called "making a breaking change."

Breaking schema changes between versions requires the use of [conversion
webhooks](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/#webhook-conversion).

New versions may define new optional parameters, but new required fields are
a "breaking change."

Crossplane XRDs use Kubernetes custom resource definitions for versioning. 
Read the Kubernetes documentation on [versions in
CustomResourceDefinitions](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/)
for more background on versions and breaking changes. 

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

Changing or expanding the XRD schema requires restarting the [Crossplane
pod]({{<ref "./pods#crossplane-pod">}}) to take effect.
{{< /hint >}}

### Enable Claims

Optionally, XRDs can allow Claims to use the XRD API. 

{{<hint "note" >}}

Read the [Claims]({{<ref "./claims">}}) page for more
information about Claims.
{{</hint >}}

XRDs offer Claims with a 
{{<hover label="claim" line="10">}}claimNames{{</hover >}} object.

The {{<hover label="claim" line="10">}}claimNames{{</hover >}} defines a 
{{<hover label="claim" line="11">}}kind{{</hover >}} and 
{{<hover label="claim" line="12">}}plural{{</hover >}} like the XRD 
{{<hover label="claim" line="7">}}names{{</hover >}} object.   
Also like XRD 
{{<hover label="claim" line="7">}}names{{</hover >}}, use UpperCamelCase
for the
{{<hover label="claim" line="11">}}kind{{</hover >}} and lowercase for the 
{{<hover label="claim" line="12">}}plural{{</hover >}}.

The Claim 
{{<hover label="claim" line="11">}}kind{{</hover >}} and 
{{<hover label="claim" line="12">}}plural{{</hover >}} must be unique. They
can't match any other Claim or other XRD 
{{<hover label="claim" line="8">}}kind{{</hover >}}.

{{<hint "tip" >}}
Common Crossplane convention is to use 
{{<hover label="claim" line="10">}}claimNames{{</hover >}} that match the XRD 
{{<hover label="claim" line="7">}}names{{</hover >}}, but without the beginning
"x."
{{</hint >}}

```yaml {label="claim",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: xDatabase
    plural: xdatabases
  claimNames:
    kind: Database
    plural: databases
  versions:
  # Removed for brevity
```

### Manage connection secrets

By default, any connection secrets 

## Webhooks
apis/apiextensions/v1/xrd_webhooks.go
### Influencing External Names

The `crossplane.io/external-name` annotation has special meaning to Crossplane
managed resources - it specifies the name (or identifier) of the resource in the
external system, for example the actual name of a `CloudSQLInstance` in the GCP
API. Some managed resources don't let you specify an external name - in those
cases Crossplane will set it for you to whatever the external system requires.

If you add the `crossplane.io/external-name` annotation to a claim Crossplane
will automatically propagate it when it creates an XR. It's good practice to
have your `Composition` further propagate the annotation to one or more composed
resources, but it's not required.

# Document XRD Conditions
https://github.com/crossplane/docs/issues/448

## What happens when you delete xrd?

# Restart XR and claim controllers when XRDs are updated
https://github.com/crossplane/docs/issues/288

## CompositeResourceDefinitions

Below is an example `CompositeResourceDefinition` that includes all configurable
fields.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  # XRDs must be named '<plural>.<group>', per the plural and group names below.
  name: xpostgresqlinstances.example.org
spec:
  # This XRD defines an XR in the 'example.org' API group.
  group: example.org
  # The kind of this XR will be 'XPostgreSQLInstance`. You may also optionally
  # specify a singular name and a listKind.
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
  # This type of XR offers a claim. Omit claimNames if you don't want to do so.
  # The claimNames must be different from the names above - a common convention
  # is that names are prefixed with 'X' while claim names are not. This lets app
  # team members think of creating a claim as (e.g.) 'creating a
  # PostgreSQLInstance'.
  claimNames:
    kind: PostgreSQLInstance
    plural: postgresqlinstances
  # Each type of XR can declare any keys they write to their connection secret
  # which will act as a filter during aggregation of the connection secret from
  # composed resources. It's recommended to provide the set of keys here so that
  # consumers of claims and XRs can see what to expect in the connection secret.
  # If no key is given, then all keys in the aggregated connection secret will
  # be written to the connection secret of the XR.
  connectionSecretKeys:
  - hostname
  # Each type of XR may specify a default Composite Delete Policy to be used
  # when the Claim has no compositeDeletePolicy.  The valid values are Background
  # and Foreground, and the default is Background.  See the description of the
  # compositeDeletePolicy parameter for more information.
  defaultCompositeDeletePolicy: Background
  # Each type of XR may specify a default Composition to be used when none is
  # specified (e.g. when the XR has no compositionRef or selector). A similar
  # enforceCompositionRef field also exists to allow XRs to enforce a specific
  # Composition that should always be used.
  defaultCompositionRef:
    name: example
  # Each type of XR may specify a default Composition Update Policy to be used
  # when the Claim has no compositionUpdatePolicy.  The valid values are Automatic
  # and Manual and the default is Automatic.
  defaultCompositionUpdatePolicy: Automatic
  # Each type of XR may be served at different versions - e.g. v1alpha1, v1beta1
  # and v1 - simultaneously. Currently Crossplane requires that all versions
  # have an identical schema, so this is mostly useful to 'promote' a type of XR
  # from alpha to beta to production ready.
  versions:
  - name: v1alpha1
    # Served specifies that XRs should be served at this version. It can be set
    # to false to temporarily disable a version, for example to test whether
    # doing so breaks anything before a version is removed wholesale.
    served: true
    # Referenceable denotes the version of a type of XR that Compositions may
    # use. Only one version may be referenceable.
    referenceable: true
    # Schema is an OpenAPI schema just like the one used by Kubernetes CRDs. It
    # determines what fields your XR and claim will have. Note that Crossplane
    # will automatically extend with some additional Crossplane machinery.
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              parameters:
                type: object
                properties:
                  storageGB:
                    type: integer
                required:
                - storageGB
            required:
            - parameters
          status:
            type: object
            properties:
              address:
                description: Address of this MySQL server.
                type: string
```

Take a look at the Kubernetes [CRD documentation][crd-docs] for a more detailed
guide to writing OpenAPI schemas. Note that the following fields are reserved
for Crossplane machinery, and will be ignored if your schema includes them:

* `spec.resourceRef`
* `spec.resourceRefs`
* `spec.claimRef`
* `spec.writeConnectionSecretToRef`
* `status.conditions`
* `status.connectionDetails`

> If your `CompositeResourceDefinition` isn't working as you'd expect you can
> try running `kubectl describe xrd` for details - pay particular attention to
> any events and status conditions.
