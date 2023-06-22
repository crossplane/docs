---
title: Claims
weight: 50
---

# Claim annotations
https://github.com/crossplane/docs/issues/281
(I can't find the thing being referenced)

### Claiming Composite Resources

Crossplane uses Composite Resource Claims (or just claims, for short) to allow
application operators to provision and manage XRs. When we talk about using XRs
it's typically implied that the XR is being used via a claim. Claims are almost
identical to their corresponding XRs. It helps to think of a claim as an
application team’s interface to an XR. You could also think of claims as the
public (app team) facing part of the opinionated platform API, while XRs are the
private (platform team) facing part.

A claim for the `XPostgreSQLInstance` XR above would look like this:

```yaml
apiVersion: database.example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  namespace: default
  name: my-db
spec:
  parameters:
    storageGB: 20
  compositionRef:
    name: production
  writeConnectionSecretToRef:
    name: my-db-connection-details
```

There are three key differences between an XR and a claim:

1. Claims are namespaced, while XRs (and Managed Resources) are cluster scoped.
1. Claims are of a different `kind` than the XR - by convention the XR's `kind`
   without the proceeding `X`. For example a `PostgreSQLInstance` claims an
   `XPostgreSQLInstance`.
1. An active claim contains a reference to its corresponding XR, while an XR
   contains both a reference to the claim an array of references to the managed
   resources it composes.

Not all XRs offer a claim - doing so is optional. See the XRD section of the
[Composition reference][xr-ref] to learn how to offer a claim.

![Diagram showing the relationship between claims and XRs][claims-and-xrs]

Claims may seem a little superfluous at first, but they enable some handy
scenarios, including:

- **Private XRs.** Sometimes a platform team might not want a type of XR to be
  directly consumed by their application teams. For example because the XR
  represents 'supporting' infrastructure - consider the above VPC `XNetwork` XR. App
  teams might create `PostgreSQLInstance` claims that _reference_ (i.e. consume)
  an `XNetwork`, but they shouldn't be _creating their own_. Similarly, some
  kinds of XR might be intended only for 'nested' use - intended only to be
  composed by other XRs.

- **Global XRs**. Not all infrastructure is conceptually namespaced. Say your
  organisation uses team scoped namespaces. A `PostgreSQLInstance` that belongs
  to Team A should probably be part of the `team-a` namespace - you'd represent
  this by creating a `PostgreSQLInstance` claim in that namespace. On the other
  hand the `XNetwork` XR we mentioned previously could be referenced (i.e. used)
  by XRs from many different namespaces - it doesn't exist to serve a particular
  team.

- **Pre-provisioned XRs**. Finally, separating claims from XRs allows a platform
  team to pre-provision certain kinds of XR. Typically an XR is created
  on-demand in response to the creation of a claim, but it's also possible for a
  claim to instead request an existing XR. This can allow application teams to
  instantly claim infrastructure like database instances that would otherwise
  take minutes to provision on-demand.


This reference provides detailed examples of defining, configuring, and using
Composite Resources in Crossplane. You can also refer to Crossplane's [API
documentation][api-docs] for more details. If you're looking for a more general
overview of Composite Resources and Composition in Crossplane, try the
[Composite Resources][xr-concepts] page under Concepts.

## Composite Resources and Claims

The type and most of the schema of Composite Resources and claims are largely of
your own choosing, but there is some common 'machinery' injected into them.
Here's a hypothetical XR that doesn't have any user-defined fields and thus only
includes the automatically injected Crossplane machinery:

