---
title: Composition Revisions
weight: 35
description: "Manage changes to Compositions with revisions"
---

This guide discusses the use of "Composition Revisions" to make and roll
back changes to a Crossplane [`Composition`][composition type]. It assumes
familiarity with Crossplane and
[Compositions].

A `Composition` configures how Crossplane should reconcile a Composite Resource
(XR). Put otherwise, when you create an XR the selected `Composition` determines
what resources Crossplane creates in response. For example,
you define a `PlatformDB` XR, which represents your organisation's common
database configuration of an Azure MySQL Server and some firewall rules. The
`Composition` contains the 'base' configuration for the MySQL server and the
firewall rules that the `PlatformDB` configuration extends.

A `Composition` associates with multiple XRs that use it. You might
define a `Composition` named `big-platform-db` that's used by ten different
`PlatformDB` XRs. Often, in the interest of self-service, a different team manages the `Composition`
than the actual `PlatformDB` XRs. For example
a platform team member may write and maintain the `Composition`,
while individual app teams create `PlatformDB` XRs that use said
`Composition`.

Each `Composition` is mutable - you can update it as your organisation's needs
change. Updating a `Composition` without Composition Revisions can be a
risky process. Crossplane constantly uses the `Composition` to ensure that your
actual infrastructure - your MySQL Servers and firewall rules - match your
desired state. If you have 10 `PlatformDB` XRs all using the `big-platform-db`
`Composition`, all 10 of those XRs are instantly updated following
any updates you make to the `big-platform-db` `Composition`.

Composition Revisions allow XRs to opt out of automatic updates. Instead you can
update your XRs to use the latest `Composition` settings at your own pace.
This enables you to [canary] changes to your infrastructure, or to roll back
some XRs to previous `Composition` settings without rolling back all XRs.

## Using composition revisions

When you enable Composition Revisions three things happen:

1. Crossplane creates a `CompositionRevision` for each `Composition` update.
1. Composite Resources gain a `spec.crossplane.compositionRevisionRef` field that specifies
   which `CompositionRevision` they use.
1. Composite Resources gain a `spec.crossplane.compositionUpdatePolicy` field that
   specifies how Crossplane should update them to new Composition Revisions.

Each time you edit a `Composition` Crossplane automatically creates a
`CompositionRevision` that represents that 'revision' of the `Composition` -
that unique state. Crossplane allocates each revision an increasing revision number.
This gives `CompositionRevision` consumers an idea about which revision is
'newest'.

You can discover which revisions exist using `kubectl`:

```console
# Find all revisions of the Composition named 'example'
kubectl get compositionrevision -l crossplane.io/composition-name=example
```

This should produce output something like:

```console
NAME              REVISION   AGE
example-18pdgs2   1          4m36s
example-2bgdr31   2          73s
example-xjrdmzz   3          61s
```

> A `Composition` is a mutable resource that you can update as your needs
> change over time. Each `CompositionRevision` is an immutable snapshot of those
> needs at a particular time.

Crossplane behaves the same way by default whether you enable Composition Revisions or not. When you enable Composition Revisions all XRs
default to the `Automatic` `compositionUpdatePolicy`. XRs support two update
policies:

* `Automatic`: Automatically use the latest `CompositionRevision`. (Default)
* `Manual`: Require manual intervention to change `CompositionRevision`.

The below XR uses the `Manual` policy.
When you use this policy, the XR selects the latest `CompositionRevision` when
it's first created.
You must manually update it when you wish it to use another
`CompositionRevision`.

```yaml
apiVersion: example.org/v1alpha1
kind: PlatformDB
metadata:
  namespace: default
  name: example
spec:
  storageGB: 20
  crossplane:
    # The Manual policy specifies that you don't want this XR to update to the
    # latest CompositionRevision automatically.
    compositionUpdatePolicy: Manual
    compositionRef:
      name: example
```

Crossplane sets an XR's `compositionRevisionRef` automatically at creation time
regardless of your chosen `compositionUpdatePolicy`. If you choose the `Manual`
policy you must edit the `compositionRevisionRef` field when you want your XR to
use a different `CompositionRevision`.

```yaml
apiVersion: example.org/v1alpha1
kind: PlatformDB
metadata:
  namespace: default
  name: example
spec:
  storageGB: 20
  crossplane:
    compositionUpdatePolicy: Manual
    compositionRef:
      name: example
    # Update the referenced CompositionRevision if and when you are ready.
    compositionRevisionRef:
      name: example-18pdg
```

## Complete example

This tutorial discusses how CompositionRevisions work and how they manage Composite Resource
(XR) updates. This starts with a `Composition` and `CompositeResourceDefinition` (XRD) that defines a `MyVPC`
resource and continues with creating multiple XRs to observe different upgrade paths. Crossplane
assigns different CompositionRevisions to composite resources each time you update the composition.

### Preparation

#### Deploy composition and XRD examples
Apply the example Composition.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  labels:
    channel: dev
  name: myvpcs.aws.example.upbound.io
