---
title: GCP Quickstart Part 3
weight: 120
tocHidden: true
---

{{< hint "important" >}}
This guide is part 3 of a series. 

Follow **[part 1]({{<ref "provider-gcp" >}})** 
to install Crossplane and connect your Kubernetes cluster to GCP. 

Follow **[part 2]({{<ref "provider-gcp-part-2" >}})** to create a _composition_,
_custom resource definition_ and a _claim_.
{{< /hint >}}

[Part 2]({{<ref "provider-gcp-part-2" >}}) created a _composite resource
definition_ to define the schema of the custom API. Users create a _claim_ to
use the custom API and apply their options. Part 2 didn't show how the options
set in a _claim_ change or get applied the associated _composite resources_.

## Prerequisites
* Complete quickstart [part 1]({{<ref "provider-gcp" >}}) and [Part 2]({{<ref
  "provider-gcp-part-2" >}}) to install Crossplane and the quickstart
  configurations.
  
{{<expand "Skip parts 1 and 2 and just get started" >}}

1. Add the Crossplane Helm repository and install Crossplane.
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

2. When the Crossplane pods finish installing and are ready, apply the GCP Provider.
   
```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: upbound-provider-gcp
spec:
  package: xpkg.upbound.io/upbound/provider-gcp:v0.28.0
EOF
```

3. Create a file called `gcp-credentials.json` with your GCP service account 
JSON file.

{{< hint type="tip" >}}
The 
[GCP documentation](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) 
provides information on how to generate a service account JSON file.
{{< /hint >}}

4. Create a Kubernetes secret from the GCP JSON file
```shell {label="kube-create-secret",copy-lines="all"}
kubectl create secret \
generic gcp-secret \
-n crossplane-system \
--from-file=creds=./gcp-credentials.json
```

5. Create a _ProviderConfig_
Include your 
{{< hover label="providerconfig" line="7" >}}GCP project ID{{< /hover >}} in the
_ProviderConfig_ settings.

{{< hint type="warning" >}}
Find your GCP project ID from the `project_id` field of the 
`gcp-credentials.json` file.
{{< /hint >}}

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


6. Create a _composition_
```yaml {copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: topic-with-bucket
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XTopicBucket
  resources:
    - name: crossplane-quickstart-bucket
      base:
        apiVersion: storage.gcp.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            location: US
    - name: crossplane-quickstart-topic
      base:
        apiVersion: pubsub.gcp.upbound.io/v1beta1
        kind: Topic
        spec:
          forProvider:
            messageStoragePolicy:
              - allowedPersistenceRegions: 
                - "us-central1"
EOF
```

7. Create a _composite resource definition_
```yaml {copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xtopicbuckets.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: XTopicBucket
    plural: xtopicbuckets
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
              location:
                type: string
                oneOf:
                  - pattern: '^EU$'
                  - pattern: '^US$'
            required:
              - location
  claimNames:
    kind: TopicBucket
    plural: topicbuckets
EOF
```

8. Create a new namespace
```shell
kubectl create namespace test
```

{{</expand >}}

## Enable composition patches
In a _composition_, `patches` map fields in the custom API to fields inside the
_managed resources_.

The example _composition_ has two _managed resources_, a 
{{<hover label="compResources" line="8">}}bucket{{</hover>}} and a
{{<hover label="compResources" line="15">}}topic{{</hover>}}.

```yaml {label="compResources"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
resources:
    - name: crossplane-quickstart-bucket
      base:
        apiVersion: storage.gcp.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            location: US
    - name: crossplane-quickstart-topic
      base:
        apiVersion: pubsub.gcp.upbound.io/v1beta1
        kind: Topic
        spec:
          forProvider:
            messageStoragePolicy:
              - allowedPersistenceRegions: 
                - "us-central1"
```
<!-- vale Google.We = NO -->
The custom API defined a single option, 
{{<hover label="xrdSnip" line="12">}}location{{</hover>}}. A 
{{<hover label="xrdSnip" line="12">}}location{{</hover>}} can be either 
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
    kind: XDatabase
# Removed for brevity
      spec:
        type: object
        properties:
          location:
            type: string
            oneOf:
              - pattern: '^EU$'
              - pattern: '^US$'
