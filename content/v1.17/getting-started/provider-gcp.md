---
title: GCP Quickstart
weight: 140
---

Connect Crossplane to GCP to create and manage cloud resources from Kubernetes 
with the 
[Upbound GCP Provider](https://marketplace.upbound.io/providers/upbound/provider-family-gcp/).

This guide is in two parts:
* Part 1 walks through installing Crossplane, configuring the provider to
authenticate to GCP and creating a _Managed Resource_ in GCP directly from 
your Kubernetes cluster. This shows Crossplane can communicate with GCP.
* [Part 2]({{< ref "provider-gcp-part-2" >}}) shows how to build and access a 
  custom API with Crossplane.
## Prerequisites
This quickstart requires:
* a Kubernetes cluster with at least 2 GB of RAM
* permissions to create pods and secrets in the Kubernetes cluster
* [Helm](https://helm.sh/) version v3.2.0 or later
* a GCP account with permissions to create a storage bucket
* GCP [account keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
* GCP [Project ID](https://support.google.com/googleapi/answer/7014113?hl=en)

{{<include file="/master/getting-started/install-crossplane-include.md" type="page" >}}

## Install the GCP provider

Install the provider into the Kubernetes cluster with a Kubernetes configuration 
file. 

```shell {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-gcp-storage
spec:
  package: xpkg.upbound.io/upbound/provider-gcp-storage:v0.41.0
EOF
```

The Crossplane {{< hover label="provider" line="3" >}}Provider{{</hover>}}
installs the Kubernetes _Custom Resource Definitions_ (CRDs) representing GCP storage
services. These CRDs allow you to create GCP resources directly inside 
Kubernetes.

Verify the provider installed with `kubectl get providers`. 


```shell {copy-lines="1",label="getProvider"}
kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                                AGE
provider-gcp-storage          True        True      xpkg.upbound.io/upbound/provider-gcp-storage:v0.41.0   36s
upbound-provider-family-gcp   True        True      xpkg.upbound.io/upbound/provider-family-gcp:v0.41.0    29s
```

The Storage Provider installs a second Provider, the
{{<hover label="getProvider" line="4">}}upbound-provider-family-gcp{{</hover>}} 
provider.   
The family provider manages authentication to GCP across all GCP family
Providers. 

You can view the new CRDs with `kubectl get crds`.  
Every CRD maps to a unique GCP service Crossplane can provision and manage.

{{< hint "tip" >}}
See details about all the supported CRDs in the 
[Upbound Marketplace](https://marketplace.upbound.io/providers/upbound/provider-family-gcp/).
{{< /hint >}}


## Create a Kubernetes secret for GCP
The provider requires credentials to create and manage GCP resources. Providers 
use a Kubernetes _Secret_ to connect the credentials to the provider.

First generate a Kubernetes _Secret_ from a Google Cloud service account JSON 
file and then configure the Provider to use it.

### Generate a GCP service account JSON file
For basic user authentication, use a Google Cloud service account JSON file. 

{{< hint "tip" >}}
The 
[GCP documentation](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) 
provides information on how to generate a service account JSON file.
{{< /hint >}}

Save this JSON file as `gcp-credentials.json`


### Create a Kubernetes secret with the GCP credentials
A Kubernetes generic secret has a name and contents. Use 
{{< hover label="kube-create-secret" line="1">}}kubectl create secret{{< /hover >}} 
to generate the secret object named 
{{< hover label="kube-create-secret" line="2">}}gcp-secret{{< /hover >}} in the 
{{< hover label="kube-create-secret" line="3">}}crossplane-system{{</ hover >}} 
namespace.  
Use the {{< hover label="kube-create-secret" line="4">}}--from-file={{</hover>}}
argument to set the value to the contents of the 
{{< hover label="kube-create-secret" line="4">}}gcp-credentials.json{{< /hover >}} 
file.


```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret \
generic gcp-secret \
-n crossplane-system \
--from-file=creds=./gcp-credentials.json
```

View the secret with `kubectl describe secret`

{{< hint "note" >}}
The file size may be a different depending on the contents.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl describe secret gcp-secret -n crossplane-system
Name:         gcp-secret
Namespace:    crossplane-system
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
creds:  2330 bytes
```

{{< hint type="note" >}}
The
[Authentication](https://docs.upbound.io/providers/provider-gcp/authentication/) 
section of the GCP Provider documentation describes other authentication methods.
{{< /hint >}}

## Create a ProviderConfig
A `ProviderConfig` customizes the settings of the GCP Provider.  

Include your 
{{< hover label="providerconfig" line="7" >}}GCP project ID{{< /hover >}} in the
_ProviderConfig_ settings.

{{< hint "tip" >}}
Find your GCP project ID from the `project_id` field of the 
`gcp-credentials.json` file.
{{< /hint >}}

Apply the 
{{< hover label="providerconfig" line="2">}}ProviderConfig{{</ hover >}} with
the command: 

{{< editCode >}}
```yaml {label="providerconfig",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: gcp.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  projectID: $@<PROJECT_ID>$@
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: gcp-secret
      key: creds
EOF
```
{{< /editCode >}}

This attaches the GCP credentials, saved as a Kubernetes secret, as a 
{{< hover label="providerconfig" line="10">}}secretRef{{</ hover>}}.

The {{< hover label="providerconfig" line="12">}}spec.credentials.secretRef.name{{< /hover >}} value is the name of the Kubernetes secret containing the GCP credentials in the 
{{< hover label="providerconfig" line="11">}}spec.credentials.secretRef.namespace{{< /hover >}}.

## Create a managed resource
A _managed resource_ is anything Crossplane creates and manages outside of the 
Kubernetes cluster. This example creates a GCP storage bucket with Crossplane.  
The storage bucket is a _managed resource_.

{{< hint "note" >}}
To generate a unique name use 
{{<hover label="xr" line="5">}}generateName{{</hover >}} instead of `name`.
{{< /hint >}}

Create the Bucket with the following command:

```yaml {label="xr",copy-lines="all"}
cat <<EOF | kubectl create -f -
apiVersion: storage.gcp.upbound.io/v1beta1
kind: Bucket
metadata:
  generateName: crossplane-bucket-
  labels:
    docs.crossplane.io/example: provider-gcp
spec:
  forProvider:
    location: US
  providerConfigRef:
    name: default
EOF
```

The {{< hover label="xr" line="2">}}apiVersion{{< /hover >}} and 
{{< hover label="xr" line="3">}}kind{{</hover >}} are from the provider's CRDs.

The {{< hover label="xr" line="10">}}spec.forProvider.location{{< /hover >}} 
tells GCP which GCP region to use when deploying resources.  
For a 
{{<hover label="xr" line="3">}}bucket{{</hover >}} the 
region can be any 
[GCP multi-region location](https://cloud.google.com/storage/docs/locations#location-mr) 

Use `kubectl get bucket` to verify Crossplane created the bucket.

{{< hint type="tip" >}}
Crossplane created the bucket when the values `READY` and `SYNCED` are `True`.  
This may take up to 5 minutes.  
{{< /hint >}}

```shell {copy-lines="1"}
kubectl get bucket
NAME                      READY   SYNCED   EXTERNAL-NAME             AGE
crossplane-bucket-8b7gw   True    True     crossplane-bucket-8b7gw   2m2s
```

## Delete the managed resource
Before shutting down your Kubernetes cluster, delete the GCP bucket just 
created.

Use `kubectl delete bucket` to remove the bucket. 

{{<hint "tip" >}}
Use the `--selector` flag to delete by label instead of by name.
{{</hint>}}

```shell {copy-lines="1"}
kubectl delete bucket --selector docs.crossplane.io/example=provider-gcp
bucket.storage.gcp.upbound.io "crossplane-bucket-8b7gw" deleted
```

## Next steps 
* [**Continue to part 2**]({{< ref "provider-gcp-part-2">}}) to create a 
Crossplane _Composite Resource_ and _Claim_.
* Explore GCP resources that can Crossplane can configure in the 
[Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-family-gcp/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with 
Crossplane users and contributors.