spec:
  compositeTypeRef:
    apiVersion: aws.example.upbound.io/v1alpha1
    kind: MyVPC
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: my-vpc
        base:
          apiVersion: ec2.aws.m.upbound.io/v1beta1
          kind: VPC
          spec:
            forProvider:
              region: us-west-1
              cidrBlock: 192.168.0.0/16
              enableDnsSupport: true
              enableDnsHostnames: true
```

Apply the example XRD.
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: myvpcs.aws.example.upbound.io
spec:
  group: aws.example.upbound.io
  names:
    kind: MyVPC
    plural: myvpcs
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
              id:
                type: string
                description: ID of this VPC that other objects will use to refer to it.
            required:
            - id
```

Verify that Crossplane created the Composition revision
```shell
kubectl get compositionrevisions -o="custom-columns=NAME:.metadata.name,REVISION:.spec.revision,CHANNEL:.metadata.labels.channel"
```
Expected Output:
```shell
NAME                                    REVISION   CHANNEL
myvpcs.aws.example.upbound.io-ad265bc   1          dev
```

{{< hint "note" >}}
The label `dev` is automatically created from the Composition.
{{< /hint >}}


### Create composite resources
This tutorial has four composite resources to cover different update policies and composition selection options.
The default behavior is updating XRs to the latest revision of the Composition. You can change this by setting
`compositionUpdatePolicy: Manual` in the XR. It's also possible to select the latest revision with a specific label
with `compositionRevisionSelector.matchLabels` together with `compositionUpdatePolicy: Automatic`.

#### Default update policy
Create an XR without a `compositionUpdatePolicy` defined. The update policy is `Automatic` by default:
```yaml
apiVersion: aws.example.upbound.io/v1alpha1
kind: MyVPC
metadata:
  namespace: default
  name: vpc-auto
spec:
  id: vpc-auto
```
Expected Output:
```shell
myvpc.aws.example.upbound.io/vpc-auto created
```

#### Manual update policy
Create a Composite Resource with `compositionUpdatePolicy: Manual` and `compositionRevisionRef`.
```yaml
apiVersion: aws.example.upbound.io/v1alpha1
kind: MyVPC
metadata:
  namespace: default
  name: vpc-man
spec:
  id: vpc-man
  crossplane:
    compositionUpdatePolicy: Manual
    compositionRevisionRef:
      name: myvpcs.aws.example.upbound.io-ad265bc
```

Expected Output:
```shell
myvpc.aws.example.upbound.io/vpc-man created
```

#### Using a selector
Create an XR with a `compositionRevisionSelector` of `channel: dev`:
```yaml
apiVersion: aws.example.upbound.io/v1alpha1
kind:  MyVPC
metadata:
  namespace: default
  name: vpc-dev
spec:
  id: vpc-dev
  crossplane:
    compositionRevisionSelector:
      matchLabels:
        channel: dev
```
Expected Output:
```shell
myvpc.aws.example.upbound.io/vpc-dev created
```

Create an XR with a `compositionRevisionSelector` of `channel: staging`:
```yaml
apiVersion: aws.example.upbound.io/v1alpha1
kind: MyVPC
metadata:
  namespace: default
  name: vpc-staging
spec:
  id: vpc-staging
  crossplane:
    compositionRevisionSelector:
      matchLabels:
        channel: staging
```

Expected Output:
```shell
myvpc.aws.example.upbound.io/vpc-staging created
```

Verify the Composite Resource with the label `channel: staging` doesn't have a `REVISION`.
All other XRs have a `REVISION` matching the created Composition Revision.
```shell
kubectl get composite -o="custom-columns=NAME:.metadata.name,SYNCED:.status.conditions[0].status,REVISION:.spec.crossplane.compositionRevisionRef.name,POLICY:.spec.crossplane.compositionUpdatePolicy,MATCHLABEL:.spec.crossplane.compositionRevisionSelector.matchLabels"
```
Expected Output:
```shell
NAME          SYNCED   REVISION                                POLICY      MATCHLABEL
vpc-auto      True     myvpcs.aws.example.upbound.io-ad265bc   Automatic   <none>
vpc-dev       True     myvpcs.aws.example.upbound.io-ad265bc   Automatic   map[channel:dev]
vpc-man       True     myvpcs.aws.example.upbound.io-ad265bc   Manual      <none>
vpc-staging   False    <none>                                  Automatic   map[channel:staging]
```

{{< hint "note" >}}
The `vpc-staging` XR label doesn't match any existing Composition Revisions.
{{< /hint >}}

### Create new composition revisions
Crossplane creates a new CompositionRevision when you create or update a Composition. Label and annotation changes
also trigger a new CompositionRevision.

#### Update the composition label
Update the `Composition` label to `channel: staging`:
```shell
kubectl label composition myvpcs.aws.example.upbound.io channel=staging --overwrite
```
Expected Output:
```shell
composition.apiextensions.crossplane.io/myvpcs.aws.example.upbound.io labeled
```

