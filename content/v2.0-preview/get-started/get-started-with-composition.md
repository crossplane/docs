---
title: Get Started With Composition
weight: 200
---

This guide shows how to create a new kind of custom resource named `App`. When a
user calls the custom resource API to create an `App`, Crossplane creates a
`Deployment` and a `Service`.

**Crossplane calls this _composition_.** The `App` is _composed of_ the
`Deployment` and the `Service`.


{{<hint "tip">}}
The guide shows how to configure composition using YAML, Python, KCL, and
templated YAML. You can pick your preferred language.
{{</hint>}}

An `App` custom resource looks like this:

```yaml
apiVersion: example.crossplane.io/v1
kind: App
metadata:
  namespace: default
  name: my-app
spec:
  image: nginx
status:
  replicas: 2  # Copied from the Deployment's status
  address: 10.0.0.1  # Copied from the Service's status
```

**The `App` is the custom API Crossplane users use to configure an app.**

When users create an `App` Crossplane creates this `Deployment` and `Service`:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: default
  name: my-app-dhj3a
  labels:
    example.crossplane.io/app: my-app  # Copied from the App's name
spec:
  replicas: 2
  selector:
    matchLabels:
      example.crossplane.io/app: my-app  # Copied from the App's name
  template:
    metadata:
      labels:
        example.crossplane.io/app: my-app  # Copied from the App's name
    spec:
      containers:
      - name: app
        image: nginx  # Copied from the App's spec
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  namespace: default
  name: my-app-03mda
  labels:
    example.crossplane.io/app: my-app  # Copied from the App's name
spec:
  selector:
    example.crossplane.io/app: my-app  # Copied from the App's name
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
```

Crossplane builds on Kubernetes, so users can use `kubectl` or any other tool
from the Kubernetes ecosystem to work with apps.

{{<hint "tip">}}
Kubernetes custom resources are just JSON REST APIs, so users can use any tool
that supports REST APIs to work with apps.
{{</hint>}}

## Prerequisites

This quickstart requires:

* A Kubernetes cluster with at least 2 GB of RAM
* The Crossplane v2 preview [installed on the Kubernetes cluster]({{<ref "install">}})

## Create the custom resource

Follow these steps to create a new kind of custom resource using Crossplane:

1. [Define](#define-the-schema) the schema of the `App` custom resource
1. [Install](#install-the-function) the function you want to use to configure
    how Crossplane composes apps
1. [Configure](#configure-the-composition) how Crossplane composes apps

After you complete these steps you can
[use the new `App` custom resource](#use-the-custom-resource).

### Define the schema

Crossplane calls a custom resource that's powered by composition a _composite
resource_, or XR.

{{<hint "note">}}
Kubernetes calls user-defined API resources _custom resources_.

Crossplane calls user-defined API resources that use composition _composite
resources_.

A composite resource is a kind of custom resource.
{{</hint>}}

Create this _composite resource definition_ (XRD) to define the schema of the
new `App` composite resource (XR).

```yaml
apiVersion: apiextensions.crossplane.io/v2alpha1
kind: CompositeResourceDefinition
metadata:
  name: apps.example.crossplane.io
spec:
  scope: Namespaced
  group: example.crossplane.io
  names:
    kind: App
    plural: apps
  versions:
  - name: v1
    served: true
    referenceable: true
    schema:
     openAPIV3Schema:
       type: object
       properties:
        spec:
          type: object
          properties:
            image:
              description: The app's OCI container image.
              type: string
          required:
          - image
        status:
          type: object
          properties:
            replicas:
              description: The number of available app replicas.
              type: integer
            address:
              description: The app's IP address.
              type: string
```

Save the XRD as `xrd.yaml` and apply it:

```shell
kubectl apply -f xrd.yaml
```

Check that Crossplane has established the XRD:

``` shell {copy-lines="1"}
kubectl get -f xrd.yaml
NAME                         ESTABLISHED   OFFERED   AGE
apps.example.crossplane.io   True                    21s
```

Now that Crossplane has established the XRD, Kubernetes is serving API requests
for the new `App` XR.

Crossplane now knows it's responsible for the new `App` XR, but it doesn't know
what to do when you create or update one. You tell Crossplane what to do by
[installing a function](#install-the-function) and
[configuring a composition](#configure-the-composition).

### Install the function

You can use different _composition functions_ to configure what Crossplane does
when someone creates or updates a composite resource (XR). Composition functions
are like configuration language plugins.

Pick what language to use to configure how Crossplane turns an `App` XR into a
`Deployment` and a `Service`.

{{< tabs >}}

{{< tab "YAML" >}}
YAML is a good choice for small, static compositions. It doesn't support loops
or conditionals.

Create this composition function to install YAML support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: crossplane-contrib-function-patch-and-transform
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.8.2
```

