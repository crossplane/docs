---
title: AWS Quickstart Part 3
weight: 120
tocHidden: true
---

{{< hint "important" >}}
This guide is part 3 of a series. 

Follow **[part 1]({{<ref "provider-aws" >}})** 
to install Crossplane and connect your Kubernetes cluster to AWS. 

Follow **[part 2]({{<ref "provider-aws-part-2" >}})** to create a _composition_,
_custom resource definition_ and a _claim_.
{{< /hint >}}

[Part 2]({{<ref "provider-aws-part-2" >}}) created a _composite resource
definition_ to define the schema of the custom API. Users create a _claim_ to
use the custom API and apply their options. Part 2 didn't show how the options
set in a _claim_ change or get applied the associated _composite resources_.

## Prerequisites
* Complete quickstart [part 1]({{<ref "provider-aws" >}}) and [Part 2]({{<ref
  "provider-aws-part-2" >}}) to install Crossplane and the quickstart
  configurations.
  
{{<expand "Skip parts 1 and 2 and just get started" >}}
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
  name: upbound-provider-aws
spec:
  package: xpkg.upbound.io/upbound/provider-aws:v0.27.0
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

6. Create a _composition_
```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: dynamo-with-bucket
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: database
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
EOF
```

7. Create a _composite resource definition_
```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: databases.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: database
    plural: databases
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
    kind: custom-database
    plural: custom-databases
EOF
```

8. Create a new namespace
```shell
kubectl create namespace test
```

{{</expand >}}

## Enable patches
In a _composition_ `patches` map fields in the custom API to fields inside the
_managed resources_.

The _composition_ has two _managed resources_, a 
{{<hover label="compResources" line="8">}}bucket{{</hover>}} and a
{{<hover label="compResources" line="19">}}table{{</hover>}}.

```yaml {label="compResources"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
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
```
<!-- vale Google.We = NO -->
The custom API defined a single option, 
{{<hover label="xrdSnip" line="12">}}region{{</hover>}}. A 
{{<hover label="xrdSnip" line="12">}}region{{</hover>}} can be either 
{{<hover label="xrdSnip" line="15">}}EU{{</hover>}} or
{{<hover label="xrdSnip" line="16">}}US{{</hover>}}. 
<!-- vale Google.We = YES -->

```yaml {label="xrdSnip"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
# Removed for brevity
spec:
  group: custom-api.example.org
  names:
    kind: database
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
inside the _composition_. 

A {{<hover label="patch" line="12">}}patch{{</hover>}} has a
{{<hover label="patch" line="13">}}fromField{{</hover>}} and a
{{<hover label="patch" line="14">}}toField{{</hover>}} specifying which value
_from_ the custom API should apply _to_ the _managed resource_.  
Patches can create a 
{{<hover label="patch" line="15">}}transform{{</hover>}} to change the _from_
field before it's applied.  

The transform
{{<hover label="patch" line="16">}}type{{</hover>}} is what kind of change to
make on the _from_ field. Types of changes could include appending a string,
preforming a math operation or mapping one value to another. 

Applying a {{<hover label="patch" line="12">}}patch{{</hover>}} to the 
{{<hover label="patch" line="8">}}Bucket{{</hover>}} uses the custom API 
{{<hover label="patch" line="13">}}region{{</hover>}} to use as the _managed resource_
{{<hover label="patch" line="11">}}region{{</hover>}}. 

<!-- vale Google.We = NO -->
The custom API value "EU" is 
{{<hover label="patch" line="18">}}mapped{{</hover>}} to the value "eu-north-1"
and "US" is {{<hover label="patch" line="19">}}mapped{{</hover>}} to the value
"us-east-2."
<!-- vale Google.We = YES -->


```yaml {label="patch"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
resources:
    - name: s3Bucket
      base:
        apiVersion: s3.aws.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            region: us-east-2
      patches:
        - fromFieldPath: "region"
          toFieldPath: "spec.forProvider.region"
          transforms:
             - type: map
               map: 
                EU: "eu-north-1"
                US: "us-east-2"
```
<!-- vale Google.We = NO -->
Patching is a powerful tool enabling simpler or abstracted APIs. A developer
doesn't need to know the specific AWS region identifier, only the abstracted
option of "EU" or "US."
<!-- vale Google.We = YES -->

### Apply the updated composition
Apply the same `patch` to the `Table` _managed resource_ and apply the updated
_composition_.

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: dynamo-with-bucket
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: database
  resources:
    - name: s3Bucket
      base:
        apiVersion: s3.aws.upbound.io/v1beta1
        kind: Bucket
        metadata:
          name: crossplane-quickstart-bucket
        spec:
          providerConfigRef:
            name: default
        patches:
        - fromFieldPath: "spec.region"
          toFieldPath: "spec.forProvider.region"
          transforms:
             - type: map
               map: 
                EU: "eu-north-1"
                US: "us-east-1"
    - name: dynamoDB
      base:
        apiVersion: dynamodb.aws.upbound.io/v1beta1
        kind: Table
        metadata:
          name: crossplane-quickstart-database
        spec:
          forProvider:
            writeCapacity: 1
            readCapacity: 1
            attribute:
              - name: S3ID
                type: S
            hashKey: S3ID
      patches:
        - fromFieldPath: "spec.region"
          toFieldPath: "spec.forProvider.region"
          transforms:
            - type: map
              map: 
                EU: "eu-north-1"
                US: "us-east-1"
EOF
```

### Create a claim
Create a new _claim_ and set the 
{{<hover label="claim" line="8" >}}region{{</hover >}} to "EU."

```yaml {label="claim"}
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: custom-database
metadata:
  name: claimed-eu-database
  namespace: test
spec:
  region: "EU"
EOF
```

