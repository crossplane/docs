---
title: Composite Resource Definitions
weight: 40
---

# Document XRD Conditions
https://github.com/crossplane/docs/issues/448


# Restart XR and claim controllers when XRDs are updated
https://github.com/crossplane/docs/issues/288

## CompositeResourceDefinitions

Below is an example `CompositeResourceDefinition` that includes all configurable
fields.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  # XRDs must be named '<plural>.<group>', per the plural and group names below.
  name: xpostgresqlinstances.example.org
spec:
  # This XRD defines an XR in the 'example.org' API group.
  group: example.org
  # The kind of this XR will be 'XPostgreSQLInstance`. You may also optionally
  # specify a singular name and a listKind.
  names:
    kind: XPostgreSQLInstance
    plural: xpostgresqlinstances
  # This type of XR offers a claim. Omit claimNames if you don't want to do so.
  # The claimNames must be different from the names above - a common convention
  # is that names are prefixed with 'X' while claim names are not. This lets app
  # team members think of creating a claim as (e.g.) 'creating a
  # PostgreSQLInstance'.
  claimNames:
    kind: PostgreSQLInstance
    plural: postgresqlinstances
  # Each type of XR can declare any keys they write to their connection secret
  # which will act as a filter during aggregation of the connection secret from
  # composed resources. It's recommended to provide the set of keys here so that
  # consumers of claims and XRs can see what to expect in the connection secret.
  # If no key is given, then all keys in the aggregated connection secret will
  # be written to the connection secret of the XR.
  connectionSecretKeys:
  - hostname
  # Each type of XR may specify a default Composite Delete Policy to be used
  # when the Claim has no compositeDeletePolicy.  The valid values are Background
  # and Foreground, and the default is Background.  See the description of the
  # compositeDeletePolicy parameter for more information.
  defaultCompositeDeletePolicy: Background
  # Each type of XR may specify a default Composition to be used when none is
  # specified (e.g. when the XR has no compositionRef or selector). A similar
  # enforceCompositionRef field also exists to allow XRs to enforce a specific
  # Composition that should always be used.
  defaultCompositionRef:
    name: example
  # Each type of XR may specify a default Composition Update Policy to be used
  # when the Claim has no compositionUpdatePolicy.  The valid values are Automatic
  # and Manual and the default is Automatic.
  defaultCompositionUpdatePolicy: Automatic
  # Each type of XR may be served at different versions - e.g. v1alpha1, v1beta1
  # and v1 - simultaneously. Currently Crossplane requires that all versions
  # have an identical schema, so this is mostly useful to 'promote' a type of XR
  # from alpha to beta to production ready.
  versions:
  - name: v1alpha1
    # Served specifies that XRs should be served at this version. It can be set
    # to false to temporarily disable a version, for example to test whether
    # doing so breaks anything before a version is removed wholesale.
    served: true
    # Referenceable denotes the version of a type of XR that Compositions may
    # use. Only one version may be referenceable.
    referenceable: true
    # Schema is an OpenAPI schema just like the one used by Kubernetes CRDs. It
    # determines what fields your XR and claim will have. Note that Crossplane
    # will automatically extend with some additional Crossplane machinery.
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              parameters:
                type: object
                properties:
                  storageGB:
                    type: integer
                required:
                - storageGB
            required:
            - parameters
          status:
            type: object
            properties:
              address:
                description: Address of this MySQL server.
                type: string
```

Take a look at the Kubernetes [CRD documentation][crd-docs] for a more detailed
guide to writing OpenAPI schemas. Note that the following fields are reserved
for Crossplane machinery, and will be ignored if your schema includes them:

* `spec.resourceRef`
* `spec.resourceRefs`
* `spec.claimRef`
* `spec.writeConnectionSecretToRef`
* `status.conditions`
* `status.connectionDetails`

> If your `CompositeResourceDefinition` isn't working as you'd expect you can
> try running `kubectl describe xrd` for details - pay particular attention to
> any events and status conditions.
