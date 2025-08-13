---
title: Get Started With Managed Resources
weight: 300
---

This guide shows how to install and use a new kind of custom resource called
`Bucket`. When a user calls the custom resource API to create a `Bucket`,
Crossplane creates a bucket in AWS S3.

**Crossplane calls this a _managed resource_**. A managed resource is a
ready-made custom resource that manages something outside of the control plane.

A `Bucket` managed resource looks like this:

```yaml
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  namespace: default
  name: crossplane-bucket-example
spec:
  forProvider:
    region: us-east-2
```

{{<hint "note">}}
Kubernetes calls third party API resources _custom resources_.
{{</hint>}}

## Prerequisites

This guide requires:

* A Kubernetes cluster with at least 2 GB of RAM
* Crossplane v2 [installed on the Kubernetes cluster]({{<ref "install">}})
* An AWS account with permissions to create an S3 storage bucket
* AWS [access keys](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds)


## Install support for the managed resource

Follow these steps to install support for the `Bucket` managed resource:

1. [Install](#install-the-provider) the provider
1. [Save](#save-the-providers-credentials) the provider's credentials as a secret
1. [Configure](#configure-the-provider) the provider to use the secret

After you complete these steps you can
[use the `Bucket` managed resource](#use-the-managed-resource).

### Install the provider

A Crossplane _provider_ installs support for a set of related managed resources.
The AWS S3 provider installs support for all the AWS S3 managed resources.

Create this provider to install the AWS S3 provider:

```yaml {label="provider",copy-lines="all"}
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: crossplane-contrib-provider-aws-s3
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v2.0.0
```

Save this as `provider.yaml` and apply it:

```shell {label="kube-apply-provider",copy-lines="all"}
kubectl apply -f provider.yaml
```

Check that Crossplane installed the provider:

```shell {copy-lines="1",label="getProvider"}
kubectl get providers
NAME                                     INSTALLED   HEALTHY   PACKAGE                                                                                     AGE
crossplane-contrib-provider-family-aws   True        True      xpkg.crossplane.io/crossplane-contrib/provider-family-aws:v2.0.0   27s
crossplane-contrib-provider-aws-s3       True        True      xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v2.0.0       31s
```

{{<hint "note">}}
The S3 provider installs a second provider, the
{{<hover label="getProvider" line="4">}}crossplane-contrib-provider-family-aws{{</hover >}}.
The family provider manages authentication to AWS across all AWS family
providers.
{{</hint>}}

Crossplane installed the AWS S3 provider. The provider needs credentials to
connect to AWS. Before you can use managed resources, you have to
[save the provider's credentials](#save-the-providers-credentials) and
[configure the provider to use them](#configure-the-provider).

### Save the provider's credentials

The provider needs credentials to create and manage AWS resources. Providers use
a Kubernetes _secret_ to connect the credentials to the provider.

Generate a secret from your AWS key-pair.

{{<hint "tip">}}
The [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-creds)
provides information on how to generate AWS Access keys.
{{</hint>}}

Create a file containing the AWS account `aws_access_key_id` and
`aws_secret_access_key`:

{{< editCode >}}
```ini {copy-lines="all"}
[default]
aws_access_key_id = $@<aws_access_key>$@
aws_secret_access_key = $@<aws_secret_key>$@
```
{{< /editCode >}}

Save the text file as `aws-credentials.ini`.

{{<hint "note">}}
The [Authentication](https://docs.upbound.io/providers/provider-aws/authentication/)
section of the AWS Provider documentation describes other authentication methods.
{{</hint>}}

Create a secret from the text file:

```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret generic aws-secret \
  --namespace=crossplane-system \
  --from-file=creds=./aws-credentials.ini
```

{{<hint "important">}}
Crossplane providers don't have to store their credentials in a secret. They
can load their credentials from multiple sources.
{{</hint>}}

Next, [configure the provider](#configure-the-provider) to use the credentials.

### Configure the provider

A {{< hover label="providerconfig" line="2">}}provider configuration{{</ hover >}}
customizes the settings of the AWS Provider.

All providers need a configuration to tell them where to load credentials.

Create this cluster-wide provider configuration:

```yaml {label="providerconfig",copy-lines="all"}
apiVersion: aws.m.upbound.io/v1beta1
kind: ClusterProviderConfig
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

Save the provider configuration as `providerconfig.yaml` and apply it:

```shell {label="kube-apply-providerconfig",copy-lines="all"}
kubectl apply -f providerconfig.yaml
```

This tells the provider to load credentials from
[the secret](#save-the-providers-credentials).

{{<hint "note">}}
This example uses a `ClusterProviderConfig` that applies to managed resources
across all namespaces.

You can also use a namespaced `ProviderConfig` that only applies to managed
resources in a specific namespace. See the [`providerConfigRef`]({{<ref "../managed-resources/managed-resources#providerconfigref">}}) 
section in the managed resources docs for more details.
{{</hint>}}

## Use the managed resource

{{<hint "note">}}
AWS S3 bucket names must be globally unique. This example uses `generateName` to
generate a random name. Any unique name is acceptable.
{{</hint>}}

```yaml {label="bucket"}
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  namespace: default
  generateName: crossplane-bucket-
spec:
  forProvider:
    region: us-east-2
```

Save the bucket to `bucket.yaml` and apply it:

```shell {label="kube-create-bucket",copy-lines="all"}
kubectl create -f bucket.yaml
```

Check that Crossplane created the bucket:

```shell {copy-lines="1"}
kubectl get buckets.s3.aws.m.upbound.io
NAME                      SYNCED   READY   EXTERNAL-NAME             AGE
crossplane-bucket-7tfcj   True     True    crossplane-bucket-7tfcj   3m4s
```

{{<hint "tip">}}
Crossplane created the bucket when the values `READY` and `SYNCED` are `True`.
{{</hint>}}

Delete the bucket:

```shell {copy-lines="1"}
kubectl delete buckets.s3.aws.m.upbound.io crossplane-bucket-7tfcj
bucket.s3.aws.m.upbound.io "crossplane-bucket-7tfcj" deleted
```

When you delete the bucket managed resource, Crossplane deletes the S3 bucket
from AWS.

{{<hint "important">}}
Make sure to delete the S3 bucket before uninstalling the provider or shutting
down your control plane. If those are no longer running, they can't clean up any
managed resources and you would need to do so manually.
{{</hint>}}

## Next steps

Crossplane allows you to compose **any kind of resource** into custom APIs for
your users, which includes managed resources. Enjoy the freedom that Crossplane
gives you to compose the diverse set of resources your applications need for
their unique environments, scenarios, and requirements.

Follow [Get Started with Composition]({{<ref "../get-started/get-started-with-composition">}})
to learn more about how composition works.
