---
title: AWS Quickstart Part 2
weight: 120
tocHidden: true
aliases:
  - /master/getting-started/provider-aws-part-3
---

{{< hint "important" >}}
This guide is part 2 of a series.  

[**Part 1**]({{<ref "provider-aws" >}}) covers
to installing Crossplane and connect your Kubernetes cluster to AWS.

{{< /hint >}}

This guide walks you through building and accessing a custom API with Crossplane.

## Prerequisites
* Complete [quickstart part 1]({{<ref "provider-aws" >}}) connecting Kubernetes
  to AWS.
* an AWS account with permissions to create an AWS S3 storage bucket and a
  DynamoDB instance

{{<expand "Skip part 1 and just get started" >}}
1. Add the Crossplane Helm repository and install Crossplane
```shell
helm repo add \
crossplane-stable https://charts.crossplane.io/stable
helm repo update

helm install crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace
```

2. When the Crossplane pods finish installing and are ready, apply the AWS Provider
   
```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: xpkg.upbound.io/upbound/provider-aws-s3:v1.1.0
EOF
```

3. Create a file with your AWS keys
```ini
[default]
aws_access_key_id = <aws_access_key>
aws_secret_access_key = <aws_secret_key>
```

4. Create a Kubernetes secret from the AWS keys
```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret \
generic aws-secret \
-n crossplane-system \
--from-file=creds=./aws-credentials.txt
```

5. Create a _ProviderConfig_
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
{{</expand >}}

## Install the DynamoDB Provider

Part 1 only installed the AWS S3 Provider. This section deploys an S3 bucket 
along with a DynamoDB Table.  
Deploying a DynamoDB Table requires the DynamoDB Provider as well. 

Add the new Provider to the cluster. 

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-dynamodb
spec:
  package: xpkg.upbound.io/upbound/provider-aws-dynamodb:v1.1.0
EOF
```

View the new DynamoDB provider with `kubectl get providers`.


```shell {copy-lines="1"}
kubectl get providers
NAME                          INSTALLED   HEALTHY   PACKAGE                                                 AGE
provider-aws-dynamodb         True        True      xpkg.upbound.io/upbound/provider-aws-dynamodb:v1.1.0     3m55s
provider-aws-s3               True        True      xpkg.upbound.io/upbound/provider-aws-s3:v1.1.0           13m
upbound-provider-family-aws   True        True      xpkg.upbound.io/upbound/provider-family-aws:v1.1.0       13m
```

## Create a custom API

<!-- vale alex.Condescending = NO -->
Crossplane allows you to build your own custom APIs for your users, abstracting
away details about the cloud provider and their resources. You can make your API
as complex or simple as you wish. 
<!-- vale alex.Condescending = YES -->

The custom API is a Kubernetes object.  
Here is an example custom API.

```yaml {label="exAPI"}
apiVersion: database.example.com/v1alpha1
kind: NoSQL
metadata:
  name: my-nosql-database
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
{{<hover label="version" line="1">}}database.example.com{{</hover>}}.

Because this is the first version of the API, this guide uses the version
{{<hover label="version" line="1">}}v1alpha1{{</hover>}}.

```yaml {label="version",copy-lines="none"}
apiVersion: database.example.com/v1alpha1
```

### Define a kind

The API group is a logical collection of related APIs. In a group are
individual kinds representing different resources.

For example a `database` group may have a `Relational` and `NoSQL` kinds.

