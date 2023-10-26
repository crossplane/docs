---
title: Composition Functions
state: beta
alphaVersion: "1.11"
betaVersion: "1.14"
weight: 80
description: "Composition Functions allow you to template resources using general-purpose programming languages"
aliases: 
  - /knowledge-base/guides/composition-functions
---

Composition functions (or just functions, for short) are custom programs that
template Crossplane resources. Crossplane calls composition functions to
determine what resources it should create when you create a composite resource
(XR). You can write a function to template resources using a general purpose
programming language like Go or Python. Using a general purpose programming
language allows a Function to use more advanced logic to template resources,
like loops and conditionals.

You can build a function using general purpose programming languages such as Go
or Python. The Crossplane community has also built functions that let you
template Crossplane resources using [CUE](https://cuelang.org), Helm-like
[Go templates](https://pkg.go.dev/text/template) or
[Patch and Transforms]({{<ref "./patch-and-transform">}}).

## Install a composition function

Installing a Function creates a function pod. Crossplane sends requests to this
pod to ask it what resources to create when you create a composite resource.

Install a Function with a Crossplane
{{<hover label="install" line="2">}}Function{{</hover >}} object setting the
{{<hover label="install" line="6">}}spec.package{{</hover >}} value to the
location of the function package.


For example, to install Function Patch and Transform,

```yaml {label="install"}
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.1.4
```

{{< hint "tip" >}}
Functions are Crossplane Packages. Read more about Packages in the
[Packages documentation]({{<ref "packages" >}}).
{{< /hint >}}

By default, the Function pod installs in the same namespace as Crossplane
(`crossplane-system`).

## Verify a composition function

View the status of a Function with `kubectl get functions`

During the install a Function reports `INSTALLED` as `True` and `HEALTHY` as
`Unknown`.

```shell {copy-lines="1"}
kubectl get functions
NAME                              INSTALLED   HEALTHY   PACKAGE                                                                  AGE
function-patch-and-transform      True        Unknown   xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.1.4   10s
```

After the Function install completes and it's ready for use the `HEALTHY` status
reports `True`.

## Use a function in a composition

Crossplane calls a Function to determine what resources it should create when
you create a composite resource. The Function also tells Crossplane what to do
with these resources when a you update or delete a composite resource.

When Crossplane calls a Function it sends it the current state of the composite
resource. It also sends it the current state of any managed resources the
composite resource owns.

Crossplane knows what Function to call when a composite resource changes by
looking at the Composition the composite resource uses.

{{<expand "Confused about Composite Resources and Compositions?" >}}
Crossplane has four core components that users commonly mix up:

* [Composition]({{<ref "./compositions">}}) - A template to define how to create
  resources.
* [CompositeResourceDefinition]({{<ref "./composite-resource-definitions">}})
  (`XRD`) - A custom API specification. 
* [Composite Resource]({{<ref "./composite-resources">}}) (`XR`) - Created by
  using the custom API defined in a CompositeResourceDefinition. XRs use the
  Composition template to create new managed resources. 
* [Claim]({{<ref "./claims" >}}) (`XRC`) - Like a Composite Resource, but with
  namespace scoping. 
{{</expand >}}

You must set the Composition {{<hover label="single" line="6">}}mode{{</hover>}}
to `Pipeline` to use a Function. To use a Function, add a {{<hover
label="single" line="7">}}pipeline{{</hover>}} of steps inside your Composition
{{<hover label="single" line="4">}}spec{{</hover>}}.

The pipeline must have a step {{<hover label="single"
line="8">}}step{{</hover>}} that calls the Function. The {{<hover label="single"
line="8">}}step{{</hover>}} must specify the {{<hover label="single"
line="10">}}name{{</hover>}} of the Function to call. Here the step references
the name {{<hover label="single"
line="10">}}function-patch-and-transform{{</hover>}}.

Some Functions allow you to specify an {{<hover label="single"
line="11">}}input{{</hover>}}. Different Functions each have a different
{{<hover label="single" line="13">}}kind{{</hover>}} of input. This example uses
Function Patch and Transform. Function Patch and Transform is a function that
implements Crossplane resource templates. Its input kind is `Resources`, and it
accepts [Patch and Transform]({{<ref "./patch-and-transform">}}) {{<hover
label="single" line="14">}}resources{{</hover>}} as input.

```yaml {label="single",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
spec:
  # Removed for Brevity
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
```

{{<hint "important">}}
You can't specify resource templates using the Composition's `spec.resources`
field when you use composition functions. When a Composition's `spec.mode` is
`Pipeline` you can only specify `spec.pipeline`.
{{< /hint >}}

## Use a pipeline of functions in a composition

Crossplane can ask more than one Function what to do when a composite resource
changes. When a Composition has a pipeline of two or more steps, Crossplane
calls them all. It calls them in the order they appear in the pipeline.

<!-- vale Microsoft.Auto = NO -->
<!--
  This linter does not allow "auto-ready", which is part of the name of the
  function.
-->
Crossplane passes each Function in the pipeline the result of the previous
Function. This enables powerful combinations of Functions. In this example,
Crossplane calls {{<hover label="double" line="10">}}function-cue{{</hover>}} to
create an S3 bucket. Crossplane then passes the bucket to {{<hover
label="double" line="23">}}function-auto-ready{{</hover>}}, which marks the
composite resource as ready when the bucket becomes ready.
<!-- vale Microsoft.Auto = YES -->

```yaml {label="double",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
spec:
  # Removed for Brevity
  mode: Pipeline
  pipeline:
  - step: cue-export-resources
    functionRef:
      name: function-cue
    input:
      apiVersion: cue.fn.crossplane.io/v1beta1
      kind: CUEInput
      name: storage-bucket
      export:
        target: Resources
        value: |
          apiVersion: "s3.aws.upbound.io/v1beta1"
          kind: "Bucket"
          spec: forProvider: region: "us-east-2"
  - step: automatically-detect-readiness
    functionRef:
      name: function-auto-ready
```

## Test a composition that uses functions

You can preview the output of any composition that uses composition functions
using the Crossplane CLI. You don't need a Crossplane control plane to do
this. The Crossplane CLI uses Docker Engine to run functions.

```shell
crossplane beta render xr.yaml composition.yaml functions.yaml
```

Provide a composite resource, composition and composition functions to render
the output locally. 

{{<expand "The xr.yaml, composition.yaml and function.yaml files used in the example">}}

You can recreate the output below using by running `crossplane beta render` with
these files.

The `xr.yaml` file contains the composite resource to render:

```yaml
apiVersion: example.crossplane.io/v1
kind: XBucket
metadata:
  name: example-render
spec:
  bucketRegion: us-east-2
```

The `composition.yaml` file contains the Composition to use to render the
composite resource:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: example-render
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1
    kind: XBucket
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
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.bucketRegion
          toFieldPath: spec.forProvider.region
```

The `functions.yaml` file contains the Functions the Composition references in
its pipeline steps:

```yaml
---
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.1.4
```
{{</expand>}}

`crossplane beta render` prints resources as YAML to stdout. It prints the
composite resource first, followed by the resources the composition functions
created.

```yaml
---
apiVersion: example.crossplane.io/v1
kind: XBucket
metadata:
  name: example-render
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  annotations:
    crossplane.io/composition-resource-name: storage-bucket
  generateName: example-render-
  labels:
    crossplane.io/composite: example-render
  ownerReferences:
  - apiVersion: example.crossplane.io/v1
    blockOwnerDeletion: true
    controller: true
    kind: XBucket
    name: example-render
    uid: ""
spec:
  forProvider:
    region: us-east-2
```

{{<hint "important">}}
Running `crossplane beta render` requires [Docker](https://www.docker.com).

See the [Crossplane CLI docs](https://github.com/crossplane/docs/pull/584) to
learn how to install and use the Crossplane CLI.
{{< /hint >}}

## Disable composition functions

Crossplane enables composition functions by default. Disable support for
composition functions by disabling the beta feature flag in Crossplane with
`helm install --args`.

```shell
helm install crossplane --namespace crossplane-system crossplane-stable/crossplane \
    --create-namespace \
    --set "args='{--enable-composition-functions=false}'"
```

The preceding Helm command installs Crossplane with the composition functions
feature flag disabled. Confirm you have disabled composition functions by
looking for a log line:

```shell {copy-lines="1"}
 kubectl -n crossplane-system logs -l app=crossplane
{"level":"info","ts":1674535093.36186,"logger":"crossplane","msg":"Beta feature enabled","flag":"EnableBetaCompositionFunctions"}
```

If you don't see the log line emitted when Crossplane starts, you have disabled
composition functions.
