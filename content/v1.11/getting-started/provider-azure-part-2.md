---
title: Azure Quickstart Part 2
weight: 120
tocHidden: true
---

{{< hint "important" >}}
This guide is part 2 of a series. Follow **[part 1]({{<ref "provider-azure" >}})** 
to install Crossplane and connect your Kubernetes cluster to Azure.

**[Part 3]({{<ref "provider-azure-part-3">}})** covers patching _CompositeResources_
and using Crossplane _Packages_.
{{< /hint >}}

This section creates a _[Composition](#create-a-composition)_, 
_[CompositeResourceDefinition](#define-a-composite-resource)_ and a
_[Claim](#create-a-claim)_
to create a custom Kubernetes API to create Azure resources. This custom API 
is a _composite resource_ (XR) API.

## Prerequisites
* Complete [quickstart part 1]({{<ref "provider-azure" >}}) connecting 
  Kubernetes to Azure.
* an Azure account with permissions to create an Azure Virtual Machine and
  Virtual Networking

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
  name: upbound-provider-azure
spec:
  package: xpkg.upbound.io/upbound/provider-azure:v0.32.0
EOF
```

3. Use the Azure CLI to create a service principal and save the JSON output as 
   `azure-crednetials.json`
{{< editCode >}}
```console
az ad sp create-for-rbac \
--sdk-auth \
--role Owner \
--scopes /subscriptions/$$<subscription_id>$$
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

## Create a composition
[Part 1]({{<ref "provider-azure" >}}) created a single _managed resource_.
A _Composition_ is a template to create one or more _managed resource_ at the 
same time.

This sample _composition_ creates an Linux Virtual Machine and the required
networking components. 

Compositions have multiple components:
* The individual managed resources.
* The Composition kind and version.
* A Composite type reference. 

The following steps describe each of these components before 
[applying the final Composition](#apply-the-composition). 

### Define a virtual network
Define a `virtualnetwork` resource using the configuration from the previous 
section:

{{< hint "note" >}}
Don't apply this configuration. This YAML is part of a larger
definition. 
{{< /hint >}}

```yaml {copy-lines="none"}
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetwork
metadata:
  name: crossplane-quickstart-network
spec:
  forProvider:
    addressSpace:
      - 10.0.0.0/16
    location: "Central US"
    resourceGroupName: <resource_group_name>
```

### Define a subnet resource
Next, define a `Subnet` resource.

{{< hint "note" >}}
Don't apply this configuration. This YAML is part of a larger
definition. 
{{< /hint >}}

```yaml {label="subnet",copy-lines="none"}
apiVersion: network.azure.upbound.io/v1beta1
kind: Subnet
metadata:
  name: crossplane-quickstart-subnet
spec:
  forProvider:
    addressPrefixes:
      - 10.0.1.0/24
    resourceGroupName: <resource_group_name>
```

### Define a network interface
Define a network interface to attach to the virtual machine.

{{< hint "note" >}}
Don't apply this configuration. This YAML is part of a larger
definition. 
{{< /hint >}}

```yaml {label="nic",copy-lines="none"}
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkInterface
metadata:
  name: crossplane-quickstart-nic
spec:
  forProvider:
    ipConfiguration:
      - name: crossplane-quickstart-configuration
        privateIpAddressAllocation: Dynamic
    location: "Central US"
    resourceGroupName: <resource_group_name>
```

### Define a virtual machine
Define the `LinuxVirtualMachine` with its settings. 

{{< hint "note" >}}
Don't apply this configuration. This YAML is part of a larger
definition. 
{{< /hint >}}

```yaml {label="vm",copy-lines="none"}
apiVersion: compute.azure.upbound.io/v1beta1
kind: LinuxVirtualMachine
metadata:
  name: crossplane-quickstart-vm
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
    size: Standard_B1ms	
    sourceImageReference:
      - offer: debian-11
        publisher: Debian
        sku: 11-backports-gen2
        version: latest
    resourceGroupName: <resource_group_name>
```

### Create the composition object
The _Composition_ combines all the managed resources into a single object.

A 
{{<hover label="compName" line="2">}}Composition{{</ hover>}} comes from the
{{<hover label="compName" line="1">}}Crossplane{{</ hover>}} 
API resources.

Create any {{<hover label="compName" line="4">}}name{{</ hover>}} for this _Composition_.

```yaml {label="compName",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: crossplane-quickstart-vm-with-network
```

Add all the defined resources to the 
{{<hover label="specResources" line="6">}}spec.resources{{</ hover>}} 
section of the _Composition_.

Give each resource a 
{{<hover label="specResources" line="7">}}name{{</ hover>}} 
and put the resource definition under the
{{<hover label="specResources" line="8">}}base{{</ hover>}} 
key.

Add your {{<hover label="specResources" line="16">}}resourceGroupName{{< /hover >}} 
for each resource in the Composition. 

{{<hint "important" >}}
The contents of the 
{{<hover label="specResources" line="8">}}base{{</ hover>}} key 
doesn't include the `metadata` field from the managed resources.
{{< /hint >}}

```yaml {label="specResources",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: crossplane-quickstart-vm-with-network
spec:
  resources:
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
            resourceGroupName: <resource_group_name>
# Removed for brevity
```

{{<hint "tip" >}}
Crossplane provides the 
{{<hover label="specResources" line="16">}}matchControllerRef{{</hover>}} value
to automatically link resources created by the same _Composition_.
{{</hint >}}

_Compositions_ are a template for generating resources. A _composite
resource_ actually creates the resources.

A _Composition_ defines what _composite resources_ can use this
template. 

_Compositions_ do this with the 
{{<hover label="compRef" line="6">}}spec.compositeTypeRef{{</ hover>}}
definition.

{{< hint "tip" >}}
Crossplane recommends prefacing the `kind` with an `X` to show it's a Composition.
{{< /hint >}}

```yaml {label="compRef",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: crossplane-quickstart-vm-with-network
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XVirtualMachine
  resources:
    # Removed for Brevity    
```

A _composite resource_ is actually a custom Kubernetes API type you define. The
platform team controls the kind, API endpoint and version.

<!-- vale gitlab.SentenceLength = NO -->
<!-- Length is because of shortcodes, ignore -->
With this {{<hover label="compRef" line="6">}}spec.compositeTypeRef{{</ hover>}}
Crossplane only allows _composite resources_ from the API group
{{<hover label="compRef" line="7">}}custom-api.example.org{{</ hover>}} 
that are of
{{<hover label="compRef" line="8">}}kind: XVirtualMachine{{</ hover>}}
to use this template to create resources. 
<!-- vale gitlab.SentenceLength = YES -->

### Apply the composition
Apply the full _Composition_ to your Kubernetes cluster.

{{<hint "important" >}}
Add your {{<hover label="fullComp" line="27">}}resourceGroupName{{</hover>}} to
each resource. 
{{< /hint >}}

{{< editCode >}}
```yaml {label="fullComp"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: crossplane-quickstart-vm-with-network
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XVirtualMachine
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
            resourceGroupName: $$<resource_group_name>$$
            size: Standard_B1ms
            sourceImageReference:
              - offer: debian-11
                publisher: Debian
                sku: 11-backports-gen2
                version: latest
            networkInterfaceIdsSelector:
              matchControllerRef: true
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
            resourceGroupName: $$<resource_group_name>$$
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
            resourceGroupName: $$<resource_group_name>$$
    - name: quickstart-network
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: VirtualNetwork
        spec:
          forProvider:
            addressSpace:
              - 10.0.0.0/16
            location: "Central US"
            resourceGroupName: $$<resource_group_name>$$
EOF
```
{{< /editCode >}}

Confirm the _Composition_ exists with `kubectl get composition`

```shell {copy-lines="1"}
kubectl get composition
NAME                                    XR-KIND           XR-APIVERSION                     AGE
crossplane-quickstart-vm-with-network   XVirtualMachine   custom-api.example.org/v1alpha1   5s
```

Again, the _Composition_ is only a template. At this point, Crossplane hasn't 
created any resources inside of Azure. 

## Define a composite resource

The _Composition_ that was just created limited which _composite resources_ can
use that template. 

A _composite resource_ is a custom API defined by the platform teams.  
A _CompositeResourceDefinition_ defines the schema for a _composite resource_.


A _CompositeResourceDefinition_ installs the custom API type into Kubernetes
and defines what `spec` keys and values are valid when calling this new custom API.

Before creating a _composite resource_ Crossplane requires a _CompositeResourceDefinition_.

{{< hint "tip" >}}
_CompositeResourceDefinitions_ are also called `XRDs` for short. 
{{< /hint >}}

Just like a _Composition_ the 
{{<hover label="xrdName" line="2" >}}CompositeResourceDefinition{{</hover>}} 
is part of the 
{{<hover label="xrdName" line="1" >}}Crossplane{{</hover>}}
API group.

The _XRD_ {{<hover label="xrdName" line="4" >}}name{{</hover>}} is the new
API endpoint.

{{< hint "tip" >}}
Crossplane recommends using a plural name for the _XRD_ 
{{<hover label="xrdName" line="4" >}}name{{</hover>}}.
{{< /hint >}}

```yaml {label="xrdName",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xvirtualmachines.custom-api.example.org
```

The _XRD's_
{{<hover label="xrdGroup" line="5" >}}spec{{</hover>}} defines the new custom
API.

### Define the API endpoint and kind
First, define the new API
{{<hover label="xrdGroup" line="6" >}}group{{</hover>}}.  
Next, create the API {{<hover label="xrdGroup" line="8" >}}kind{{</hover>}} and
{{<hover label="xrdGroup" line="9" >}}plural{{</hover>}}.

```yaml {label="xrdGroup",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xvirtualmachines.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: XVirtualMachine
    plural: xvirtualmachines
```

{{<hint "note" >}}
The _XRD_ {{<hover label="xrdGroup" line="6" >}}group{{</hover>}} matches the _composition_ {{<hover label="noteComp"
line="5">}}apiVersion{{</hover>}} and the 
_XRD_ {{<hover label="xrdGroup" line="8" >}}kind{{</hover>}} matches the _composition_ 
{{<hover label="noteComp" line="6">}}compositeTypeRef.kind{{</hover>}}.

```yaml {label="noteComp",copy-lines="none"}
kind: Composition
# Removed for brevity
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XVirtualMachine
```
{{< /hint >}}

### Set the API version
In Kubernetes, all API endpoints have a version to show the stability of the API
and track revisions. 

Apply a version to the _XRD_ with a 
{{<hover label="xrdVersion" line="11">}}versions.name{{</hover>}}. 
This matches the 
{{<hover label="noteComp"line="5">}}compositeTypeRef.apiVersion{{</hover>}}

_XRDs_ require both
{{<hover label="xrdVersion" line="12">}}versions.served{{</hover>}}
and
{{<hover label="xrdVersion" line="13">}}versions.referenceable{{</hover>}}.

```yaml {label="xrdVersion",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xvirtualmachines.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: XVirtualMachine
    plural: xvirtualmachines
  versions:
  - name: v1alpha1
    served: true
    referenceable: true
```

{{<hint "note" >}}
For more information on defining versions in Kubernetes read the 
[API versioning](https://kubernetes.io/docs/reference/using-api/#api-versioning) section of the Kubernetes documentation.
{{< /hint >}}

### Create the API schema
With an API endpoint named, now define the API schema, or what's allowed
inside the `spec` of the new Kubernetes object.

{{< hint "note" >}}
_XRDs_ follow the Kubernetes 
[_CustomResourceDefinition_ rules for schemas](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#specifying-a-structural-schema). 
{{</hint >}}

Place the API 
{{< hover label="xrdSchema" line="8" >}}schema{{</hover>}}
under the 
{{< hover label="xrdSchema" line="7" >}}version.name{{</hover>}} 

The _XRD_ type defines the next lines. They're always the same.

<!-- vale write-good.TooWordy = NO -->
<!-- allow "validate" -->
{{< hover label="xrdSchema" line="9" >}}openAPIV3Schema{{</hover>}} specifies
how the schema gets validated.
<!-- vale write-good.TooWordy = YES -->

Next, the entire API is an 
{{< hover label="xrdSchema" line="10" >}}object{{</hover>}}
with a
{{< hover label="xrdSchema" line="11" >}}property{{</hover>}} of
{{< hover label="xrdSchema" line="12" >}}spec{{</hover>}}.

The 
{{< hover label="xrdSchema" line="12" >}}spec{{</hover>}} is also an 
{{< hover label="xrdSchema" line="13" >}}object{{</hover>}} with
{{< hover label="xrdSchema" line="14" >}}properties{{</hover>}}.

```yaml {label="xrdSchema",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
  # Removed for brevity
  versions:
  - name: v1alpha1
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
```

{{< hint "tip" >}}
For more information on the values allowed in a _CompositeResourceDefinition_ view its schema with
`kubectl explain xrd`
{{< /hint >}}

Now, define the custom API. Your custom API continues under the last
{{<hover label="xrdSchema" line="14">}}properties{{</hover>}} definition in the
previous example.

This custom API has only one setting:
<!-- vale Google.We = NO -->
* {{<hover label="customAPI" line="4" >}}region{{</hover >}} - where to deploy
the resources, a choice of "EU" or "US"

Users can't change any other settings of the VM or its network.

The{{<hover label="customAPI" line="4" >}}region{{</hover >}}
is a {{<hover label="customAPI" line="5" >}}string{{</hover >}}
and can match the regular expression that's
{{<hover label="customAPI" line="6" >}}oneOf{{</hover >}}
{{<hover label="customAPI" line="7" >}}EU{{</hover >}}
or
{{<hover label="customAPI" line="8" >}}US{{</hover >}}.

This API requires the setting 
{{<hover label="customAPI" line="10" >}}region{{</hover >}}.


```yaml {label="customAPI",copy-lines="none"}
# Removed for brevity
# schema.openAPIV3Schema.type.properties.spec
properties:
  region:
    type: string
    oneOf:
      - pattern: '^EU$'
      - pattern: '^US$'
required:
  - region
```

### Enable claims to the API
Tell this _XRD_ to offer a _claim_ by defining the _claim_ API endpoint under
the _XRD_ {{<hover label="XRDclaim" line="4">}}spec{{< /hover >}}.

{{< hint "tip" >}}
Crossplane recommends a _Claim_ {{<hover label="XRDclaim" line="10" >}}kind{{</ hover>}} match the _Composite Resource_ (XR) 
{{<hover label="XRDclaim" line="7" >}}kind{{</ hover>}},
without the preceding `X`.
{{< /hint >}}


```yaml {label="XRDclaim",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
# Removed for brevity
  names:
    kind: XVirtualMachine
    plural: xvirtualmachines
  claimNames:
    kind: VirtualMachine
    plural: virtualmachines
```

{{<hint "note" >}}
The [Claims](#create-a-claim) section later in this guide discusses _claims_.
{{< /hint >}}

### Apply the CompositeResourceDefinition
Apply the complete _XRD_ to your Kubernetes cluster.


```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xvirtualmachines.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: XVirtualMachine
    plural: xvirtualmachines
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
              region:
                type: string
                oneOf:
                  - pattern: '^EU$'
                  - pattern: '^US$'
            required:
              - region
  claimNames:
    kind: VirtualMachine
    plural: virtualmachines
EOF
```

Verify Kubernetes created the XRD with `kubectl get xrd`

```shell {copy-lines="1",label="getXRD"}
kubectl get xrd
NAME                                      ESTABLISHED   OFFERED   AGE
xvirtualmachines.custom-api.example.org   True          True      4s
```

## Create a composite resource
Creating an _XRD_ allows the creation _composite resources_.

A _composite resource_ uses the custom API created in the _XRD_.

The _XRD_ maps the _composite resource_ values to the _Composition_ template and
creates new _managed resources_.

Looking at part of the _XRD_:

```yaml {label="xrdSnip",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
  group: custom-api.example.org
  names:
    kind: XVirtualMachine
# Removed for brevity
      spec:
        type: object
        properties:
          region:
            type: string
            oneOf:
              - pattern: '^EU$'
              - pattern: '^US$'
```

The _XRD_ {{<hover label="xrdSnip" line="5">}}group{{</hover>}}
becomes the _composite resource_ 
{{<hover label="xr" line="2">}}apiVersion{{</hover>}}.

The _XRD_ {{<hover label="xrdSnip" line="7">}}kind{{</hover>}}
is the _composite resource_ 
{{<hover label="xr" line="3">}}kind{{</hover>}}

The _XRD_ API {{<hover label="xrdSnip" line="9">}}spec{{</hover>}} defines the
_composite resource_ {{<hover label="xr" line="6">}}spec{{</hover>}}.

The _XRD_ {{<hover label="xrdSnip" line="11">}}properties{{</hover>}} section
defines the options for the _composite resource_ 
{{<hover label="xr" line="6">}}spec{{</hover>}}.

The one option is {{<hover label="xrdSnip" line="12">}}region{{</hover>}} and it
can be either {{<hover label="xrdSnip" line="15">}}EU{{</hover>}} or 
{{<hover label="xrdSnip" line="16">}}US{{</hover>}}. 

This _composite resource_ uses 
{{<hover label="xr" line="7">}}region: US{{</hover>}}.
<!-- vale Google.We = YES -->
### Apply the composite resource

Apply the composite resource to the Kubernetes cluster. 

```yaml {label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: XVirtualMachine
metadata:
  name: my-composite-resource
spec: 
  region: "US"
EOF
```

### Verify the composite resource
Verify Crossplane created the _composite resource_ with 
`kubectl get xvirtualmachine`

{{< hint "tip" >}}
It may take up to 10 minutes for Azure to create the Virtual Machine resources.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get xvirtualmachine
NAME                    SYNCED   READY   COMPOSITION                             AGE
my-composite-resource   True     True    crossplane-quickstart-vm-with-network   5m2s
```

{{<hint "tip" >}}
Use `kubectl get <kind>` to view a specific `kind` of _composite resource_.  
View all _composite resources_ with `kubectl get composite`.
{{< /hint >}}


Both `SYNCED` and `READY` are `True` when Crossplane created the Azure 
resources.

Now look at the `linuxvirtualmachine` and `networkinterface` 
_managed resources_ with
`kubectl get linuxvirtualmachine` and `kubectl get networkinterface`.

```shell {copy-lines="1"}
kubectl get linuxvirtualmachine
NAME                          READY   SYNCED   EXTERNAL-NAME                 AGE
my-composite-resource-w564c   True    True     my-composite-resource-w564c   8m33s
```

```shell {copy-lines="1"}
kubectl get networkinterface
NAME                          READY   SYNCED   EXTERNAL-NAME                 AGE
my-composite-resource-72ft8   True    True     my-composite-resource-72ft8   8m54s
```

The _composite resource_ automatically generated the _managed resources_.

Using `kubectl describe` on a _managed resource_ shows the `Owner References` is
the _composite resource_.

```yaml {copy-lines="1"}
 kubectl describe linuxvirtualmachine | grep "Owner References" -A5
  Owner References:
    API Version:           custom-api.example.org/v1alpha1
    Block Owner Deletion:  true
    Controller:            true
    Kind:                  XVirtualMachine
    Name:                  my-composite-resource
```

Each _composite resource_ creates and owns a unique set of _managed resources_.
If you create a second _composite resource_ Crossplane creates a new
`LinuxVirtualMachine` and new networking resources. 

```yaml {label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: XVirtualMachine
metadata:
  name: my-second-composite-resource
spec: 
  region: "US"
EOF
```

Again, use `kubectl get xvirtualmachine` to view both _composite resources_.

```shell {copy-lines="1"}
kubectl get xvirtualmachine
NAME                           SYNCED   READY   COMPOSITION                             AGE
my-composite-resource          True     True    crossplane-quickstart-vm-with-network   15m
my-second-composite-resource   True     True    crossplane-quickstart-vm-with-network   4m15s
```

And see there are two `linuxvirtualmachine` and two `networkinterface` 
_managed resources_.

```shell {copy-lines="1"}
kubectl get linuxvirtualmachine
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
my-composite-resource-w564c          True    True     my-composite-resource-w564c          16m
my-second-composite-resource-s92lw   True    True     my-second-composite-resource-s92lw   5m8s
```

```shell {copy-lines="1"}
kubectl get networkinterface
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
my-composite-resource-72ft8          True    True     my-composite-resource-72ft8          16m
my-second-composite-resource-wcnnv   True    True     my-second-composite-resource-wcnnv   5m21s
```

### Delete the composite resources
Because the _composite resource_ is the `Owner` of the _managed resources_, when
Crossplane deletes the _composite resource_, it also deletes the _managed resources_ automatically.

Delete the new _composite resource_ with `kubectl delete xvirtualmachine`.

{{<hint "tip" >}}
Delete a specific _composite resource_ with `kubectl delete <kind>` or
`kubectl delete composite`.
{{< /hint >}}

Delete the second composition
```shell
kubectl delete xvirtualmachine my-second-composite-resource
```

{{<hint "note">}}
It may take up to five minutes before Crossplane finishes deleting resources.
{{</hint >}}

Now only one virtual machine and network interface exist.

```shell {copy-lines="1"}
kubectl get linuxvirtualmachines
NAME                          READY   SYNCED   EXTERNAL-NAME                 AGE
my-composite-resource-w564c   True    True     my-composite-resource-w564c   28m
```

```shell {copy-lines="1"}
kubectl get networkinterface
NAME                          READY   SYNCED   EXTERNAL-NAME                 AGE
my-composite-resource-72ft8   True    True     my-composite-resource-72ft8   29m
```

Delete the other _composite resource_ to remove the last `linuxvirtualmachines` 
and `networkinterface` _managed resources_.

```shell
kubectl delete xvirtualmachine my-composite-resource
```

_Composite resources_ are great for creating one or more related resources against
a template, but all _composite resources_ exist at the Kubernetes "cluster
level." There's no isolation between _composite resources_. Crossplane uses
_Claims_ to create resources with namespace isolation. 

## Create a claim

_Claims_, just like _composite resources_ use the custom API defined in the
_XRD_. Unlike a _composite resource_, Crossplane can create _Claims_ in a
namespace.

### Create a new Kubernetes namespace
Create a new namespace with `kubectl create namespace`.

```shell
kubectl create namespace test
```

Look at the _XRD_ to see the parameters for the _Claim_.
A _Claim_ uses the same {{<hover label="XRDclaim2" line="6" >}}group{{</hover>}}
a _composite resource_ uses but a different 
{{<hover label="XRDclaim2" line="8" >}}kind{{</hover>}}.

```yaml {label="XRDclaim2",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
# Removed for brevity
  group: custom-api.example.org
  claimNames:
    kind: VirtualMachine
    plural: virtualmachines
```

Like the _composite resource_, create a new object with the 
{{<hover label="claim" line="2" >}}custom-api.example.org{{</hover>}} API
endpoint.

The _XRD_
{{<hover label="XRDclaim2" line="8" >}}claimNames.kind{{</hover>}} defines the
{{<hover label="claim" line="3" >}}kind{{</hover>}}.

The {{<hover label="claim" line="7" >}}spec{{</hover>}} uses the same
API options as the _composite resource_.

### Apply the claim
Apply the _claim_ to your Kubernetes cluster.

```yaml {label="claim"}
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: VirtualMachine
metadata:
  name: claimed-virtualmachine
  namespace: test
spec:
  region: "US"
EOF
```

### Verify the claim
Verify Crossplane created the _claim_ with `kubectl get virtualmachine` in the 
`test` namespace.

{{<hint "tip" >}}
View claims with `kubectl get <kind>` or use `kubectl get claim` to view all
_Claims_.
{{</hint >}}

```shell {copy-lines="1"}
kubectl get virtualmachine -n test
NAME                     SYNCED   READY   CONNECTION-SECRET   AGE
claimed-virtualmachine   True     True                        3m40s
```

When Crossplane creates a _Claim_, a unique _composite resource_ is also
created. View the new _composite resource_ with `kubectl get xvirtualmachine`.

```shell {copy-lines="1"}
kubectl get xvirtualmachine
NAME                           SYNCED   READY   COMPOSITION                             AGE
claimed-virtualmachine-cw6cv   True     True    crossplane-quickstart-vm-with-network   3m57s
```

The _composite resource_ exists at the "cluster scope" while the _Claim_ exists
at the "namespace scope."

Create a second namespace and a second claim.

```yaml
kubectl create namespace test2
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: VirtualMachine
metadata:
  name: claimed-virtualmachine
  namespace: test2
spec:
  region: "US"
EOF
```

View the _claims_ in all namespaces with `kubectl get virtualmachine -A`

```shell {copy-lines="1"}
kubectl get virtualmachine -A
NAMESPACE   NAME                     SYNCED   READY   CONNECTION-SECRET   AGE
test        claimed-virtualmachine   True     True                        12m
test2       claimed-virtualmachine   True     True                        7m35s
```

Now look at the _composite resources_ at the cluster scope.

```shell {copy-lines="1"}
kubectl get xvirtualmachine
NAME                           SYNCED   READY   COMPOSITION                             AGE
claimed-virtualmachine-7jth5   True     True    crossplane-quickstart-vm-with-network   7m53s
claimed-virtualmachine-cw6cv   True     True    crossplane-quickstart-vm-with-network   12m
```

Crossplane created a second _composite resource_ for the second _Claim_.

Looking at the virtual machines and network interfaces shows two of each 
resource, one for each claim.

```shell {copy-lines="1"}
kubectl get linuxvirtualmachines
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
claimed-virtualmachine-7jth5-v2gsh   True    True     claimed-virtualmachine-7jth5-v2gsh   8m10s
claimed-virtualmachine-cw6cv-w8v65   True    True     claimed-virtualmachine-cw6cv-w8v65   13m
```

```shell {copy-lines="1"}
kubectl get networkinterface
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
claimed-virtualmachine-7jth5-hj657   True    True     claimed-virtualmachine-7jth5-hj657   8m44s
claimed-virtualmachine-cw6cv-f9z4f   True    True     claimed-virtualmachine-cw6cv-f9z4f   13m
```

### Delete the claims
Removing the _claims_ removes the _composite resources_ and the associated
_managed resources_.

```shell
kubectl delete virtualmachine claimed-virtualmachine -n test
kubectl delete virtualmachine claimed-virtualmachine -n test2
```

Verify Crossplane removed all the _managed resources_.

```shell {copy-lines="1"}
kubectl get linuxvirtualmachines
No resources found
```

```shell {copy-lines="1"}
kubectl get networkinterface
No resources found
```

Claims are powerful tools to give users resources in their own isolated
namespace. But these examples haven't shown how the custom API can change
the settings defined in the _Composition_. This _composition patching_ applies
the API settings when creating resources. 
[Part 3]({{< ref "provider-azure-part-3">}}) of this guide covers _composition
patches_ and making all this configuration portable in Crossplane _Packages_. 

## Next steps
* **[Continue to part 3]({{< ref "provider-azure-part-3">}})** to learn
  about _patching_ resources and creating Crossplane _Packages_.
* Explore Azure resources that Crossplane can configure in the 
  [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-azure/latest/crds).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with Crossplane users and contributors.