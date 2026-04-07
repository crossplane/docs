---
title: Scalable Composition
weight: 84
description: "Expose the Kubernetes scale subresource on a composite resource to
  enable kubectl scale, HPA, and KEDA"
---

An XRD can expose the Kubernetes
[`scale` subresource](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#scale-subresource)
on a composite resource. Exposing the `scale` subresource enables standard
Kubernetes scaling tools, including `kubectl scale`, the
[Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/),
and [KEDA](https://keda.sh/), to control the composite resource without knowing
its full schema.

## Example overview

This guide shows how to expose the `scale` subresource by creating a `MyApp`
composite resource that wraps a Kubernetes `Deployment`.

When a user creates a `MyApp`, Crossplane provisions a `Deployment` and wires
the replica count between the composite resource and the `Deployment`. Standard
Kubernetes scaling tools can then drive the replica count without knowing the
full schema of `MyApp`.

An example `MyApp` XR looks like this:

```yaml {copy-lines="none"}
apiVersion: example.org/v1alpha1
kind: MyApp
metadata:
  name: my-app
spec:
  replicas: 1
```

**Behind the scenes, Crossplane:**

1. Creates a `Deployment` (the composed resource) with the requested replica
   count
2. Writes back the observed replica count from the `Deployment` to
   `status.replicas` on the `MyApp`
3. Marks `MyApp` as ready when the `Deployment` is healthy

Because `MyApp` exposes the `scale` subresource, you can scale it without
knowing its full schema:

```shell {copy-lines="none"}
kubectl scale myapp/my-app --replicas=3
```

The Horizontal Pod Autoscaler and KEDA can also target `MyApp` directly using
the same `scale` subresource.

## Prerequisites

This guide requires:

* A Kubernetes cluster
* Crossplane [installed on the Kubernetes cluster]({{<ref "../get-started/install">}})

## Install the functions

Install `function-patch-and-transform` to compose resources and patch
fields between the composite resource and its composed resources:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.10.3
```

Save the function as `fn-pat.yaml` and apply it:

```shell
kubectl apply -f fn-pat.yaml
```

This guide also uses `function-auto-ready`. This function automatically
marks composed resources as ready when they're healthy:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-auto-ready
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-auto-ready:v0.6.3
```

Save this as `fn-auto-ready.yaml` and apply it:

```shell
kubectl apply -f fn-auto-ready.yaml
```

Check that Crossplane installed the functions:

```shell {copy-lines="1"}
kubectl get pkg
NAME                                                      INSTALLED   HEALTHY   PACKAGE                                                                      AGE
function.pkg.crossplane.io/function-auto-ready            True        True      xpkg.crossplane.io/crossplane-contrib/function-auto-ready:v0.6.3             2s
function.pkg.crossplane.io/function-patch-and-transform   True        True      xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.10.3   16s
```

## Configure the XRD

Configure the `scale` subresource per version in the XRD's
{{<hover label="xrdscale" line="22">}}subresources{{</hover>}} field.

```yaml {label="xrdscale"}
apiVersion: apiextensions.crossplane.io/v2
kind: CompositeResourceDefinition
metadata:
  name: myapps.example.org
spec:
  group: example.org
  names:
    kind: MyApp
    plural: myapps
  scope: Namespaced
  versions:
  - additionalPrinterColumns:
    - jsonPath: .spec.replicas
      name: DESIRED
      type: string
    - jsonPath: .status.replicas
      name: CURRENT
      type: string
    name: v1alpha1
    served: true
    referenceable: true
    subresources:
      scale:
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.replicas
        labelSelectorPath: .status.labelSelector
    schema:
      openAPIV3Schema:
        properties:
          spec:
            properties:
              replicas:
                type: integer
          status:
            properties:
              replicas:
                type: integer
              labelSelector:
                type: string
```

Save this as `xrd-scale.yaml` and apply it:

```shell
kubectl apply -f xrd-scale.yaml
```

Verify the XRD exists:

```shell {copy-lines="1"}
kubectl get xrd
NAME                 ESTABLISHED   OFFERED   AGE
myapps.example.org   True                    6s
```

The `scale` block has three fields:

* {{<hover label="xrdscale" line="24">}}specReplicasPath{{</hover>}}: the
  JSON path to the field in the composite resource's `spec` that holds the
  desired replica count. This field must exist in the XRD schema.
* {{<hover label="xrdscale" line="25">}}statusReplicasPath{{</hover>}}: the
  JSON path to the field in the composite resource's `status` that holds the
  observed replica count. This field must exist in the XRD schema.
* {{<hover label="xrdscale" line="26">}}labelSelectorPath{{</hover>}}: an
  optional JSON path to a `string` field in `status` that holds a serialized
  label selector. Required by the Horizontal Pod Autoscaler.

{{<hint "important">}}
Crossplane propagates the `scale` configuration to the generated CRD.
The composition author must implement the scaling logic, for example
by patching `spec.replicas` from the composite resource into a
composed `Deployment`.
{{</hint>}}

## Implement scaling in a Composition

After enabling the `scale` subresource on the XRD, wire the replica count into
the composed resources in the Composition. The following example uses
`function-patch-and-transform` to forward `spec.replicas` from the composite
resource to a `Deployment`:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: myapp
spec:
  compositeTypeRef:
    apiVersion: example.org/v1alpha1
    kind: MyApp
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: deployment
        base:
          apiVersion: apps/v1
          kind: Deployment
          spec:
            replicas: 1
            selector:
              matchLabels:
                app: nginx
            template:
              metadata:
                labels:
                  app: nginx
              spec:
                containers:
                - name: nginx
                  image: nginx:1.29.7-alpine
                  ports:
                  - containerPort: 80
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: spec.replicas
          toFieldPath: spec.replicas
        - type: ToCompositeFieldPath
          fromFieldPath: status.readyReplicas
          toFieldPath: status.replicas
  - step: automatically-detect-readiness
    functionRef:
      name: function-auto-ready
```

Save this as `composition-scale.yaml` and apply it:

```shell
kubectl apply -f composition-scale.yaml
```

Verify the composition exists:

```shell {copy-lines="1"}
kubectl get compositions
NAME    XR-KIND   XR-APIVERSION          AGE
myapp   MyApp     example.org/v1alpha1   3s
```

The composition must also write back the current replica count to
`status.replicas` (and `status.labelSelector` if used) so that autoscalers and
`kubectl scale --current-replicas` read the correct replica count.

## Create a `MyApp` composite resource

With the XRD and Composition in place, create a `MyApp` composite resource:

```yaml
apiVersion: example.org/v1alpha1
kind: MyApp
metadata:
  name: my-app
spec:
  replicas: 1
```

Verify the current replica count:

```shell {copy-lines="1"}
kubectl get myapp/my-app
NAME     DESIRED   CURRENT   SYNCED   READY   COMPOSITION   AGE
my-app   1         1         True     True    myapp         108s
```

## Use the scale subresource

After applying the XRD and Composition, scale a composite resource with
`kubectl scale`:

```shell
kubectl scale myapp/my-app --replicas=3
```

Verify the current replica count:

```shell {copy-lines="1"}
kubectl get myapp/my-app
NAME     DESIRED   CURRENT   SYNCED   READY   COMPOSITION   AGE
my-app   3         3         True     True    myapp         3m26s
```
