---
title: Azure Quickstart Part 3
weight: 120
tocHidden: true
---

{{< hint "important" >}}
This guide is part 3 of a series. 

Follow **[part 1]({{<ref "provider-azure" >}})** 
to install Crossplane and connect your Kubernetes cluster to Azure. 

Follow **[part 2]({{<ref "provider-azure-part-2" >}})** to create a _composition_,
_custom resource definition_ and a _claim_.
{{< /hint >}}

[Part 2]({{<ref "provider-azure-part-2" >}}) created a 
_CompositeResourceDefinition_ to define the schema of the custom API. 
Users create a _Claim_ to use the custom API and apply their options. 
Part 2 didn't show how the options set in a _Claim_ change or get 
applied to the associated _composite resources_.

## Prerequisites
* Complete quickstart [part 1]({{<ref "provider-azure" >}}) and [part 2]({{<ref
  "provider-azure-part-2" >}}) to install Crossplane and the quickstart
  configurations.
  
{{<expand "Skip parts 1 and 2 and just get started" >}}
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

6. Create a _composition_
{{< hint "tip" >}}
Apply your 
{{<hover label="Composition" line="27">}}resourceGroupName{{</hover>}} to each resource.
{{< /hint >}}

{{< editCode >}}
```yaml {label="Composition"}
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

7. Create a _CompositeResourceDefinition_
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

8. Create a new namespace
```shell
kubectl create namespace test
```

{{</expand >}}

## Enable composition patches
In a _Composition_ `patches` map fields in the custom API to fields inside the
_managed resources_.

The example _Composition_ has four _managed resources_. A {{<hover label="compResources" line="8" >}}LinuxVirtualMachine{{</hover>}}, 
{{<hover label="compResources" line="12" >}}NetworkInterface{{</hover>}}, 
{{<hover label="compResources" line="16" >}}Subnet{{</hover>}} and a 
{{<hover label="compResources" line="20" >}}VirtualNetwork{{</hover>}}.


```yaml {label="compResources",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
resources:
    - name: quickstart-vm
      base:
        apiVersion: compute.azure.upbound.io/v1beta1
        kind: LinuxVirtualMachine
    - name: quickstart-nic
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: NetworkInterface
    - name: quickstart-subnet
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: Subnet
    - name: quickstart-network
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: VirtualNetwork    
```
<!-- vale Google.We = NO -->
The custom API defined a single option, 
{{<hover label="xrdSnip" line="12">}}region{{</hover>}}. A 
{{<hover label="xrdSnip" line="12">}}region{{</hover>}} can be either 
{{<hover label="xrdSnip" line="15">}}EU{{</hover>}} or
{{<hover label="xrdSnip" line="16">}}US{{</hover>}}. 
<!-- vale Google.We = YES -->

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

Creating a _composition_ `patch` allows Crossplane to update the settings of the
_composite resource_. Patches apply to the individual _managed resources_
inside the _Composition_. 

A {{<hover label="patch" line="13">}}patch{{</hover>}} has a
{{<hover label="patch" line="14">}}fromField{{</hover>}} and a
{{<hover label="patch" line="15">}}toField{{</hover>}} specifying which value
_from_ the custom API should apply _to_ a field in the _managed resource_.  
Patches can create a 
{{<hover label="patch" line="16">}}transform{{</hover>}} to change the _from_
field before it's applied.  

The transform
{{<hover label="patch" line="17">}}type{{</hover>}} is what kind of change to
make on the _from_ field. Types of changes could include appending a string,
preforming a math operation or mapping one value to another. 

Applying a {{<hover label="patch" line="13">}}patch{{</hover>}} to the 
{{<hover label="patch" line="8">}}LinuxVirtualMachine{{</hover>}} uses the 
custom API 
{{<hover label="patch" line="14">}}region{{</hover>}} to use as the 
_managed resource_
{{<hover label="patch" line="15">}}location{{</hover>}}. 

<!-- vale Google.We = NO -->
The custom API value "EU" is 
{{<hover label="patch" line="19">}}mapped{{</hover>}} to the value 
"Sweden Central"
and "US" is {{<hover label="patch" line="20">}}mapped{{</hover>}} to the value
"Central US."
<!-- vale Google.We = YES -->


```yaml {label="patch",copy-lines="none"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
  resources:
    - name: quickstart-vm
      base:
        apiVersion: compute.azure.upbound.io/v1beta1
        kind: LinuxVirtualMachine
        spec:
          forProvider:
            location: "Central US"
            # Removed for Brevity
      patches:
        - fromFieldPath: "spec.region"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"
```
<!-- vale Google.We = NO -->
Patching is a powerful tool enabling simpler or abstracted APIs. A developer
isn't required to know the specific Azure location names, only the abstracted
option of "EU" or "US."
<!-- vale Google.We = YES -->

### Apply the updated composition
Apply the same `patch` to all other _managed resource_ 
and apply the updated _Composition_.

{{< hint "tip" >}}
Update each `resourceGroupName` with your Azure Resource Group.
{{< /hint >}}

{{< editCode >}}
```yaml
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
      patches:
        - fromFieldPath: "spec.region"
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
            resourceGroupName: $$<resource_group_name>$$
      patches:
        - fromFieldPath: "spec.region"
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
            resourceGroupName: $$<resource_group_name>$$
      patches:
        - fromFieldPath: "spec.region"
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
            location: "Sweden Central"
            resourceGroupName: $$<resource_group_name>$$
      patches:
        - fromFieldPath: "spec.region"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"
EOF
```
{{< /editCode >}}

### Create a claim
Create a new _claim_ and set the 
{{<hover label="claim" line="8" >}}region{{</hover >}} to "EU."

```yaml {label="claim"}
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: VirtualMachine
metadata:
  name: claimed-eu-virtualmachine
  namespace: test
spec:
  region: "EU"
EOF
```

View the _Claim_ with `kubectl get claim`

{{< hint "note" >}}
It may take up to 10 minutes for the Claim to be `READY`.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get claim -n test
NAME                        SYNCED   READY   CONNECTION-SECRET   AGE
claimed-eu-virtualmachine   True     True                        6m2s
```

The claim reports `SYNCED` and `READY` as `True` after Crossplane creates
all the _managed resources_.

Describe the `LinuxVirtualMachine` resource to see the Azure location is `Sweden
Central`.

```shell {copy-lines="1"}
kubectl describe linuxvirtualmachine | grep "At Provider\|Location"
    Location:                         Sweden Central
  At Provider:
    Location:                         swedencentral
```

<!-- vale Google.We = NO -->
Using {{<hover label="claim" line="8" >}}region: "EU"{{</hover >}} patches the
_composite resource_, updating the Azure location from `Central US` to 
`Sweden Central`.
The developer creating the claim isn't required to know which specific Azure 
location or the location naming conventions. Using the abstract API options of 
"EU" or "US" the developer places their resources in the desired location.
<!-- vale Google.We = YES -->

Deleting the claim removes the _managed resources_.

{{<hint "note" >}}
The _managed resources_ take up to 5 minutes to delete.
{{< /hint >}}

```shell
kubectl delete virtualmachine claimed-eu-virtualmachine -n test
```

## Create a Crossplane configuration package

Crossplane _configuration packages_ allow users to combine their 
_CustomResourceDefinition_ and _Composition_ files into a single OCI image. 

{{< hint "note" >}}
The [Open Container Initiative](https://opencontainers.org/faq/) 
defines the OCI image standard.  
An OCI images is a standard way to package data.
{{< /hint >}}

You can host configuration packages in image registries like 
[Docker Hub](https://hub.docker.com/) or the
[Upbound Marketplace](https://marketplace.upbound.io/). 

Crossplane can download and install configuration packages into a Kubernetes
cluster. 

Creating a configuration package makes your Crossplane custom APIs portable
and versioned. 

Building and installing configuration packages requires an OCI image compatible
tool. 

{{< hint "note" >}}
You can use any software that builds OCI images. This includes
[Docker](https://www.docker.com/) or 
[Upbound's Up CLI](https://github.com/upbound/up).
{{< /hint >}}

A configuration package includes at least three files:
* `crossplane.yaml` defines the metadata of the package.
* `definition.yaml` is the _CompositeResourceDefinition_ for the package.
* `composition.yaml` is the _Composition_ template for the package. 

<!-- vale gitlab.Substitutions = NO -->
<!-- yaml is in the filename -->
### Create a crossplane.yaml file
<!-- vale gitlab.Substitutions = YES -->
Configuration packages describe their contents and requirements with a 
`crossplane.yaml` file.

The `crossplane.yaml` file lists the required Crossplane _Providers_ and their
compatible versions as well as the required Crossplane version. 

The Crossplane
{{<hover label="xpyaml" line="1" >}}meta.pkg{{</hover>}} API defines the schema
for a 
{{<hover label="xpyaml" line="2" >}}Configuration{{</hover>}}.

Inside the {{<hover label="xpyaml" line="5" >}}spec{{</hover>}} define the
required Crossplane
{{<hover label="xpyaml" line="7" >}}version{{</hover>}}.

The {{<hover label="xpyaml" line="8" >}}dependsOn{{</hover>}} section lists the
dependencies for a package. 

This package lists the Upbound 
{{<hover label="xpyaml" line="9" >}}provider-azure{{</hover>}}
version {{<hover label="xpyaml" line="10" >}}0.32.0{{</hover>}} or later as a
dependency.

{{<hint "tip" >}}
Crossplane automatically installs dependencies. Dependencies can include other
configuration packages.
{{< /hint >}}

```yaml {label="xpyaml",copy-lines="none"}
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: crossplane-azure-quickstart
spec:
  crossplane:
    version: ">=v1.11.0"
  dependsOn:
    - provider: xpkg.upbound.io/upbound/provider-azure
      version: ">=v0.32.0"
```

Create a new directory and save the `crossplane.yaml` file.

```yaml
mkdir crossplane-azure-quickstart
cat <<EOF > crossplane-azure-quickstart/crossplane.yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: crossplane-azure-quickstart
spec:
  crossplane:
    version: ">=v1.12.0"
  dependsOn:
    - provider: xpkg.upbound.io/upbound/provider-azure
      version: ">=v0.32.0"
EOF
```

<!-- vale gitlab.Substitutions = NO -->
<!-- yaml is in the filename -->
### Create a definition.yaml file
<!-- vale gitlab.Substitutions = YES -->

A configuration package requires a _CompositeResourceDefinition_ (XRD) to 
define the custom API.

Save the _XRD_ as `definition.yaml` in the same directory as the
`crossplane.yaml` file.

```yaml
cat <<EOF > crossplane-azure-quickstart/definition.yaml
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

<!-- vale gitlab.Substitutions = NO -->
<!-- yaml is in the filename -->
### Create a composition.yaml file
<!-- vale gitlab.Substitutions = YES -->

The _Composition_ template creates the _managed resources_ and allows _patches_
to customize the _managed resources_.

Copy the _Composition_ into the `composition.yaml` file in the same directory as
`crossplane.yaml`.

{{< hint "tip" >}}
Update each `resourceGroupName` with your Azure Resource Group.
{{< /hint >}}

{{< editCode >}}
```yaml
cat <<EOF > crossplane-azure-quickstart/composition.yaml
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
      patches:
        - fromFieldPath: "spec.region"
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
            resourceGroupName: $$<resource_group_name>$$
      patches:
        - fromFieldPath: "spec.region"
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
            resourceGroupName: $$<resource_group_name>$$
      patches:
        - fromFieldPath: "spec.region"
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
            location: "Sweden Central"
            resourceGroupName: $$<resource_group_name>$$
      patches:
        - fromFieldPath: "spec.region"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "Sweden Central"
                US: "Central US"
EOF
```
{{< /editCode >}}

### Install the Crossplane command-line
To build a configuration package install the Crossplane Kubernetes command-line
extension. 

```shell
wget "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh"
chmod +x install.sh
./install.sh
```

Follow the directions and move the `kubectl-crossplane` binary to the correct
directory. 

Verify the Crossplane command-line installed with `kubectl crossplane --help`

```shell {copy-lines="1"}
kubectl crossplane --help
Usage: kubectl crossplane <command>

A command line tool for interacting with Crossplane.

Flags:
  -h, --help       Show context-sensitive help.
  -v, --version    Print version and quit.
      --verbose    Print verbose logging statements.
# Ouptut removed for brevity
```

### Build a configuration package

Use the `kubectl crossplane` command to create an `.xpkg` file containing the
custom APIs and Crossplane configuration.

```shell
kubectl crossplane build configuration -f crossplane-azure-quickstart/ --name="crossplane-azure-quickstart"
```

Now an `.xpkg` OCI image is inside the `crossplane-azure-quickstart` directory.

```shell {copy-lines="1"}
ls crossplane-azure-quickstart/
composition.yaml  crossplane-azure-quickstart.xpkg  crossplane.yaml  definition.yaml
```

## Next steps
* Explore Azure resources that Crossplane can configure in the [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-azure/latest/crds).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with Crossplane users and contributors.
* Read more about [Crossplane concepts]({{<ref "../concepts" >}})