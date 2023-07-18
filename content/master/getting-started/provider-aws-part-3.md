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
            region: "us-east-2"
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

## Enable composition patches
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
            region: "us-east-2"
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
            region: "us-east-2"
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
isn't required to know the specific AWS region identifier, only the abstracted
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
          forProvider:
            name: default
            region: "us-east-2"
      patches:
        - fromFieldPath: "spec.region"
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
            writeCapacity: 1
            readCapacity: 1
            attribute:
              - name: S3ID
                type: S
            hashKey: S3ID
            region: "us-east-2"
      patches:
        - fromFieldPath: "spec.region"
          toFieldPath: "spec.forProvider.region"
          transforms:
            - type: map
              map: 
                EU: "eu-north-1"
                US: "us-east-2"
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

View the _claim_ with `kubectl get claim`

```shell
kubectl get claim -n test
NAME                  SYNCED   READY   CONNECTION-SECRET   AGE
claimed-eu-database   True     True                        18m
```

The claim reports `SYNCED` and `READY` as `True` after Crossplane creates
all the _managed resources_.

Describe the `Table` resource to see the AWS region is `eu-north-1`.

```shell
kubectl describe table | grep arn:aws
    Arn:           arn:aws:dynamodb:eu-north-1:622343227358:table/claimed-eu-database-2sh9w-dhvw6
```

<!-- vale Google.We = NO -->
Using {{<hover label="claim" line="8" >}}region: "EU"{{</hover >}} patches the
_composite resource_, updating the AWS region from `us-east-2` to `eu-north-1`.
The developer creating the claim isn't required to know which specific AWS 
region or the naming conventions. Using the abstract API options of "EU" or "US" 
the developer places their resources in the desired location.
<!-- vale Google.We = YES -->

Deleting the claim removes the _managed resources_.

{{<hint "note" >}}
The _managed resources_ take up to 5 minutes to delete.
{{< /hint >}}

```shell
kubectl delete claim claimed-eu-database -n test
```

## Create a Crossplane configuration package

Crossplane _configuration packages_ allow users to combine their _custom
resource definition_ and _composition_ files into an OCI image. 

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
[Upbound's Up CLI)](https://github.com/upbound/up).
{{< /hint >}}

A configuration package includes three files:
* `crossplane.yaml` defines the metadata of the package.
* `definition.yaml` is the _composite resource definition_ for the package.
* `composition.yaml` is the _composition_ template for the package. 

<!-- vale gitlab.Substitutions = NO -->
<!-- yaml is in the filename -->
### Create a crossplane.yaml file
<!-- vale gitlab.Substitutions = YES -->
Configuration packages describe their contents and requirements with a 
`crossplane.yaml` file.

The `crossplane.yaml` file lists the required Crossplane _providers_ and their
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
{{<hover label="xpyaml" line="9" >}}provider-aws{{</hover>}}
version {{<hover label="xpyaml" line="10" >}}0.27.0{{</hover>}} or later as a
dependency.

{{<hint "tip" >}}
Crossplane automatically installs dependencies. Dependencies can include other
configuration packages.
{{< /hint >}}

```yaml {label="xpyaml"}
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: crossplane-aws-quickstart
spec:
  crossplane:
    version: ">=v1.11.0"
  dependsOn:
    - provider: xpkg.upbound.io/upbound/provider-aws
      version: ">=v0.27.0"
```

Create a new directory and save the `crossplane.yaml` file.

```yaml
mkdir crossplane-aws-quickstart
cat <<EOF > crossplane-aws-quickstart/crossplane.yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: crossplane-aws-quickstart
spec:
  crossplane:
    version: ">=v1.11.0"
  dependsOn:
    - provider: xpkg.upbound.io/upbound/provider-aws
      version: ">=v0.27.0"
EOF
```

<!-- vale gitlab.Substitutions = NO -->
<!-- yaml is in the filename -->
### Create a definition.yaml file
<!-- vale gitlab.Substitutions = YES -->

A configuration package requires a _composite resource definition_ (XRD) to define the
custom API.

Save the _XRD_ as `definition.yaml` in the same directory as the
`crossplane.yaml` file.

```yaml
cat <<EOF > crossplane-aws-quickstart/definition.yaml
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

<!-- vale gitlab.Substitutions = NO -->
<!-- yaml is in the filename -->
### Create a composition.yaml file
<!-- vale gitlab.Substitutions = YES -->

The _composition_ template creates the _managed resources_ and allows _patches_
to customize the _managed resources_.

Copy the _composition_ into the `composition.yaml` file in the same directory as
`crossplane.yaml`.

```yaml
cat <<EOF > crossplane-aws-quickstart/composition.yaml
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

### Install the Crossplane command-line
To build a configuration package install the Crossplane Kubernetes command-line
extension. 

```shell
curl "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh"
./install.sh
sudo mv kubectl-crossplane /usr/bin
```

Verify the Crossplane command-line installed with `kubectl crossplane --help`

```shell
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
kubectl crossplane build configuration -f crossplane-aws-quickstart/ --name="crossplane-aws-quickstart"
```

Now an `.xpkg` OCI image is inside the `crossplane-aws-quickstart` directory.

```shell
ls crossplane-aws-quickstart/
composition.yaml  crossplane-aws-quickstart.xpkg  crossplane.yaml  definition.yaml
```

## Next steps
* Explore AWS resources that Crossplane can configure in the [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-family-aws/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with Crossplane users and contributors.
* Read more about [Crossplane concepts]({{<ref "../concepts" >}})