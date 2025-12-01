---
title: Alibaba Cloud Quickstart
weight: 100
---

Connect Crossplane to Alibaba Cloud to create and manage cloud resources from Kubernetes
with  
[provider-upjet-alibabacloud](https://github.com/crossplane-contrib/provider-upjet-alibabacloud).

This guide is in two parts:
* Part 1 walks through installing Crossplane, configuring the provider to
  authenticate to Alibaba Cloud and creating a _Managed Resource_ in Alibaba Cloud directly from your
  Kubernetes cluster. This shows Crossplane can communicate with Alibaba Cloud.
* [Part 2]({{< ref "provider-alibabacloud-part-2" >}}) shows how to build and access a
  custom API with Crossplane.

## Prerequisites

This quickstart requires:

* a Kubernetes cluster with at least 2 GB of RAM
* permissions to create pods and secrets in the Kubernetes cluster
* [Helm](https://helm.sh/) version v3.2.0 or later
* an Alibaba Cloud account with permissions to create a VPC
* Alibaba Cloud [access keys](https://help.aliyun.com/document_detail/53045.html) (AccessKey ID and AccessKey Secret)

{{<include file="/master/getting-started/install-crossplane-include.md" type="page" >}}

## Install the Alibaba Cloud provider

Install the Alibaba Cloud OSS provider into the Kubernetes cluster with a Kubernetes
configuration file.

```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-upjet-alibabacloud
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-upjet-alibabacloud:v0.2.0
EOF
```

The Crossplane {{< hover label="provider" line="3" >}}Provider{{}}
installs the Kubernetes Custom Resource Definitions (CRDs) representing Alibaba Cloud
services. These CRDs allow you to create Alibaba Cloud resources directly inside
Kubernetes.

Verify the provider installed with `kubectl get providers`.
```shell {copy-lines="1",label="getProvider"}
$ kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                                                 AGE
provider-upjet-alibabacloud   True        True      xpkg.upbound.io/crossplane-contrib/provider-upjet-alibabacloud:v0.2.0   128m
```
You can view the new CRDs with `kubectl get crds`.
Every CRD maps to a unique Alibaba Cloud service Crossplane can provision and manage.

{{< hint type="tip" >}}
See details about all the supported CRDs in the
[provider examples](https://github.com/crossplane-contrib/provider-upjet-alibabacloud/tree/main/examples).
{{< /hint >}}

## Create a Kubernetes secret for Alibaba Cloud
The provider requires credentials to create and manage Alibaba Cloud resources.
Providers use a Kubernetes Secret to connect the credentials to the provider.

Generate a Kubernetes Secret from your Alibaba Cloud access keys and
then configure the Provider to use it.

### Generate an Alibaba Cloud credential
For basic user authentication, use an Alibaba Cloud access keys file.

{{< hint type="tip" >}}
The [Alibaba Cloud documentation](https://www.alibabacloud.com/help/en/ram/user-guide/create-an-accesskey-pair)
provides information on how to generate Alibaba Cloud access keys.
{{< /hint >}}

Create a `Secret` object named
{{< hover label="kube-create-secret" line="2">}}alibabacloud-secret{{< /hover >}}  
in the {{< hover label="kube-create-secret" line="3">}}crossplane-system{{</ hover >}} namespace
with the `stringData` containing the Alibaba Cloud accessKeyId and accessKeySecret.

{{< editCode >}}
```yaml {label="configSecret",copy-lines="all"}
apiVersion: v1
kind: Secret
metadata:
  name: alibabacloud-secret
  namespace: crossplane-system
type: Opaque
stringData:
  credentials: |
    {
      "access_key": $@<alibaba_cloud_access_key>$@,
      "secret_key": $@<alibaba_cloud_secret_key>$@
    }
```
{{< /editCode >}}
Save this text file as `alibabacloud-credential.yaml`.

## Create a Kubernetes secret with the Alibaba Cloud credentials

Apply the secret file to generate the secret object.
```shell {label="kube-create-secret",copy-lines="all"}
kubectl apply -f alibabacloud-credential.yaml
```
Verify the secret was created with `kubectl describe secrets`.
{{< hint type="note" >}}
The size may be larger if there are extra blank spaces in your text file.
{{< /hint >}}
```shell {copy-lines="1",label="getSecret"}
$ kubectl describe secret alibabacloud-secret -n crossplane-system
Name:         alibabacloud-secret
Namespace:    crossplane-system
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
credentials:  97 bytes
```
## Create a ProviderConfig
A {{< hover label="providerconfig" line="3">}}ProviderConfig{{</ hover >}}
customizes the settings of the Alibaba Cloud Provider.

Apply the
{{< hover label="providerconfig" line="3">}}ProviderConfig{{</ hover >}}
with this Kubernetes configuration file:
```yaml {label="providerconfig",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: alibabacloud.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: alibabacloud-secret
      key: credentials
EOF
```
This attaches the Alibaba Cloud credentials, saved as a Kubernetes secret, as a
{{< hover label="providerconfig" line="9">}}secretRef{{</ hover>}}.

The
{{< hover label="providerconfig" line="11">}}spec.credentials.secretRef.name{{< /hover >}}
value is the name of the Kubernetes secret containing the Alibaba Cloud credentials in the
{{< hover label="providerconfig" line="10">}}spec.credentials.secretRef.namespace{{< /hover >}}.

## Create a managed resource
A _managed resource_ is anything Crossplane creates and manages outside of the Kubernetes cluster.  

This guide creates an Alibaba Cloud VPC with Crossplane.  

The VPC is a _managed resource_.

```yaml {label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: vpc.alibabacloud.crossplane.io/v1alpha1
kind: VPC
metadata:
  name: crossplane-vpc
spec:
  forProvider:
    region: cn-zhangjiakou
    cidrBlock: 10.0.0.0/8
    description: test
    enableIpv6: true
    ipv6Isp: BGP
    vpcName: crossplane-quickstart-vpc
EOF
```
The {{< hover label="xr" line="2">}}apiVersion{{< /hover >}} and
{{< hover label="xr" line="3">}}kind{{}} are from the provider's CRDs.

The {{< hover label="xr" line="8">}}spec.forProvider.region{{< /hover >}} tells
Alibaba Cloud which region to use when deploying resources.

The region can be any
[Alibaba Cloud region](https://www.alibabacloud.com/help/en/cloud-migration-guide-for-beginners/latest/regions-and-zones) code.

Use `kubectl get vpcs` to verify Crossplane created the VPC.

{{< hint type="tip" >}}
Crossplane created the vpc when the values READY and SYNCED are True.
This may take up to 1 minutes.
{{< /hint >}}
```shell {label="getVpc",copy-lines="all"}
$ kubectl get vpcs
NAME             SYNCED   READY   EXTERNAL-NAME               AGE
crossplane-vpc   True     True    vpc-8vb3c********   15s
```

## Delete the managed resource
Before shutting down your Kubernetes cluster, delete the VPC just created.

Use `kubectl delete vpc <vpc name>` to remove the vpc.

```shell {label="deleteVpc",copy-lines="all"}
$ kubectl delete vpc crossplane-vpc
vpc.vpc.alibabacloud.crossplane.io "crossplane-vpc" deleted
```
## Next steps
* [**Continue to part 2**]({{< ref "provider-alibabacloud-part-2">}}) to create and use a 
custom API with Crossplane.
* [**Learn more about Crossplane**](https://crossplane.io/)
* [**Learn more about Alibaba Cloud**](https://www.alibabacloud.com/)
* [**Continue to part 2**]({{< ref "provider-alibabacloud-part-2">}}) to create and use a
  custom API with Crossplane.
* Explore AlibabaCloud resources that Crossplane can configure in the
  [provider CRD reference](https://github.com/crossplane-contrib/provider-upjet-alibabacloud/blob/main/package/crds).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with
  Crossplane users and contributors.