Save the function as `fn.yaml` and apply it:

```shell
kubectl apply -f fn.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f fn.yaml
NAME                                              INSTALLED   HEALTHY   PACKAGE                                                                     AGE
crossplane-contrib-function-patch-and-transform   True        True      xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.8.2   10s
```
{{< /tab >}}

{{< tab "Templated YAML" >}}
Templated YAML is a good choice if you're used to writing
[Helm charts](https://helm.sh).

Create this composition function to install templated YAML support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: crossplane-contrib-function-go-templating
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-go-templating:v0.9.2
```

Save the function as `fn.yaml` and apply it:

```shell
kubectl apply -f fn.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f fn.yaml
NAME                                        INSTALLED   HEALTHY   PACKAGE                                                               AGE
crossplane-contrib-function-go-templating   True        True      xpkg.crossplane.io/crossplane-contrib/function-go-templating:v0.9.2   9s
```
{{< /tab >}}

{{< tab "Python" >}}
Python is a good choice for compositions with dynamic logic. You can use the
full [Python standard library](https://docs.python.org/3/library/index.html).

Create this composition function to install Python support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: crossplane-contrib-function-python
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-python:v0.1.0
```

Save the function as `fn.yaml` and apply it:

```shell
kubectl apply -f fn.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f fn.yaml
NAME                                 INSTALLED   HEALTHY   PACKAGE                                                        AGE
crossplane-contrib-function-python   True        True      xpkg.crossplane.io/crossplane-contrib/function-python:v0.1.0   12s
```
{{< /tab >}}

{{< tab "KCL" >}}
[KCL](https://kcl-lang.io) is a good choice for compositions with dynamic logic.
It's fast and sandboxed.

Create this composition function to install KCL support:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: crossplane-contrib-function-kcl
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-kcl:v0.11.2
```

Save the function as `fn.yaml` and apply it:

```shell
kubectl apply -f fn.yaml
```

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f fn.yaml
NAME                              INSTALLED   HEALTHY   PACKAGE                                                      AGE
crossplane-contrib-function-kcl   True        True      xpkg.crossplane.io/crossplane-contrib/function-kcl:v0.11.2   6s
```
{{< /tab >}}

{{</ tabs >}}

### Configure the composition

A composition tells Crossplane what functions to call when you create or
update a composite resource (XR).

Create a composition to tell Crossplane what to do when you create or update an
`App` XR.

{{< tabs >}}

{{< tab "YAML" >}}
Create this composition to use YAML to configure Crossplane:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: app-yaml
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1
    kind: App
  mode: Pipeline
  pipeline:
  - step: create-deployment-and-service
    functionRef:
      name: crossplane-contrib-function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: deployment
        base:
          apiVersion: apps/v1
          kind: Deployment
          spec:
            replicas: 2
            template:
              spec:
                containers:
                - name: app
                  ports:
                  - containerPort: 80
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: metadata.labels[example.crossplane.io/app]
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.selector.matchLabels[example.crossplane.io/app]
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.template.metadata.labels[example.crossplane.io/app]
        - type: FromCompositeFieldPath
          fromFieldPath: spec.image
          toFieldPath: spec.template.spec.containers[0].image
        - type: ToCompositeFieldPath
          fromFieldPath: status.availableReplicas
          toFieldPath: status.replicas
        readinessChecks:
        - type: MatchCondition
          matchCondition:
            type: Available
            status: "True"
      - name: service
        base:
          apiVersion: v1
          kind: Service
          spec:
            ports:
            - protocol: TCP
              port: 8080
              targetPort: 80
        patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: metadata.labels[example.crossplane.io/app]
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.selector[example.crossplane.io/app]
        - type: ToCompositeFieldPath
          fromFieldPath: spec.clusterIP
          toFieldPath: status.address
        readinessChecks:
        - type: NonEmpty
          fieldPath: spec.clusterIP
```
{{< /tab >}}

{{< tab "Templated YAML" >}}
Create this composition to use templated YAML to configure Crossplane:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: app-templated-yaml
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1
    kind: App
  mode: Pipeline
  pipeline:
  - step: create-deployment-and-service
    functionRef:
      name: crossplane-contrib-function-go-templating
    input:
      apiVersion: gotemplating.fn.crossplane.io/v1beta1
      kind: GoTemplate
      source: Inline
      inline:
        template: |
          ---
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            annotations:
              gotemplating.fn.crossplane.io/composition-resource-name: deployment
              {{ if eq (.observed.resources.deployment | getResourceCondition "Available").Status "True" }}
              gotemplating.fn.crossplane.io/ready: "True"
              {{ end }}
            labels:
              example.crossplane.io/app: {{ .observed.composite.resource.metadata.name }}
          spec:
            replicas: 2
            selector:
              matchLabels:
                example.crossplane.io/app: {{ .observed.composite.resource.metadata.name }}
            template:
              metadata:
                labels:
                  example.crossplane.io/app: {{ .observed.composite.resource.metadata.name }}
              spec:
                containers:
                - name: app
                  image: {{ .observed.composite.resource.spec.image }}
                  ports:
                  - containerPort: 80
          ---
          apiVersion: v1
          kind: Service
          metadata:
            annotations:
              gotemplating.fn.crossplane.io/composition-resource-name: service
              {{ if (get (getComposedResource . "service").spec "clusterIP") }}
              gotemplating.fn.crossplane.io/ready: "True"
              {{ end }}
            labels:
              example.crossplane.io/app: {{ .observed.composite.resource.metadata.name }}
          spec:
            selector:
              example.crossplane.io/app: {{ .observed.composite.resource.metadata.name }}
            ports:
            - protocol: TCP
              port: 8080
              targetPort: 80
          ---
          apiVersion: example.crossplane.io/v1
          kind: App
          status:
            replicas: {{ get (getComposedResource . "deployment").status "availableReplicas" | default 0 }}
            address: {{ get (getComposedResource . "service").spec "clusterIP" | default "" | quote }}
```
{{< /tab >}}

{{< tab "Python" >}}
Create this composition to use Python to configure Crossplane:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: app-python
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1
    kind: App
  mode: Pipeline
  pipeline:
  - step: create-deployment-and-service
    functionRef:
      name: crossplane-contrib-function-python
    input:
      apiVersion: python.fn.crossplane.io/v1beta1
      kind: Script
      script: |
        def compose(req, rsp):
            observed_xr = req.observed.composite.resource

            rsp.desired.resources["deployment"].resource.update({
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                  "labels": {"example.crossplane.io/app": observed_xr["metadata"]["name"]},
                },
                "spec": {
                    "replicas": 2,
                    "selector": {"matchLabels": {"example.crossplane.io/app": observed_xr["metadata"]["name"]}},
                    "template": {
                      "metadata": {
                        "labels": {"example.crossplane.io/app": observed_xr["metadata"]["name"]},
                      },
                      "spec": {
                        "containers": [{
                          "name": "app",
                          "image": observed_xr["spec"]["image"],
                          "ports": [{"containerPort": 80}]
                        }],
                      },
                    },
                },
            })

            observed_deployment = req.observed.resources["deployment"].resource
            if "status" in observed_deployment:
              if "availableReplicas" in observed_deployment["status"]:
                rsp.desired.composite.resource.get_or_create_struct("status")["replicas"] = observed_deployment["status"]["availableReplicas"]
              if "conditions" in observed_deployment["status"]:
                for condition in observed_deployment["status"]["conditions"]:
                  if condition["type"] == "Available" and condition["status"] == "True":
                    rsp.desired.resources["deployment"].ready = True

            rsp.desired.resources["service"].resource.update({
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                  "labels": {"example.crossplane.io/app": observed_xr["metadata"]["name"]},
                },
                "spec": {
                  "selector": {"example.crossplane.io/app": observed_xr["metadata"]["name"]},
                  "ports": [{"protocol": "TCP", "port": 8080, "targetPort": 80}],
                },
            })

            observed_service = req.observed.resources["service"].resource
            if "spec" in observed_service and "clusterIP" in observed_service["spec"]:
              rsp.desired.composite.resource.get_or_create_struct("status")["address"] = observed_service["spec"]["clusterIP"]
              rsp.desired.resources["service"].ready = True
