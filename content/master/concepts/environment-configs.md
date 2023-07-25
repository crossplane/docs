---
title: Environment Configurations
weight: 90
state: alpha
alphaVersion: "1.11"
description: "Environment Configurations or EnvironmentConfigs are an in-memory datastore used in patching Compositions"
---

A Crossplane EnvironmentConfig is an in-memory data store. Composition 
patches can read from and write to an environment.

Crossplane supports multiple EnvironmentConfigs, each acting as a unique
data store. 

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

## Patching with EnvironmentConfigs

To patch data from or to an EnvironmentConfig, reference the EnvironmentConfig
inside a Composition's 
{{<hover label="comp" line="6">}}environment{{</hover>}} field.

The {{<hover label="comp" line="7">}}environmentConfigs{{</hover>}} field is a
list of environments this Composition can use. 

{{<hint "tip" >}}
Read about EnvironmentConfig patch types in the 
[Patch and Transform]({{<ref "./patch-and-transform">}}) documentation.
{{< /hint >}}

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
<!--
TODO: Add Policies
TODO: Add webhook validations
-->
