---
title: App Compositions Quickstart
weight: 200
---

In the previous quickstarts, you learn how to build and access a custom API with Crossplane geared for Cloud infrastructure (such as a _bucket_). Crossplane's composition engine is equally suitable for composing resources on a Kubernetes app cluster. In this guide, you'll learn to create a Composite Resource API that deploys multiple resources together onto a Kubernetes cluster.

## Prerequisites

* A Kubernetes cluster with Crossplane installed.
* `kubectl` installed.

## Create a custom application API

Use the [composition]({{<ref "../concepts/compositions">}}) feature of Crossplane to define a new Kubernetes API for deploying an application composed of a `Deployment`, a `Service`, and an `Ingress`. The custom API is a Kubernetes object. Below is an example of the API we'll create.

```yaml {label="exAPI"}
apiVersion: application.example.com/v1alpha1
kind: Application
metadata:
  name: my-application
spec: 
  image: "nginx"
  ingress:
    enabled: false
```

### Apply the API

Apply this XRD to create the custom application API in your Kubernetes cluster. 

```yaml {label="xrd",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xapplications.application.example.com
spec:
  group: application.example.com
  names:
    kind: XApplication
    plural: xapplications
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              image:
                type: string
              ingress:
                type: object
                properties:
                  enabled:
                    type: boolean
                    default: true
            required:
              - image
    served: true
    referenceable: true
  claimNames:
    kind: Application
    plural: applications
EOF
```

{{<hint "tip" >}}
For more details on the fields and options of Composite Resource Definitions
read the 
[XRD documentation]({{<ref "../concepts/composite-resource-definitions">}}). 
{{< /hint >}}

View the installed XRD with `kubectl get xrd`.  

```shell {copy-lines="1"}
kubectl get xrd
NAME                                   ESTABLISHED   OFFERED   AGE
xapplications.application.example.com  True          True      2s
```

View the new custom API endpoints with `kubectl api-resources | grep application`

```shell {copy-lines="1",label="apiRes"}
kubectl api-resources | grep application
applications                                     application.example.com/v1alpha1       true         Application
xapplications                                    application.example.com/v1alpha1       false        XApplication
```

## Create a deployment template

Define a [composition]({{<ref "../concepts/compositions">}}) that takes the API inputs and templates the underlying Kubernetes resources.

This template creates a `Deployment`, `Service`, and an `Ingress`. 

This Composition takes the user's container image input and optionally configures an ingress in the cluster.

Crossplane's composition engine is flexible and supports a growing list of modules, called _composition functions_ to drive the templatization of resources. You can use:

