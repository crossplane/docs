---
title: Environment Configurations
weight: 75
state: alpha
alphaVersion: "1.11"
description: "Environment Configurations or EnvironmentConfigs are an in-memory datastore used in patching Compositions"
---

<!--
TODO: Add Policies
-->


A Crossplane EnvironmentConfig is a cluster scoped 
[ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/)-like 
resource used
by Compositions. Compositions can use the environment to store information from
individual resources or to apply [patches]({{<ref "patch-and-transform">}}).

Crossplane supports multiple EnvironmentConfigs, each acting as a unique
data store. 

When Crossplane creates a composite resource, Crossplane merges all the 
EnvironmentConfigs referenced in the associated Composition and creates a unique
in-memory environment for that composite resource.

The composite resource can read and write data to their unique 
in-memory environment.

{{<hint "important" >}}
The in-memory environment is unique to each composite resource.  
A composite resource can't read data in another composite resource's
environment. 
{{< /hint >}}

## Enable EnvironmentConfigs
EnvironmentConfigs are an alpha feature. Alpha features aren't enabled by
default.

Enable EnvironmentConfig support by 
[changing the Crossplane pod setting]({{<ref "./pods#change-pod-settings">}})
and enabling  
{{<hover label="deployment" line="12">}}--enable-environment-configs{{</hover>}}
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
        - --enable-environment-configs
```

{{<hint "tip" >}}

The [Crossplane install guide]({{<ref "../software/install#feature-flags">}}) 
describes enabling feature flags like 
{{<hover label="deployment" line="12">}}--enable-environment-configs{{</hover>}}
with Helm.
{{< /hint >}}

<!-- vale Google.Headings = NO -->
## Create an EnvironmentConfig
<!-- vale Google.Headings = YES -->

An {{<hover label="env1" line="2">}}EnvironmentConfig{{</hover>}} has a single
object field,
{{<hover label="env1" line="5">}}data{{</hover>}}.

An EnvironmentConfig supports any data inside the 
{{<hover label="env1" line="5">}}data{{</hover>}} field.

Here an example 
{{<hover label="env1" line="2">}}EnvironmentConfig{{</hover>}}.

```yaml {label="env1"}
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
  key3:
    - item1
    - item2