Verify that Crossplane creates a new Composition revision:
```shell
kubectl get compositionrevisions -o="custom-columns=NAME:.metadata.name,REVISION:.spec.revision,CHANNEL:.metadata.labels.channel"
```
Expected Output:
```shell
NAME                                    REVISION   CHANNEL
myvpcs.aws.example.upbound.io-727b3c8   2          staging
myvpcs.aws.example.upbound.io-ad265bc   1          dev
```

Verify that Crossplane assigns the Composite Resources `vpc-auto` and `vpc-staging` to Composite `revision:2`.
XRs `vpc-man` and `vpc-dev` are still assigned to the original `revision:1`:

```shell
kubectl get composite -o="custom-columns=NAME:.metadata.name,SYNCED:.status.conditions[0].status,REVISION:.spec.crossplane.compositionRevisionRef.name,POLICY:.spec.crossplane.compositionUpdatePolicy,MATCHLABEL:.spec.crossplane.compositionRevisionSelector.matchLabels"
```
Expected Output:
```shell
NAME          SYNCED   REVISION                                POLICY      MATCHLABEL
vpc-auto      True     myvpcs.aws.example.upbound.io-727b3c8   Automatic   <none>
vpc-dev       True     myvpcs.aws.example.upbound.io-ad265bc   Automatic   map[channel:dev]
vpc-man       True     myvpcs.aws.example.upbound.io-ad265bc   Manual      <none>
vpc-staging   True     myvpcs.aws.example.upbound.io-727b3c8   Automatic   map[channel:staging]
```

{{< hint "note" >}}
`vpc-auto` always use the latest Revision.
`vpc-staging` now matches the label applied to Revision `revision:2`.
{{< /hint >}}

#### Update composition spec and label
Update the Composition to disable DNS support in the VPC and change the label from `staging` back to `dev`.

Apply the following changes to update the `Composition` spec and label:
```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  labels:
    channel: dev
  name: myvpcs.aws.example.upbound.io
spec:
  compositeTypeRef:
    apiVersion: aws.example.upbound.io/v1alpha1
    kind: MyVPC
  mode: Pipeline
  pipeline:
  - step: patch-and-transform
    functionRef:
      name: function-patch-and-transform
    input:
      apiVersion: pt.fn.crossplane.io/v1beta1
      kind: Resources
      resources:
      - name: my-vpc
        base:
          apiVersion: ec2.aws.m.upbound.io/v1beta1
          kind: VPC
          spec:
            forProvider:
              region: us-west-1
              cidrBlock: 192.168.0.0/16
              enableDnsSupport: false
              enableDnsHostnames: true
```

Expected Output:
```shell
composition.apiextensions.crossplane.io/myvpcs.aws.example.upbound.io configured
```

Verify that Crossplane creates a new Composition revision:

```shell
kubectl get compositionrevisions -o="custom-columns=NAME:.metadata.name,REVISION:.spec.revision,CHANNEL:.metadata.labels.channel"
```
Expected Output:
```shell
NAME                                    REVISION   CHANNEL
myvpcs.aws.example.upbound.io-727b3c8   2          staging
myvpcs.aws.example.upbound.io-ad265bc   1          dev
myvpcs.aws.example.upbound.io-f81c553   3          dev
```

{{< hint "note" >}}
Changing the label and the spec values simultaneously is critical for deploying new changes to the `dev` channel.
{{< /hint >}}

Verify Crossplane assigns the Composite Resources `vpc-auto` and `vpc-dev` to Composite `revision:3`.
Crossplane assigns `vpc-staging` to `revision:2`, and still assigns `vpc-man` to the original `revision:1`:

```shell
kubectl get composite -o="custom-columns=NAME:.metadata.name,SYNCED:.status.conditions[0].status,REVISION:.spec.crossplane.compositionRevisionRef.name,POLICY:.spec.crossplane.compositionUpdatePolicy,MATCHLABEL:.spec.crossplane.compositionRevisionSelector.matchLabels"
```
Expected Output:
```shell
NAME          SYNCED   REVISION                                POLICY      MATCHLABEL
vpc-auto      True     myvpcs.aws.example.upbound.io-f81c553   Automatic   <none>
vpc-dev       True     myvpcs.aws.example.upbound.io-f81c553   Automatic   map[channel:dev]
vpc-man       True     myvpcs.aws.example.upbound.io-ad265bc   Manual      <none>
vpc-staging   True     myvpcs.aws.example.upbound.io-727b3c8   Automatic   map[channel:staging]
```


{{< hint "note" >}}
`vpc-dev` matches the updated label applied to Revision `revision:3`.
`vpc-staging` matches the label applied to Revision `revision:2`.
{{< /hint >}}


[composition type]: {{<ref "compositions">}}
[Compositions]: {{<ref "compositions">}}
[canary]: https://martinfowler.com/bliki/CanaryRelease.html
[install guide]: {{<ref "../get-started/install">}}