- [Patch and Transform](https://marketplace.upbound.io/functions/crossplane-contrib/function-patch-and-transform)
- [Go Templating](https://marketplace.upbound.io/functions/crossplane-contrib/function-go-templating)
- [KCL](https://marketplace.upbound.io/functions/crossplane-contrib/function-kcl/)
- [CUE](https://marketplace.upbound.io/functions/crossplane-contrib/function-cue)

and more. You can find composition functions built by the community on the [Upbound Marketplace](https://marketplace.upbound.io/functions). The snippet below demonstrates two of these implementations. Pick whichever you prefer and apply the Composition to your cluster. 

{{< tabs >}}
{{< tab "Patch and Transform" >}}

```yaml {label="comp",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: app-composition
spec:
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
            apiVersion: kubernetes.crossplane.io/v1alpha2
            kind: Object
            metadata:
              name: app-deployment
            spec:
              forProvider:
                manifest:
                  apiVersion: "apps/v1"
                  kind: Deployment
                  metadata:
                    namespace: default
                    annotations:
                      krm.kcl.dev/composition-resource-name: "deployment"
                  spec:
                    replicas: 3
                    selector:
                      matchLabels:
                        app: patch-me
                    template:
                      metadata:
                        labels:
                          app: patch-me
                      spec:
                        containers:
                        - name: patch-me
                          image: patch-me
                          ports:
                          - containerPort: 80
          patches:
            - type: FromCompositeFieldPath
              fromFieldPath: "metadata.name"
              toFieldPath: "spec.forProvider.manifest.spec.selector.matchLabels.app"
            - type: FromCompositeFieldPath
              fromFieldPath: "metadata.name"
              toFieldPath: "spec.forProvider.manifest.spec.template.metadata.labels.app"
            - type: FromCompositeFieldPath
              fromFieldPath: "metadata.name"
              toFieldPath: "spec.forProvider.manifest.spec.template.spec.containers[0].name"
            - type: FromCompositeFieldPath
              fromFieldPath: "spec.image"
              toFieldPath: "spec.forProvider.manifest.spec.template.spec.containers[0].image"
        - name: service
          base:
            apiVersion: kubernetes.crossplane.io/v1alpha2
            kind: Object
            metadata:
              name: app-service
            spec:
              forProvider:
                manifest:
                  apiVersion: v1
                  kind: Service
                  metadata:
                    name: patch-me
                    namespace: default
                  spec:
                    selector:
                      app: patch-me
                    ports:
                    - protocol: "TCP"
                      port: 80
                      targetPort: 80
          patches:
            - type: FromCompositeFieldPath
              fromFieldPath: "metadata.name"
              toFieldPath: "spec.forProvider.manifest.metadata.name"
              transforms:
              - type: string
                string:
                  type: Format
                  fmt: "%s-service"
            - type: FromCompositeFieldPath
              fromFieldPath: "metadata.name"
              toFieldPath: "spec.forProvider.manifest.spec.selector.app"
        - name: ingress
          base:
            apiVersion: kubernetes.crossplane.io/v1alpha2
            kind: Object
            metadata:
              name: app-ingress
            spec:
              forProvider:
                manifest:
                  apiVersion: "networking.k8s.io/v1"
                  kind: Ingress
                  metadata:
                    name: patch-me
                    namespace: default
                  annotations:
                    kubernetes.io/ingress.class: "alb"
                    alb.ingress.kubernetes.io/scheme: "internet-facing"
                    alb.ingress.kubernetes.io/target-type: "ip"
                    alb.ingress.kubernetes.io/healthcheck-path: "/health"
                    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]'
                    alb.ingress.kubernetes.io/target-group-attributes: "stickiness.enabled=true,stickiness.lb_cookie.duration_seconds=60"
                  spec:
                    rules:
                    - http:
                        paths:
                        - path: "/"
                          pathType: "Prefix"
                          backend:
                            service:
                              name: patch-me
                              port:
                                number: 80
          patches:
            - type: FromCompositeFieldPath
              fromFieldPath: "metadata.name"
              toFieldPath: "spec.forProvider.manifest.metadata.name"
              transforms:
              - type: string
                string:
                  type: Format
                  fmt: "%s-ingress"
            - type: FromCompositeFieldPath
              fromFieldPath: "metadata.name"
              toFieldPath: "spec.forProvider.manifest.spec.rules[0].http.paths[0].backend.service.name"
  - step: filter-composed-resources
    functionRef:
      name: function-cel-filter
    input:
      apiVersion: cel.fn.crossplane.io/v1beta1
      kind: Filters
      filters:
      - name: ingress
        expression: observed.composite.resource.spec.ingress.enabled == true
  compositeTypeRef:
    apiVersion: application.example.com/v1alpha1
    kind: XApplication
EOF
```

Apply this Function to install `function-patch-and-transform`:

```yaml {label="install"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-patch-and-transform:v0.1.4
EOF
```

Apply this Function to install `function-cel-filter`:

```yaml {label="install"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1beta1
kind: Function
metadata:
  name: function-cel-filter
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-cel-filter:v0.1.1
EOF
```

{{<hint "tip" >}}
Read the [Composition documentation]({{<ref "../concepts/compositions">}}) for
more information on configuring Compositions and all the available options.

Read the 
[Patch and Transform function documentation]({{<ref "../guides/function-patch-and-transform">}}) 
for more information on how it uses patches to map user inputs to Composition
resource templates.
{{< /hint >}}

{{< /tab >}}

{{< tab "KCL" >}}

Save the following to a file called `composition-kcl.yaml` locally, then apply it to your cluster:

```yaml {label="comp",copy-lines="all"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: app-composition
spec:
  mode: Pipeline
  pipeline:
  - step: compose-kcl
    functionRef:
      name: function-kcl
    input:
      apiVersion: krm.kcl.dev/v1alpha1
      kind: KCLInput
      metadata:
        name: basic
      spec:
        target: Resources
        source: |
          oxr = option("params").oxr
          deployment = {
              apiVersion: "kubernetes.crossplane.io/v1alpha2"
              kind: "Object"
              metadata.name = "app-deployment"
              spec.forProvider.manifest = {
                apiVersion: "apps/v1"
                kind: "Deployment"
                metadata.namespace: "default"
                metadata.annotations: {
                  "krm.kcl.dev/composition-resource-name" = "deployment"
                }
                spec = {
                  replicas: 3
                  selector.matchLabels.app: oxr?.metadata?.name
                  template = {
                    metadata.labels.app: oxr?.metadata?.name
                    spec = {
                      containers = [{
                        name: oxr?.metadata?.name
                        image: oxr?.spec?.image
                        ports = [{
                          containerPort: 80
                        }]
                      }]
                    }
                  }
                }
              }
          } 
          service = {
              apiVersion: "kubernetes.crossplane.io/v1alpha2"
              kind: "Object"
              metadata.name = "app-service"
              metadata.annotations: {
                "krm.kcl.dev/composition-resource-name" = "service"
              }
              spec.forProvider.manifest = {
                apiVersion: "v1"
                kind: "Service"
                metadata.name: '${oxr.metadata.name}-service'
                metadata.namespace: "default"
                spec = {
                  selector.app: oxr?.metadata?.name
                  ports: [{
                    protocol: "TCP"
                    port: 80
                    targetPort: 80
                  }]
                }
              }
          }
          ingress = [{
              apiVersion: "kubernetes.crossplane.io/v1alpha2"
              kind: "Object"
              metadata.name = "app-ingress"
              metadata.annotations: {
                "krm.kcl.dev/composition-resource-name" = "ingress"
              }
              spec.forProvider.manifest = {
                apiVersion: "networking.k8s.io/v1"
                kind: "Ingress"
                metadata.name: '${oxr.metadata.name}-ingress'
                metadata.namespace: "default"
                annotations = {
                  "kubernetes.io/ingress.class": "alb"
                  "alb.ingress.kubernetes.io/scheme": "internet-facing"
                  "alb.ingress.kubernetes.io/target-type": "ip"
                  "alb.ingress.kubernetes.io/healthcheck-path": "/health"
                  "alb.ingress.kubernetes.io/listen-ports": '[{"HTTP": 80}]'
                  "alb.ingress.kubernetes.io/target-group-attributes": "stickiness.enabled=true,stickiness.lb_cookie.duration_seconds=60"
                }
                spec.rules = [{
                  http.paths = [{
                    path: "/"
                    pathType: "Prefix"
                    backend.service = {
                      name: oxr?.metadata?.name 
                      port.number: 80
                    }
                  }]
                }]
              }
          }] if oxr?.spec.ingress.enabled else []
          _items = [deployment, service]
          _items += ingress
          items = _items
  compositeTypeRef:
    apiVersion: application.example.com/v1alpha1
    kind: XApplication
```

Apply it to your cluster:
```shell
kubectl apply -f composition-kcl.yaml
```

Apply this Function to install `function-kcl`:

```yaml {label="install"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-kcl
spec:
  package: xpkg.upbound.io/crossplane-contrib/function-kcl:v0.11.1
EOF
```

{{<hint "tip" >}}
Read the [Composition documentation]({{<ref "../concepts/compositions">}}) for
more information on configuring Compositions and all the available options.
{{< /hint >}}

{{< /tab >}}
{{< /tabs >}}

View the Composition with `kubectl get composition`

```shell {copy-lines="1"}
kubectl get composition
NAME              XR-KIND        XR-APIVERSION                      AGE
app-composition   XApplication   application.example.com/v1alpha1   5s
```

### Install and configure provider-kubernetes

This guide uses _provider-kubernetes_ to compose resources running in the same cluster where Crossplane is installed. Install the provider in your cluster:

```shell
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-kubernetes
spec:
  package: xpkg.upbound.io/upbound/provider-kubernetes:v0
EOF
```

Configure the provider to have permission to create resources in the cluster.

```shell
SA=$(kubectl -n crossplane-system get sa -o name | grep provider-kubernetes | sed -e 's|serviceaccount\/|crossplane-system:|g')
kubectl create clusterrolebinding provider-kubernetes-admin-binding --clusterrole cluster-admin --serviceaccount="${SA}"
cat <<EOF | kubectl apply -f -
apiVersion: kubernetes.crossplane.io/v1alpha1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: InjectedIdentity
EOF
```

The composition above uses [provider-kubernetes](https://marketplace.upbound.io/providers/upbound/provider-kubernetes) to compose other resources in the same Kubernetes cluster where Crossplane's installed. Whereas many other Crossplane providers define several high-fidelity Managed Resources, _provider-kubernetes_ defines a `kind: Object`. This API type can be used to manage **any** Kubernetes object--not just Kubernetes core resources, but also other Custom Resources defined by any Kubernetes Operator or Controller installed on the same cluster.

{{<hint "tip" >}}
Crossplane compositions natively compose Crossplane Managed Resources and _provider-kubernetes_ is crucial for enabling Crossplane to compose other types of Kubernetes resource. In the [Crossplane V2 proposal](https://blog.crossplane.io/announcing-crossplane-v2-proposal/), Crossplane compositions will natively support _any_ Kubernetes resource, not just Managed Resources.
{{< /hint >}}

Read the provider-kubernetes [documentation](https://github.com/crossplane-contrib/provider-kubernetes) on GitHub to learn about advanced configuration options.

## Access the custom API

With the custom API (XRD) installed and associated to a resource template
(Composition) users can access the API to create resources.

Create an {{<hover label="xr" line="2">}}Application{{</hover>}} object to create the
cloud resources.

```yaml {copy-lines="all",label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: application.example.com/v1alpha1
kind: XApplication
metadata:
  name: my-app
spec: 
  image: "nginx"
  ingress:
    enabled: true
EOF
```

View the resource with `kubectl get xapplications`.

```shell {copy-lines="1"}
kubectl get xapplications
NAME    SYNCED   READY   COMPOSITION       AGE
my-app  True     True    app-composition   14s
```

This object is a Crossplane _composite resource_ (also called an `XR`).  
It's a
single object representing the collection of resources created from the
Composition template. 

View the individual resources with `kubectl get managed`

```shell {copy-lines="1"}
kubectl get managed
NAME                                             KIND         PROVIDERCONFIG   SYNCED   READY   AGE
object.kubernetes.crossplane.io/app-deployment   Deployment   default          True     True    45s
object.kubernetes.crossplane.io/app-ingress      Ingress      default          True     True    45s
object.kubernetes.crossplane.io/app-service      Service      default          True     True    45s
```

Delete the resources with `kubectl delete xapplication`.

```shell {copy-lines="1"}
kubectl delete xapplication my-app
xapplication.application.example.com "my-app" deleted
```

Verify Crossplane deleted the resources with `kubectl get managed`

```shell {copy-lines="1"}
kubectl get managed
No resources found
```