```

{{<hint "tip">}}
You can write your own function in Python.

It's a good idea to write your own function for larger configurations. When you
write your own function you can write multiple files of Python. You don't embed
the Python in YAML, so it's easier to use a Python IDE.

Read the [guide to writing a composition function in Python]({{<ref "../guides/write-a-composition-function-in-python">}}).
{{</hint>}}
{{< /tab >}}

{{< tab "KCL" >}}
Create this composition to use KCL to configure Crossplane:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: app-kcl
spec:
  compositeTypeRef:
    apiVersion: example.crossplane.io/v1
    kind: App
  mode: Pipeline
  pipeline:
  - step: create-deployment-and-service
    functionRef:
      name: crossplane-contrib-function-kcl
    input:
      apiVersion: krm.kcl.dev/v1alpha1
      kind: KCLInput
      spec:
        source: |
          observed_xr = option("params").oxr

          _desired_deployment = {
            apiVersion = "apps/v1"
            kind = "Deployment"
            metadata = {
              annotations = {
                "krm.kcl.dev/composition-resource-name" = "deployment"
              }
              labels = {"example.crossplane.io/app" = observed_xr.metadata.name}
            }
            spec = {
              replicas = 2
              selector.matchLabels = {"example.crossplane.io/app" = observed_xr.metadata.name}
              template = {
                metadata.labels = {"example.crossplane.io/app" = observed_xr.metadata.name}
                spec.containers = [{
                  name = "app"
                  image = observed_xr.spec.image
                  ports = [{containerPort = 80}]
                }]
              }
            }
          }

          observed_deployment = option("params").ocds["deployment"]?.Resource
          if any_true([c.type == "Available" and c.status == "True" for c in observed_deployment?.status?.conditions or []]):
            _desired_deployment.metadata.annotations["krm.kcl.dev/ready"] = "True"

          _desired_service = {
            apiVersion = "v1"
            kind = "Service"
            metadata = {
              annotations = {
                "krm.kcl.dev/composition-resource-name" = "service"
              }
              labels = {"example.crossplane.io/app" = observed_xr.metadata.name}
            }
            spec = {
              selector = {"example.crossplane.io/app" = observed_xr.metadata.name}
              ports = [{protocol = "TCP", port = 8080, targetPort = 80}]
            }
          }

          observed_service = option("params").ocds["service"]?.Resource
          if observed_service?.spec?.clusterIP:
            _desired_service.metadata.annotations["krm.kcl.dev/ready"] = "True"
            
          _desired_xr = {
            **option("params").dxr

            status.address = observed_service?.spec?.clusterIP or ""
            status.replicas = observed_deployment?.status?.availableReplicas or 0
          }

          items = [_desired_deployment, _desired_service, _desired_xr]
```
{{< /tab >}}

