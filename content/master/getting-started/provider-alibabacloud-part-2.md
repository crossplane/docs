---
title: Alibaba Cloud Quickstart Part 2
weight: 120
tocHidden: true
aliases:
  - /master/getting-started/provider-alibabacloud-part-2
---

{{< hint "important" >}}
This guide is part 2 of a series.

[**Part 1**]({{<ref "provider-alibabacloud" >}}) covers
installing Crossplane and connecting your Kubernetes cluster to Alibaba Cloud.

{{< /hint >}}

This guide walks you through building and accessing a custom API with Crossplane.

## Prerequisites

* Complete [quickstart part 1]({{<ref "provider-alibabacloud" >}}) connecting Kubernetes
  to Alibaba Cloud.
* an Alibaba Cloud account with permissions to create an ECS instance, VPC, VSwitch and SecurityGroup.

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

2. When the Crossplane pods finish installing and are ready, apply the Alibaba Cloud Provider

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

3. Create a file with your Alibaba Cloud access keys

```yaml
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

4. Create a Kubernetes secret from the Alibaba Cloud keys

```shell
kubectl apply -f alibabacloud-credential.yaml
```

5. Create a ProviderConfig

```
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
{{</expand >}}

## Create a custom API

Crossplane allows you to build your own custom APIs for your users, abstracting
away details about the cloud provider and their resources. You can make your API
as complex or simple as you wish.

The custom API is a Kubernetes object.
Here is an example custom API.

```yaml {label="exAPI"}
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
metadata:
  name: my-vm
spec:
  location: "CN"
```

Like any Kubernetes object the API has a
{{}}version{{}},
{{}}kind{{}} and
{{}}spec{{}}.

## Define a group and version

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
{{<hover label="version" line="1">}}compute.example.com{{</hover>}}.

Because this is the first version of the API, this guide uses the version
{{<hover label="version" line="1">}}v1alpha1{{</hover>}}.

```yaml {label="version",copy-lines="none"}
apiVersion: compute.example.com/v1alpha1
```

## Define a kind

The API group is a logical collection of related APIs. In a group are
individual kinds representing different resources.

For example a `database` group may have a `Relational` and `NoSQL` kinds.

