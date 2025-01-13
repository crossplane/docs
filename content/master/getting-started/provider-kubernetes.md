 ---
title: KubeAdm Quickstart 
weight: 110
---

Connect Crossplane to in-cluster kubernetes to create and manage resources from Kubernetes 
with the 
[Upbound Kubernetes Provider](https://marketplace.upbound.io/providers/upbound/provider-kubernetes/).

## Prerequisites
This quickstart requires:
* a Kubernetes cluster with at least 2 GB of RAM
* permissions to create pods and secrets in the Kubernetes cluster
* [Helm](https://helm.sh/) version v3.2.0 or later
* CNI

{{<include file="/master/getting-started/install-crossplane-include.md" type="page" >}}

## Install the Kubernetes provider

Install the Azure Network resource provider into the Kubernetes cluster with a Kubernetes configuration 
file. 

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-network
spec:
  package: xpkg.upbound.io/upbound/provider-kubernetes:v0.16.0
  runtimeConfigRef:
    apiVersion: pkg.crossplane.io/v1beta1
    kind: DeploymentRuntimeConfig
    name: provider-kubernetes
EOF
```
```yaml
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1beta1
kind: DeploymentRuntimeConfig
metadata:
  name: provider-kubernetes
spec:
  serviceAccountTemplate:
    metadata:
      name: provider-kubernetes
EOF
---
```yaml {label="ClusterRoleBinding",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: provider-kubernetes-cluster-admin
subjects:
  - kind: ServiceAccount
    name: provider-kubernetes
    namespace: crossplane-system
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
EOF
---
The Crossplane {{< hover label="provider" line="3" >}}Provider{{</hover>}}
installs the Kubernetes _Custom Resource Definitions_ (CRDs) representing Kubernetes objects.
These CRDs allow you to create resources inside Kubernetes.
Verify the provider installed with `kubectl get providers`. 


```shell {copy-lines="1",label="getProvider"}
kubectl get providers
NAME                            INSTALLED   HEALTHY   PACKAGE                                                  AGE
provider-kubernetes          True        True      xpkg.upbound.io/upbound/provider-azure-network:v1.16.0  38s
```



## Create a ProviderConfig
A `ProviderConfig` customizes the settings of the Kubernetes Provider.  

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: kubernetes.crossplane.io/v1alpha1
kind: ProviderConfig
metadata:
  name: kubernetes-provider
spec:
  credentials:
    source: InjectedIdentity
EOF
```



## Create a Composite resource definition
A `CompositeResourceDefinition` (XRDs) define the schema for a custom API.
Users create composite resources (XRs) and Claims (XCs) using the API schema defined by an XRD.

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xkubernetesapps.kubernetes.example.org
spec:
  group: kubernetes.example.org
  names:
    kind: XKubernetesApp
    plural: xkubernetesapps
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
                replicas:
                  type: integer
                  default: 2
                image:
                  type: string
                  default: nginx:latest
                port:
                  type: integer
                  default: 80
                hostname:
                  type: string
                  default: example.com
              required:
                - replicas
                - image
                - port
                - hostname
EOF
```
## Create a Composition
A `Composition` is a template for creating multiple managed resources as a single object.
A Composition composes individual managed resources together into a larger, reusable, solution.

```yaml 
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: xkubernetesapp-composition
spec:
  compositeTypeRef:
    apiVersion: kubernetes.example.org/v1alpha1
    kind: XKubernetesApp
  resources:
    - name: deployment
      base:
        apiVersion: kubernetes.crossplane.io/v1alpha2
        kind: Object
        spec:
          forProvider:
            manifest:
              apiVersion: apps/v1
              kind: Deployment
              metadata:
                name: example-deployment
                namespace: default
              spec:
                replicas: 1
                selector:
                  matchLabels:
                    app: example-app
                template:
                  metadata:
                    labels:
                      app: example-app
                  spec:
                    containers:
                      - name: example-container
                        image: nginx:latest
                        ports:
                          - containerPort: 80
          providerConfigRef:
            name: kubernetes-provider
      patches:
        - fromFieldPath: "spec.replicas"
          toFieldPath: "spec.forProvider.manifest.spec.replicas"
        - fromFieldPath: "spec.image"
          toFieldPath: "spec.forProvider.manifest.spec.template.spec.containers[0].image"
    - name: service
      base:
        apiVersion: kubernetes.crossplane.io/v1alpha2
        kind: Object
        spec:
          forProvider:
            manifest:
              apiVersion: v1
              kind: Service
              metadata:
                name: example-service
                namespace: default
              spec:
                selector:
                  app: example-app
                ports:
                  - protocol: TCP
                    port: 80
                    targetPort: 80
          providerConfigRef:
            name: kubernetes-provider
      patches:
        - fromFieldPath: "spec.port"
          toFieldPath: "spec.forProvider.manifest.spec.ports[0].port"
EOF
```
## Create an Abstracted application
Leverage the composition to create an abstraction

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: kubernetes.example.org/v1alpha1
kind: XKubernetesApp
metadata:
  name: my-kubernetes-app
spec:
  replicas: 3
  image: nginx
  port: 8080
  hostname: my-app.example.com
EOF
```
```shell
kubectl get pods
NAME                                  READY   STATUS    RESTARTS   AGE
example-deployment-5f76bbff9b-c5n2r   1/1     Running   0          15s
example-deployment-5f76bbff9b-lch2p   1/1     Running   0          12s
example-deployment-5f76bbff9b-w5n9h   1/1     Running   0          20s
```
* Explore Kubernetes resources that Crossplane can configure in the 
  [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/kubernetes-provider/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with 
  Crossplane users and contributors.   