The `kind` can be anything, but it must be 
[UpperCamelCased](https://kubernetes.io/docs/contribute/style/style-guide/#use-upper-camel-case-for-api-objects).

This API's kind is 
{{<hover label="kind" line="2">}}NoSQL{{</hover>}}

```yaml {label="kind",copy-lines="none"}
apiVersion: database.example.com/v1alpha1
kind: NoSQL
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
apiVersion: database.example.com/v1alpha1
kind: NoSQL
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
combination of the {{<hover label="xrd" line="9">}}plural{{</hover>}} and 
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
  name: nosqls.database.example.com
spec:
  group: database.example.com
  names:
    kind: NoSQL
    plural: nosqls
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
    kind: NoSQLClaim
    plural: nosqlclaim
EOF
```

Adding the {{<hover label="xrd" line="29">}}claimNames{{</hover>}} allows users
to access this API either at the cluster level with the 
{{<hover label="xrd" line="9">}}nosql{{</hover>}} endpoint or in a namespace
with the 
{{<hover label="xrd" line="29">}}nosqlclaim{{</hover>}} endpoint. 

The namespace scoped API is a Crossplane _Claim_.

{{<hint "tip" >}}
For more details on the fields and options of Composite Resource Definitions
read the 
[XRD documentation]({{<ref "../concepts/composite-resource-definitions">}}). 
{{< /hint >}}

View the installed XRD with `kubectl get xrd`.  

```shell {copy-lines="1"}
kubectl get xrd
NAME                          ESTABLISHED   OFFERED   AGE
nosqls.database.example.com   True          True      2s
```

View the new custom API endpoints with `kubectl api-resources | grep nosql`

```shell {copy-lines="1",label="apiRes"}
kubectl api-resources | grep nosql
nosqlclaim                                     database.example.com/v1alpha1          true         NoSQLClaim
nosqls                                         database.example.com/v1alpha1          false        NoSQL
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

This template creates an AWS 
{{<hover label="comp" line="13">}}S3{{</hover>}}
{{<hover label="comp" line="14">}}Bucket{{</hover>}} and a 
{{<hover label="comp" line="33">}}DynamoDB{{</hover>}}
{{<hover label="comp" line="34">}}Table{{</hover>}}.

Crossplane uses {{<hover label="comp" line="19">}}patches{{</hover>}} to apply
the user's input to the resource template.  
This Composition takes the user's 
{{<hover label="comp" line="21">}}location{{</hover>}} input and uses it as the 
{{<hover label="comp" line="16">}}region{{</hover>}} used in the individual 
resource.

Apply this Composition to your cluster. 

```yaml {label="comp",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: dynamo-with-bucket
spec:
  resources:
    - name: s3Bucket
      base:
        apiVersion: s3.aws.upbound.io/v1beta1
        kind: Bucket
        metadata:
          name: crossplane-quickstart-bucket
        spec:
          forProvider:
            region: us-east-2
          providerConfigRef:
            name: default
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.region"
          transforms:
            - type: map
              map: 
                EU: "eu-north-1"
                US: "us-east-2"
    - name: dynamoDB
      base:
        apiVersion: dynamodb.aws.upbound.io/v1beta1
        kind: Table
        metadata:
          name: crossplane-quickstart-database
        spec:
          forProvider:
            region: "us-east-2"
            writeCapacity: 1
            readCapacity: 1
            attribute:
              - name: S3ID
                type: S
            hashKey: S3ID
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.region"
          transforms:
            - type: map
              map: 
                EU: "eu-north-1"
                US: "us-east-2"
  compositeTypeRef:
    apiVersion: database.example.com/v1alpha1
    kind: NoSQL
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
NAME                 XR-KIND   XR-APIVERSION                   AGE
dynamo-with-bucket   NoSQL     database.example.com/v1alpha1   3s
```



## Access the custom API

With the custom API (XRD) installed and associated to a resource template
(Composition) users can access the API to create resources.

Create a {{<hover label="xr" line="2">}}NoSQL{{</hover>}} object to create the
cloud resources.

```yaml {copy-lines="all",label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: database.example.com/v1alpha1
kind: NoSQL
metadata:
  name: my-nosql-database
spec: 
  location: "US"
EOF
```

View the resource with `kubectl get nosql`.

```shell {copy-lines="1"}
kubectl get nosql
NAME                SYNCED   READY   COMPOSITION          AGE
my-nosql-database   True     True    dynamo-with-bucket   14s
```

This object is a Crossplane _composite resource_ (also called an `XR`).  
It's a
single object representing the collection of resources created from the
Composition template. 

View the individual resources with `kubectl get managed`

```shell {copy-lines="1"}
kubectl get managed
NAME                                                    READY   SYNCED   EXTERNAL-NAME             AGE
table.dynamodb.aws.upbound.io/my-nosql-database-t5wtx   True    True     my-nosql-database-t5wtx   33s

NAME                                               READY   SYNCED   EXTERNAL-NAME             AGE
bucket.s3.aws.upbound.io/my-nosql-database-xtzph   True    True     my-nosql-database-xtzph   33s
```

Delete the resources with `kubectl delete nosql`.

```shell {copy-lines="1"}
kubectl delete nosql my-nosql-database
nosql.database.example.com "my-nosql-database" deleted
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

Accessing the API `nosql` happens at the cluster scope.  
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
apiVersion: database.example.com/v1alpha1
kind: NoSQLClaim
metadata:
  name: my-nosql-database
  namespace: crossplane-test
spec: 
  location: "US"
EOF
```
View the Claim with `kubectl get claim -n crossplane-test`.

```shell {copy-lines="1"}
kubectl get claim -n crossplane-test
NAME                SYNCED   READY   CONNECTION-SECRET   AGE
my-nosql-database   True     True                        17s
```

The Claim automatically creates a composite resource, which creates the managed
resources. 

View the Crossplane created composite resource with `kubectl get composite`.

```shell {copy-lines="1"}
kubectl get composite
NAME                      SYNCED   READY   COMPOSITION          AGE
my-nosql-database-t9qrw   True     True    dynamo-with-bucket   77s
```

Again, view the managed resources with `kubectl get managed`.

```shell {copy-lines="1"}
kubectl get managed
NAME                                                          READY   SYNCED   EXTERNAL-NAME                   AGE
table.dynamodb.aws.upbound.io/my-nosql-database-t9qrw-dcpwv   True    True     my-nosql-database-t9qrw-dcpwv   116s

NAME                                                     READY   SYNCED   EXTERNAL-NAME                   AGE
bucket.s3.aws.upbound.io/my-nosql-database-t9qrw-g98lv   True    True     my-nosql-database-t9qrw-g98lv   117s
```

Deleting the Claim deletes all the Crossplane generated resources.

`kubectl delete claim -n crossplane-test my-nosql-database`

```shell {copy-lines="1"}
kubectl delete claim -n crossplane-test my-nosql-database
nosqlclaim.database.example.com "my-nosql-database" deleted
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
* Explore AWS resources that Crossplane can configure in the 
  [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-family-aws/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with 
  Crossplane users and contributors.
* Read more about the [Crossplane concepts]({{<ref "../concepts">}}) to find out what else you can do
  with Crossplane. 
