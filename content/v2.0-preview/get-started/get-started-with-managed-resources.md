---
title: Get Started With Managed Resources
weight: 200
---

Connect Crossplane to AWS to create and manage cloud resources from Kubernetes
with [provider-upjet-aws](https://github.com/crossplane-contrib/provider-upjet-aws).

A _managed resource_ is anything Crossplane creates and manages outside of the
control plane.

This guide creates an AWS S3 bucket with Crossplane. The S3 bucket is a _managed resource_.

## Prerequisites
This quickstart requires:

* A Kubernetes cluster with at least 2 GB of RAM
* The Crossplane v2 preview [installed on the Kubernetes cluster]({{<ref "install">}})
* An AWS account with permissions to create an S3 storage bucket
* AWS [access keys](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds)

## Install the AWS provider
Install the AWS S3 provider into the Kubernetes cluster with a Kubernetes
configuration file.

```yaml {label="provider",copy-lines="all"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v1.22.0-crossplane-v2-preview.0
```

Save this to a file called `provider.yaml`, then apply it with:
```shell {label="kube-apply-provider",copy-lines="all"}
kubectl apply -f provider.yaml
```

The Crossplane {{< hover label="provider" line="2" >}}Provider{{</hover>}}
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

{{< hint "tip" >}}
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

{{< hint "tip" >}}
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

{{< hint "note" >}}
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

## Create a ProviderConfig
A {{< hover label="providerconfig" line="2">}}ProviderConfig{{</ hover >}}
customizes the settings of the AWS Provider:

```yaml {label="providerconfig",copy-lines="all"}
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
```

Save this to a file called `providerconfig.yaml`, then apply it with:

```shell {label="kube-apply-providerconfig",copy-lines="all"}
kubectl apply -f providerconfig.yaml
```

This attaches the AWS credentials, saved as a Kubernetes secret, as a
{{< hover label="providerconfig" line="8">}}secretRef{{</ hover>}}.

## Create a managed resource
{{< hint "note" >}}
AWS S3 bucket names must be globally unique. To generate a unique name the example uses a random hash.
Any unique name is acceptable.
{{< /hint >}}

```yaml {label="bucket"}
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  namespace: default
  generateName: crossplane-bucket-
spec:
  forProvider:
    region: us-east-2
  providerConfigRef:
    name: default
```

Save this to a file called `bucket.yaml`, then apply it with:

```shell {label="kube-create-bucket",copy-lines="all"}
kubectl create -f bucket.yaml
```

The {{< hover label="bucket" line="5">}}metadata.generateName{{< /hover >}} gives a
pattern that Kubernetes will use to create a unique name for the bucket in S3.
The generated name will look like `crossplane-bucket-<hash>`.

Use `kubectl -n default get buckets.s3.aws.m.upbound.io` to verify Crossplane created the bucket.

{{< hint "tip" >}}
Crossplane created the bucket when the values `READY` and `SYNCED` are `True`.
This may take up to 5 minutes.
{{< /hint >}}

```shell {copy-lines="1"}
kubectl -n default get buckets.s3.aws.m.upbound.io
NAME                      SYNCED   READY   EXTERNAL-NAME             AGE
crossplane-bucket-7tfcj   True     True    crossplane-bucket-7tfcj   3m4s
```

## Delete the managed resource
When you are finished with your S3 bucket, use `kubectl -n default
delete buckets.s3.aws.m.upbound.io <bucketname>` to remove the bucket.

```shell {copy-lines="1"}
kubectl -n default delete buckets.s3.aws.m.upbound.io crossplane-bucket-7tfcj
bucket.s3.aws.m.upbound.io "crossplane-bucket-7tfcj" deleted
```

{{< hint "important" >}}
Make sure to delete the S3 bucket before uninstalling the provider or shutting
down your control plane. If those are no longer running, they can't clean up any
managed resources and you would need to do so manually.
{{< /hint >}}

## Composing managed resources
Crossplane allows you to compose **any type of resource** into custom APIs for
your users, which includes managed resources. Enjoy the freedom that Crossplane
gives you to compose the diverse set of resources your applications need for
their unique environments, scenarios, and requirements.

Follow [Get Started with Composition]({{<ref "../get-started/get-started-with-composition">}})
to learn more about how composition works.

## Next steps
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with
  Crossplane users and contributors.
