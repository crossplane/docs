---
title: Azure Quickstart 
weight: 110
---

Connect Crossplane to Azure to create and manage cloud resources from Kubernetes 
with the 
[Upbound Azure Provider](https://marketplace.upbound.io/providers/upbound/provider-family-azure/).

This guide is in two parts:
* Part 1 walks through installing Crossplane, configuring the provider to
authenticate to Azure and creating a _Managed Resource_ in Azure directly from 
your Kubernetes cluster. This shows Crossplane can communicate with Azure.
* [Part 2]({{< ref "provider-azure-part-2" >}}) shows how to build and access a 
  custom API with Crossplane.

## Prerequisites
This quickstart requires:
* a Kubernetes cluster with at least 2 GB of RAM
* permissions to create pods and secrets in the Kubernetes cluster
* [Helm](https://helm.sh/) version v3.2.0 or later
* an Azure account with permissions to create an 
  [Azure Virtual Machine](https://learn.microsoft.com/en-us/azure/virtual-machines/) 
  and
  [Virtual Network](https://learn.microsoft.com/en-us/azure/virtual-network/)
* an Azure account with permissions to create an Azure [service principal](https://learn.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals#service-principal-object) and an [Azure resource group](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal)

{{<include file="/master/getting-started/install-crossplane-include.md" type="page" >}}

## Install the Azure provider

Install the Azure Network resource provider into the Kubernetes cluster with a Kubernetes configuration 
file. 

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

The Crossplane {{< hover label="provider" line="3" >}}Provider{{</hover>}}
installs the Kubernetes _Custom Resource Definitions_ (CRDs) representing Azure Networking
services. These CRDs allow you to create Azure resources directly inside 
Kubernetes.

Verify the provider installed with `kubectl get providers`. 


```shell {copy-lines="1",label="getProvider"}
kubectl get providers
NAME                            INSTALLED   HEALTHY   PACKAGE                                                  AGE
provider-azure-network          True        True      xpkg.upbound.io/upbound/provider-azure-network:v0.42.1   38s
upbound-provider-family-azure   True        True      xpkg.upbound.io/upbound/provider-family-azure:v0.42.1    26s
```

The Network Provider installs a second Provider, the
{{<hover label="getProvider" line="4">}}upbound-provider-family-azure{{</hover>}} 
provider.   
The family provider manages authentication to Azure across all Azure family
Providers. 

You can view the new CRDs with `kubectl get crds`.  
Every CRD maps to a unique Azure service Crossplane can provision and manage.

{{< hint type="tip" >}}
See details about all the supported CRDs in the 
[Upbound Marketplace](https://marketplace.upbound.io/providers/upbound/provider-family-azure/v0.42.1).
{{< /hint >}}


## Create a Kubernetes secret for Azure
The provider requires credentials to create and manage Azure resources. 
Providers use a Kubernetes _Secret_ to connect the credentials to the provider.

This guide generates an Azure service principal JSON file and saves it as a 
Kubernetes _Secret_.

### Install the Azure command-line
Generating an [authentication file](https://docs.microsoft.com/en-us/azure/developer/go/azure-sdk-authorization#use-file-based-authentication) requires the Azure command-line.  
Follow the documentation from Microsoft to [Download and install the Azure command-line](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).

Log in to the Azure command-line.

```command
az login
```
### Create an Azure service principal
Follow the Azure documentation to [find your Subscription ID](https://docs.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id) from the Azure Portal.

Using the Azure command-line and provide your Subscription ID create a service principal and authentication file.

{{< editCode >}}
```console {copy-lines="all"}
az ad sp create-for-rbac \
--sdk-auth \
--role Owner \
--scopes /subscriptions/$@<subscription_id>$@
```
{{< /editCode >}}

Save your Azure JSON output as `azure-credentials.json`.

{{< hint type="note" >}}
The
[Authentication](https://docs.upbound.io/providers/provider-azure/authentication/) 
section of the Azure Provider documentation describes other authentication methods.
{{< /hint >}}

### Create a Kubernetes secret with the Azure credentials
A Kubernetes generic secret has a name and contents. Use {{< hover label="kube-create-secret" line="1">}}kubectl create secret{{< /hover >}} to generate the secret object named {{< hover label="kube-create-secret" line="2">}}azure-secret{{< /hover >}} in the {{< hover label="kube-create-secret" line="3">}}crossplane-system{{</ hover >}} namespace.  

<!-- vale gitlab.Substitutions = NO -->
<!-- ignore .json file name -->
Use the {{< hover label="kube-create-secret" line="4">}}--from-file={{</hover>}} argument to set the value to the contents of the  {{< hover label="kube-create-secret" line="4">}}azure-credentials.json{{< /hover >}} file.
<!-- vale gitlab.Substitutions = YES -->
```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret \
generic azure-secret \
-n crossplane-system \
--from-file=creds=./azure-credentials.json
```

View the secret with `kubectl describe secret`

{{< hint type="note" >}}
The size may be larger if there are extra blank spaces in your text file.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl describe secret azure-secret -n crossplane-system
Name:         azure-secret
Namespace:    crossplane-system
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
creds:  629 bytes
```

## Create a ProviderConfig
A `ProviderConfig` customizes the settings of the Azure Provider.  

Apply the {{< hover label="providerconfig" line="5">}}ProviderConfig{{</ hover >}} with the command:
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

This attaches the Azure credentials, saved as a Kubernetes secret, as a {{< hover label="providerconfig" line="9">}}secretRef{{</ hover>}}.

The {{< hover label="providerconfig" line="11">}}spec.credentials.secretRef.name{{< /hover >}} value is the name of the Kubernetes secret containing the Azure credentials in the {{< hover label="providerconfig" line="10">}}spec.credentials.secretRef.namespace{{< /hover >}}.


## Create a managed resource
A _managed resource_ is anything Crossplane creates and manages outside of the 
Kubernetes cluster. This example creates an Azure Virtual Network with 
Crossplane. The Virtual Network is a _managed resource_.

{{< hint type="note" >}}
Add your Azure Resource Group name. Follow the Azure documentation to 
[create a resource group](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal)
if you don't have one.
{{< /hint >}}

{{< editCode >}}
```yaml {label="xr"}
cat <<EOF | kubectl create -f -
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetwork
metadata:
  name: crossplane-quickstart-network
spec:
  forProvider:
    addressSpace:
      - 10.0.0.0/16
    location: "Sweden Central"
    resourceGroupName: docs
EOF
```
{{< /editCode >}}

The {{< hover label="xr" line="2">}}apiVersion{{< /hover >}} and 
{{< hover label="xr" line="3">}}kind{{</hover >}} are from the provider's CRDs.

The {{< hover label="xr" line="10">}}spec.forProvider.location{{< /hover >}} 
tells Azure which location to use when deploying the resource. 

Use `kubectl get virtualnetwork.network` to verify Crossplane created the
Azure Virtual Network.

{{< hint type="tip" >}}
Crossplane created the virtual network when the values `READY` and `SYNCED` are `True`.  
This may take up to 5 minutes.  
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get virtualnetwork.network
NAME                            READY   SYNCED   EXTERNAL-NAME                   AGE
crossplane-quickstart-network   True    True     crossplane-quickstart-network   10m
```

## Delete the managed resource
Before shutting down your Kubernetes cluster, delete the virtual network just 
created.

Use `kubectl delete virtualnetwork.network` to delete the virtual network. 


```shell {copy-lines="1"}
kubectl delete virtualnetwork.network crossplane-quickstart-network
virtualnetwork.network.azure.upbound.io "crossplane-quickstart-network" deleted
```

## Next steps
* [**Continue to part 2**]({{< ref "provider-azure-part-2">}}) to create and use
  a custom API with Crossplane.
* Explore Azure resources that Crossplane can configure in the 
  [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-family-azure/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with 
  Crossplane users and contributors.