```

<!-- vale Google.Headings = NO -->
## Select an EnvironmentConfig
<!-- vale Google.Headings = YES -->

Select the EnvironmentConfigs to use
inside a Composition's 
{{<hover label="comp" line="6">}}environment{{</hover>}} field.

The {{<hover label="comp" line="7">}}environmentConfigs{{</hover>}} field is a
list of environments this Composition can use. 

Select an environment by 
{{<hover label="comp" line="8">}}Reference{{</hover>}} or 
by 
{{<hover label="comp" line="11">}}Selector{{</hover>}}.

A 
{{<hover label="comp" line="8">}}Reference{{</hover>}}
selects an environment by 
{{<hover label="comp" line="10">}}name{{</hover>}}.  
The 
{{<hover label="comp" line="11">}}Selector{{</hover>}} selects an environment
based on the 
{{<hover label="comp" line="13">}}Labels{{</hover>}} applied to the environment. 

```yaml {label="comp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  environment:
    environmentConfigs:
    - type: Reference
      ref:
        name: example-environment
    - type: Selector
      selector:
        matchLabels:
      # Removed for brevity
```

If a Composition uses multiple 
{{<hover label="comp" line="7">}}environmentConfigs{{</hover>}}
Crossplane merges them together in the order they're listed. 

{{<hint "note" >}}
If multiple 
{{<hover label="comp" line="7">}}environmentConfigs{{</hover>}}
use the same key, the Composition uses the value of the last environment listed.
{{</hint >}}

### Select by name

Select an environment by name with
{{<hover label="byName" line="8">}}type: Reference{{</hover>}}. 

Define the
{{<hover label="byName" line="9">}}ref{{</hover>}} object and the 
{{<hover label="byName" line="10">}}name{{</hover>}} matching the exact name of
the environment.


For example, select the 
{{<hover label="byName" line="7">}}environmentConfig{{</hover>}}
named
{{<hover label="byName" line="10">}}example-environment{{</hover>}}

```yaml {label="byName",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  environment:
    environmentConfigs:
    - type: Reference
      ref:
        name: example-environment
```

### Select by label

Select an environment by labels with a
{{<hover label="byLabel" line="8">}}type: Selector{{</hover>}}.  

Define the {{<hover label="byLabel" line="9">}}selector{{</hover>}} object.  

The
{{<hover label="byLabel" line="10">}}matchLabels{{</hover>}} object contains a
list of labels to match on. 

Selecting a label requires matching both the label 
{{<hover label="byLabel" line="11">}}key{{</hover>}} 
and the value of key. 

When matching the label's value, provide an exact value with a 
{{<hover label="byLabel" line="12">}}type: Value{{</hover>}} and provide the value
to match in the 
{{<hover label="byLabel" line="13">}}value{{</hover>}} field.

Crossplane can also match a label's value based on an input in the composite
resource. Use 
{{<hover label="byLabel" line="15">}}type: FromCompositeFieldPath{{</hover>}} 
and provide the field to match in the 
{{<hover label="byLabel" line="16">}}valueFromFieldPath{{</hover>}} field.

```yaml {label="byLabel",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  environment:
    environmentConfigs:
    - type: Selector
      selector: 
        matchLabels:
          - key: my-label-key
            type: Value
            value: my-label-value
          - key: my-label-key
            type: FromCompositeFieldPath
            valueFromFieldPath: spec.parameters.deploy
  resources:
  # Removed for brevity
```

#### Manage selector results

Selecting environments by labels may return more than one environment.  
The Composition sorts all the results by the name of the environments and
only uses the first environment in the sorted list. 

Set the {{<hover label="selectResults" line="10">}}mode{{</hover>}} as 
{{<hover label="selectResults" line="10">}}mode: Multiple{{</hover>}} to return
all matched environments. Use 
{{<hover label="selectResults" line="19">}}mode: Single{{</hover>}} to 
return a single environment.

{{<hint "note" >}}
Sorting and the selection 
{{<hover label="selectResults" line="10">}}mode{{</hover>}}
only applies to a single 
{{<hover label="selectResults" line="8">}}type: Selector{{</hover>}}. 

This doesn't change how Compositions merge multiple
{{<hover label="selectResults" line="7">}}environmentConfigs{{</hover>}}.
{{< /hint >}}


```yaml {label="selectResults"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  environment:
    environmentConfigs:
    - type: Selector
      selector:
        mode: Multiple
        matchLabels:
          - key: my-label-key
            type: Value
            value: my-label-value
          - key: my-label-key
            type: FromCompositeFieldPath
            valueFromFieldPath: spec.parameters.deploy
    - type: Selector
      selector:
        mode: Single
        matchLabels:
          - key: my-other-label-key
            type: Value
            value: my-other-label-value
          - key: my-other-label-key
            type: FromCompositeFieldPath
            valueFromFieldPath: spec.parameters.deploy
```

When using 
{{<hover label="maxMatch" line="10">}}mode: Multiple{{</hover>}} limit the
number of returned environments with
{{<hover label="maxMatch" line="11">}}maxMatch{{</hover>}} and define the
maximum number of environments returned. 

Use `minMatch` and define the minimum 
number of environments returned.

The Composition sorts the returned environments alphabetically by name. Sort the
environments on a different field with 
{{<hover label="maxMatch" line="12">}}sortByFieldPath{{</hover>}} and define
the field to sort by. 


```yaml {label="maxMatch"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  environment:
    environmentConfigs:
    - type: Selector
      selector:
        mode: Multiple
        maxMatch: 4
        sortByFieldPath: metadata.annotations[sort.by/weight]
        matchLabels:
          - key: my-label-key
            type: Value
            value: my-label-value
          - key: my-label-key
            type: FromCompositeFieldPath
            valueFromFieldPath: spec.parameters.deploy
```

The environments selected by
{{<hover label="maxMatch" line="18">}}matchLabels{{</hover>}} are then merged
into any other environments listed in the 
{{<hover label="maxMatch" line="7">}}environmentConfigs{{</hover>}}.

#### Optional selector labels
By default, Crossplane issues an error if a
{{<hover label="byLabelOptional" line="16">}}valueFromFieldPath{{</hover>}}
field doesn't exist in the composite resource.  

Add
{{<hover label="byLabelOptional" line="17">}}fromFieldPathPolicy{{</hover>}}
as {{<hover label="byLabelOptional" line="17">}}Optional{{</hover>}} 
to ignore a field if it doesn't exist.

```yaml {label="byLabelOptional",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  environment:
    environmentConfigs:
      - type: Selector
        selector:
          matchLabels:
            - key: my-first-label-key
              type: Value
              value: my-first-label-value
            - key: my-second-label-key
              type: FromCompositeFieldPath
              valueFromFieldPath: spec.parameters.deploy
              fromFieldPathPolicy: Optional
  resources:
  # Removed for brevity
```


Set a default value for an optional label by setting the default
{{<hover label="byLabelOptionalDefault" line="15">}}value{{</hover>}} for the
{{<hover label="byLabelOptionalDefault" line="14">}}key{{</hover>}} first, then
define the
{{<hover label="byLabelOptionalDefault" line="20">}}Optional{{</hover>}} label.

For example, this Composition defines
{{<hover label="byLabelOptionalDefault" line="16">}}value: my-default-value{{</hover>}}
for the key {{<hover label="byLabelOptionalDefault" line="14">}}my-second-label-key{{</hover>}}.
If the label
{{<hover label="byLabelOptionalDefault" line="17">}}my-second-label-key{{</hover>}}
exists, Crossplane uses the value from the label instead.

```yaml {label="byLabelOptionalDefault",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  environment:
    environmentConfigs:
      - type: Selector
        selector:
          matchLabels:
            - key: my-first-label-key
              type: Value
              value: my-label-value
            - key: my-second-label-key
              type: Value
              value: my-default-value
            - key: my-second-label-key
              type: FromCompositeFieldPath
              valueFromFieldPath: spec.parameters.deploy
              fromFieldPathPolicy: Optional
  resources:
  # Removed for brevity
```

{{<hint "warning" >}}
Crossplane applies values in order. The value of the last key defined always takes precedence.

Defining the default value _after_ the label always overwrites the label
value.
{{< /hint >}}

## Patching with EnvironmentConfigs

When Crossplane creates or updates a composite resource, Crossplane 
merges all the specified EnvironmentConfigs into an in-memory environment.

The composite resource can read or write data between the EnvironmentConfig and
composite resource or between the EnvironmentConfig and individual resources
defined inside the composite resource. 

{{<hint "tip" >}}
Read about EnvironmentConfig patch types in the 
[Patch and Transform]({{<ref "./patch-and-transform">}}) documentation.
{{< /hint >}}

<!-- these two sections are duplicated in the compositions doc with different header depths --> 

### Patch a composite resource
To patch the composite resource use
{{< hover label="xrpatch" line="7">}}patches{{</hover>}} inside of the 
{{< hover label="xrpatch" line="5">}}environment{{</hover>}}.

Use the 
{{< hover label="xrpatch" line="5">}}ToCompositeFieldPath{{</hover>}} to copy
data from the in-memory environment to the composite resource.  
Use the 
{{< hover label="xrpatch" line="5">}}FromCompositeFieldPath{{</hover>}} to copy
data from the composite resource to the in-memory environment.

```yaml {label="xrpatch",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
spec:
  environment:
  # Removed for Brevity
      patches:
      - type: ToCompositeFieldPath
        fromFieldPath: tags
        toFieldPath: metadata.labels[envTag]
      - type: FromCompositeFieldPath
        fromFieldPath: metadata.name
        toFieldPath: newEnvironmentKey
```

Individual resources can use any data written to the in-memory environment.

### Patch an individual resource
To patch an individual resource, inside the 
{{<hover label="envpatch" line="16">}}patches{{</hover>}} of the 
resource, use 
{{<hover label="envpatch" line="17">}}ToEnvironmentFieldPath{{</hover>}} to copy
data from the resource to the in-memory environment.  
Use {{<hover label="envpatch" line="20">}}FromEnvironmentFieldPath{{</hover>}}
to copy data to the resource from the in-memory environment.

```yaml {label="envpatch",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
spec:
  environment:
  # Removed for Brevity
  resources:
  # Removed for Brevity
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

The [Patch and Transform]({{<ref "./patch-and-transform">}}) documentation has
more information on patching individual resources.

<!-- End duplicated content -->