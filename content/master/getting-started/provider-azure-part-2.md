---
title: Azure Quickstart Part 2
weight: 120
tocHidden: true
aliases:
  - /master/getting-started/provider-azure-part-3
---

{{< hint "important" >}}
This guide is part 2 of a series.  

[**Part 1**]({{<ref "provider-azure" >}}) covers
to installing Crossplane and connect your Kubernetes cluster to Azure.

{{< /hint >}}

This guide walks you through building and accessing a custom API with Crossplane.

## Prerequisites
* Complete [quickstart part 1]({{<ref "provider-azure" >}}) connecting Kubernetes
  to Azure.
* an Azure account with permissions to create an Azure Virtual Machine, Resource
 Group and Virtual Networking.

{{<expand "Skip part 1 and just get started" >}}
1. Add the Crossplane Helm repository and install Crossplane
```shell
helm repo add \
crossplane-stable https://charts.crossplane.io/stable
helm repo update
&&
helm install crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace
```

2. When the Crossplane pods finish installing and are ready, apply the Azure 
   Provider
   
```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-network
spec:
  package: xpkg.upbound.io/upbound/provider-azure-network:v0.42.1
EOF
```

3. Use the Azure CLI to create a service principal and save the JSON output as 
   `azure-crednetials.json`
{{< editCode >}}
```console
az ad sp create-for-rbac \
--sdk-auth \
--role Owner \
--scopes /subscriptions/$@<subscription_id>$@
```
{{</ editCode >}}

4. Create a Kubernetes secret from the Azure JSON file.
```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret \
generic azure-secret \
-n crossplane-system \
--from-file=creds=./azure-credentials.json
```

5. Create a _ProviderConfig_
```yaml {label="providerconfig",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: azure.upbound.io/v1beta1
metadata:
  name: default
kind: ProviderConfig
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: azure-secret
      key: creds
EOF
```
{{</expand >}}

## Create a custom API

<!-- vale alex.Condescending = NO -->
Crossplane allows you to build your own custom APIs for your users, abstracting
away details about the cloud provider and their resources. You can make your API
as complex or simple as you wish. 
<!-- vale alex.Condescending = YES -->

The custom API is a Kubernetes object.  
Here is an example custom API.

```yaml {label="exAPI"}
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
metadata:
  name: my-vm
spec: 
  location: "US"
```

Like any Kubernetes object the API has a 
{{<hover label="exAPI" line="1">}}version{{</hover>}}, 
{{<hover label="exAPI" line="2">}}kind{{</hover>}} and 
{{<hover label="exAPI" line="5">}}spec{{</hover>}}.