The `kind` can be anything, but it must be
[UpperCamelCased](https://kubernetes.io/docs/contribute/style/style-guide/#use-upper-camel-case-for-api-objects).

This API's kind is
{{<hover label="kind" line="2">}}NoSQL{{</hover>}}

```yaml {label="kind",copy-lines="none"}
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
```

## Define a spec

The most important part of an API is the schema. The schema defines the inputs
accepted from users.

This API allows users to provide a
{{<hover label="spec" line="4">}}location{{</hover>}} of where to run their
cloud resources.

All other resource settings can't be configurable by the users. This allows
Crossplane to enforce any policies and standards without worrying about
user errors.

```yaml {label="spec",copy-lines="none"}
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
spec:
  location: "CN"
```

## Apply the API

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
{{<hover label="xrd" line="23">}}CN{{</hover>}} or
{{<hover label="xrd" line="24">}}US{{</hover>}}.

Apply this XRD to create the custom API in your Kubernetes cluster.

```yaml {label="xrd",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: virtualmachines.compute.example.com
spec:
  group: compute.example.com
  names:
    kind: VirtualMachine
    plural: virtualmachines
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
                    - pattern: '^CN$'
                    - pattern: '^US$'
                availabilityZone:
                  type: string
                  oneOf:
                    - pattern: '^CN$'
                    - pattern: '^US$'
              required:
                - location
                - availabilityZone
      served: true
      referenceable: true
  claimNames:
    kind: VirtualMachineClaim
    plural: virtualmachineclaims
EOF
```
Adding the {{<hover label="xrd" line="29">}}claimNames{{</hover>}} allows users
to access this API either at the cluster level with the
{{<hover label="xrd" line="9">}}VirtualMachine{{</hover>}} endpoint or in a namespace
with the
{{<hover label="xrd" line="30">}}VirtualMachineClaim{{</hover>}} endpoint.

The namespace scoped API is a Crossplane _Claim_.

{{<hint "tip" >}}
For more details on the fields and options of Composite Resource Definitions
read the
[XRD documentation]({{<ref "../concepts/composite-resource-definitions">}}).
{{< /hint >}}

View the installed XRD with `kubectl get xrd`.

```shell {copy-lines="1"}
$ kubectl get xrd
NAME                                  ESTABLISHED   OFFERED   AGE
virtualmachines.compute.example.com   True          True      7s
```

View the new custom API endpoints with `kubectl api-resources | grep VirtualMachine`

```shell
kubectl api-resources | grep nosql
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

This template creates an Alibaba Cloud
{{<hover label="comp" line="11">}}ECSInstance{{</hover>}}
{{<hover label="comp" line="46">}}SecurityGroup{{</hover>}},
{{<hover label="comp" line="69">}}VSwitch{{</hover>}} and
{{<hover label="comp" line="90">}}VPC{{</hover>}}.

This Composition takes the user's
{{<hover label="comp" line="36">}}location{{</hover>}} input and uses it as the
{{<hover label="comp" line="37">}}location{{</hover>}} used in the individual
resource.

{{<hint "important" >}}
This Composition uses an array of resource templates. You can patch each
template with data copied from the custom API. Crossplane calls this a _Patch
and Transform_ Composition.

You don't have to use Patch and Transform. Crossplane supports a variety of
alternatives, including Go Templating and CUE. You can also write a function in
Go or Python to template your resources.

Read the [Composition documentation]({{<ref "../concepts/compositions">}}) for
more information on configuring Compositions and all the available options.
{{< /hint >}}

Apply this Composition to your cluster.

```yaml {label="comp",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: crossplane-quickstart-vm-with-network
spec:
  mode: Pipeline
  pipeline:
    - step: patch-and-transform
      functionRef:
        name: function-patch-and-transform
      input:
        apiVersion: pt.fn.crossplane.io/v1beta1
        kind: Resources
        resources:
          - name: quickstart-vm
            base:
              apiVersion: ecs.alibabacloud.crossplane.io/v1alpha1
              kind: Instance
              metadata:
                annotations:
                  meta.upbound.io/example-id: ecs/v1alpha1/instance
                labels:
                  testing.upbound.io/example-name: instance
                name: instance
              spec:
                forProvider:
                  region: cn-zhangjiakou
                  availabilityZone: cn-zhangjiakou-a
                  dataDisks:
                    - category: cloud_efficiency
                      description: disk2
                      encrypted: true
                      name: disk2
                      size: 20
                  imageId: ubuntu_18_04_64_20G_alibase_20190624.vhd
                  instanceName: crossplane-example
                  instanceType: ecs.n4.large
                  internetMaxBandwidthOut: 10
                  securityGroupSelector:
                    matchLabels:
                      testing.upbound.io/example-name: group
                  systemDiskCategory: cloud_efficiency
                  systemDiskDescription: test_foo_system_disk_description
                  systemDiskName: crossplane-example
                  vswitchIdSelector:
                    matchLabels:
                      testing.upbound.io/example-name: vswitch
            patches:
              - type: FromCompositeFieldPath
                fromFieldPath: "spec.location"
                toFieldPath: "spec.forProvider.region"
                transforms:
                  - type: map
                    map:
                      CN: "cn-zhangjiakou"
                      US: "us-west-1"
              - type: FromCompositeFieldPath
                fromFieldPath: "spec.availabilityZone"
                toFieldPath: "spec.forProvider.availabilityZone"
                transforms:
                  - type: map
                    map:
                      CN: "cn-zhangjiakou-a"
                      US: "us-west-1a"
          - name: quickstart-securitygroup
            base:
              apiVersion: ecs.alibabacloud.crossplane.io/v1alpha1
              kind: SecurityGroup
              metadata:
                annotations:
                  meta.upbound.io/example-id: ecs/v1alpha1/instance
                labels:
                  testing.upbound.io/example-name: group
                name: group
              spec:
                forProvider:
                  region: cn-zhangjiakou
                  description: foo
                  securityGroupName: crossplane-example
                  vpcIdSelector:
                    matchLabels:
                      testing.upbound.io/example-name: vpc
            patches:
              - type: FromCompositeFieldPath
                fromFieldPath: "spec.location"
                toFieldPath: "spec.forProvider.region"
                transforms:
                  - type: map
                    map:
                      CN: "cn-zhangjiakou"
                      US: "us-west-1"
          - name: quickstart-vswitch
            base:
              apiVersion: vpc.alibabacloud.crossplane.io/v1alpha1
              kind: Vswitch
              metadata:
                annotations:
                  meta.upbound.io/example-id: ecs/v1alpha1/instance
                labels:
                  testing.upbound.io/example-name: vswitch
                name: vswitch
              spec:
                forProvider:
                  region: cn-zhangjiakou
                  cidrBlock: 172.16.0.0/24
                  vpcIdSelector:
                    matchLabels:
                      testing.upbound.io/example-name: vpc
                  vswitchName: crossplane-example
                  zoneId: cn-zhangjiakou-a
            patches:
              - type: FromCompositeFieldPath
                fromFieldPath: "spec.location"
                toFieldPath: "spec.forProvider.region"
                transforms:
                  - type: map
                    map:
                      CN: "cn-zhangjiakou"
                      US: "us-west-1"
              - type: FromCompositeFieldPath
                fromFieldPath: "spec.availabilityZone"
                toFieldPath: "spec.forProvider.zoneId"
                transforms:
                  - type: map
                    map:
                      CN: "cn-zhangjiakou-a"
                      US: "us-west-1a"
          - name: quickstart-vpc
            base:
              apiVersion: vpc.alibabacloud.crossplane.io/v1alpha1
              kind: VPC
              metadata:
                annotations:
                  meta.upbound.io/example-id: ecs/v1alpha1/instance
                labels:
                  testing.upbound.io/example-name: vpc
                name: vpc
              spec:
                forProvider:
                  region: cn-zhangjiakou
                  cidrBlock: 172.16.0.0/16
                  vpcName: crossplane-example
            patches:
              - type: FromCompositeFieldPath
                fromFieldPath: "spec.location"
                toFieldPath: "spec.forProvider.region"
                transforms:
                  - type: map
                    map:
                      CN: "cn-zhangjiakou"
                      US: "us-west-1"
  compositeTypeRef:
    apiVersion: compute.example.com/v1alpha1
    kind: VirtualMachine
EOF
```

The {{<hover label="comp" line="52">}}compositeTypeRef{{</hover >}} defines
which custom APIs can use this template to create resources.

A Composition uses a pipeline of _composition functions_ to define the cloud
resources to deploy. This template uses
{{<hover label="comp" line="10">}}function-patch-and-transform{{</hover>}}.
You must install the function before you can use it in a Composition.

Apply this Function to install `function-patch-and-transform`:
```yaml {label="install"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Function
metadata:
  name: function-patch-and-transform
spec:
  package: xpkg.crossplane.io/crossplane-contrib/function-patch-and-transform:v0.8.2
EOF
```
{{<hint "tip" >}}
Read the [Composition documentation]({{<ref "../concepts/compositions">}}) for
more information on configuring Compositions and all the available options.

Read the
[Patch and Transform function documentation]({{<ref "../guides/function-patch-and-transform">}})
for more information on how it uses patches to map user inputs to Composition
resource templates.
{{< /hint >}}

View the Composition with `kubectl get composition`

```shell {copy-lines="1"}
$ kubectl get composition
NAME                                    XR-KIND          XR-APIVERSION                  AGE
crossplane-quickstart-vm-with-network   VirtualMachine   compute.example.com/v1alpha1   2m30s
```

## Access the custom API

With the custom API (XRD) installed and associated to a resource template
(Composition) users can access the API to create resources.

Create a {{<hover label="xr" line="3">}}VirtualMachine{{</hover>}} object to
create the cloud resources.

```yaml {copy-lines="all",label="xr"}
cat <<EOF | kubectl apply -f -
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachine
metadata:
  name: my-vm
spec:
  location: "CN"
  availabilityZone: "CN"
EOF
```

View the resource with `kubectl get VirtualMachine`.

{{< hint "note" >}}
It may take up to five minutes for the resources to provision.
{{< /hint >}}

```shell {copy-lines="1"}
$ kubectl get VirtualMachine
NAME    SYNCED   READY   COMPOSITION                             AGE
my-vm   True     True    crossplane-quickstart-vm-with-network   2m30s
```
This object is a Crossplane _composite resource_ (also called an `XR`).
It's a
single object representing the collection of resources created from the
Composition template.

View the individual resources with `kubectl get managed`

```shell {copy-lines="1"}
$ kubectl get managed
NAME                                               SYNCED   READY   EXTERNAL-NAME            AGE
instance.ecs.alibabacloud.crossplane.io/instance   True     True    i-8vb7is*******   2m24s

NAME                                                 SYNCED   READY   EXTERNAL-NAME             AGE
securitygroup.ecs.alibabacloud.crossplane.io/group   True     True    sg-8vbbk**********   2m24s

NAME                                     SYNCED   READY   EXTERNAL-NAME               AGE
vpc.vpc.alibabacloud.crossplane.io/vpc   True     True    vpc-8vb************   2m26s

NAME                                             SYNCED   READY   EXTERNAL-NAME               AGE
vswitch.vpc.alibabacloud.crossplane.io/vswitch   True     True    vsw-8vb6f04ot************   2m26s
```

Accessing the API created all five resources defined in the template and linked
them together.

Delete the resources with `kubectl delete VirtualMachine`.

```shell {copy-lines="1"}
$ kubectl delete VirtualMachine my-vm
virtualmachine.compute.example.com "my-vm" deleted
```

Verify Crossplane deleted the resources with `kubectl get managed`

{{<hint "note" >}}
It may take up to 5 minutes to delete the resources.
{{< /hint >}}

```shell {copy-lines="1"}
$ kubectl get managed
No resources found
```

## Using the API with namespaces

Accessing the API `VirtualMachine` happens at the cluster scope.
Most organizations
isolate their users into namespaces.

A Crossplane _Claim_ is the custom API in a namespace.

Creating a _Claim_ is just like accessing the custom API endpoint, but with the
{{<hover label="claim" line="3">}}kind{{</hover>}}
from the custom API's `claimNames`.

Create a new namespace to test create a Claim in.

```shell
$ kubectl create namespace crossplane-test
```

Then create a Claim in the `crossplane-test` namespace.

```yaml {label="claim",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: compute.example.com/v1alpha1
kind: VirtualMachineClaim
metadata:
  name: my-namespaced-vm
  namespace: crossplane-test
spec:
  location: "CN"
  availabilityZone: "CN"
EOF
```
View the Claim with `kubectl get claim -n crossplane-test`.

```shell {copy-lines="1"}
$ kubectl get claim -n crossplane-test
NAME               SYNCED   READY   CONNECTION-SECRET   AGE
my-namespaced-vm   True     True                        100s
```

The Claim automatically creates a composite resource, which creates the managed
resources.

View the Crossplane created composite resource with `kubectl get composite`.

```shell {copy-lines="1"}
$ kubectl get composite
NAME                     SYNCED   READY   COMPOSITION                             AGE
my-namespaced-vm-pjt8c   True     True    crossplane-quickstart-vm-with-network   114s
```

Again, view the managed resources with `kubectl get managed`.

```shell {copy-lines="1"}
NAME                                               SYNCED   READY   EXTERNAL-NAME            AGE
instance.ecs.alibabacloud.crossplane.io/instance   True     True    i-8vbaj0********   2m25s

NAME                                                 SYNCED   READY   EXTERNAL-NAME             AGE
securitygroup.ecs.alibabacloud.crossplane.io/group   True     True    sg-8vb4pghz********   2m26s

NAME                                     SYNCED   READY   EXTERNAL-NAME               AGE
vpc.vpc.alibabacloud.crossplane.io/vpc   True     True    vpc-8vb7gz92*******   2m28s

NAME                                             SYNCED   READY   EXTERNAL-NAME               AGE
vswitch.vpc.alibabacloud.crossplane.io/vswitch   True     True    vsw-8vbo4dng2*******   2m28s
```

Deleting the Claim deletes all the Crossplane generated resources.

`kubectl delete claim -n crossplane-test my-namespaced-vm`

```shell {copy-lines="1"}
$ kubectl delete claim -n crossplane-test my-namespaced-vm
virtualmachineclaim.compute.example.com "my-namespaced-vm" deleted
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
* Explore AlibabaCloud resources that Crossplane can configure in the
  [Provider CRD reference](https://github.com/crossplane-contrib/provider-upjet-alibabacloud/tree/main/package/crds).
* Join the [Crossplane Slack](https://slack.crossplane.io/) and connect with
  Crossplane users and contributors.
* Read more about the [Crossplane concepts]({{<ref "../concepts">}}) to find out
  what else you can do with Crossplane.
