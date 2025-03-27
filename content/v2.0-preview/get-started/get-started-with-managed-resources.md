---
title: Get Started With Managed Resources
weight: 200
---

Connect Crossplane to AWS to create and manage cloud resources from Kubernetes
with [provider-upjet-aws](https://github.com/crossplane-contrib/provider-upjet-aws).


## Prerequisites
This quickstart requires:

* A Kubernetes cluster with at least 2 GB of RAM
* The Crossplane v2 preview [installed on the Kubernetes cluster]({{<ref "install">}})
* An AWS account with permissions to create an S3 storage bucket
* AWS [access keys](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds)

## About Managed Resources in Crossplane v2
A _managed resource_ is anything Crossplane creates and manages outside of the
Kubernetes cluster.

This guide creates an AWS S3 bucket with Crossplane.

The S3 bucket is a _managed resource_.

Crossplane v2 allows you to compose namespaced resources. To better support this
new ability, managed resources (MRs) are now namespaced in Providers that have
been updated for Crossplane v2.

To support backwards compatibility while users are adopting Crossplane v2, each
provider will offer the legacy cluster scoped MRs in addition to the new
namespaced MRs.

For example, when the AWS provider that has been upated to support Crossplane v2
is installed during this guide, you will see two CRDs for each type of managed
resource:

1. A legacy cluster scoped MR in the `*.aws.upbound.io` API group
1. A namespaced MR in the `*.aws.m.upbound.io` API group

{{< hint type="tip" >}}
More about namespaced managed resources can be read in the [Crossplane v2 proposal](https://github.com/crossplane/crossplane/pull/6255).
{{< /hint >}}

## Install the AWS provider

Install the AWS S3 provider into the Kubernetes cluster with a Kubernetes
configuration file.

```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v1.22.0-crossplane-v2-preview.0
EOF
```

The Crossplane {{< hover label="provider" line="3" >}}Provider{{</hover>}}
installs the Kubernetes _Custom Resource Definitions_ (CRDs) representing AWS S3
services. These CRDs allow you to create AWS resources directly inside
Kubernetes.

Verify the provider installed with `kubectl get providers`.


```shell {copy-lines="1",label="getProvider"}
kubectl get providers
NAME                                     INSTALLED   HEALTHY   PACKAGE                                                                                     AGE
crossplane-contrib-provider-family-aws   True        True      xpkg.crossplane.io/crossplane-contrib/provider-family-aws:v1.22.0-crossplane-v2-preview.0   27s
provider-aws-s3                          True        True      xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v1.22.0-crossplane-v2-preview.0       31s
```

The S3 Provider installs a second Provider, the
{{<hover label="getProvider" line="4">}}crossplane-contrib-provider-family-aws{{</hover >}}.
The family provider manages authentication to AWS across all AWS family
Providers.

You can view the new CRDs with `kubectl get crds`.
Every CRD maps to a unique AWS service Crossplane can provision and manage.

{{< hint type="tip" >}}
See details about all the supported CRDs in the
[provider examples](https://github.com/crossplane-contrib/provider-upjet-aws/tree/main/examples).
{{< /hint >}}

## Create a Kubernetes secret for AWS
The provider requires credentials to create and manage AWS resources.
Providers use a Kubernetes _Secret_ to connect the credentials to the provider.

Generate a Kubernetes _Secret_ from your AWS key-pair and
then configure the Provider to use it.

### Generate an AWS key-pair file
For basic user authentication, use an AWS Access keys key-pair file.

{{< hint type="tip" >}}
The [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds)
provides information on how to generate AWS Access keys.
{{< /hint >}}

Create a text file containing the AWS account `aws_access_key_id` and `aws_secret_access_key`.

{{< editCode >}}
```ini {copy-lines="all"}
[default]
aws_access_key_id = $@<aws_access_key>$@
aws_secret_access_key = $@<aws_secret_key>$@
```
{{< /editCode >}}

Save this text file as `aws-credentials.txt`.

{{< hint type="note" >}}
The [Authentication](https://docs.upbound.io/providers/provider-aws/authentication/) section of the AWS Provider documentation describes other authentication methods.
{{< /hint >}}

### Create a Kubernetes secret with the AWS credentials
A Kubernetes generic secret has a name and contents.
Use
{{< hover label="kube-create-secret" line="1">}}kubectl create secret{{</hover >}}
to generate the secret object named
{{< hover label="kube-create-secret" line="2">}}aws-secret{{< /hover >}}
in the {{< hover label="kube-create-secret" line="3">}}crossplane-system{{</ hover >}} namespace.

Use the {{< hover label="kube-create-secret" line="4">}}--from-file={{</hover>}} argument to set the value to the contents of the  {{< hover label="kube-create-secret" line="4">}}aws-credentials.txt{{< /hover >}} file.

```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret \
generic aws-secret \
-n crossplane-system \
--from-file=creds=./aws-credentials.txt
```

View the secret with `kubectl describe secret`

{{< hint type="note" >}}
The size may be larger if there are extra blank spaces in your text file.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl describe secret aws-secret -n crossplane-system
Name:         aws-secret
Namespace:    crossplane-system
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
creds:  114 bytes
```

## Create a ProviderConfig
A {{< hover label="providerconfig" line="3">}}ProviderConfig{{</ hover >}}
customizes the settings of the AWS Provider.

Apply the
{{< hover label="providerconfig" line="3">}}ProviderConfig{{</ hover >}}
with the this Kubernetes configuration file:
```yaml {label="providerconfig",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: aws.upbound.io/v1beta1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-secret
      key: creds
EOF
```

This attaches the AWS credentials, saved as a Kubernetes secret, as a
{{< hover label="providerconfig" line="9">}}secretRef{{</ hover>}}.

The
{{< hover label="providerconfig" line="11">}}spec.credentials.secretRef.name{{< /hover >}}
value is the name of the Kubernetes secret containing the AWS credentials in the
{{< hover label="providerconfig" line="10">}}spec.credentials.secretRef.namespace{{< /hover >}}.

## Create a namespace
Before we can create our namespaced S3 bucket managed resource, we must create a
namespace for it.

```shell {label="kube-create-namespace",copy-lines="all"}
kubectl create namespace crossplane-aws-app
```

## Create a managed resource
{{< hint type="note" >}}
AWS S3 bucket names must be globally unique. To generate a unique name the example uses a random hash.
Any unique name is acceptable.
{{< /hint >}}

```yaml {label="xr"}
cat <<EOF | kubectl create -f -
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  namespace: crossplane-aws-app
  generateName: crossplane-bucket-
spec:
  forProvider:
    region: us-east-2
  providerConfigRef:
    name: default
EOF
```

The {{< hover label="xr" line="2">}}apiVersion{{< /hover >}} and
{{< hover label="xr" line="3">}}kind{{</hover >}} are from the provider's CRDs.

The {{< hover label="xr" line="6">}}metadata.generateName{{< /hover >}} gives a
pattern that the provider will use to create a unique name for the bucket in S3.
The generated name will look like `crossplane-bucket-<hash>`.

The {{< hover label="xr" line="9">}}spec.forProvider.region{{< /hover >}} tells
AWS which AWS region to use when deploying resources.

The region can be any
[AWS Regional endpoint](https://docs.aws.amazon.com/general/latest/gr/rande.html#regional-endpoints) code.

Use `kubectl -n crossplane-aws-app get buckets.s3.aws.m.upbound.io` to verify Crossplane created the bucket.

{{< hint type="tip" >}}
Crossplane created the bucket when the values `READY` and `SYNCED` are `True`.
This may take up to 5 minutes.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl -n crossplane-aws-app get buckets.s3.aws.m.upbound.io
NAME                      SYNCED   READY   EXTERNAL-NAME             AGE
crossplane-bucket-7tfcj   True     True    crossplane-bucket-7tfcj   3m4s
```

## Delete the managed resource
Before shutting down your Kubernetes cluster, delete the S3 bucket just created.

Use `kubectl -n crossplane-aws-app delete buckets.s3.aws.m.upbound.io <bucketname>` to remove the bucket.

```shell {copy-lines="1"}
kubectl -n crossplane-aws-app delete buckets.s3.aws.m.upbound.io crossplane-bucket-7tfcj
bucket.s3.aws.m.upbound.io "crossplane-bucket-7tfcj" deleted
```

## Composing managed resources
Crossplane v2 allows you to compose **any type of resource** into custom APIs
for your users, which includes managed resources. Enjoy the freedom that
Crossplane v2 gives you to compose the diverse set of resources your
applications need for their unique environments, scenarios, and requirements.

Follow [Get Started with Composition]({{<ref "../get-started/get-started-with-composition">}})
to learn more about how composition works.

## Next steps
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with
  Crossplane users and contributors.