```

Creating a _composition_ `patch` allows Crossplane to update the settings of a
_composite resource_. Patches apply to an individual _managed resource_
inside the _composition_. 

A {{<hover label="patch" line="14">}}patch{{</hover>}} has a
{{<hover label="patch" line="15">}}fromField{{</hover>}} and a
{{<hover label="patch" line="16">}}toField{{</hover>}} specifying which value
_from_ the custom API should apply _to_ a field in the _managed resource_.  
Patches can create a 
{{<hover label="patch" line="17">}}transform{{</hover>}} to change the _from_
field before it's applied.  

The transform
{{<hover label="patch" line="18">}}type{{</hover>}} is what kind of change to
make on the _from_ field. Types of changes could include appending a string,
preforming a math operation or mapping one value to another. 

Applying a {{<hover label="patch" line="14">}}patch{{</hover>}} to the 
{{<hover label="patch" line="8">}}Topic{{</hover>}} uses the custom API 
{{<hover label="patch" line="15">}}spec.location{{</hover>}} field to use as the 
_managed resource_
{{<hover label="patch" line="12">}}allowedPersistenceRegions{{</hover>}} value.

<!-- vale Google.We = NO -->
The custom API value "EU" is 
{{<hover label="patch" line="20">}}mapped{{</hover>}} to the value 
"europe-central2" and "US" is 
{{<hover label="patch" line="21">}}mapped{{</hover>}} to the value
"us-central1."
<!-- vale Google.We = YES -->


```yaml {label="patch"}
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
# Removed for Brevity
resources:
    - name: crossplane-quickstart-topic
      base:
        apiVersion: pubsub.gcp.upbound.io/v1beta1
        kind: Topic
        spec:
          forProvider:
            messageStoragePolicy:
              - allowedPersistenceRegions: 
                - "us-central1"
      patches:
        - fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.messageStoragePolicy[*].allowedPersistenceRegions[*]"
          transforms:
            - type: map
              map: 
                EU: "europe-central2"
                US: "us-central1"
```
<!-- vale Google.We = NO -->
Patching is a powerful tool enabling simpler or abstracted APIs. Developers
aren't required to know the specific GCP region, just the abstracted
option of "EU" or "US."
<!-- vale Google.We = YES -->

### Apply the updated composition
Apply a similar `patch` to the `Bucket` _managed resource_ and apply the updated
_composition_.

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: topic-with-bucket
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XTopicBucket
  resources:
    - name: crossplane-quickstart-bucket
      base:
        apiVersion: storage.gcp.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            location: "US"
      patches:
        - fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "EU"
                US: "US"
    - name: crossplane-quickstart-topic
      base:
        apiVersion: pubsub.gcp.upbound.io/v1beta1
        kind: Topic
        spec:
          forProvider:
            messageStoragePolicy:
              - allowedPersistenceRegions: 
                - "us-central1"
      patches:
        - fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.messageStoragePolicy[*].allowedPersistenceRegions[*]"
          transforms:
            - type: map
              map: 
                EU: "europe-central2"
                US: "us-central1"
EOF
```

### Create a claim
Create a new _claim_ and set the 
{{<hover label="claim" line="8" >}}location{{</hover >}} to "EU."

```yaml {label="claim"}
cat <<EOF | kubectl apply -f -
apiVersion: custom-api.example.org/v1alpha1
kind: TopicBucket
metadata:
  name: claimed-eu-topic-with-bucket
  namespace: test
spec:
  location: "EU"
EOF
```

View the _claim_ with `kubectl get claim`

```shell {copy-lines="1"}
kubectl get TopicBucket -n test
NAME                           SYNCED   READY   CONNECTION-SECRET   AGE
claimed-eu-topic-with-bucket   True     True                        2m26s
```

The claim reports `SYNCED` and `READY` as `True` after Crossplane creates
all the _managed resources_.

Describe the `Topic` resource to see the GCP location is 
{{< hover label="topicLocation" line="5">}}europe-central2{{< /hover >}}.

```shell {copy-lines="1",label="topicLocation"}
kubectl describe topic | grep "For Provider" -A3
  For Provider:
    Message Storage Policy:
      Allowed Persistence Regions:
        europe-central2
```

Describe the `Bucket` resource to see the GCP location is also set to 
{{<hover label="bucketLocation" line="3">}}EU{{</hover>}}.

```shell {copy-lines="1",label="bucketLocation"}
kubectl describe bucket | grep "For Provider" -A1
  For Provider:
    Location:                  EU
```

