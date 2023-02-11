---
title: AWS Quickstart Part 2
weight: 120
tocHidden: true
---

{{< hint "important" >}}
This guide is part 2 of a series. Follow **[part 1]({{<ref "provider-aws" >}})** 
to install Crossplane and connect your Kubernetes cluster to AWS.

**[Part 3]({{<ref "provider-aws-part-3">}})** covers patching _composite resources_
and using Crossplane _packages_.
{{< /hint >}}

This section creates a _[Composition](#create-a-composition)_, 
_[Composite Resource Definition](#define-a-composite-resource)_ and a
_[Claim](#create-a-claim)_
to create a custom Kubernetes API to create AWS resources. This custom API is a
_Composite Resource_ (XR) API.

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
&&
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
  name: upbound-provider-aws
spec:
  package: xpkg.upbound.io/upbound/provider-aws:v0.27.0
EOF
```

3. Create a file called `aws-credentials.txt` with your AWS keys
{{< editCode >}}
```ini {copy-lines="all"}
[default]
aws_access_key_id = $$<aws_access_key>$$
aws_secret_access_key = $$<aws_secret_key>$$
```
{{</ editCode >}}

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

## Create a composition
[Part 1]({{<ref "provider-aws" >}}) created a single _managed resource_.
A _Composition_ is a template to create multiple _managed resources_ at the same time.

This sample _composition_ creates an DynamoDB instance and associated S3 storage 
bucket. 

{{< hint "note" >}}
This example comes from the AWS recommendation for 
[storing large DynamoDB attributes in S3](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-use-s3-too.html#bp-use-s3-too-large-values). 
{{< /hint >}}

To create a _composition_, first define each individual managed resource.

### Create an S3 bucket object
Define a `bucket` resource using the configuration from the previous section:

{{< hint "note" >}}
Don't apply this configuration. This YAML is part of a larger
definition. 
{{< /hint >}}

```yaml
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  name: crossplane-quickstart-bucket
spec:
  forProvider:
    region: "us-east-2"
  providerConfigRef:
    name: default
```

### Create a DynamoDB table resource
Next, define a DynamoDB `table` resource. 

{{< hint "tip" >}}
The [Upbound Marketplace](https://marketplace.upbound.io/) provides
[schema
documentation](https://marketplace.upbound.io/providers/upbound/provider-aws/v0.27.0/resources/dynamodb.aws.upbound.io/Table/v1beta1)
for a `Table` resource.
{{< /hint >}}

The _AWS Provider_ defines the 
{{<hover line="1" label="dynamoMR">}}apiVersion{{</hover>}} 
and 
{{<hover line="2" label="dynamoMR">}}kind{{</hover>}}.

DynamoDB instances require a
{{<hover line="7" label="dynamoMR">}}region{{</hover>}},
{{<hover line="8" label="dynamoMR">}}writeCapacity{{</hover>}}
and 
{{<hover line="9" label="dynamoMR">}}readCapacity{{</hover>}}
parameters.

The {{<hover line="10" label="dynamoMR">}}attribute{{</hover>}} section creates
the database "Partition key" and "Hash key."

This example creates a single key named 
{{<hover line="11" label="dynamoMR">}}S3ID{{</hover>}} of type
{{<hover line="12" label="dynamoMR">}}S{{</hover>}} for "string" 
```yaml {label="dynamoMR"}
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
```

{{< hint "note" >}}
DynamoDB specifics are beyond the scope of this guide. Read the 
[DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
for more information.
{{</hint >}}

### Create the composition object
The _composition_ combines the two resource definitions.

A 
{{<hover label="compName" line="2">}}Composition{{</ hover>}} comes from the
{{<hover label="compName" line="1">}}Crossplane{{</ hover>}} 
API resources.

Create any {{<hover label="compName" line="4">}}name{{</ hover>}} for this _composition_.

```yaml {label="compName"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: dynamodb-with-bucket
```

Add the resources to the 
{{<hover label="specResources" line="5">}}spec.resources{{</ hover>}} 
section of the _composition_.

Give each resource a 
{{<hover label="specResources" line="7">}}name{{</ hover>}} 
and put the resource definition under the
{{<hover label="specResources" line="8">}}base{{</ hover>}} 
key.

```yaml {label="specResources"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: dynamodb-with-bucket
spec:
  resources:
    - name: s3-bucket
      base:
        apiVersion: s3.aws.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            region: "us-east-2"
          providerConfigRef:
            name: default
    - name: dynamodb
      base:
        apiVersion: dynamodb.aws.upbound.io/v1beta1
        kind: Table
        spec:
          forProvider:
            region: "us-east-2"
            writeCapacity: 1
            readCapacity: 1
            attribute:
              - name: S3ID
                type: S
            hashKey: S3ID
```

Put the entire resource definition including the 
{{<hover label="specResources" line="20">}}apiVersion{{</ hover>}} and resource
settings under the 
{{<hover label="specResources" line="19">}}base{{</ hover>}}.

_Compositions_ are only a template for generating resources. A _composite
resource_ actually creates the resources.

A _composition_ defines what _composite resources_ can use this
template. 

_Compositions_ do this with the 
{{<hover label="compRef" line="6">}}spec.compositeTypeRef{{</ hover>}}
definition.

{{< hint "tip" >}}
Crossplane recommends prefacing the `kind` with an `X` to show it's a Composition.
{{< /hint >}}

```yaml {label="compRef"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: dynamodb-with-bucket
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XDatabase
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
{{<hover label="compRef" line="8">}}kind: XDatabase{{</ hover>}}
to use this template to create resources. 
<!-- vale gitlab.SentenceLength = YES -->

### Apply the composition
Apply the full _Composition_ to your Kubernetes cluster.

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: dynamodb-with-bucket
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XDatabase
  resources:
    - name: s3-bucket
      base:
        apiVersion: s3.aws.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            region: us-east-2
          providerConfigRef:
            name: default
    - name: dynamodb
      base:
        apiVersion: dynamodb.aws.upbound.io/v1beta1
        kind: Table
        spec:
          forProvider:
            region: "us-east-2"
            writeCapacity: 1
            readCapacity: 1
            attribute:
              - name: S3ID
                type: S
            hashKey: S3ID
EOF
```

Confirm the _composition_ exists with `kubectl get composition`

```shell {copy-lines="1"}
kubectl get composition
NAME                   AGE
dynamodb-with-bucket   28s
```

## Define a composite resource

The _composition_ that was just created limited which _composite resources_ can
use that template. 

A _composite resource_ is a custom API defined by the platform teams.  
A _composite resource definition_ defines the schema for a _composite resource_.


A _composite resource definition_ installs the custom API type into Kubernetes
and defines what `spec` keys and values are valid when calling this new custom API.

Before creating a _composite resource_ Crossplane requires a _composite resource definition_.

{{< hint "tip" >}}
_Composite resource definitions_ are also called `XRDs` for short. 
{{< /hint >}}

Just like a _composition_ the 
{{<hover label="xrdName" line="2" >}}composite resource definition{{</hover>}} 
is part of the 
{{<hover label="xrdName" line="1" >}}Crossplane{{</hover>}}
API group.

The _XRD_ {{<hover label="xrdName" line="4" >}}name{{</hover>}} is the new
API endpoint.

{{< hint "tip" >}}
Crossplane recommends using a plural name for the _XRD_ 
{{<hover label="xrdName" line="4" >}}name{{</hover>}}.
{{< /hint >}}

```yaml {label="xrdName"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: databases.custom-api.example.org
```

The _XRD's_
{{<hover label="xrdGroup" line="5" >}}spec{{</hover>}} defines the new custom
API.

### Define the API endpoint and kind
First, define the new API
{{<hover label="xrdGroup" line="6" >}}group{{</hover>}}.  
Next, create the API {{<hover label="xrdGroup" line="8" >}}kind{{</hover>}} and
{{<hover label="xrdGroup" line="9" >}}plural{{</hover>}}.

```yaml {label="xrdGroup"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: databases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: XDatabase
    plural: xdatabases
```

{{<hint "note" >}}
The _XRD_ {{<hover label="xrdGroup" line="6" >}}group{{</hover>}} matches the _composition_ {{<hover label="noteComp"
line="5">}}apiVersion{{</hover>}} and the 
_XRD_ {{<hover label="xrdGroup" line="8" >}}kind{{</hover>}} matches the _composition_ 
{{<hover label="noteComp" line="6">}}compositeTypeRef.kind{{</hover>}}.

```yaml {label="noteComp"}
kind: Composition
# Removed for brevity
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XDatabase
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

```yaml {label="xrdVersion"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: custom-api-definition
spec:
  group: custom-api.example.org
  names:
    kind: XDatabase
    plural: databases
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
[_custom resource definition_ rules for schemas](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#specifying-a-structural-schema). 
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

```yaml {label="xrdSchema"}
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
For more information on the values allowed in a _composite resource definition_ view its schema with
`kubectl explain compositeresourcedefinition`
{{< /hint >}}

Now, define the custom API. Your custom API continues under the last
{{<hover label="xrdSchema" line="14">}}properties{{</hover>}} definition in the
previous example.

This custom API has only one setting:
<!-- vale Google.We = NO -->
* {{<hover label="customAPI" line="4" >}}region{{</hover >}} - where to deploy
the resources, a choice of "EU" or "US"


Users can't change any other settings of the S3 bucket or DynamoDB instance. 

The{{<hover label="customAPI" line="4" >}}region{{</hover >}}
is a {{<hover label="customAPI" line="5" >}}string{{</hover >}}
and can match the regular expression that's
{{<hover label="customAPI" line="6" >}}oneOf{{</hover >}}
{{<hover label="customAPI" line="7" >}}EU{{</hover >}}
or
{{<hover label="customAPI" line="8" >}}US{{</hover >}}.

This API requires the setting 
{{<hover label="customAPI" line="10" >}}region{{</hover >}}.


```yaml {label="customAPI"}
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


```yaml {label="XRDclaim"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
# Removed for brevity
  names:
    kind: XDatabase
    plural: xdatabases
  claimNames:
    kind: Database
    plural: databases
```

{{<hint "note" >}}
The [Claims](#create-a-claim) section later in this guide discusses _claims_.
{{< /hint >}}

### Apply the composite resource definition
Apply the complete _XRD_ to your Kubernetes cluster.


```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xdatabases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: XDatabase
    plural: xdatabases
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
    kind: Database
    plural: databases
EOF
```

Verify Kubernetes created the XRD with `kubectl get xrd`

```shell {copy-lines="1",label="getXRD"}
kubectl get xrd
NAME                                ESTABLISHED   OFFERED   AGE
xdatabases.custom-api.example.org   True          True      10s
```

## Create a composite resource
Creating an _XRD_ allows the creation _composite resources_.

_Composite resources_ are a convenient way to create multiple resources with a standard template. 

A _composite resource_ uses the custom API created in the _XRD_.

Looking at part of the _XRD_:

```yaml {label="xrdSnip"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
  group: custom-api.example.org
  names:
    kind: XDatabase
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
kind: XDatabase
metadata:
  name: my-composite-resource
spec: 
  region: "US"
EOF
```

### Verify the composite resource
Verify Crossplane created the _composite resource_ with `kubectl get xdatabase`

```shell {copy-lines="1"}
kubectl get xdatabase
NAME                    SYNCED   READY   COMPOSITION          AGE
my-composite-resource   True     True    dynamo-with-bucket   31s
```

Both `SYNCED` and `READY` are `True` when Crossplane created the AWS resources.

Now look at the S3 `bucket` and DynmoDB `table` _managed resources_ with
`kubectl get bucket` and `kubectl get table`.

```shell {copy-lines="1"}
kubectl get bucket
NAME                          READY   SYNCED   EXTERNAL-NAME                 AGE
my-composite-resource-8b6tx   True    True     my-composite-resource-8b6tx   56s
```

```shell {copy-lines="1"}
kubectl get table
NAME                          READY   SYNCED   EXTERNAL-NAME                 AGE
my-composite-resource-m6vk6   True    True     my-composite-resource-m6vk6   59s
```

The _composite resource_ automatically generated both _managed resources_.

Using `kubectl describe` on a _managed resource_ shows the `Owner References` is
the _composite resource_.

```yaml {copy-lines="1"}
kubectl describe bucket | grep "Owner References" -A5
  Owner References:
    API Version:           custom-api.example.org/v1alpha1
    Block Owner Deletion:  true
    Controller:            true
    Kind:                  XDatabase
    Name:                  my-composite-resource
```

Each _composite resource_ creates and owns a unique set of _managed resources_.
If you create a second _composite resource_ Crossplane creates a new S3 `bucket`
and DynamoDB `table`.

```yaml {label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: XDatabase
metadata:
  name: my-second-composite-resource
spec: 
  region: "US"
EOF
```

Again, use `kubectl get xdatabase` to view both _composite resources_.

```shell {copy-lines="1"}
kubectl get xdatabase
NAME                           SYNCED   READY   COMPOSITION          AGE
my-composite-resource          True     True    dynamo-with-bucket   2m21s
my-second-composite-resource   True     True    dynamo-with-bucket   42s
```

And see there are two `bucket` and two `table` _managed resources_.

```shell {copy-lines="1"}
kubectl get bucket
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
my-composite-resource-8b6tx          True    True     my-composite-resource-8b6tx          2m57s
my-second-composite-resource-z22lc   True    True     my-second-composite-resource-z22lc   78s
```

```shell {copy-lines="1"}
kubectl get table
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
my-composite-resource-m6vk6          True    True     my-composite-resource-m6vk6          3m
my-second-composite-resource-nsz6j   True    True     my-second-composite-resource-nsz6j   81s
```

### Delete the composite resources
Because the _composite resource_ is the `Owner` of the _managed resources_, when
Crossplane deletes the _composite resource_, it also deletes the _managed resources_ automatically.

Delete the new _composite resource_ with `kubectl delete xdatabase`.

```shell
kubectl delete xdatabase my-second-composite-resource
```

{{<hint "note">}}
There may a delay in deleting the _managed resources_. Crossplane is making API
calls to AWS and waits for AWS to confirm they deleted the resources before
updating the state in Kubernetes.
{{</hint >}}

Now only one bucket and table exist.

```shell {copy-lines="1"}
kubectl get bucket
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
my-composite-resource-8b6tx   True    True     my-composite-resource-8b6tx   7m34s
```

```shell {copy-lines="1"}
kubectl get table
NAME                                 READY   SYNCED   EXTERNAL-NAME                        AGE
my-composite-resource-m6vk6   True    True     my-composite-resource-m6vk6   7m37s
```

Delete the second _composite resource_ to remove the last `bucket` and `table`
_managed resources_.

```shell
kubectl delete xdatabase my-composite-resource
```

_Composite resources_ are great for creating multiple related resources against
a template, but all _composite resources_ exist at the Kubernetes "cluster
level." There's no isolation between _composite resources_. Crossplane uses
_claims_ to create resources with namespace isolation. 

## Create a claim

_Claims_, just like _composite resources_ use the custom API defined in the
_XRD_. Unlike a _composite resource_, Crossplane can create _claims_ in a
namespace.

### Create a new Kubernetes namespace
Create a new namespace with `kubectl create namespace`.

```shell
kubectl create namespace test
```

A _claim_ uses the same {{<hover label="XRDclaim2" line="6" >}}group{{</hover>}}
a _composite resource_ uses but a different 
{{<hover label="XRDclaim2" line="8" >}}kind{{</hover>}}.

```yaml {label="XRDclaim2"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
# Removed for brevity
  group: custom-api.example.org
  claimNames:
    kind: Database
    plural: databases
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
kind: Database
metadata:
  name: claimed-database
  namespace: test
spec:
  region: "US"
EOF
```

### Verify the claim
Verify Crossplane created the _claim_ with `kubectl get database` in the `test`
namespace.

```shell {copy-lines="1"}
kubectl get database -n test
NAME               SYNCED   READY   CONNECTION-SECRET   AGE
claimed-database   True     True                        35s
```

When Crossplane creates a _claim_, a unique _composite resource_ is also
created. View the new _composite resource_ with `kubectl get xdatabase`.

```shell {copy-lines="1"}
kubectl get xdatabase
NAME                     SYNCED   READY   COMPOSITION          AGE
claimed-database-6xsgq   True     True    dynamo-with-bucket   46s
```

The _composite resource_ exists at the "cluster scope" while the _claim_ exists
at the "namespace scope."

Create a second namespace and a second claim.

```shell
kubectl create namespace test2
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: Database
metadata:
  name: claimed-database
  namespace: test2
spec:
  region: "US"
EOF
```

View the _claims_ in all namespaces with `kubectl get database -A`

```shell {copy-lines="1"}
kubectl get database -A
NAMESPACE   NAME               SYNCED   READY   CONNECTION-SECRET   AGE
test        claimed-database   True     True                        4m32s
test2       claimed-database   True     True                        43s
```

Now look at the _composite resources_ at the cluster scope.

```shell {copy-lines="1"}
kubectl get xdatabase
NAME                     SYNCED   READY   COMPOSITION          AGE
claimed-database-6xsgq   True     True    dynamo-with-bucket   8m37s
claimed-database-f54qv   True     True    dynamo-with-bucket   4m47s
```

Crossplane created a second _composite resource_ for the second _claim_.

Looking at the S3 `bucket` and DynamoDB `table` shows two of each resource, one
for each claim.

```shell {copy-lines="1"}
kubectl get bucket
NAME                           READY   SYNCED   EXTERNAL-NAME                  AGE
claimed-database-6xsgq-l9d8z   True    True     claimed-database-6xsgq-l9d8z   9m18s
claimed-database-f54qv-9542v   True    True     claimed-database-f54qv-9542v   5m28s
```

```shell {copy-lines="1"}
kubectl get table
NAME                           READY   SYNCED   EXTERNAL-NAME                  AGE
claimed-database-6xsgq-nmxhs   True    True     claimed-database-6xsgq-nmxhs   11m
claimed-database-f54qv-qrsdj   True    True     claimed-database-f54qv-qrsdj   7m24s
```

### Delete the claims
Removing the _claims_ removes the _composite resources_ and the associated
_managed resources_.

```shell
kubectl delete database claimed-database -n test
kubectl delete database claimed-database -n test2
```

Verify Crossplane removed all the _managed resources_.

```shell
kubectl get bucket
No resources found
```

```shell
kubectl get table
No resources found
```

Claims are powerful tools to give users resources in their own isolated
namespace. But these examples haven't shown how the custom API can change
the settings defined in the _composition_. This _composition patching_ applies
the API settings when creating resources. 
[Part 3]({{< ref "provider-aws-part-3">}}) of this guide covers _composition
patches_ and making all this configuration portable in Crossplane _packages_. 

## Next steps
* **[Continue to part 3]({{< ref "provider-aws-part-3">}})** to create a learn
  about _patching_ resources and creating Crossplane _packages_.
* Explore AWS resources that Crossplane can configure in the [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-aws/latest/crds).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with Crossplane users and contributors.