### Define a group and version
To create your own API start by defining an 
[API group](https://kubernetes.io/docs/reference/using-api/#api-groups) and 
[version](https://kubernetes.io/docs/reference/using-api/#api-versioning).  

The _group_ can be any value, but common convention is to map to a fully
qualified domain name. 

<!-- vale gitlab.SentenceLength = NO -->
The version shows how mature or stable the API is and increments when changing,
adding or removing fields in the API.
<!-- vale gitlab.SentenceLength = YES -->

Crossplane doesn't require specific versions or a specific version naming 
convention, but following 
[Kubernetes API versioning guidelines](https://kubernetes.io/docs/reference/using-api/#api-versioning)
is strongly recommended. 

* `v1alpha1` - A new API that may change at any time.
* `v1beta1` - An existing API that's considered stable. Breaking changes are
  strongly discouraged.
* `v1` - A stable API that doesn't have breaking changes. 

This guide uses the group 
{{<hover label="version" line="1">}}compute.example.com{{</hover>}}.

Because this is the first version of the API, this guide uses the version
{{<hover label="version" line="1">}}v1alpha1{{</hover>}}.

```yaml {label="version",copy-lines="none"}
apiVersion: compute.example.com/v1alpha1
```

### Define a kind

The API group is a logical collection of related APIs. In a group are
individual kinds representing different resources.

For example a `compute` group may have a `VirtualMachine` and `BareMetal` kinds.

The `kind` can be anything, but it must be 
[UpperCamelCased](https://kubernetes.io/docs/contribute/style/style-guide/#use-upper-camel-case-for-api-objects).

This API's kind is 
{{<hover label="kind" line="2">}}VirtualMachine{{</hover>}}

```yaml {label="kind",copy-lines="none"}
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
```

### Define a spec

The most important part of an API is the schema. The schema defines the inputs
accepted from users. 

This API allows users to provide a 
{{<hover label="spec" line="4">}}location{{</hover>}} of where to run their 
cloud resources.

All other resource settings can't be configurable by the users. This allows
Crossplane to enforce any policies and standards without worrying about
user errors. 

```yaml {label="spec",copy-lines="none"}
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
spec: 
  location: "US"
```

### Apply the API

Crossplane uses 
{{<hover label="xrd" line="3">}}Composite Resource Definitions{{</hover>}} 
(also called an `XRD`) to install your custom API in
Kubernetes. 

The XRD {{<hover label="xrd" line="6">}}spec{{</hover>}} contains all the
information about the API including the 
{{<hover label="xrd" line="7">}}group{{</hover>}},
{{<hover label="xrd" line="12">}}version{{</hover>}},
{{<hover label="xrd" line="9">}}kind{{</hover>}} and 
{{<hover label="xrd" line="13">}}schema{{</hover>}}.

The XRD's {{<hover label="xrd" line="5">}}name{{</hover>}} must be the
combination of the {{<hover label="xrd" line="10">}}plural{{</hover>}} and 
{{<hover label="xrd" line="7">}}group{{</hover>}}.

The {{<hover label="xrd" line="13">}}schema{{</hover>}} uses the
{{<hover label="xrd" line="14">}}OpenAPIv3{{</hover>}} specification to define
the API {{<hover label="xrd" line="17">}}spec{{</hover>}}.  

The API defines a {{<hover label="xrd" line="20">}}location{{</hover>}} that
must be {{<hover label="xrd" line="22">}}oneOf{{</hover>}} either 
{{<hover label="xrd" line="23">}}EU{{</hover>}} or 
{{<hover label="xrd" line="24">}}US{{</hover>}}.

Apply this XRD to create the custom API in your Kubernetes cluster. 

```yaml {label="xrd",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: virtualmachines.compute.example.com
spec:
  group: compute.example.com
  names:
    kind: VirtualMachine
    plural: virtualmachines
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              location:
                type: string
                oneOf:
                  - pattern: '^EU$'
                  - pattern: '^US$'
            required:
              - location
    served: true
    referenceable: true
  claimNames:
    kind: VirtualMachineClaim
    plural: virtualmachineclaims
EOF
```

Adding the {{<hover label="xrd" line="29">}}claimNames{{</hover>}} allows users
to access this API either at the cluster level with the 
{{<hover label="xrd" line="9">}}VirtualMachine{{</hover>}} endpoint or in a namespace
with the 
{{<hover label="xrd" line="30">}}VirtualMachineClaim{{</hover>}} endpoint. 

The namespace scoped API is a Crossplane _Claim_.

{{<hint "tip" >}}
For more details on the fields and options of Composite Resource Definitions
read the 
[XRD documentation]({{<ref "../concepts/composite-resource-definitions">}}). 
{{< /hint >}}

View the installed XRD with `kubectl get xrd`.  

```shell {copy-lines="1"}
kubectl get xrd
NAME                                  ESTABLISHED   OFFERED   AGE
virtualmachines.compute.example.com   True          True      43s
```

View the new custom API endpoints with `kubectl api-resources | grep VirtualMachine`

```shell {copy-lines="1",label="apiRes"}
kubectl api-resources | grep VirtualMachine
virtualmachineclaims              compute.example.com/v1alpha1           true         VirtualMachineClaim
virtualmachines                   compute.example.com/v1alpha1           false        VirtualMachine
```

## Create a deployment template

When users access the custom API Crossplane takes their inputs and combines them
with a template describing what infrastructure to deploy. Crossplane calls this
template a _Composition_.

The {{<hover label="comp" line="3">}}Composition{{</hover>}} defines all the 
cloud resources to deploy.
Each entry in the template
is a full resource definitions, defining all the resource settings and metadata
like labels and annotations. 

This template creates an Azure
{{<hover label="comp" line="11">}}LinuxVirtualMachine{{</hover>}}
{{<hover label="comp" line="46">}}NetworkInterface{{</hover>}}, 
{{<hover label="comp" line="69">}}Subnet{{</hover>}}
{{<hover label="comp" line="90">}}VirtualNetwork{{</hover>}} and
{{<hover label="comp" line="110">}}ResourceGroup{{</hover>}}.

Crossplane uses {{<hover label="comp" line="34">}}patches{{</hover>}} to apply
the user's input to the resource template.  
This Composition takes the user's 
{{<hover label="comp" line="36">}}location{{</hover>}} input and uses it as the 
{{<hover label="comp" line="37">}}location{{</hover>}} used in the individual 
resource.

Apply this Composition to your cluster. 

```yaml {label="comp",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: crossplane-quickstart-vm-with-network
spec:
  resources:
    - name: quickstart-vm
      base:
        apiVersion: compute.azure.upbound.io/v1beta1
        kind: LinuxVirtualMachine
        spec:
          forProvider:
            adminUsername: adminuser
            adminSshKey:
              - publicKey: ssh-rsa
                  AAAAB3NzaC1yc2EAAAADAQABAAABAQC+wWK73dCr+jgQOAxNsHAnNNNMEMWOHYEccp6wJm2gotpr9katuF/ZAdou5AaW1C61slRkHRkpRRX9FA9CYBiitZgvCCz+3nWNN7l/Up54Zps/pHWGZLHNJZRYyAB6j5yVLMVHIHriY49d/GZTZVNB8GoJv9Gakwc/fuEZYYl4YDFiGMBP///TzlI4jhiJzjKnEvqPFki5p2ZRJqcbCiF4pJrxUQR/RXqVFQdbRLZgYfJ8xGB878RENq3yQ39d8dVOkq4edbkzwcUmwwwkYVPIoDGsYLaRHnG+To7FvMeyO7xDVQkMKzopTQV8AuKpyvpqu0a9pWOMaiCyDytO7GGN
                  example@docs.crossplane.io
                username: adminuser
            location: "Central US"
            osDisk:
              - caching: ReadWrite
                storageAccountType: Standard_LRS
            resourceGroupNameSelector:
              matchControllerRef: true
            size: Standard_B1ms
            sourceImageReference:
              - offer: debian-11
                publisher: Debian
                sku: 11-backports-gen2
                version: latest
            networkInterfaceIdsSelector:
              matchControllerRef: true
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"
    - name: quickstart-nic
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: NetworkInterface
        spec:
          forProvider:
            ipConfiguration:
              - name: crossplane-quickstart-configuration
                privateIpAddressAllocation: Dynamic
                subnetIdSelector:
                  matchControllerRef: true
            location: "Central US"
            resourceGroupNameSelector:
              matchControllerRef: true
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"            
    - name: quickstart-subnet
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: Subnet
        spec:
          forProvider:
            addressPrefixes:
              - 10.0.1.0/24
            virtualNetworkNameSelector:
              matchControllerRef: true
            resourceGroupNameSelector:
              matchControllerRef: true
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"
    - name: quickstart-network
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: VirtualNetwork
        spec:
          forProvider:
            addressSpace:
              - 10.0.0.0/16
            location: "Central US"
            resourceGroupNameSelector:
              matchControllerRef: true
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"
    - name: crossplane-resourcegroup
      base:
        apiVersion: azure.upbound.io/v1beta1
        kind: ResourceGroup
        spec:
          forProvider:
            location: Central US
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"
  compositeTypeRef:
    apiVersion: compute.example.com/v1alpha1
    kind: VirtualMachine
EOF
```

The {{<hover label="comp" line="52">}}compositeTypeRef{{</hover >}} defines
which custom APIs can use this template to create resources.

{{<hint "tip" >}}
Read the [Composition documentation]({{<ref "../concepts/compositions">}}) for
more information on configuring Compositions and all the available options.

Read the 
[Patch and Transform documentation]({{<ref "../concepts/patch-and-transform">}}) 
for more information on how Crossplane uses patches to map user inputs to
Composition resource templates.
{{< /hint >}}

View the Composition with `kubectl get composition`

```shell {copy-lines="1"}
kubectl get composition
NAME                                    XR-KIND           XR-APIVERSION                     AGE
crossplane-quickstart-vm-with-network   XVirtualMachine   custom-api.example.org/v1alpha1   77s
```

## Install the Azure virtual machine provider

Part 1 only installed the Azure Virtual Network Provider. To deploying virtual
machines requires the Azure Compute provider as well. 

Add the new Provider to the cluster. 

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-compute
spec:
  package: xpkg.upbound.io/upbound/provider-azure-compute:v0.42.1
EOF
```

View the new Compute provider with `kubectl get providers`.


```shell {copy-lines="1"}
kubectl get providers
NAME                            INSTALLED   HEALTHY   PACKAGE                                                  AGE
provider-azure-compute          True        True      xpkg.upbound.io/upbound/provider-azure-compute:v0.42.1   25s
provider-azure-network          True        True      xpkg.upbound.io/upbound/provider-azure-network:v0.42.1   3h
upbound-provider-family-azure   True        True      xpkg.upbound.io/upbound/provider-family-azure:v0.42.1    3h
```

## Access the custom API

With the custom API (XRD) installed and associated to a resource template
(Composition) users can access the API to create resources.

Create a {{<hover label="xr" line="3">}}VirtualMachine{{</hover>}} object to 
create the cloud resources.

```yaml {copy-lines="all",label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
metadata:
  name: my-vm
spec: 
  location: "EU"
EOF
```

View the resource with `kubectl get VirtualMachine`.

{{< hint "note" >}}
It may take up to five minutes for the resources to provision.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get VirtualMachine
NAME    SYNCED   READY   COMPOSITION                             AGE
my-vm   True     True    crossplane-quickstart-vm-with-network   3m3s
```

This object is a Crossplane _composite resource_ (also called an `XR`).  
It's a
single object representing the collection of resources created from the
Composition template. 

View the individual resources with `kubectl get managed`

```shell {copy-lines="1"}
kubectl get managed
NAME                                         READY   SYNCED   EXTERNAL-NAME   AGE
resourcegroup.azure.upbound.io/my-vm-7jb4n   True    True     my-vm-7jb4n     3m43s

NAME                                                       READY   SYNCED   EXTERNAL-NAME   AGE
linuxvirtualmachine.compute.azure.upbound.io/my-vm-5h7p4   True    True     my-vm-5h7p4     3m43s

NAME                                                    READY   SYNCED   EXTERNAL-NAME   AGE
networkinterface.network.azure.upbound.io/my-vm-j7fpx   True    True     my-vm-j7fpx     3m43s

NAME                                          READY   SYNCED   EXTERNAL-NAME   AGE
subnet.network.azure.upbound.io/my-vm-b2dqt   True    True     my-vm-b2dqt     3m43s

NAME                                                  READY   SYNCED   EXTERNAL-NAME   AGE
virtualnetwork.network.azure.upbound.io/my-vm-pd2sw   True    True     my-vm-pd2sw     3m43s
```

Accessing the API created all five resources defined in the template and linked
them together. 

Look at a specific resource to see it's created in the location used in the API.

```yaml {copy-lines="1"}
kubectl describe linuxvirtualmachine | grep Location
    Location:                         Sweden Central
    Location:                         swedencentral
```

Delete the resources with `kubectl delete VirtualMachine`.

```shell {copy-lines="1"}
kubectl delete VirtualMachine my-vm
virtualmachine.compute.example.com "my-vm" deleted
```

Verify Crossplane deleted the resources with `kubectl get managed`

{{<hint "note" >}}
It may take up to 5 minutes to delete the resources.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get managed
No resources found
```

## Using the API with namespaces

Accessing the API `VirtualMachine` happens at the cluster scope.  
Most organizations
isolate their users into namespaces.  

A Crossplane _Claim_ is the custom API in a namespace.

Creating a _Claim_ is just like accessing the custom API endpoint, but with the
{{<hover label="claim" line="3">}}kind{{</hover>}} 
from the custom API's `claimNames`.

Create a new namespace to test create a Claim in. 

```shell
kubectl create namespace crossplane-test
```

Then create a Claim in the `crossplane-test` namespace.

```yaml {label="claim",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: my-namespaced-vm
  namespace: crossplane-test
spec: 
  location: "EU"
EOF
```
View the Claim with `kubectl get claim -n crossplane-test`.

```shell {copy-lines="1"}
kubectl get claim -n crossplane-test
NAME               SYNCED   READY   CONNECTION-SECRET   AGE
my-namespaced-vm   True     True                        5m11s
```

The Claim automatically creates a composite resource, which creates the managed
resources. 

View the Crossplane created composite resource with `kubectl get composite`.

```shell {copy-lines="1"}
kubectl get composite
NAME                     SYNCED   READY   COMPOSITION                             AGE
my-namespaced-vm-r7gdr   True     True    crossplane-quickstart-vm-with-network   5m33s
```

Again, view the managed resources with `kubectl get managed`.

```shell {copy-lines="1"}
NAME                                                          READY   SYNCED   EXTERNAL-NAME                  AGE
resourcegroup.azure.upbound.io/my-namespaced-vm-r7gdr-cvzw6   True    True     my-namespaced-vm-r7gdr-cvzw6   5m51s

NAME                                                                        READY   SYNCED   EXTERNAL-NAME                  AGE
linuxvirtualmachine.compute.azure.upbound.io/my-namespaced-vm-r7gdr-vrbgb   True    True     my-namespaced-vm-r7gdr-vrbgb   5m51s

NAME                                                                     READY   SYNCED   EXTERNAL-NAME                  AGE
networkinterface.network.azure.upbound.io/my-namespaced-vm-r7gdr-hwrb8   True    True     my-namespaced-vm-r7gdr-hwrb8   5m51s

NAME                                                           READY   SYNCED   EXTERNAL-NAME                  AGE
subnet.network.azure.upbound.io/my-namespaced-vm-r7gdr-gh468   True    True     my-namespaced-vm-r7gdr-gh468   5m51s

NAME                                                                   READY   SYNCED   EXTERNAL-NAME                  AGE
virtualnetwork.network.azure.upbound.io/my-namespaced-vm-r7gdr-5qhz7   True    True     my-namespaced-vm-r7gdr-5qhz7   5m51s
```

Deleting the Claim deletes all the Crossplane generated resources.

`kubectl delete claim -n crossplane-test my-VirtualMachine-database`

```shell {copy-lines="1"}
kubectl delete claim -n crossplane-test my-namespaced-vm
virtualmachineclaim.compute.example.com "my-namespaced-vm" deleted
```

{{<hint "note" >}}
It may take up to 5 minutes to delete the resources.
{{< /hint >}}

Verify Crossplane deleted the composite resource with `kubectl get composite`.

```shell {copy-lines="1"}
kubectl get composite
No resources found
```

Verify Crossplane deleted the managed resources with `kubectl get managed`.

```shell {copy-lines="1"}
kubectl get managed
No resources found
```

## Next steps
* Explore Azure resources that Crossplane can configure in the 
  [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-family-azure/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with 
  Crossplane users and contributors.
* Read more about the [Crossplane concepts]({{<ref "../concepts">}}) to find out
  what else you can do with Crossplane. 