<!-- vale Google.We = NO -->
Using {{<hover label="claim" line="8" >}}location: "EU"{{</hover >}} in the
claim patches the _composite resource_, updating the `Topic` GCP region from 
`us-central1` to `europe-central-2` and the `Bucket` from GCP region `US` to GCP
region `EU`.  
The developer creating the claim isn't required to know which specific GCP 
region or the naming conventions. Using the abstract API options of "EU" or "US" 
the developer places their resources in the desired location.

In this example, patching also allows platform teams to ensure all resources are 
in the same location.
<!-- vale Google.We = YES -->

Deleting the claim removes the _managed resources_.

{{<hint "note" >}}
The _managed resources_ take up to 5 minutes to delete.
{{< /hint >}}

```shell
kubectl delete TopicBucket claimed-eu-topic-with-bucket -n test
```

## Create a Crossplane configuration package

Creating a configuration package makes your Crossplane custom APIs portable
and versioned. 

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

Building and installing configuration packages requires an OCI image compatible
tool. 

{{< hint "note" >}}
You can use any software that builds OCI images. This includes
[Docker](https://www.docker.com/) or 
[Upbound's Up command-line tool](https://github.com/upbound/up)
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
{{<hover label="xpyaml" line="9" >}}provider-gcp{{</hover>}}
version {{<hover label="xpyaml" line="10" >}}0.28.0{{</hover>}} or later as a
dependency.

{{<hint "tip" >}}
Crossplane automatically installs dependencies. Dependencies can include other
configuration packages.
{{< /hint >}}

```yaml {label="xpyaml"}
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: crossplane-gcp-quickstart
spec:
  crossplane:
    version: ">=v1.11.0"
  dependsOn:
    - provider: xpkg.upbound.io/upbound/provider-gcp
      version: ">=v0.28.0"
```

Create a new directory and save the `crossplane.yaml` file.

```yaml {copy-lines="all"}
mkdir crossplane-gcp-quickstart
cat <<EOF > crossplane-gcp-quickstart/crossplane.yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: crossplane-gcp-quickstart
spec:
  crossplane:
    version: ">=v1.11.0"
  dependsOn:
    - provider: xpkg.upbound.io/upbound/provider-gcp
      version: ">=v0.28.0"
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

```yaml {copy-lines="all"}
cat <<EOF > crossplane-gcp-quickstart/definition.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xtopicbuckets.custom-api.example.org
spec:
  group: custom-api.example.org
  names:
    kind: XTopicBucket
    plural: xtopicbuckets
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
              location:
                type: string
                oneOf:
                  - pattern: '^EU$'
                  - pattern: '^US$'
            required:
              - location
  claimNames:
    kind: TopicBucket
    plural: topicbuckets
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
cat <<EOF > crossplane-gcp-quickstart/composition.yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: topic-with-bucket
spec:
  compositeTypeRef:
    apiVersion: custom-api.example.org/v1alpha1
    kind: XTopicBucket
  resources:
    - name: crossplane-quickstart-bucket
      base:
        apiVersion: storage.gcp.upbound.io/v1beta1
        kind: Bucket
        spec:
          forProvider:
            location: "US"
      patches:
        - fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.location"
          transforms:
            - type: map
              map: 
                EU: "EU"
                US: "US"
    - name: crossplane-quickstart-topic
      base:
        apiVersion: pubsub.gcp.upbound.io/v1beta1
        kind: Topic
        spec:
          forProvider:
            messageStoragePolicy:
              - allowedPersistenceRegions: 
                - "us-central1"
      patches:
        - fromFieldPath: "spec.location"
          toFieldPath: "spec.forProvider.messageStoragePolicy[*].allowedPersistenceRegions[*]"
          transforms:
            - type: map
              map: 
                EU: "europe-central2"
                US: "us-central1"
EOF
```

### Install the Crossplane command-line
To build a configuration package install the Crossplane Kubernetes command-line
extension. 

```shell
wget "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh"
chmod +x install.sh
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
kubectl crossplane build configuration -f crossplane-gcp-quickstart/ --name="crossplane-gcp-quickstart"
```

Now an `.xpkg` OCI image is inside the `crossplane-gcp-quickstart` directory.

```shell
ls crossplane-gcp-quickstart/
composition.yaml  crossplane-gcp-quickstart.xpkg  crossplane.yaml  definition.yaml
```

## Next steps
* Explore GCP resources that Crossplane can configure in the [Provider CRD reference](https://marketplace.upbound.io/providers/upbound/provider-family-gcp/).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with Crossplane users and contributors.
* Read more about [Crossplane concepts]({{<ref "../concepts" >}})