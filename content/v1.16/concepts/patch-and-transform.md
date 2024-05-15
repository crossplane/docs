---
title: Patch and Transforms
weight: 70
description: "Crossplane Compositions use patches and transforms to modify inputs from claims and composite resources before creating managed resources"
---

Crossplane Compositions allow for "patch and transform" operations. With patches
a Composition can apply changes to the resources defined by the Composition. 

When users create Claims, Crossplane passes the settings in the Claim to
the associated composite resource. Patches can use these settings to change the
associated composite resource or managed resources. 

Examples of using patch and transforms include:
 * changing the name of the external resource
 * mapping generic terms like "east" or "west" to specific provider locations
 * appending custom labels or strings to resource fields


{{<hint "note" >}}
<!-- vale alex.Condescending = NO -->
Crossplane expects patch and transform operations to be simple changes.  
Use [Composition Functions]({{<ref "./composition-functions">}}) for more
complex or programmatic modifications.
<!-- vale  alex.Condescending = YES -->
{{</hint >}}


A Composition [patch](#create-a-patch) is the action of changing a field.  
A Composition [transform](#transform-a-patch) modifies the values before 
applying the patch.

## Create a patch

Patches are part of an individual 
{{<hover label="createComp" line="4">}}resource{{</hover>}} inside a 
{{<hover label="createComp" line="2">}}Composition{{</hover>}}.

The {{<hover label="createComp" line="8">}}patches{{</hover>}} field takes a
list of patches to apply to the individual resource. 

Each patch has a {{<hover label="createComp" line="9">}}type{{</hover>}}, which
defines what kind of patch action Crossplane applies. 

Patches reference fields inside a composite resource or Composition differently
depending on the patch type, but all patches reference a 
{{<hover label="createComp" line="10">}}fromFieldPath{{</hover>}} and
{{<hover label="createComp" line="11">}}toFieldPath{{</hover>}}.

The {{<hover label="createComp" line="10">}}fromFieldPath{{</hover>}} defines
the patch's input values. 
The {{<hover label="createComp" line="11">}}toFieldPath{{</hover>}} defines the
data to change with a patch.

Here is an example patch applied to a resource in a Composition. 
```yaml {label="createComp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
spec:
  resources:
    - name: my-composed-resource
      base:
        # Removed for brevity
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.field1
          toFieldPath: metadata.labels["patchLabel"]
```

### Selecting fields

Crossplane selects fields in a composite resource or managed
resource with
a subset of 
[JSONPath selectors](https://kubernetes.io/docs/reference/kubectl/jsonpath/),
called "field selectors."

Field selectors can select any field in a composite resource or managed resource 
object, including the `metadata`, `spec` or `status` fields. 

Field selectors can be a string matching a field name or an array index, in
brackets. Field names may use a `.` character to select child elements.

#### Example field selectors
Here are some example selectors from a composite resource object.
{{<table "table" >}}
| Selector | Selected element | 
| --- | --- |
| `kind` | {{<hover label="select" line="3">}}kind{{</hover>}} |
| `metadata.labels['crossplane.io/claim-name']` | {{<hover label="select" line="7">}}my-example-claim{{</hover>}} |
| `spec.desiredRegion` | {{<hover label="select" line="11">}}eu-north-1{{</hover>}} |
| `spec.resourceRefs[0].name` | {{<hover label="select" line="16">}}my-example-claim-978mh-r6z64{{</hover>}} |
{{</table >}}

```yaml {label="select",copy-lines="none"}
$ kubectl get composite -o yaml
apiVersion: example.org/v1alpha1
kind: xExample
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
  # Removed for brevity
```

## Reuse a patch

A Composition can reuse a patch object on multiple resources with a 
PatchSet.

To create a PatchSet, define a 
{{<hover label="patchset" line="5">}}PatchSets{{</hover>}} object inside the 
Composition's
{{<hover label="patchset" line="4">}}spec{{</hover>}}. 

Each patch inside a PatchSet has a 
{{<hover label="patchset" line="6">}}name{{</hover>}} and a list of
{{<hover label="patchset" line="7">}}patches{{</hover>}}.  

{{<hint "note" >}}
For multiple PatchSets only use a single 
{{<hover label="patchset" line="5">}}PatchSets{{</hover>}} object.  

Identify each unique PatchSet with a unique 
{{<hover label="patchset" line="6">}}name{{</hover>}}.
{{</hint >}}

Apply the PatchSet to a resource with a patch
{{<hover label="patchset" line="16">}}type: PatchSet{{</hover>}}.  
Set the 
{{<hover label="patchset" line="17">}}patchSetName{{</hover>}} to the 
{{<hover label="patchset" line="6">}}name{{</hover>}} of the PatchSet.

```yaml {label="patchset"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
spec:
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

Compositions can't directly patch between resources in the same Composition.  
For example, generating a network resource and patching the resource name to 
a compute resource. 

{{<hint "important">}}
The [ToEnvironmentFieldPath](#toenvironmentfieldpath) patch can't read from a
`Status` field.
{{< /hint >}}

A resource can patch to a user-defined 
{{<hover label="xrdPatch" line="13">}}Status{{</hover>}}
field in the composite resource.

A resource can then read from that 
{{<hover label="xrdPatch" line="13">}}Status{{</hover>}} 
field to patch a field. 

First, define a custom
{{<hover label="xrdPatch" line="13">}}Status{{</hover>}}
in the Composite Resource Definition and a custom field, for example
{{<hover label="xrdPatch" line="16">}}secondResource{{</hover>}}

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

Inside the Composition the resource with the source data uses a
{{<hover label="patchBetween" line="10">}}ToCompositeFieldPath{{</hover>}}
patch to write data to the 
{{<hover label="patchBetween" line="12">}}status.secondResource{{</hover>}} 
field in the composite resource. 

The destination resource uses a 
{{<hover label="patchBetween" line="19">}}FromCompositeFieldPath{{</hover>}}
patch to read data from the composite resource
{{<hover label="patchBetween" line="20">}}status.secondResource{{</hover>}} 
field in the composite resource and write it to a label named 
{{<hover label="patchBetween" line="21">}}secondResource{{</hover>}} in the
managed resource.

```yaml {label="patchBetween",copy-lines="9-11"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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

Describe the composite resource to view the 
{{<hover label="descCompPatch" line="5">}}resources{{</hover>}} and the 
{{<hover label="descCompPatch" line="11">}}status.secondResource{{</hover>}}
value. 

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

Describe the destination managed resource to see the label 
{{<hover label="bucketlabel" line="5">}}secondResource{{</hover>}}.

```yaml {label="bucketlabel",copy-lines="none"}
$ kubectl describe bucket
kubectl describe bucket my-example-claim-jp7rx-fttpj
Name:         my-example-claim-jp7rx-fttpj
Labels:       crossplane.io/composite=my-example-claim-jp7rx
              secondResource=my-example-claim-jp7rx-gfg4m
```

## Types of patches
Crossplane supports multiple patch types, each using a different source for data
and applying the patch to a different location. 

{{<hint "important" >}}

This section describes patches applied to individual resources inside a
Composition.  

For information about applying patches to an entire composite resource with a
Composition's `environment.patches` read the 
[Environment Configurations]({{<ref "environment-configs" >}}) documentation.

{{< /hint >}}

Summary of Crossplane patches
{{< table "table table-hover" >}}
| Patch Type | Data Source | Data Destination | 
| ---  | --- | --- | 
| [FromCompositeFieldPath](#fromcompositefieldpath) | A field in the composite resource. | A field in the patched managed resource. | 
| [ToCompositeFieldPath](#tocompositefieldpath) | A field in the patched managed resource. | A field in the composite resource. |  
| [CombineFromComposite](#combinefromcomposite) | Multiple fields in the composite resource. | A field in the patched managed resource. | 
| [CombineToComposite](#combinetocomposite) | Multiple fields in the patched managed resource. | A field in the composite resource. | 
| [FromEnvironmentFieldPath](#fromenvironmentfieldpath) | Data in the in-memory EnvironmentConfig Environment | A field in the patched managed resource. | 
| [ToEnvironmentFieldPath](#toenvironmentfieldpath) | A field in the patched managed resource. | The in-memory EnvironmentConfig Environment. | 
| [CombineFromEnvironment](#combinefromenvironment) | Multiple fields in the in-memory EnvironmentConfig Environment. | A field in the patched managed resource. | 
| [CombineToEnvironment](#combinetoenvironment) | Multiple fields in the patched managed resource. | A field in the in-memory EnvironmentConfig Environment. | 
{{< /table >}}

{{<hint "note" >}}
All the following examples use the same set of Compositions, 
CompositeResourceDefinitions, Claims and EnvironmentConfigs.  
Only the applied patches change between
examples. 

All examples rely on Upbound
[provider-aws-s3](https://marketplace.upbound.io/providers/upbound/provider-aws-s3/)
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
apiVersion: apiextensions.crossplane.io/v1alpha1
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

The 
{{<hover label="fromComposite" line="12">}}FromCompositeFieldPath{{</hover>}}
patch takes a value in a composite resource and applies it to a field in the 
managed resource. 

{{< hint "tip" >}}
Use the 
{{<hover label="fromComposite" line="12">}}FromCompositeFieldPath{{</hover>}}
patch to apply options from users in their Claims to settings in managed
resource `forProvider` settings. 
{{< /hint >}}

For example, to use the value 
{{<hover label="fromComposite" line="13">}}desiredRegion{{</hover>}} provided by
a user in a composite resource to a managed resource's
{{<hover label="fromComposite" line="10">}}region{{</hover>}}. 

The {{<hover label="fromComposite" line="13">}}fromFieldPath{{</hover>}} value
is a field in the composite resource. 

The {{<hover label="fromComposite" line="14">}}toFieldPath{{</hover>}} value is
the field in the managed resource to change. 

```yaml {label="fromComposite",copy-lines="9-11"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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

View the managed resource to see the updated 
{{<hover label="fromCompMR" line="6">}}region{{</hover>}}

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

The 
{{<hover label="toComposite" line="12">}}ToCompositeFieldPath{{</hover>}} writes 
data from an individual managed resource to
the composite resource that created it.

{{< hint "tip" >}}
Use {{<hover label="toComposite" line="12">}}ToCompositeFieldPath{{</hover>}}
patches to take data from one managed resource in a Composition and use it in a
second managed resource in the same Composition. 
{{< /hint >}}

For example, after Crossplane creates a new managed resource, take the value 
{{<hover label="toComposite" line="13">}}hostedZoneID{{</hover>}} and apply it
as a 
{{<hover label="toComposite" line="14">}}label{{</hover>}} in the composite
resource.

```yaml {label="toComposite",copy-lines="9-11"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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
{{<hover label="toCompMR" line="6">}}Hosted Zone Id{{</hover>}} field.
```yaml {label="toCompMR",copy-lines="none"}
$ kubectl describe bucket
Name:         my-example-claim-p5pxf-5vnp8
# Removed for brevity
Status:
  At Provider:
    Hosted Zone Id:       Z2O1EMRO9K5GLX
    # Removed for brevity
```

Next view the composite resource and confirm the patch applied the 
{{<hover label="toCompositeXR" line="3">}}label{{</hover>}}
```yaml {label="toCompositeXR",copy-lines="none"}
$ kubectl describe composite
Name:         my-example-claim-p5pxf
Labels:       ZoneID=Z2O1EMRO9K5GLX
```

{{<hint "important">}}
Crossplane doesn't apply the patch to the composite resource until the next
reconcile loop, after creating the managed resource. This creates a delay
between a managed resource being Ready and applying the patch.
{{< /hint >}}


<!-- vale Google.Headings = NO -->
### CombineFromComposite
<!-- vale Google.Headings = YES -->

The 
{{<hover label="combineFromComp" line="12">}}CombineFromComposite{{</hover>}}
patch takes values from the composite resource, combines them and applies them
to the managed resource. 

{{< hint "tip" >}}
Use the 
{{<hover label="combineFromComp" line="12">}}CombineFromComposite{{</hover>}}
patch to create complex strings, like security policies and apply them to
a managed resource. 
{{< /hint >}}

For example, use the Claim value 
{{<hover label="combineFromComp" line="15">}}desiredRegion{{</hover>}} and 
{{<hover label="combineFromComp" line="16">}}field2{{</hover>}} to generate the
managed resource's
{{<hover label="combineFromComp" line="20">}}name{{</hover>}}

The 
{{<hover label="combineFromComp" line="12">}}CombineFromComposite{{</hover>}}
patch only supports the 
{{<hover label="combineFromComp" line="13">}}combine{{</hover>}} option. 

The {{<hover label="combineFromComp" line="14">}}variables{{</hover>}} are the
list of 
{{<hover label="combineFromComp" line="15">}}fromFieldPath{{</hover>}} values
from the composite resource to combine. 

The only supported 
{{<hover label="combineFromComp" line="17">}}strategy{{</hover>}} is 
{{<hover label="combineFromComp" line="17">}}strategy: string{{</hover>}}.

Optionally you can apply a 
{{<hover label="combineFromComp" line="19">}}string.fmt{{</hover>}}, based on 
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the 
strings.

The {{<hover label="combineFromComp" line="20">}}toFieldPath{{</hover>}} is the
field in the managed resource to apply the new string to. 

```yaml {label="combineFromComp",copy-lines="11-20"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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

The 
{{<hover label="combineToComposite" line="12">}}CombineToComposite{{</hover>}}
patch takes values from the managed resource, combines them and applies them
to the composite resource. 

{{<hint "tip" >}}
Use {{<hover label="combineToComposite" line="12">}}CombineToComposite{{</hover>}}
patches to create a single field like a URL from multiple fields in a managed
resource. 
{{< /hint >}}

For example, use the managed resource 
{{<hover label="combineToComposite" line="15">}}name{{</hover>}} and 
{{<hover label="combineToComposite" line="16">}}region{{</hover>}} to generate a
custom 
{{<hover label="combineToComposite" line="20">}}url{{</hover>}}
field. 

{{< hint "important" >}}
Writing custom fields in the Status field of a composite resource requires
defining the custom fields in the CompositeResourceDefinition first. 

{{< /hint >}}

The 
{{<hover label="combineToComposite" line="12">}}CombineToComposite{{</hover>}}
patch only supports the 
{{<hover label="combineToComposite" line="13">}}combine{{</hover>}} option. 

The {{<hover label="combineToComposite" line="14">}}variables{{</hover>}} are the
list of 
{{<hover label="combineToComposite" line="15">}}fromFieldPath{{</hover>}} 
the managed resource to combine. 

The only supported 
{{<hover label="combineToComposite" line="17">}}strategy{{</hover>}} is 
{{<hover label="combineToComposite" line="17">}}strategy: string{{</hover>}}.

Optionally you can apply a 
{{<hover label="combineToComposite" line="19">}}string.fmt{{</hover>}}, based on 
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the 
strings.

The {{<hover label="combineToComposite" line="20">}}toFieldPath{{</hover>}} is the
field in the composite resource to apply the new string to. 

```yaml {label="combineToComposite",copy-lines="9-11"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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
[EnvironmentConfigs]({{<ref "./environment-configs">}}) documentation.
{{< /hint >}}

The 
{{<hover label="fromEnvField" line="12">}}FromEnvironmentFieldPath{{</hover>}}
patch takes values from the in-memory EnvironmentConfig environment and applies
them to the managed resource.

{{<hint "tip" >}}
Use 
{{<hover label="fromEnvField" line="12">}}FromEnvironmentFieldPath{{</hover>}}
to apply custom managed resource settings based on the current environment.  
{{< /hint >}}

For example, use the environment's 
{{<hover label="fromEnvField" line="13">}}locations.eu{{</hover>}} value and
apply it as the 
{{<hover label="fromEnvField" line="14">}}region{{</hover>}}.

```yaml {label="fromEnvField",copy-lines="9-11"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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
EnvironmentConfigs are an alpha feature. They aren't enabled by default.  

For more information about using an EnvironmentConfig, read the 
[EnvironmentConfigs]({{<ref "./environment-configs">}}) documentation.
{{< /hint >}}

The 
{{<hover label="toEnvField" line="12">}}ToEnvironmentFieldPath{{</hover>}}
patch takes values the managed resource and applies them to the in-memory 
EnvironmentConfig environment.

{{<hint "tip" >}}
Use 
{{<hover label="toEnvField" line="12">}}ToEnvironmentFieldPath{{</hover>}}
write data to the environment that any FromEnvironmentFieldPath
patch can access. 
{{< /hint >}}

For example, use the desired
{{<hover label="toEnvField" line="13">}}region{{</hover>}} value and
apply it as the environment's
{{<hover label="toEnvField" line="14">}}key1{{</hover>}}.


```yaml {label="toEnvField",copy-lines="9-11"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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
EnvironmentConfigs are an alpha feature. They aren't enabled by default.  

For more information about using an EnvironmentConfig, read the 
[EnvironmentConfigs]({{<ref "./environment-configs">}}) documentation.
{{< /hint >}}

The 
{{<hover label="combineFromEnv" line="12">}}CombineFromEnvironment{{</hover>}}
patch combines multiple values from the in-memory EnvironmentConfig environment and applies
them to the managed resource.

{{<hint "tip" >}}
Use 
{{<hover label="combineFromEnv" line="12">}}CombineFromEnvironment{{</hover>}}
patch to create complex strings, like security policies and apply them to
a managed resource. 
{{< /hint >}}

For example, combine multiple fields in the environment to create a unique 
{{<hover label="combineFromEnv" line="20">}}annotation{{</hover>}}
. 

The 
{{<hover label="combineFromEnv" line="12">}}CombineFromEnvironment{{</hover>}}
patch only supports the 
{{<hover label="combineFromEnv" line="13">}}combine{{</hover>}} option. 

The only supported 
{{<hover label="combineFromEnv" line="14">}}strategy{{</hover>}} is 
{{<hover label="combineFromEnv" line="14">}}strategy: string{{</hover>}}.

The {{<hover label="combineFromEnv" line="15">}}variables{{</hover>}} are the
list of 
{{<hover label="combineFromEnv" line="16">}}fromFieldPath{{</hover>}} values
from the in-memory environment to combine. 

Optionally you can apply a 
{{<hover label="combineFromEnv" line="19">}}string.fmt{{</hover>}}, based on 
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the 
strings.

The {{<hover label="combineFromEnv" line="20">}}toFieldPath{{</hover>}} is the
field in the managed resource to apply the new string to. 


```yaml {label="combineFromEnv",copy-lines="11-20"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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
{{<hover label="combineFromEnvDesc" line="4">}}annotation{{</hover>}}.

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
EnvironmentConfigs are an alpha feature. They aren't enabled by default.  

For more information about using an EnvironmentConfig, read the 
[EnvironmentConfigs]({{<ref "./environment-configs">}}) documentation.
{{< /hint >}}

The 
{{<hover label="combineToEnv" line="12">}}CombineToEnvironment{{</hover>}}
patch combines multiple values from the managed resource and applies them to the in-memory EnvironmentConfig environment.

{{<hint "tip" >}}
Use 
{{<hover label="combineToEnv" line="12">}}CombineToEnvironment{{</hover>}}
patch to create complex strings, like security policies to use in other managed resources. 
{{< /hint >}}

For example, combine multiple fields in the managed resource to create a unique
string and store it in the environment's
{{<hover label="combineToEnv" line="20">}}key2{{</hover>}} value. 

The string combines the
managed resource 
{{<hover label="combineToEnv" line="16">}}Kind{{</hover>}} and 
{{<hover label="combineToEnv" line="17">}}region{{</hover>}}.

The 
{{<hover label="combineToEnv" line="12">}}CombineToEnvironment{{</hover>}}
patch only supports the 
{{<hover label="combineToEnv" line="13">}}combine{{</hover>}} option. 

The only supported 
{{<hover label="combineToEnv" line="14">}}strategy{{</hover>}} is 
{{<hover label="combineToEnv" line="14">}}strategy: string{{</hover>}}.

The {{<hover label="combineToEnv" line="15">}}variables{{</hover>}} are the
list of 
{{<hover label="combineToEnv" line="16">}}fromFieldPath{{</hover>}} 
values in the managed resource to combine. 

Optionally you can apply a 
{{<hover label="combineToEnv" line="19">}}string.fmt{{</hover>}}, based on 
[Go string formatting](https://pkg.go.dev/fmt) to specify how to combine the 
strings.

The {{<hover label="combineToEnv" line="20">}}toFieldPath{{</hover>}} is the
key in the environment to write the new string to. 

```yaml {label="combineToEnv",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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

Apply a transform directly to an individual patch with the 
{{<hover label="transform1" line="15">}}transforms{{</hover>}} field. 

A 
{{<hover label="transform1" line="15">}}transform{{</hover>}} 
requires a 
{{<hover label="transform1" line="16">}}type{{</hover>}}, indicating the
transform action to take. 

The other transform field is the same as the 
{{<hover label="transform1" line="16">}}type{{</hover>}}, in this example, 
{{<hover label="transform1" line="17">}}map{{</hover>}}.

The other fields depend on the patch type used. 

This example uses a 
{{<hover label="transform1" line="16">}}type: map{{</hover>}} transform, taking 
the input 
{{<hover label="transform1" line="13">}}spec.desiredRegion{{</hover>}}, matching
it to either 
{{<hover label="transform1" line="18">}}us{{</hover>}} or 
{{<hover label="transform1" line="19">}}eu{{</hover>}} and returning the
corresponding AWS region for the 
{{<hover label="transform1" line="14">}}spec.forProvider.region{{</hover>}}
value. 

```yaml {label="transform1",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for brevity
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

The {{<hover label="convert" line="6">}}convert{{</hover>}} transform type 
changes the input data type to a different data type.

{{< hint "tip" >}}
Some provider APIs require a field to be a string. Use a 
{{<hover label="convert" line="7">}}convert{{</hover>}} type to 
change any boolean or integer fields to strings. 
{{< /hint >}}

A {{<hover label="convert" line="6">}}convert{{</hover>}} 
transform requires a {{<hover label="convert" line="8">}}toType{{</hover>}}, 
defining the output data type. 

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
`1`, `t`, `T`, `TRUE`, `True` and `true`  
equal to the boolean value `True`.  

The strings   
`0`, `f`, `F`, `FALSE`, `False` and `false`   
are equal to the boolean value `False`. 

#### Converting numbers to booleans
Crossplane considers the integer `1` and float `1.0` equal to the boolean
value `True`.  
Any other integer or float value is `False`.

#### Converting booleans to numbers
Crossplane converts the boolean value `True` to the integer `1` or float64
`1.0`.  

The value `False` converts to the integer `0` or float64 `0.0`

#### Converting strings to float64
When converting from a `string` to a 
{{<hover label="format" line="3">}}float64{{</hover>}} Crossplane supports 
an optional  
{{<hover label="format" line="4">}}format: quantity{{</hover>}} field.

Using {{<hover label="format" line="4">}}format: quantity{{</hover>}} translates 
size suffixes like `M` for megabyte or `Mi` for megabit into the correct float64
value. 

{{<hint "note" >}}
Refer to the [Go language docs](https://pkg.go.dev/k8s.io/apimachinery/pkg/api/resource#Quantity) 
for a full list of supported suffixes.
{{</hint >}}

Add {{<hover label="format" line="4">}}format: quantity{{</hover>}} to the 
{{<hover label="format" line="1">}}convert{{</hover>}} object to enable quantity
suffix support. 

```yaml {label="format",copy-lines="all"}
- type: convert
  convert:
   toType: float64
   format: quantity
```

#### Converting strings to objects

Crossplane converts JSON strings to objects.

Add {{<hover label="object" line="4">}}format: json{{</hover>}} to the 
{{<hover label="object" line="1">}}convert{{</hover>}} object which is
the only supported string format for this conversion.

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
{{<hover label="patch-key" line="8">}}customized key{{</hover>}}:

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

Add {{<hover label="array" line="4">}}format: json{{</hover>}} to the 
{{<hover label="array" line="1">}}convert{{</hover>}} object which is
the only supported string format for this conversion.

```yaml {label="array",copy-lines="all"}
- type: convert
  convert:
   toType: array
   format: json
```

### Map transforms
The {{<hover label="map" line="6">}}map{{</hover>}} transform type 
_maps_ an input value to an output value. 

{{< hint "tip" >}}
The {{<hover label="map" line="6">}}map{{</hover>}} transform is useful for
translating generic region names like `US` or `EU` to provider specific region
names. 
{{< /hint >}}

The {{<hover label="map" line="6">}}map{{</hover>}} transform compares the value
from the {{<hover label="map" line="3">}}fromFieldPath{{</hover>}} to the
options listed in the {{<hover label="map" line="6">}}map{{</hover>}}.  

If Crossplane finds the value, Crossplane puts
the mapped value in the {{<hover label="map" line="4">}}toFieldPath{{</hover>}}.

{{<hint "note" >}}
Crossplane throws an error for the patch if the value isn't found.
{{< /hint >}}

{{<hover label="map" line="3">}}spec.field1{{</hover>}} is the string
{{<hover label="map" line="8">}}"field1-text"{{</hover>}} then Crossplane uses
the string 
{{<hover label="map" line="8">}}firstField{{</hover>}} for the 
{{<hover label="map" line="4">}}annotation{{</hover>}}.  

If
{{<hover label="map" line="3">}}spec.field1{{</hover>}} is the string
{{<hover label="map" line="8">}}"field2-text"{{</hover>}} then Crossplane uses
the string 
{{<hover label="map" line="8">}}secondField{{</hover>}} for the 
{{<hover label="map" line="4">}}annotation{{</hover>}}.  

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
In this example, the value of 
{{<hover label="map" line="3">}}spec.field1{{</hover>}} is 
{{<hover label="comositeMap" line="5">}}field1-text{{</hover>}}.

```yaml {label="comositeMap",copy-lines="none"}
$ kubectl describe composite
Name:         my-example-claim-twx7n
Spec:
  # Removed for brevity
  field1:         field1-text
```

The annotation applied to the managed resource is 
{{<hover label="mrMap" line="4">}}firstField{{</hover>}}.

```yaml {label="mrMap",copy-lines="none"}
$ kubectl describe bucket
Name:         my-example-claim-twx7n-ndb2f
Annotations:  crossplane.io/composition-resource-name: bucket1
              myAnnotation: firstField
# Removed for brevity.
```

### Match transform
The {{<hover label="match" line="6">}}match{{</hover>}} transform is like the
`map` transform.  

The {{<hover label="match" line="6">}}match{{</hover>}} 
transform adds support for regular expressions along with exact
strings and can provide default values if there isn't a match.

A {{<hover label="match" line="7">}}match{{</hover>}} object requires a 
{{<hover label="match" line="8">}}patterns{{</hover>}} object.

The {{<hover label="match" line="8">}}patterns{{</hover>}} is a list of one or
more patterns to attempt to match the input value against. 

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

Match {{<hover label="match" line="8">}}patterns{{</hover>}} can be either 
{{<hover label="match" line="9">}}type: literal{{</hover>}} to match an
exact string or 
{{<hover label="match" line="11">}}type: regexp{{</hover>}} to match a
regular expression. 

{{<hint "note" >}}
Crossplane stops processing matches after the first pattern match.
{{< /hint >}}

#### Match an exact string
Use a {{<hover label="matchLiteral" line="8">}}pattern{{</hover>}} with 
{{<hover label="matchLiteral" line="9">}}type: literal{{</hover>}} to match an 
exact string. 

On a successful match Crossplane provides the 
{{<hover label="matchLiteral" line="11">}}result:{{</hover>}} to
the patch {{<hover label="matchLiteral" line="4">}}toFieldPath{{</hover>}}. 

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
Use a {{<hover label="matchRegex" line="8">}}pattern{{</hover>}} with 
{{<hover label="matchRegex" line="9">}}type: regexp{{</hover>}} to match a regular
expression.  
Define a 
{{<hover label="matchRegex" line="10">}}regexp{{</hover>}} key with the value of the
regular expression to match.

On a successful match Crossplane provides the 
{{<hover label="matchRegex" line="11">}}result:{{</hover>}} to
the patch {{<hover label="matchRegex" line="4">}}toFieldPath{{</hover>}}. 

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

Use
{{<hover label="defaultValue" line="12">}}fallbackTo: Value{{</hover>}} to
provide a default value if a match isn't found.

For example if the string 
{{<hover label="defaultValue" line="10">}}unknownString{{</hover>}} isn't
matched, Crossplane provides the 
{{<hover label="defaultValue" line="12">}}Value{{</hover>}} 
{{<hover label="defaultValue" line="13">}}StringNotFound{{</hover>}} to the 
{{<hover label="defaultValue" line="4">}}toFieldPath{{</hover>}} 


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

To use the original input as the fallback value use 
{{<hover label="defaultInput" line="12">}}fallbackTo: Input{{</hover>}}.

Crossplane uses the original 
{{<hover label="defaultInput" line="3">}}fromFieldPath{{</hover>}} input for the 
{{<hover label="defaultInput" line="4">}}toFieldPath{{</hover>}} value.
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

Use the {{<hover label="math" line="6">}}math{{</hover>}} transform to multiply
an input or apply a minimum or maximum value. 

{{<hint "important">}}
A {{<hover label="math" line="6">}}math{{</hover>}} transform only supports
integer inputs. 
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

The {{<hover label="clampMin" line="8">}}type: clampMin{{</hover>}} uses a defined 
minimum value if an input is larger than the 
{{<hover label="clampMin" line="8">}}type: clampMin{{</hover>}} value.

For example, this 
{{<hover label="clampMin" line="8">}}type: clampMin{{</hover>}} requires an
input to be greater than 
{{<hover label="clampMin" line="9">}}20{{</hover>}}.

If an input is lower than 
{{<hover label="clampMin" line="9">}}20{{</hover>}}, Crossplane uses the 
{{<hover label="clampMin" line="9">}}clampMin{{</hover>}} value for the 
{{<hover label="clampMin" line="4">}}toFieldPath{{</hover>}}.

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

The {{<hover label="clampMax" line="8">}}type: clampMax{{</hover>}} uses a defined 
minimum value if an input is larger than the 
{{<hover label="clampMax" line="8">}}type: clampMax{{</hover>}} value.

For example, this 
{{<hover label="clampMax" line="8">}}type: clampMax{{</hover>}} requires an
input to be less than 
{{<hover label="clampMax" line="9">}}5{{</hover>}}.

If an input is higher than 
{{<hover label="clampMax" line="9">}}5{{</hover>}}, Crossplane uses the 
{{<hover label="clampMax" line="9">}}clampMax{{</hover>}} value for the 
{{<hover label="clampMax" line="4">}}toFieldPath{{</hover>}}.

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

The {{<hover label="multiply" line="8">}}type: multiply{{</hover>}} multiplies
the input by the {{<hover label="multiply" line="9">}}multiply{{</hover>}} 
value.

For example, this 
{{<hover label="multiply" line="8">}}type: multiply{{</hover>}} multiplies the
value from the {{<hover label="multiply" line="3">}}fromFieldPath{{</hover>}}
value by {{<hover label="multiply" line="9">}}2{{</hover>}}


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
The {{<hover label="multiply" line="9">}}multiply{{</hover>}} value only
supports integers.
{{< /hint >}}

### String transforms

The {{<hover label="string" line="6">}}string{{</hover>}} transform applies
string formatting or manipulation to string inputs.

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
{{<hover label="string" line="7">}}types{{</hover>}}

* [Convert](#string-convert)
* [Format](#string-format)
* [Join](#join)
* [Regexp](#regular-expression-type)
* [TrimPrefix](#trim-prefix)
* [TrimSuffix](#trim-suffix)

#### String convert

The {{<hover label="stringConvert" line="9">}}type: convert{{</hover>}}
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
The {{<hover label="typeFormat" line="9">}}type: format{{</hover>}}
applies [Go string formatting](https://pkg.go.dev/fmt) to the input. 

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

The {{<hover label="typeJoin" line="8">}}type: Join{{</hover>}} joins all
values in the input array into a string using the given separator.

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
The {{<hover label="typeRegex" line="8">}}type: Regexp{{</hover>}} extracts
the part of the input matching a regular expression. 

Optionally use a 
{{<hover label="typeRegex" line="11">}}group{{</hover>}} to match a regular
expression capture group.  
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

The {{<hover label="typeTrimP" line="8">}}type: TrimPrefix{{</hover>}} uses 
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

The {{<hover label="typeTrimS" line="8">}}type: TrimSuffix{{</hover>}} uses 
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

## Patch policies

Crossplane supports two types of patch policies:
* `fromFieldPath`
* `mergeOptions`

<!-- vale Google.Headings = NO -->
### fromFieldPath policy
<!-- vale Google.Headings = YES -->

Using a `fromFieldPath: Required` policy on a patch requires the
`fromFieldPath` to exist in the composite resource.

{{<hint "tip" >}}
If a resource patch isn't working applying the `fromFieldPath: Required` policy
may produce an error in the composite resource to help troubleshoot. 
{{< /hint >}}

By default, Crossplane applies the policy `fromFieldPath: Optional`. With
`fromFieldPath: Optional` Crossplane 
ignores a patch if the `fromFieldPath` doesn't exist.   

With 
{{<hover label="required" line="6">}}fromFieldPath: Required{{</hover>}} 
the composite resource produces an error if the
{{<hover label="required" line="6">}}fromFieldPath{{</hover>}} doesn't exist. 

```yaml {label="required"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: metadata.annotations["eu"]
    policy:
      fromFieldPath: Required
```

### Merge options

By default when applying a patch the destination data is overridden. Use 
{{<hover label="merge" line="6">}}mergeOptions{{</hover>}} to allow patches to 
merge arrays and objects without overwriting them. 

With an array input, use 
{{<hover label="merge" line="7">}}appendSlice: true{{</hover>}} to append the
array data to the end of the existing array.

With an object, use 
{{<hover label="merge" line="8">}}keepMapValues: true{{</hover>}} to leave
existing object keys in tact. The patch updates any matching keys between the
input and destination data. 

```yaml {label="merge"}
patches:
  - type: FromCompositeFieldPath
    fromFieldPath: spec.desiredRegion
    toFieldPath: metadata.annotations["eu"]
    policy:
      mergeOptions:
        appendSlice: true
        keepMapValues: true
```