{{</ tabs >}}

Save the composition as `composition.yaml` and apply it:

```shell
kubectl apply -f composition.yaml
```

{{<hint "note">}}
A composition can include multiple functions.

Functions can change the results of earlier functions in the pipeline.
Crossplane uses the result returned by the last function.
{{</hint>}}

## Use the custom resource

Crossplane now understands `App` custom resources.

Create an `App`:

```yaml
apiVersion: example.crossplane.io/v1
kind: App
metadata:
  namespace: default
  name: my-app
spec:
  image: nginx
```

Save the `App` as `app.yaml` and apply it:

```shell
kubectl apply -f app.yaml
```

Check that the `App` is ready:

```shell {copy-lines="1"}
kubectl get -f app.yaml
NAME     SYNCED   READY   COMPOSITION   AGE
my-app   True     True    app-yaml      56s
```

{{<hint "note">}}
The `COMPOSITION` column shows what composition the `App` is using.

You can create multiple compositions for each kind of XR.
[Read the XR page]({{<ref "../concepts/composite-resources">}}) to learn how to
select which composition Crossplane uses.
{{</hint>}}

Check that Crossplane created a `Deployment` and a `Service`:

```shell {copy-lines="1"}
kubectl get deploy,service -l example.crossplane.io/app=my-app
NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-app-2r2rk   2/2     2            2           11m

NAME                   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
service/my-app-xfkzg   ClusterIP   10.96.148.56   <none>        8080/TCP   11m
```

{{<hint "tip">}}
Use `kubectl edit -f app.yaml` to edit the `App`'s image. Crossplane updates
the `Deployment`'s image to match.
{{</hint>}}

Delete the `App`.

```shell {copy-lines="1"}
kubectl delete -f app.yaml
```

When you delete the `App`, Crossplane deletes the `Deployment` and `Service`.

## Next steps

Managed resources (MRs) are ready-made Kubernetes custom resources. 

Crossplane has an extensive library of managed resources you can use to manage
almost any cloud provider, or cloud native software.

[Get started with managed resources]({{<ref "get-started-with-managed-resources">}})
to learn more about them.

You can use MRs with composition. Try updating your `App` composition to include
an MR.
