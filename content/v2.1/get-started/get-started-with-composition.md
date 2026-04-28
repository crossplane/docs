---
title: Get Started With Composition
weight: 200
description: "Build custom APIs with Crossplane composition"
---

This guide shows how to create a new kind of custom resource named `App`. When a
user calls the custom resource API to create an `App`, Crossplane creates a
`Deployment` and a `Service`.

**Crossplane calls this _composition_.** The `App` is _composed of_ the
`Deployment` and the `Service`.


{{<hint "tip">}}
The guide shows how to configure composition using YAML, templated YAML, Python,
and KCL. You can pick your preferred language.
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

This guide requires:

* A Kubernetes cluster with at least 2 GB of RAM
* Crossplane v2 [installed on the Kubernetes cluster]({{<ref "install">}})

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

{{< manifest path="get-started/composition/xrd.yaml" >}}

Check that Crossplane has established the XRD:

``` shell {copy-lines="1"}
kubectl get -f {{< manifest-url path="get-started/composition/xrd.yaml" >}}
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

{{< manifest path="get-started/composition/fn-patch-and-transform.yaml" >}}

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f {{< manifest-url path="get-started/composition/fn-patch-and-transform.yaml" >}}
NAME                                              INSTALLED   HEALTHY   PACKAGE                                                                     AGE
crossplane-contrib-function-patch-and-transform   True        True      xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.8.2   10s
```
{{< /tab >}}

{{< tab "Templated YAML" >}}
Templated YAML is a good choice if you're used to writing
[Helm charts](https://helm.sh).

Create this composition function to install templated YAML support:

{{< manifest path="get-started/composition/fn-go-templating.yaml" >}}

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f {{< manifest-url path="get-started/composition/fn-go-templating.yaml" >}}
NAME                                        INSTALLED   HEALTHY   PACKAGE                                                               AGE
crossplane-contrib-function-go-templating   True        True      xpkg.crossplane.io/crossplane-contrib/function-go-templating:v0.9.2   9s
```
{{< /tab >}}

{{< tab "Python" >}}
Python is a good choice for compositions with dynamic logic. You can use the
full [Python standard library](https://docs.python.org/3/library/index.html).

Create this composition function to install Python support:

{{< manifest path="get-started/composition/fn-python.yaml" >}}

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f {{< manifest-url path="get-started/composition/fn-python.yaml" >}}
NAME                                 INSTALLED   HEALTHY   PACKAGE                                                        AGE
crossplane-contrib-function-python   True        True      xpkg.crossplane.io/crossplane-contrib/function-python:v0.1.0   12s
```
{{< /tab >}}

{{< tab "KCL" >}}
[KCL](https://kcl-lang.io) is a good choice for compositions with dynamic logic.
It's fast and sandboxed.

Create this composition function to install KCL support:

{{< manifest path="get-started/composition/fn-kcl.yaml" >}}

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f {{< manifest-url path="get-started/composition/fn-kcl.yaml" >}}
NAME                              INSTALLED   HEALTHY   PACKAGE                                                      AGE
crossplane-contrib-function-kcl   True        True      xpkg.crossplane.io/crossplane-contrib/function-kcl:v0.11.2   6s
```
{{< /tab >}}

{{< tab "Pythonic" >}}
[Pythonic](https://github.com/crossplane-contrib/function-pythonic?tab=readme-ov-file#function-pythonic)
is an excellent choice for compositions with dynamic logic. The full flexibility and power of python is
available using a set of python classes with an elegant and terse syntax that hides the details of the low level
Crossplane function APIs.

Create this composition function to install Pythonic support:

{{< manifest path="get-started/composition/fn-pythonic.yaml" >}}

Check that Crossplane installed the function:

```shell {copy-lines="1"}
kubectl get -f {{< manifest-url path="get-started/composition/fn-pythonic.yaml" >}}
NAME               INSTALLED  HEALTHY  PACKAGE                                                         AGE
function-pythonic  True       True     xpkg.crossplane.io/crossplane-contrib/function-pythonic:v0.3.0  1m
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

{{< manifest path="get-started/composition/composition-yaml.yaml" >}}
{{< /tab >}}

{{< tab "Templated YAML" >}}
Create this composition to use templated YAML to configure Crossplane:

{{< manifest path="get-started/composition/composition-templated-yaml.yaml" >}}
{{< /tab >}}

{{< tab "Python" >}}
Create this composition to use Python to configure Crossplane:

{{< manifest path="get-started/composition/composition-python.yaml" >}}

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

{{< manifest path="get-started/composition/composition-kcl.yaml" >}}
{{< /tab >}}

{{< tab "Pythonic" >}}
Create this composition to use Pythonic to configure Crossplane:

{{< manifest path="get-started/composition/composition-pythonic.yaml" >}}
{{< /tab >}}

{{</ tabs >}}

{{<hint "note">}}
A composition can include multiple functions.

Functions can change the results of earlier functions in the pipeline.
Crossplane uses the result returned by the last function.
{{</hint>}}

{{<hint "tip">}}
If you edit this composition to include a different kind of resource you might
need to grant Crossplane access to compose it. Read
[the composition documentation]({{<ref "../composition/compositions#grant-access-to-composed-resources">}})
to learn how to grant Crossplane access.
{{</hint>}}

## Use the custom resource

Crossplane now understands `App` custom resources.

Create an `App`:

{{< manifest path="get-started/composition/app.yaml" >}}

Check that the `App` is ready:

```shell {copy-lines="1"}
kubectl get -f {{< manifest-url path="get-started/composition/app.yaml" >}}
NAME     SYNCED   READY   COMPOSITION   AGE
my-app   True     True    app-yaml      56s
```

{{<hint "note">}}
The `COMPOSITION` column shows what composition the `App` is using.

You can create multiple compositions for each kind of XR.
[Read the XR page]({{<ref "../composition/composite-resources">}}) to learn how to
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
Edit the `App`'s image:

```shell
kubectl edit -f {{< manifest-url path="get-started/composition/app.yaml" >}}
```

Crossplane updates the `Deployment`'s image to match.
{{</hint>}}

Delete the `App`.

```shell {copy-lines="1"}
kubectl delete -f {{< manifest-url path="get-started/composition/app.yaml" >}}
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