```yaml
apiVersion: database.example.org/v1alpha1
kind: XPostgreSQLInstance
metadata:
  # This XR was created automatically by a claim, so its name is derived from
  # the claim's name.
  name: my-db-mfd1b
  annotations:
    # The external name annotation has special meaning in Crossplane. When a
    # claim creates an XR its external name will automatically be propagated to
    # the XR. Whether and how the external name is propagated to the resources
    # the XR composes is up to its Composition.
    crossplane.io/external-name: production-db-0
spec:
  # XRs have a reference to the claim that created them (or, if the XR was
  # pre-provisioned, to the claim that later claimed them).
  claimRef:
    apiVersion: database.example.org/v1alpha1
    kind: PostgreSQLInstance
    name: my-db
  # The compositeDeletePolicy specifies the propagation policy that will be used by Crossplane
  # when deleting the Composite Resource that is associated with the Claim.  The default
  # value is Background, which causes the Composite resource to be deleted using
  # the kubernetes default propagation policy of Background, and all associated
  # resources will be deleted simultaneously.  The other value for this field is Foreground,
  # which will cause the Composite resource to be deleted using Foreground Cascading Deletion.
  # Kubernetes will add a foregroundDeletion finalizer to all of the resources in the
  # dependency graph, and they will be deleted starting with the edge or leaf nodes and
  # working back towards the root Composite.  See https://kubernetes.io/docs/concepts/architecture/garbage-collection/#cascading-deletion
  # for more information on cascading deletion.
  compositeDeletePolicy: Background
  # The compositionRef specifies which Composition this XR will use to compose
  # resources when it is created, updated, or deleted. This can be omitted and
  # will be set automatically if the XRD has a default or enforced composition
  # reference, or if the below composition selector is set.
  compositionRef:
    name: production-us-east
  # The compositionSelector allows you to match a Composition by labels rather
  # than naming one explicitly. It is used to set the compositionRef if none is
  # specified explicitly.
  compositionSelector:
    matchLabels:
      environment: production
      region: us-east
      provider: gcp
  # The environment is an in-memory object that can be patched from / to during
  # rendering.
  # The environment is composed by merging the 'data' of all EnvironmentConfigs
  # referenced below. It is disposed after every reconcile.
  # NOTE: EnvironmentConfigs are an alpha feature and need to be enabled with
  #       the '--enable-environment-configs' flag on startup.
  environment:
    # EnvironmentConfigs is a list of object references that is made up of
    # name references and label selectors
    environmentConfigs:
      - type: Reference # this is the default
        ref:
          name: example-environment
      - type: Selector
        selector:
          - key: stage
            type: FromCompositeFieldPath # this is the default
            valueFromFieldPath: spec.parameters.stage
          - key: provider
            type: Value
            value: "gcp"
  # The resourceRefs array contains references to all of the resources of which
  # this XR is composed. Despite being in spec this field isn't intended to be
  # configured by humans - Crossplane will take care of keeping it updated.
  resourceRefs:
  - apiVersion: database.gcp.crossplane.io/v1beta1
    kind: CloudSQLInstance
    name: my-db-mfd1b-md9ab
  # The writeConnectionSecretToRef field specifies a Kubernetes Secret that this
  # XR should write its connection details (if any) to.
  writeConnectionSecretToRef:
    namespace: crossplane-system
    name: my-db-connection-details
status:
  # An XR's 'Ready' condition will become True when all of the resources it
  # composes are deemed ready. Refer to the Composition 'readinessChecks' field
  # for more information.
  conditions:
  - type: Ready
    statue: "True"
    reason: Available
    lastTransitionTime: 2021-10-02T07:20:50.52Z
  # The last time the XR published its connection details to a Secret.
  connectionDetails:
    lastPublishedTime: 2021-10-02T07:20:51.24Z
```

Similarly, here's an example of the claim that corresponds to the above XR:

```yaml
apiVersion: database.example.org/v1alpha1
kind: PostgreSQLInstance
metadata:
  # Claims are namespaced, unlike XRs.
  namespace: default
  name: my-db
  annotations:
    # The external name annotation has special meaning in Crossplane. When a
    # claim creates an XR its external name will automatically be propagated to
    # the XR. Whether and how the external name is propagated to the resources
    # the XR composes is up to its Composition.
    crossplane.io/external-name: production-db-0
spec:
  # The resourceRef field references the XR this claim corresponds to. You can
  # either set it to an existing (compatible) XR that you'd like to claim or
  # (the more common approach) leave it blank and let Crossplane automatically
  # create and reference an XR for you.
  resourceRef:
    apiVersion: database.example.org/v1alpha1
    kind: XPostgreSQLInstance
    name: my-db-mfd1b
  # A claim's compositionRef and compositionSelector work the same way as an XR.
  compositionRef:
    name: production-us-east
  compositionSelector:
    matchLabels:
      environment: production
      region: us-east
      provider: gcp
  # A claim's writeConnectionSecretToRef mostly works the same way as an XR's.
  # The one difference is that the Secret is always written to the namespace of
  # the claim.
  writeConnectionSecretToRef:
    name: my-db-connection-details
status:
  # A claim's 'Ready' condition will become True when its XR's 'Ready' condition
  # becomes True.
  conditions:
  - type: Ready
    statue: "True"
    reason: Available
    lastTransitionTime: 2021-10-02T07:20:50.52Z
  # The last time the claim published its connection details to a Secret.
  connectionDetails:
    lastPublishedTime: 2021-10-02T07:20:51.24Z
```

### Claiming an Existing Composite Resource

Most people create Composite Resources using a claim, but you can actually claim
an existing Composite Resource as long as its a type of XR that offers a claim
and no one else has already claimed it. To do so:

1. Set the `spec.resourceRef` of your claim to reference the existing XR.
1. Make sure the rest of your claim's spec fields match the XR's.

If your claim's spec fields don't match the XR's Crossplane will still claim it
but will then try to update the XR's spec fields to match the claim's.
