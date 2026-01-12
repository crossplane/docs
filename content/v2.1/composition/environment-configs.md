---
title: Environment Configs
weight: 75
state: beta
alphaVersion: "1.11"
betaVersion: "1.18"
description: "In-memory data stores for Compositions"
---

<!--
TODO: Add Policies
-->


A Crossplane EnvironmentConfig is a cluster-scoped, strongly typed,
[ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/)-like
resource used by Compositions. Compositions can use the environment to store
information from individual resources or to apply patches.

Crossplane supports multiple `EnvironmentConfigs`, each acting as a unique
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

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
## Create an EnvironmentConfig
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

An {{<hover label="env1" line="2">}}EnvironmentConfig{{</hover>}} has a single
object field,
{{<hover label="env1" line="5">}}data{{</hover>}}.

An EnvironmentConfig supports any data inside the
{{<hover label="env1" line="5">}}data{{</hover>}} field.

Here an example
{{<hover label="env1" line="2">}}EnvironmentConfig{{</hover>}}.

```yaml {label="env1"}
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
  key3:
    - item1
    - item2
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
## Access EnvironmentConfigs
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

[Composition Functions] supporting
[extra-resources], for example [function-environment-configs] or
[function-go-templating].

## Migration from alpha composition environment

Crossplane (`<=v1.17`) natively supported selecting `EnvironmentConfigs`,
merging them into an `in-memory environment` and patching between that,
composed and composite resources. From `v1.18`, Crossplane removed this native capability, in favor of [Composition Functions].

Users that enabled Alpha Composition Environments
(`--enable-environment-configs`) and leveraged the native features
(`spec.environment.patches`, `spec.environment.environmentConfigs` and
`*Environment` patches), have to migrate to Composition Functions to
continue doing so.

Automated migration to `Pipeline` mode is available through `crossplane beta
convert pipeline-composition`, which moves a composition using `Resource`
mode, to [function-patch-and-transform] and, if needed,
[function-environment-configs].

See the documentation of [function-environment-configs] for more details about manual
migration.

<!-- vale Google.Headings = NO -->
## Select an EnvironmentConfig using function-environment-configs
<!-- vale Google.Headings = YES -->

Select the EnvironmentConfigs to use through [function-environment-configs]'s `Input`.

The `environmentConfigs` field is a list of `EnvironmentConfigs` to
retrieve, merge and pass to the next step in the pipeline through the
[Context] at a well known key, `apiextensions.crossplane.io/environment`.

Select an environment by `Reference` or by `Selector`:

* A `Reference` selects an `EnvironmentConfig` by name.
* The `Selector` selects an `EnvironmentConfig` by labels.

```yaml {label="comp",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  - step: environmentConfigs
    functionRef:
      name: function-environment-configs
    input:
      apiVersion: environmentconfigs.fn.crossplane.io/v1beta1
      kind: Input
      spec:
        environmentConfigs:
        - type: Reference
          ref:
            name: example-environment
        - type: Selector
          selector:
            matchLabels:
            # Removed for brevity
    # the environment will be passed to the next function in the pipeline
    # as part of the context

# Next step consuming the merged environment removed for brevity...
```

If a Composition uses multiple `EnvironmentConfigs`,
[function-environment-configs] merges them together in the order they're
listed. 

### Select by name

Select an `EnvironmentConfig` by name with `type: Reference`.

Define `ref.name` to match the exact name of the environment.


For example, select the `EnvironmentConfig` named `example-environment`:

```yaml {label="byName",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  - step: environmentConfigs
    functionRef:
      name: function-environment-configs
    input:
      apiVersion: environmentconfigs.fn.crossplane.io/v1beta1
      kind: Input
      spec:
        environmentConfigs:
        - type: Reference
          ref:
            name: example-environment
```

### Select by label

Select an `EnvironmentConfig` by labels with a `type: Selector`.

Define `selector.matchLabels` to a list of selectors either of type `Value`, or `FromCompositeFieldPath`.

When matching the label's value, provide an exact value with a 
`type: Value` and provide the value to match in the `value` field.

[function-environment-configs] can also match a label's value based on an input
in the composite resource. Use `type: FromCompositeFieldPath` and provide the
field to match in the `valueFromFieldPath` field.

```yaml {label="byLabel",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  - step: environmentConfigs
    functionRef:
      name: function-environment-configs
    input:
      apiVersion: environmentconfigs.fn.crossplane.io/v1beta1
      kind: Input
      spec:
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
  # Removed for brevity
```

#### Manage selector results

Selecting environments by labels may return more than one environment.  
[function-environment-configs], by default, sorts all the results by name and
only uses the first environment in the sorted list.

Set the `selector.mode` to `Multiple` to return all matched EnvironmentConfigs.
Use `mode: Single` to return a single environment, and error out if Crossplane finds more than one match.

Sorting and the selection mode only applies to a single `Selector`.

```yaml {label="selectResults"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  - step: environmentConfigs
    functionRef:
      name: function-environment-configs
    input:
      apiVersion: environmentconfigs.fn.crossplane.io/v1beta1
      kind: Input
      spec:
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

When using `mode: Multiple` limit the number of returned `EnvironmentConfigs`
with `maxMatch` and define the maximum number to select.

Use `minMatch` and define the minimum number of environments returned.

The Function sorts the returned environments alphabetically by name by default.
Sort the environments on a different field with `sortByFieldPath` and define
the field to sort by. 


```yaml {label="maxMatch"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  - step: environmentConfigs
    functionRef:
      name: function-environment-configs
    input:
      apiVersion: environmentconfigs.fn.crossplane.io/v1beta1
      kind: Input
      spec:
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

The EnvironmentConfigs selected by `matchLabels` are then merged with all the
other ones specified.

#### Optional selector labels
By default, Crossplane issues an error if the specified `valueFromFieldPath`
field doesn't exist in the composite resource.  

Set `fromFieldPathPolicy` to `Optional` to ignore a field if it doesn't exist.

```yaml {label="byLabelOptional",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  - step: environmentConfigs
    functionRef:
      name: function-environment-configs
    input:
      apiVersion: environmentconfigs.fn.crossplane.io/v1beta1
      kind: Input
      spec:
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
                fromFieldPathPolicy: Optional
  # Removed for brevity
```


Set a default value for an optional label by setting the default `value` for
the `key` first using a `Value` selector, then define the `Optional`
`FromCompositeFieldPath` one.

For example, the Composition below defines `value: my-default-value` for the key
`my-second-label-key`. If the Composite resource defines
`spec.parameters.deploy`, [function-environment-configs] uses that instead.

```yaml {label="byLabelOptionalDefault",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  - step: environmentConfigs
    functionRef:
      name: function-environment-configs
    input:
      apiVersion: environmentconfigs.fn.crossplane.io/v1beta1
      kind: Input
      spec:
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
  # Removed for brevity
```

{{<hint "warning" >}}
[function-environment-configs](https://github.com/crossplane-contrib/function-environment-configs)
applies values in order. The value of the last key defined always takes precedence.

Defining the default value _after_ the label always overwrites the label
value.
{{< /hint >}}

## Patching with EnvironmentConfigs using function-patch-and-transform

`EnvironmentConfigs` selected as explained earlier, are then merged in an
`in-memory environment` by [function-environment-configs] and passed to the
next function in the pipeline at a well known key,
`apiextensions.crossplane.io/environment`.

You can use [function-patch-and-transform] to read or write data between the in-memory environment and
composite resource or individual composed resources.

{{<hint "tip" >}}
The Patch and Transform function can use the environment to patch composed
resources. Read about EnvironmentConfig patch types in the
[Patch and Transform function documentation]({{<ref "../guides/function-patch-and-transform">}}).
{{< /hint >}}

### Patch between Composite resource and environment

To patch between Composite resource and environment define patches at
`spec.environment.patches` in the `Resources` input of [function-patch-and-transform].

Use the `ToCompositeFieldPath` patch type to copy data from the in-memory
environment to the Composite resource. Use the `FromCompositeFieldPath` to
copy data from the Composite resource to the in-memory environment.

```yaml {label="xrpatch",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  # Removed for Brevity
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
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
# Removed for Brevity
```

Individual resources can use any data written to the in-memory environment.

You can use `CombineFromComposite` and `CombineToComposite` to combine multiple
values and write the result either to the in-memory environment or the
Composite resource, respectively.

### Patch an individual resource

To patch between individual resources and the in-memory environment, inside the
patches of the resource, use `ToEnvironmentFieldPath` to copy data from the
resource to the in-memory environment. Use `FromEnvironmentFieldPath` to copy
data to the resource from the in-memory environment.

```yaml {label="envpatch",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-composition
spec:
  mode: Pipeline
  pipeline:
  # Removed for Brevity
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      # Removed for Brevity
      resources:
        - name: vpc
          base:
            apiVersion: ec2.aws.m.upbound.io/v1beta1
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



{{<hint "tip" >}}
The [Patch and Transform]({{<ref "../guides/function-patch-and-transform">}}) documentation has more information on patching individual resources.
{{< /hint >}}

[extra-resources]: {{<ref "./compositions">}}
[function-environment-configs]: https://github.com/crossplane-contrib/function-environment-configs
[function-patch-and-transform]: {{<ref "../guides/function-patch-and-transform">}}
[function-go-templating]: https://github.com/crossplane-contrib/function-go-templating
[Composition Functions]: {{<ref "./compositions">}}
[Context]: {{<ref "./compositions/#function-pipeline-context">}}
