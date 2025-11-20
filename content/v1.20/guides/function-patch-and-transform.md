---
title: Function Patch and Transform
weight: 70
description: "A function that use patches and transforms to modify inputs from claims and composite resources before creating managed resources"
---

Function Patch and Transform allows you to write a Composition that specifies
managed resource (MR) templates, and uses "patch and transform" operations to
fill them out. Crossplane fills the templates out with values copied from a
claim or composite resource (XR).

A [patch](#create-a-patch) copies a value from one resource and _patches_ it
onto another resource. A [transform](#transform-a-patch) modifies the values
before applying the patch.

{{<hint "tip" >}}
All Compositions used Patch and Transform before Crossplane added
support for composition functions.

Function Patch and Transform works like legacy `mode: Resources` Compositions,
which Crossplane deprecated in v1.17. The difference is that it uses a
`mode: Pipeline` Composition and a function instead of a `mode: Resources`
Composition.
{{< /hint >}}

Here's an example Composition that uses Function Patch and Transform. When you
create an `AcmeBucket` XR that uses this Composition, Crossplane uses the
template to create the Amazon S3 `Bucket` MR.

Crossplane copies the value from the `AcmeBucket` XR's `spec.desiredRegion`
field and patch it onto the `Bucket` managed resource's
`spec.forProvider.region` field.

```yaml {label="intro"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: AcmeBucket
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: storage-bucket
        base:
          apiVersion: s3.aws.upbound.io/v1beta1
          kind: Bucket
          spec:
            forProvider:
              region: "us-east-2"
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.desiredRegion
          toFieldPath: spec.forProvider.region
```

{{<hint "note" >}}
Patch and transform is best for simpler compositions. It intentionally doesn't
support features like loops and conditionals.
{{</hint >}}

{{<expand "Confused about Compositions, XRDs, XRs and Claims?" >}}
Crossplane has four core components that users commonly mix up:

* [Composition]({{<ref "../concepts/compositions">}}) - A template to define
  how to create resources.
* [composite resource Definition]({{<ref "../concepts/composite-resource-definitions">}})
  (`XRD`) - A custom API specification.
* [composite resource]({{<ref "../concepts/composite-resources">}}) (`XR`) -
  Created by using the custom API defined in a composite resource Definition.
  XRs use the Composition template to create new managed resources.
* [Claim]({{<ref "../concepts/claims" >}}) (`XRC`) - Like a composite resource,
  but with namespace scoping.
{{</expand >}}

## Install the function

You must install Function Patch and Transform before you can use it in a
Composition. Apply this manifest to install Function Patch and Transform:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.8.2
```

{{<hint "tip" >}}
Read the [Composition page]({{<ref "../concepts/compositions">}}) to learn more
about Compositions and composition functions.
{{< /hint >}}


##  Resource templates

The `resources` field the function's input defines the set of things that a
composite resource creates when it uses this function.

For example, the input can define a template to create a virtual machine and an
associated storage bucket at the same time.

{{<hint "tip" >}}
Crossplane calls the resources a composite resource creates
_composed resources_.
{{< /hint >}}

The `resources` field lists the individual resources with a `name`. This name
identifies the resource inside the Composition. It isn't related to the external
name used with the Provider.

The contents of the `base` are identical to creating a standalone
[managed resource]({{<ref "../concepts/managed-resources">}}).

This example uses
[provider-upjet-aws](https://github.com/crossplane-contrib/provider-upjet-aws)
to define a S3 storage `Bucket` and EC2 compute `Instance`.

After defining the `apiVersion` and `kind`, define the `spec.forProvider` fields
defining the settings of the resource.

```yaml {copy-lines="none",label="resources"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: storage-bucket
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: "us-east-2"
- name: vm
  base:
    apiVersion: ec2.aws.upbound.io/v1beta1
    kind: Instance
    spec:
      forProvider:
        ami: ami-0d9858aa3c6322f73
        instanceType: t2.micro
        region: "us-east-2"
```

When a [composite resource]({{<ref "../concepts/composite-resources" >}}) uses
this function, the composite resource creates two new managed resources with all
the provided `spec.forProvider` settings.

The `spec` supports any settings used in a managed resource, including applying
`annotations` and `labels` or using a specific `providerConfigRef`.

{{<hint "note" >}}
Use the `crossplane.io/external-name` annotation on the resource to set
the resource's name in the external system (like AWS).
{{< /hint >}}

{{<hint "tip" >}}
You can use Function Patch and Transform to template other kinds of Crossplane
resources, like ProviderConfigs.

You can also template other kinds of composite resource (XR).

You can't template namespaced resources.
{{< /hint >}}

## Create a patch

Each entry in the `resources` list can include a list of patches. The `patches`
field takes a list of patches to apply to the individual resource.

Each patch has a `type`, which defines what kind of patch action Crossplane
applies.

Patches reference fields inside different resources depending on the patch type,
but all patches reference a `fromFieldPath` and `toFieldPath`.

The `fromFieldPath` is the path to the patch's input values. The `toFieldPath`
is the path the patch applies to.

Here's an example of a patch that copies a value from the composite resource's
`spec.field1` field to the composed Bucket's labels.

```yaml {label="createComp",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: storage-bucket
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: "us-east-2"
  patches:
    - type: FromCompositeFieldPath
      fromFieldPath: spec.field1
      toFieldPath: metadata.labels["patchLabel"]
```

### Selecting fields

Crossplane selects fields in a composite resource or managed resource with a
subset of [JSONPath selectors](https://kubernetes.io/docs/reference/kubectl/jsonpath/),
called "field paths."

Field paths can select any field in a composite resource or managed resource
object, including the `metadata`, `spec` or `status` fields.

Field paths can be a string matching a field name or an array index, in
brackets. Field names may use a `.` character to select child elements.

#### Example field paths
Here are some example selectors from a composite resource object.
{{<table "table" >}}
| Selector | Selected element |
| --- | --- |
| `kind` | `kind` |
| `metadata.labels['crossplane.io/claim-name']` | `my-example-claim` |
| `spec.desiredRegion` | `eu-north-1` |
| `spec.resourceRefs[0].name` | `my-example-claim-978mh-r6z64` |
{{</table >}}

```yaml {label="select",copy-lines="none"}
$ kubectl get composite -o yaml
apiVersion: example.org/v1alpha1
kind: XExample
metadata:
  # Removed for brevity
  labels:
    crossplane.io/claim-name: my-example-claim
    crossplane.io/claim-namespace: default
    crossplane.io/composite: my-example-claim-978mh
spec:
  desiredRegion: eu-north-1
  field1: field1-text
  resourceRefs:
  - apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    name: my-example-claim-978mh-r6z64
  - apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    name: my-example-claim-978mh-cnlhj
  - apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    name: my-example-claim-978mh-rv5nm
```

## Reuse a patch

You can reuse a patch object on multiple resources by using a PatchSet.

To create a PatchSet, define a `patchSets` object in the function's input.

Each patch inside a PatchSet has a `name` and a list of `patches`.

Apply the PatchSet to a resource with a patch `type: PatchSet`. Set the
`patchSetName` to the `name` of the PatchSet.

```yaml {label="patchset"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
patchSets:
- name: my-patchset
  patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: spec.forProvider.region
resources:
- name: bucket1
  base:
    # Removed for brevity
  patches:
    - type: PatchSet
      patchSetName: my-patchset
- name: bucket2
  base:
    # Removed for brevity
  patches:
    - type: PatchSet
      patchSetName: my-patchset
```

{{<hint "important" >}}
A PatchSet can't contain other PatchSets.

Crossplane ignores any [transforms](#transform-a-patch) or
[policies](#patch-policies) in a PatchSet.
{{< /hint >}}

## Patching between resources

Function Patch and Transform can't directly patch between two composed
resources. For example, generating a network resource and patching the resource
name to a compute resource.

A resource can patch to a user-defined `status` field in the composite resource.
Another resource can then read from that `Status` field to patch a field.

First, define a custom `status` in the composite resource Definition and a
custom field, for example `secondResource`

```yaml {label="xrdPatch",copy-lines="13-17"}
kind: CompositeResourceDefinition
# Removed for brevity.
spec:
  # Removed for brevity.
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            # Removed for brevity.
          status:
              type: object
              properties:
                secondResource:
                  type: string
```

Inside the function input the resource with the source data uses a
`ToCompositeFieldPath` patch to write data to the `status.secondResource` field
in the composite resource.

The destination resource uses a `FromCompositeFieldPath` patch to read data from
the composite resource `status.secondResource` field in the composite resource
and write it to a label named `secondResource` in the managed resource.

```yaml {label="patchBetween",copy-lines="9-11"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    # Removed for brevity
  patches:
    - type: ToCompositeFieldPath
      fromFieldPath: metadata.name
      toFieldPath: status.secondResource
- name: bucket2
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    # Removed for brevity
  patches:
    - type: FromCompositeFieldPath
      fromFieldPath: status.secondResource
      toFieldPath: metadata.labels['secondResource']
```

Describe the composite resource to view the `resources` and the
`status.secondResource` value.

```yaml {label="descCompPatch",copy-lines="none"}
$ kubectl describe composite
Name:         my-example-claim-jp7rx
Spec:
  # Removed for brevity
  Resource Refs:
    Name:         my-example-claim-jp7rx-gfg4m
    # Removed for brevity
    Name:         my-example-claim-jp7rx-fttpj
Status:
  # Removed for brevity
  Second Resource:         my-example-claim-jp7rx-gfg4m
```

Describe the destination managed resource to see the label `secondResource`.

```yaml {label="bucketlabel",copy-lines="none"}
$ kubectl describe bucket
kubectl describe bucket my-example-claim-jp7rx-fttpj
Name:         my-example-claim-jp7rx-fttpj
Labels:       crossplane.io/composite=my-example-claim-jp7rx
              secondResource=my-example-claim-jp7rx-gfg4m
```

## Patch with EnvironmentConfigs

Crossplane uses EnvironmentConfigs to create in-memory data stores. Compositions
can read and write from this data store as part of the patch process.

 EnvironmentConfigs can predefine data that Compositions can use or a composite
 resource can write data to their in-memory environment for other resources to
 read.

<!-- vale off -->
{{< hint "note" >}}
<!-- vale on -->
Read the [EnvironmentConfigs]({{<ref "../concepts/environment-configs" >}}) page
for more information on using EnvironmentConfigs.
{{< /hint >}}

To apply a patch using EnvironmentConfigs, first define which EnvironmentConfigs
to use with
`environment.environmentConfigs`.

<!-- vale Google.Quotes = NO -->
<!-- vale gitlab.SentenceLength = NO -->
<!-- ignore false positive -->
Use either a
[reference]({{<ref "../concepts/managed-resources#matching-by-name-reference" >}})
or a [selector]({{<ref "../concepts/managed-resources#matching-by-selector" >}}) to
identify the EnvironmentConfigs to use.
<!-- vale Google.Quotes = YES -->

```yaml {label="envselect",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
spec:
  environment:
    environmentConfigs:
      - ref:
          name: example-environment
  # Removed for Brevity
```

### Patch a composite resource
To patch between the composite resource and the in-memory environment use
`patches` inside of the `environment`.

Use the `ToCompositeFieldPath` to copy data from the in-memory environment to
the composite resource.

Use the `FromCompositeFieldPath` to copy data from the composite resource to the
in-memory environment.

```yaml {label="xrpatch",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
environment:
  patches:
  - type: ToCompositeFieldPath
    fromFieldPath: tags
    toFieldPath: metadata.labels[envTag]
  - type: FromCompositeFieldPath
    fromFieldPath: metadata.name
    toFieldPath: newEnvironmentKey
```

Individual resources can use any data written to their in-memory environment.

### Patch an individual resource

To patch an individual resource, inside the `patches` of the resource, use
`ToEnvironmentFieldPath` to copy data from the resource to the in-memory
environment.

Use `FromEnvironmentFieldPath` to copy data to the resource from the in-memory
environment.

```yaml {label="envpatch",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: vpc
  base:
    apiVersion: ec2.aws.upbound.io/v1beta1
    kind: VPC
    spec:
      forProvider:
        cidrBlock: 172.16.0.0/16
  patches:
  - type: ToEnvironmentFieldPath
    fromFieldPath: status.atProvider.id
    toFieldPath: vpcId
  - type: FromEnvironmentFieldPath
    fromFieldPath: tags
    toFieldPath: spec.forProvider.tags
```

The [EnvironmentConfigs]({{<ref "../concepts/environment-configs" >}}) page has
more information on EnvironmentConfigs options and usage.

## Types of patches
Function Patch and Transform supports multiple patch types, each using a
different source for data and applying the patch to a different location.

Summary of Crossplane patches
{{< table "table table-hover" >}}
| Patch Type | Data Source | Data Destination |
| ---  | --- | --- |
| [FromCompositeFieldPath](#fromcompositefieldpath) | A field in the composite resource. | A field in the composed resource. |
| [ToCompositeFieldPath](#tocompositefieldpath) | A field in the composed resource. | A field in the composite resource. |
| [CombineFromComposite](#combinefromcomposite) | Multiple fields in the composite resource. | A field in the composed resource. |
| [CombineToComposite](#combinetocomposite) | Multiple fields in the composed resource. | A field in the composite resource. |
| [FromEnvironmentFieldPath](#fromenvironmentfieldpath) | Data in the in-memory environment | A field in the composed resource. |
| [ToEnvironmentFieldPath](#toenvironmentfieldpath) | A field in the composed resource. | The in-memory environment. |
| [CombineFromEnvironment](#combinefromenvironment) | Multiple fields in the in-memory environment. | A field in the composed resource. |
| [CombineToEnvironment](#combinetoenvironment) | Multiple fields in the composed resource. | A field in the in-memory environment. |
{{< /table >}}

{{<hint "note" >}}
All the following examples use the same set of Compositions,
CompositeResourceDefinitions, Claims and EnvironmentConfigs.
Only the applied patches change between examples.

All examples rely on
[provider-aws-s3](https://github.com/crossplane-contrib/provider-upjet-aws)
to create resources.

{{< expand "Reference Composition" >}}
```yaml {copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: xExample
  environment:
    environmentConfigs:
    - ref:
        name: example-environment
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: bucket1
        base:
          apiVersion: s3.aws.upbound.io/v1beta1
          kind: Bucket
          spec:
            forProvider:
              region: us-east-2
      - name: bucket2
        base:
          apiVersion: s3.aws.upbound.io/v1beta1
          kind: Bucket
          spec:
            forProvider:
              region: us-east-2
```
{{< /expand >}}

{{<expand "Reference CompositeResourceDefinition" >}}
```yaml {copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xexamples.example.org
spec:
  group: example.org
  names:
    kind: xExample
    plural: xexamples
  claimNames:
    kind: ExampleClaim
    plural: exampleclaims
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
              field1:
                type: string
              field2:
                type: string
              field3:
                type: string
              desiredRegion:
                type: string
              boolField:
                type: boolean
              numberField:
                type: integer
          status:
              type: object
              properties:
                url:
                  type: string
```
{{< /expand >}}


{{< expand "Reference Claim" >}}
```yaml {copy-lines="all"}
apiVersion: example.org/v1alpha1
kind: ExampleClaim
metadata:
  name: my-example-claim
spec:
  field1: "field1-text"
  field2: "field2-text"
  desiredRegion: "eu-north-1"
  boolField: false
  numberField: 10
```
{{< /expand >}}

{{< expand "Reference EnvironmentConfig" >}}
```yaml {copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1beta1
kind: EnvironmentConfig
metadata:
  name: example-environment
data:
  locations:
    us: us-east-2
    eu: eu-north-1
  key1: value1
  key2: value2

```
{{< /expand >}}
{{< /hint >}}

<!-- vale Google.Headings = NO -->
### FromCompositeFieldPath
<!-- vale Google.Headings = YES -->

The `FromCompositeFieldPath` patch takes a value in a composite resource and
applies it to a field in the composed resource.

{{< hint "tip" >}}
Use the `FromCompositeFieldPath` patch to apply options from users in their
Claims to settings in managed resource `forProvider` settings.
{{< /hint >}}

For example, to use the value `desiredRegion` provided by a user in a composite
resource to a managed resource's `region`.

The `fromFieldPath` value is a field in the composite resource.

The `toFieldPath` value is the field in the composed resource to change.

```yaml {label="fromComposite",copy-lines="9-11"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
  patches:
    - type: FromCompositeFieldPath
      fromFieldPath: spec.desiredRegion
      toFieldPath: spec.forProvider.region
```

View the managed resource to see the updated `region`

```yaml {label="fromCompMR",copy-lines="1"}
$ kubectl describe bucket
Name:         my-example-claim-qlr68-29nqf
# Removed for brevity
Spec:
  For Provider:
    Region:  eu-north-1
```

<!-- vale Google.Headings = NO -->
### ToCompositeFieldPath
<!-- vale Google.Headings = YES -->

The `ToCompositeFieldPath` writes data from an individual composed resource to
the composite resource that created it.

{{< hint "tip" >}}
Use `ToCompositeFieldPath` patches to take data from one composed resource in a
Composition and use it in a second composed resource in the same Composition.
{{< /hint >}}

For example, after Crossplane creates a new managed resource, take the value
`hostedZoneID` and apply it as a `label` in the composite resource.

```yaml {label="toComposite",copy-lines="9-11"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
  patches:
    - type: ToCompositeFieldPath
      fromFieldPath: status.atProvider.hostedZoneId
      toFieldPath: metadata.labels['ZoneID']
```

View the created managed resource to see the
`Hosted Zone Id` field.
```yaml {label="toCompMR",copy-lines="none"}
$ kubectl describe bucket
Name:         my-example-claim-p5pxf-5vnp8
# Removed for brevity
Status:
  At Provider:
    Hosted Zone Id:       Z2O1EMRO9K5GLX
    # Removed for brevity
```

Next view the composite resource and confirm the patch applied the `label`

```yaml {label="toCompositeXR",copy-lines="none"}
$ kubectl describe composite
Name:         my-example-claim-p5pxf
Labels:       ZoneID=Z2O1EMRO9K5GLX
```

<!-- vale Google.Headings = NO -->
### CombineFromComposite
<!-- vale Google.Headings = YES -->

The `CombineFromComposite` patch takes values from the composite resource,
combines them and applies them to the composed resource.

{{< hint "tip" >}}
Use the `CombineFromComposite` patch to create complex strings, like security
policies and apply them to a composed resource.
{{< /hint >}}

For example, use the Claim value `desiredRegion` and `field2` to generate the
managed resource's `name`

The `CombineFromComposite` patch only supports the `combine` option.

The `variables` are the list of `fromFieldPath` values from the composite
resource to combine.

The only supported `strategy` is `strategy: string`.

Optionally you can apply a `string.fmt`, based on
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the
strings.

The `toFieldPath` is the field in the composed resource to apply the new string
to.

```yaml {label="combineFromComp",copy-lines="11-20"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
  patches:
    - type: CombineFromComposite
      combine:
        variables:
          - fromFieldPath: spec.desiredRegion
          - fromFieldPath: spec.field2
        strategy: string
        string:
          fmt: "my-resource-%s-%s"
      toFieldPath: metadata.name
```

Describe the managed resource to see the applied patch.

```yaml {label="describeCombineFromComp",copy-lines="none"}
$ kubectl describe bucket
Name:         my-resource-eu-north-1-field2-text
```

<!-- vale Google.Headings = NO -->
### CombineToComposite
<!-- vale Google.Headings = YES -->

The `CombineToComposite` patch takes values from the composed resource, combines
them and applies them to the composite resource.

{{<hint "tip" >}}
Use `CombineToComposite` patches to create a single field like a URL from
multiple fields in a managed resource.
{{< /hint >}}

For example, use the managed resource `name` and `region` to generate a custom
`url` field.

{{< hint "important" >}}
Writing custom fields in the status field of a composite resource requires
defining the custom fields in the CompositeResourceDefinition first.
{{< /hint >}}

The `CombineToComposite` patch only supports the `combine` option.

The `variables` are the list of `fromFieldPath` the managed resource to combine.

The only supported `strategy` is `strategy: string`.

Optionally you can apply a `string.fmt`, based on
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the
strings.

The `toFieldPath` is the field in the composite resource to apply the new string
to.

```yaml {label="combineToComposite",copy-lines="9-11"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
  patches:
    - type: CombineToComposite
      combine:
        variables:
          - fromFieldPath: metadata.name
          - fromFieldPath: spec.forProvider.region
        strategy: string
        string:
          fmt: "https://%s.%s.com"
      toFieldPath: status.url
```

View the composite resource to verify the applied patch.

```yaml {copy-lines="none"}
$ kubectl describe composite
Name:         my-example-claim-bjdjw
API Version:  example.org/v1alpha1
Kind:         xExample
# Removed for brevity
Status:
  # Removed for brevity
  URL:                     https://my-example-claim-bjdjw-r6ncd.us-east-2.com
```

<!-- vale Google.Headings = NO -->
### FromEnvironmentFieldPath
<!-- vale Google.Headings = YES -->

{{<hint "important" >}}
EnvironmentConfigs are an alpha feature. They aren't enabled by default.

For more information about using an EnvironmentConfig, read the
[EnvironmentConfigs documentation]({{<ref "../concepts/environment-configs">}}).
{{< /hint >}}

The `FromEnvironmentFieldPath` patch takes values from the in-memory environment
and applies them to the composed resource.

{{<hint "tip" >}}
Use `FromEnvironmentFieldPath` to apply custom managed resource settings based
on the current environment.
{{< /hint >}}

For example, use the environment's `locations.eu` value and apply it as the
`region`.

```yaml {label="fromEnvField",copy-lines="9-11"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
    patches:
    - type: FromEnvironmentFieldPath
      fromFieldPath: locations.eu
      toFieldPath: spec.forProvider.region
```

Verify managed resource to confirm the applied patch.

```yaml {copy-lines="none"}
kubectl describe bucket
Name:         my-example-claim-8vrvc-xx5sr
Labels:       crossplane.io/claim-name=my-example-claim
# Removed for brevity
Spec:
  For Provider:
    Region:  eu-north-1
  # Removed for brevity
```

<!-- vale Google.Headings = NO -->
### ToEnvironmentFieldPath
<!-- vale Google.Headings = YES -->

{{<hint "important" >}}
For more information about using an EnvironmentConfig, read the
[EnvironmentConfigs documentation]({{<ref "../concepts/environment-configs">}}).
{{< /hint >}}

The `ToEnvironmentFieldPath` patch takes a value from the composed resource and
applies it to the in-memory environment.

{{<hint "tip" >}}
Use `ToEnvironmentFieldPath` to write data to the environment that any
FromEnvironmentFieldPath patch can access.
{{< /hint >}}

For example, use the desired `region` value and apply it as the environment's
`key1`.


```yaml {label="toEnvField",copy-lines="9-11"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
    patches:
    - type: ToEnvironmentFieldPath
      fromFieldPath: spec.forProvider.region
      toFieldPath: key1
```

Because the environment is in-memory, there is no command to confirm the patch
wrote the value to the environment.


<!-- vale Google.Headings = NO -->
### CombineFromEnvironment
<!-- vale Google.Headings = YES -->

{{<hint "important" >}}
For more information about using an EnvironmentConfig, read the
[EnvironmentConfigs documentation]({{<ref "../concepts/environment-configs">}}).
{{< /hint >}}

The `CombineFromEnvironment` patch combines multiple values from the in-memory
environment and applies them to the composed resource.

{{<hint "tip" >}}
Use `CombineFromEnvironment` patch to create complex strings, like security
policies and apply them to a managed resource.
{{< /hint >}}

For example, combine multiple fields in the environment to create a unique
`annotation` .

The `CombineFromEnvironment` patch only supports the `combine` option.

The only supported `strategy` is `strategy: string`.

The `variables` are the list of `fromFieldPath` values from the in-memory
environment to combine.

Optionally you can apply a `string.fmt`, based on
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the
strings.

The `toFieldPath` is the field in the composed resource to apply the new string
to.

```yaml {label="combineFromEnv",copy-lines="11-20"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
  patches:
    - type: CombineFromEnvironment
      combine:
        strategy: string
        variables:
        - fromFieldPath: key1
        - fromFieldPath: key2
        string:
          fmt: "%s-%s"
      toFieldPath: metadata.annotations[EnvironmentPatch]
```

Describe the managed resource to see new
`annotation`.

```yaml {copy-lines="none",label="combineFromEnvDesc"}
$ kubectl describe bucket
Name:         my-example-claim-zmxdg-grl6p
# Removed for brevity
Annotations:  EnvironmentPatch: value1-value2
# Removed for brevity
```

<!-- vale Google.Headings = NO -->
### CombineToEnvironment
<!-- vale Google.Headings = YES -->

{{<hint "important" >}}
For more information about using an EnvironmentConfig, read the
[EnvironmentConfigs documentation]({{<ref "../concepts/environment-configs">}}).
{{< /hint >}}

The `CombineToEnvironment` patch combines multiple values from the composed
resource and applies them to the in-memory EnvironmentConfig environment.

{{<hint "tip" >}}
Use `CombineToEnvironment` patch to create complex strings, like security
policies to use in other managed resources.
{{< /hint >}}

For example, combine multiple fields in the managed resource to create a unique
string and store it in the environment's `key2` value.

The string combines the managed resource `Kind` and `region`.

The `CombineToEnvironment` patch only supports the `combine` option.

The only supported `strategy` is `strategy: string`.

The `variables` are the list of `fromFieldPath` values in the managed resource
to combine.

Optionally you can apply a `string.fmt`, based on
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the
strings.

The `toFieldPath` is the key in the environment to write the new string to.

```yaml {label="combineToEnv",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
  patches:
    - type: CombineToEnvironment
      combine:
        strategy: string
        variables:
        - fromFieldPath: kind
        - fromFieldPath: spec.forProvider.region
        string:
          fmt: "%s.%s"
      toFieldPath: key2
```

Because the environment is in-memory, there is no command to confirm the patch
wrote the value to the environment.

## Transform a patch

When applying a patch, Crossplane supports modifying the data before applying it
as a patch. Crossplane calls this a "transform" operation.

Summary of Crossplane transforms.
{{< table "table table-hover" >}}
| Transform Type | Action |
| ---  | --- |
| [convert](#convert-transforms) | Converts an input data type to a different type. Also called "casting." |
| [map](#map-transforms) | Selects a specific output based on a specific input. |
| [match](#match-transform) | Selects a specific output based on a string or regular expression. |
| [math](#math-transforms) | Applies a mathematical operation on the input. |
| [string](#string-transforms) | Change the input string using [Go string formatting](https://pkg.go.dev/fmt). |
{{< /table >}}

Apply a transform directly to an individual patch with the `transforms` field.

A `transform` requires a `type`, indicating the transform action to take.

The other transform field is the same as the `type`, in this example, `map`.

The other fields depend on the patch type used.

This example uses a `type: map` transform, taking the input
`spec.desiredRegion`, matching it to either `us` or `eu` and returning the
corresponding AWS region for the `spec.forProvider.region` value.

```yaml {label="transform1",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: bucket1
  base:
    apiVersion: s3.aws.upbound.io/v1beta1
    kind: Bucket
    spec:
      forProvider:
        region: us-east-2
  patches:
    - type: FromCompositeFieldPath
      fromFieldPath: spec.desiredRegion
      toFieldPath: spec.forProvider.region
      transforms:
        - type: map
          map:
            us: us-east-2
            eu: eu-north-1
```

### Convert transforms

The `convert` transform type changes the input data type to a different data
type.

{{< hint "tip" >}}
Some provider APIs require a field to be a string. Use a `convert` type to
change any boolean or integer fields to strings.
{{< /hint >}}

A `convert` transform requires a `toType`, defining the output data type.

```yaml {label="convert",copy-lines="none"}
patches:
- type: FromCompositeFieldPath
  fromFieldPath: spec.numberField
  toFieldPath: metadata.label["numberToString"]
  transforms:
    - type: convert
      convert:
        toType: string
```

Supported `toType` values:
{{< table "table table-sm table-hover" >}}
| `toType` value | Description |
| -- | -- |
| `bool` | A boolean value of `true` or `false`. |
| `float64` | A 64-bit float value. |
| `int` | A 32-bit integer value. |
| `int64` | A 64-bit integer value. |
| `string` | A string value. |
| `object` | An object. |
| `array` | An array. |
{{< /table >}}

#### Converting strings to booleans
When converting from a string to a `bool` Crossplane considers the string values
`1`, `t`, `T`, `TRUE`, `True` and `true` equal to the boolean value `True`.

The strings `0`, `f`, `F`, `FALSE`, `False` and `false` are equal to the boolean
value `False`.

#### Converting numbers to booleans
Crossplane considers the integer `1` and float `1.0` equal to the boolean value
`True`. Any other integer or float value is `False`.

#### Converting booleans to numbers
Crossplane converts the boolean value `True` to the integer `1` or float64
`1.0`.

The value `False` converts to the integer `0` or float64 `0.0`

#### Converting strings to float64
When converting from a `string` to a `float64` Crossplane supports an optional
`format: quantity` field.

Using `format: quantity` translates size suffixes like `M` for megabyte or `Mi`
for megabit into the correct float64 value.

{{<hint "note" >}}
Refer to the [Go language docs](https://pkg.go.dev/k8s.io/apimachinery/pkg/api/resource#Quantity)
for a full list of supported suffixes.
{{</hint >}}

Add `format: quantity` to the `convert` object to enable quantity suffix
support.

```yaml {label="format",copy-lines="all"}
- type: convert
  convert:
   toType: float64
   format: quantity
```

#### Converting strings to objects

Crossplane converts JSON strings to objects.

Add `format: json` to the `convert` object which is the only supported string
format for this conversion.

```yaml {label="object",copy-lines="all"}
- type: convert
  convert:
   toType: object
   format: json
```

{{< hint "tip" >}}
This conversion is useful for patching keys in an object.
{{< /hint >}}

The following example adds a tag to a resource with a
`customized key`:

```yaml {label="patch-key",copy-lines="all"}
    - type: FromCompositeFieldPath
      fromFieldPath: spec.clusterName
      toFieldPath: spec.forProvider.tags
      transforms:
      - type: string
        string:
          type: Format
          fmt: '{"kubernetes.io/cluster/%s": "true"}'
      - type: convert
        convert:
          toType: object
          format: json
```

#### Converting strings to arrays

Crossplane converts JSON strings to arrays.

Add `format: json` to the `convert` object which is the only supported string
format for this conversion.

```yaml {label="array",copy-lines="all"}
- type: convert
  convert:
   toType: array
   format: json
```

### Map transforms

The `map` transform type _maps_ an input value to an output value.

{{< hint "tip" >}}
The `map` transform is useful for translating generic region names like `US` or
`EU` to provider specific region names.
{{< /hint >}}

The `map` transform compares the value from the `fromFieldPath` to the options
listed in the `map`.

If Crossplane finds the value, Crossplane puts the mapped value in the
`toFieldPath`.

{{<hint "note" >}}
Crossplane throws an error for the patch if the value isn't found.
{{< /hint >}}

`spec.field1` is the string `"field1-text"` then Crossplane uses the string
`firstField` for the `annotation`.

If `spec.field1` is the string `"field2-text"` then Crossplane uses the string
`secondField` for the `annotation`.

```yaml {label="map",copy-lines="none"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["myAnnotation"]
    transforms:
      - type: map
        map:
          "field1-text": "firstField"
          "field2-text": "secondField"
```

In this example, the value of `spec.field1` is `field1-text`.

```yaml {label="comositeMap",copy-lines="none"}
$ kubectl describe composite
Name:         my-example-claim-twx7n
Spec:
  # Removed for brevity
  field1:         field1-text
```

The annotation applied to the managed resource is `firstField`.

```yaml {label="mrMap",copy-lines="none"}
$ kubectl describe bucket
Name:         my-example-claim-twx7n-ndb2f
Annotations:  crossplane.io/composition-resource-name: bucket1
              myAnnotation: firstField
# Removed for brevity.
```

### Match transform

The `match` transform is like the `map` transform.

The `match` transform adds support for regular expressions along with exact
strings and can provide default values if there isn't a match.

A `match` object requires a `patterns` object.

The `patterns` is a list of one or more patterns to attempt to match the input
value against.

```yaml {label="match",copy-lines="1-8"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["myAnnotation"]
    transforms:
      - type: match
        match:
          patterns:
            - type: literal
              # Removed for brevity
            - type: regexp
              # Removed for brevity
```

Match `patterns` can be either `type: literal` to match an exact string or
`type: regexp` to match a regular expression.

{{<hint "note" >}}
Crossplane stops processing matches after the first pattern match.
{{< /hint >}}

#### Match an exact string

Use a `pattern` with
`type: literal` to match an
exact string.

On a successful match Crossplane provides the
`result:` to
the patch `toFieldPath`.

```yaml {label="matchLiteral"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["myAnnotation"]
    transforms:
      - type: match
        match:
          patterns:
            - type: literal
              literal: "field1-text"
              result: "matchedLiteral"
```

#### Match a regular expression

Use a `pattern` with `type: regexp` to match a regular expression.
Define a `regexp` key with the value of the regular expression to match.

On a successful match Crossplane provides the `result:` to the patch
`toFieldPath`.

```yaml {label="matchRegex"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["myAnnotation"]
    transforms:
      - type: match
        match:
          patterns:
            - type: regexp
              regexp: '^field1.*'
              result: "foundField1"
```

#### Using default values

Optionally you can provide a default value to use if there is no matching
pattern.

The default value can either be the original input value or a defined default
value.

Use `fallbackTo: Value` to provide a default value if a match isn't found.

For example if the string `unknownString` isn't matched, Crossplane provides the
`Value` `StringNotFound` to the `toFieldPath`

```yaml {label="defaultValue"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["myAnnotation"]
    transforms:
      - type: match
        match:
          patterns:
            - type: literal
              literal: "UnknownString"
              result: "foundField1"
          fallbackTo: Value
          fallbackValue: "StringNotFound"
```

To use the original input as the fallback value use `fallbackTo: Input`.

Crossplane uses the original `fromFieldPath` input for the `toFieldPath` value.

```yaml {label="defaultInput"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["myAnnotation"]
    transforms:
      - type: match
        match:
          patterns:
            - type: literal
              literal: "UnknownString"
              result: "foundField1"
          fallbackTo: Input
```

### Math transforms

Use the `math` transform to multiply an input or apply a minimum or maximum
value.

{{<hint "important">}}
A `math` transform only supports integer inputs.
{{< /hint >}}

```yaml {label="math",copy-lines="1-7"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.numberField
    toFieldPath: metadata.annotations["mathAnnotation"]
    transforms:
      - type: math
        math:
          ...
```

<!-- vale Google.Headings = NO -->
#### clampMin
<!-- vale Google.Headings = YES -->

The `type: clampMin` uses a defined minimum value if an input is larger than the
`type: clampMin` value.

For example, this `type: clampMin` requires an input to be greater than `20`.

If an input is lower than `20`, Crossplane uses the `clampMin` value for the
`toFieldPath`.

```yaml {label="clampMin"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.numberField
    toFieldPath: metadata.annotations["mathAnnotation"]
    transforms:
      - type: math
        math:
          type: clampMin
          clampMin: 20
```

<!-- vale Google.Headings = NO -->
#### clampMax
<!-- vale Google.Headings = YES -->

The `type: clampMax` uses a defined minimum value if an input is larger than the
`type: clampMax` value.

For example, this `type: clampMax` requires an input to be less than `5`.

If an input is higher than `5`, Crossplane uses the `clampMax` value for the
`toFieldPath`.

```yaml {label="clampMax"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.numberField
    toFieldPath: metadata.annotations["mathAnnotation"]
    transforms:
      - type: math
        math:
          type: clampMax
          clampMax: 5
```

<!-- vale Google.Headings = NO -->
#### Multiply
<!-- vale Google.Headings = YES -->

The `type: multiply` multiplies the input by the `multiply` value.

For example, this `type: multiply` multiplies the value from the `fromFieldPath`
value by `2`

```yaml {label="multiply"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.numberField
    toFieldPath: metadata.annotations["mathAnnotation"]
    transforms:
      - type: math
        math:
          type: multiply
          multiply: 2
```

{{<hint "note" >}}
The `multiply` value only supports integers.
{{< /hint >}}

### String transforms

The `string` transform applies string formatting or manipulation to string
inputs.

```yaml {label="string"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["stringAnnotation"]
    transforms:
      - type: string
        string:
          type: ...
```

String transforms support the following
`types`

* [Convert](#string-convert)
* [Format](#string-format)
* [Join](#join)
* [Regexp](#regular-expression-type)
* [TrimPrefix](#trim-prefix)
* [TrimSuffix](#trim-suffix)

#### String convert

The `type: convert`
converts the input based on one of the following conversion types:
* `ToUpper` - Change the string to all upper case letters.
* `ToLower` - Change the string to all lower case letters.
* `ToBase64` - Create a new base64 string from the input.
* `FromBase64` - Create a new text string from a base64 input.
* `ToJson` - Convert the input string to valid JSON.
* `ToSha1` - Create a SHA-1 hash of the input string.
* `ToSha256` - Create a SHA-256 hash of the input string.
* `ToSha512` - Create a SHA-512 hash of the input string.
* `ToAdler32` - Create an Adler32 hash of the input string.

```yaml {label="stringConvert"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["FIELD1-TEXT"]
    transforms:
      - type: string
        string:
          type: Convert
          convert: "ToUpper"
```

#### String format

The `type: format` applies [Go string formatting](https://pkg.go.dev/fmt) to the
input.

```yaml {label="typeFormat"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.field1
    toFieldPath: metadata.annotations["stringAnnotation"]
    transforms:
      - type: string
        string:
          type: Format
          fmt: "the-field-%s"
```

#### Join

The `type: Join` joins all values in the input array into a string using the
given separator.

This transform only works with array inputs.

```yaml {label="typeJoin"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.parameters.inputList
    toFieldPath: spec.targetJoined
    transforms:
      - type: string
        string:
          type: Join
          join:
            separator: ","
```

#### Regular expression type

The `type: Regexp` extracts the part of the input matching a regular expression.

Optionally use a `group` to match a regular expression capture group.
By default Crossplane matches the entire regular expression.

```yaml {label="typeRegex"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: metadata.annotations["euRegion"]
    transforms:
      - type: string
        string:
          type: Regexp
          regexp:
            match: '^eu-(.*)-'
            group: 1
```

#### Trim prefix

The `type: TrimPrefix` uses
Go's [TrimPrefix](https://pkg.go.dev/strings#TrimPrefix) and removes characters
from the beginning of a line.

```yaml {label="typeTrimP"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: metadata.annotations["north-1"]
    transforms:
      - type: string
        string:
          type: TrimPrefix
          trim: `eu-
```

#### Trim suffix

The `type: TrimSuffix` uses
Go's [TrimSuffix](https://pkg.go.dev/strings#TrimSuffix) and removes characters
from the end of a line.

```yaml {label="typeTrimS"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: metadata.annotations["eu"]
    transforms:
      - type: string
        string:
          type: TrimSuffix
          trim: `-north-1'
```

#### Replace

The `type: Replace` replaces all occurrences of the `search` string with the `replace` string. If `replace` is an empty string, then the `search` string is removed.


```yaml {label="typeReplace"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.location
    toFieldPath: spec.forProvider.region
    transforms:
      - type: string
        string:
          type: Replace
          replace:
            search: "europe"
            replace: "eu"
```

## Patch policies

Crossplane supports two types of patch policies:
* `fromFieldPath`
* `toFieldPath`

<!-- vale Google.Headings = NO -->
### fromFieldPath policy
<!-- vale Google.Headings = YES -->

Using a `fromFieldPath: Required` policy on a patch requires the `fromFieldPath`
to exist in the data source resource.

{{<hint "tip" >}}
If a resource patch isn't working applying the `fromFieldPath: Required` policy
may produce an error in the composite resource to help troubleshoot.
{{< /hint >}}

By default, Crossplane applies the policy `fromFieldPath: Optional`. With
`fromFieldPath: Optional` Crossplane ignores a patch if the `fromFieldPath`
doesn't exist.

With `fromFieldPath: Required` the composite resource produces an error if the
`fromFieldPath` doesn't exist.

```yaml {label="required"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: metadata.annotations["eu"]
    policy:
      fromFieldPath: Required
```

<!-- vale Google.Headings = NO -->
### toFieldPath policy
<!-- vale Google.Headings = YES -->

By default when applying a patch the function replaces the destination data. Use
`toFieldPath` to allow patches to merge arrays and objects without overwriting
them.

The `toFieldPath` policy supports these options:
{{< table "table table-hover" >}}
| Policy | Action |
| ---  | --- |
| `Replace` (default) | Replace the value at `toFieldPath`. |
| `MergeObjects` | Recursively merge into the value at `toFieldPath`. Keep any conflicting object keys. |
| `ForceMergeObjects` | Recursively merge into the value at `toFieldPath`. Replace any conflicting object keys. |
| `MergeObjectsAppendArrays` | Like `MergeObjects`, but append values to arrays instead of replacing them. |
| `ForceMergeObjectsAppendArrays` | Like `ForceMergeObjects`, but append values to arrays instead of replacing them. |
{{< /table >}}

```yaml {label="merge"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: metadata.annotations["eu"]
    policy:
      toFieldPath: MergeObjectsAppendArrays
```

## Composite resource connection details

Function patch and Transform must define the specific secret keys a resource
creates with the `connectionDetails` object.

{{<table "table table-sm" >}}
| Secret Type | Description |
| --- | --- |
| `FromConnectionSecretKey` | Create a secret key matching the key of a secret generated by the resource. |
| `FromFieldPath`  | Create a secret key matching a field path of the resource. |
| `FromValue`  | Create a secret key with a predefined value. |
{{< /table >}}

{{<hint "note">}}
The `value` type must use a string value.

The `value` isn't added to the individual resource secret object. The `value`
only appears in the combined composite resource secret.
{{< /hint >}}

```yaml {label="conDeet",copy-lines="none"}
kind: Composition
spec:
  writeConnectionSecretsToNamespace: other-namespace
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: key
        base:
          # Removed for brevity
          spec:
            forProvider:
            # Removed for brevity
            writeConnectionSecretToRef:
              namespace: docs
              name: key1
        connectionDetails:
          - name: my-username
            type: FromConnectionSecretKey
            fromConnectionSecretKey: username
          - name: my-field-secret
            type: FromFieldPath
            fromFieldPath: spec.forProvider.user
          - name: my-status-secret
            type: FromValue
            value: "docs.crossplane.io"
```

The `connectionDetails` in a resource can reference a secret from a resource
with `FromConnectionSecretKey`, from another field in the resource with
`FromFieldPath` or a statically defined value with `FromValue`.

Crossplane sets the secret key to the `name` value.

Describe the secret to view the secret keys inside the secret object.

{{<hint "tip" >}}
If more than one resource generates secrets with the same secret key name,
Crossplane only saves one value.

Use a custom `name` to create unique secret keys.
{{< /hint >}}

{{<hint "important">}}
Crossplane only adds connection details listed in the `connectionDetails` to the
combined secret object.

Any connection secrets in a managed resource, not defined in the
`connectionDetails` aren't added to the combined secret object.
{{< /hint >}}


```shell {copy-lines="1"}
kubectl describe secret
Name:         my-access-key-secret
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  connection.crossplane.io/v1alpha1

Data
====
myUsername:      20 bytes
myFieldSecret:   24 bytes
myStaticSecret:  18 bytes
```

{{<hint "note" >}}
The CompositeResourceDefinition can also limit which keys Crossplane stores from
the composite resources.

By default an XRD writes all secret keys listed in the composed resources
`connectionDetails` to the combined secret object.

Read the
[CompositeResourceDefinition documentation]({{<ref "../concepts/composite-resource-definitions#manage-connection-secrets">}})
for more information on restricting secret keys.
{{< /hint >}}

For more information on connection secrets read the
[Connection Secrets concepts age]({{<ref "../concepts/connection-details">}}).

## Resource readiness checks

By default Crossplane considers a composite resource or Claim as `READY` when
the status of all created resource are `Type: Ready` and `Status: True`

Some resources, for example, a ProviderConfig, don't have a Kubernetes status
and are never considered `Ready`.

Custom readiness checks allow Compositions to define what custom conditions to
meet for a resource to be `Ready`.

{{< hint "tip" >}}
Use multiple readiness checks if a resource must meet multiple conditions for it
to be `Ready`.
{{< /hint >}}

<!-- vale Google.WordList = NO -->
Define a custom readiness check with the `readinessChecks` field on a resource.
<!-- vale Google.WordList = YES -->

Checks have a `type` defining how to match the resource and a `fieldPath` of
which field in the resource to compare.

```yaml {label="check",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: <match type>
      fieldPath: <resource field>
```

Compositions support matching resource fields by:
 * [string match](#match-a-string)
 * [integer match](#match-an-integer)
 * [non-empty match](#match-that-a-field-exists)
 * [always ready](#always-consider-a-resource-ready)
 * [condition match](#match-a-condition)
 * [boolean match](#match-a-boolean)

### Match a string

`MatchString` considers the composed resource to be ready when the value of a
field in that resource matches a specified string.

{{<hint "note" >}}
<!-- vale Google.WordList = NO -->
Crossplane only supports exact string matches. Substrings and regular
expressions aren't supported in a readiness check.
<!-- vale Google.WordList = YES -->
{{</hint >}}


For example, matching the string `Online` in the resource's
`status.atProvider.state` field.

```yaml {label="matchstring",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: MatchString
      fieldPath: status.atProvider.state
      matchString: "Online"
```

### Match an integer

`MatchInteger` considers the composed resource to be ready when the value of a
field in that resource matches a specified integer.

{{<hint "note" >}}
<!-- vale Google.WordList = NO -->
Crossplane doesn't support matching `0`.
<!-- vale Google.WordList = YES -->
{{</hint >}}

For example, matching the number `4` in the resource's `status.atProvider.state`
field.

```yaml {label="matchint",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: MatchInteger
      fieldPath: status.atProvider.state
      matchInteger: 4
```

### Match that a field exists
`NonEmpty` considers the composed resource to be ready when a field exists with
a value.

{{<hint "note" >}}
<!-- vale Google.WordList = NO -->
Crossplane considers a value of `0` or an empty string as empty.
{{</hint >}}

For example, to check that a resource's `status.atProvider.state` field isn't
empty.
<!-- vale Google.WordList = YES -->

```yaml {label="NonEmpty",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: NonEmpty
      fieldPath: status.atProvider.state
```

{{<hint "tip" >}}
Checking `NonEmpty` doesn't
require setting any other fields.
{{< /hint >}}

### Always consider a resource ready
`None` considers the composed resource to be ready as soon as it's created.
Crossplane doesn't wait for any other conditions before declaring the resource
ready.

For example, consider `my-resource` ready as soon as it's created.


```yaml {label="none",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: None
```

### Match a condition
`Condition` considers the composed resource to be ready when it finds the
expected condition type, with the expected status for it in its
`status.conditions`.

For example, consider `my-resource`, which is ready if there is a condition of
type `MyType` with a status of `Success`.

```yaml {label="condition",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: MatchCondition
      matchCondition:
        type: MyType
        status: Success
```

### Match a boolean

Two types of checks exist for matching boolean fields:
 * `MatchTrue`
 * `MatchFalse`

`MatchTrue` considers the composed resource to be ready when the value of a
field inside that resource is `true`.

`MatchFalse` considers the composed resource to be ready when the value of a
field inside that resource is `false`.

For example, consider
`my-resource`, which is
ready if
` status.atProvider.manifest.status.ready`
is `true`.

```yaml {label="matchTrue",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: MatchTrue
      fieldPath: status.atProvider.manifest.status.ready
```
{{<hint "tip" >}}
Checking `MatchTrue` doesn't
require setting any other fields.
{{< /hint >}}

`MatchFalse` matches fields that express readiness with the value `false`.

For example, consider `my-resource`, is ready if `
status.atProvider.manifest.status.pending` is `false`.

```yaml {label="matchFalse",copy-lines="none"}
apiVersion: pt.fn.crossplane.io/v1beta1
kind: Resources
resources:
- name: my-resource
  base:
    # Removed for brevity
  readinessChecks:
    - type: MatchFalse
      fieldPath: status.atProvider.manifest.status.pending
```

{{<hint "tip" >}}
Checking `MatchFalse` doesn't require setting any other fields.
{{< /hint >}}
