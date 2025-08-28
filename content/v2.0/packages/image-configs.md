---
title: Image Configs
weight: 400
description: "Centralized control of package image configuration"
---

<!-- vale write-good.Passive = NO -->

`ImageConfig` is an API for centralized control over the configuration of
Crossplane package images. It allows you to configure package manager behavior
for images globally, without needing to be referenced by other objects.

## Matching image references

`spec.matchImages` is a list of image references that the `ImageConfig` applies
to. Each item in the list specifies the type and configuration of the image
reference to match. The only supported type is `Prefix`, which matches the
prefix of the image reference. No wildcards are supported. The `type` defaults
to `Prefix` and can be omitted.

When there are multiple `ImageConfigs` matching an image reference, the one with
the longest matching prefix is selected. If there are multiple `ImageConfigs`
with the same longest matching prefix, one of them is selected
arbitrarily. Please note that this situation occurs only if there are
overlapping prefixes in the `matchImages` lists of different `ImageConfig`
resources, which should be avoided.

The default registry isn't taken into account for `ImageConfig` matching. That
is, an `ImageConfig` matching the prefix `xpkg.crossplane.io/crossplane-contrib`
doesn't match the following provider, even if the default registry is
`xpkg.crossplane.io`:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-nop
spec:
  package: crossplane-contrib/provider-nop:v0.4.0
```

## Configuring a pull secret

You can use `ImageConfig` to inject a pull secret into the Crossplane package
manager registry client whenever it interacts with the registry, such as for
dependency resolution or image pulls.

In the following example, the `ImageConfig` resource named `acme-packages` is
configured to inject the pull secret named `acme-registry-credentials` whenever
it needs to interact with the registry for images with the prefix
`registry1.com/acme-co/`.

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: ImageConfig
metadata:
  name: acme-packages
spec:
  matchImages:
    - type: Prefix
      prefix: registry1.com/acme-co/
  registry:
    authentication:
      pullSecretRef:
        name: acme-registry-credentials
```

`spec.registry.authentication.pullSecretRef` is a reference to the pull secret
that should be injected into the registry client. The secret must be of type
`kubernetes.io/dockerconfigjson` and must be in the Crossplane installation
namespace, typically `crossplane-system`. One can create the secret using the
following command:

```shell
kubectl -n crossplane-system create secret docker-registry acme-registry-credentials --docker-server=registry1.com --docker-username=<user> --docker-password=<password>
```

## Configuring signature verification

{{<hint "important" >}}
Signature verification is an alpha feature and needs to be enabled with the
`--enable-signature-verification` feature flag.
{{< /hint >}}

You can use `ImageConfig` to configure signature verification for images. When
you enable signature verification, the package manager verifies the signature of
each image before pulling it. If the signature isn't valid, the package manager
rejects the package deployment.

In the following example, the `ImageConfig` resource named `verify-acme-packages`
configures verification of the signature of images with the prefixes
`registry1.com/acme-co/configuration-foo` and
`registry1.com/acme-co/configuration-bar`. 

In the example below, the `ImageConfig` resource named `verify-acme-packages` is
set up to verify the signatures of images with the prefixes
`registry1.com/acme-co/configuration-foo` and `registry1.com/acme-co/configuration-bar`.

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: ImageConfig
metadata:
  name: verify-acme-packages
spec:
  matchImages:
    - type: Prefix
      prefix: registry1.com/acme-co/configuration-foo
    - type: Prefix
      prefix: registry1.com/acme-co/configuration-bar
  verification:
    provider: Cosign
    cosign:
      authorities:
        - name: verify acme packages
          keyless:
            identities:
              - issuer: https://token.actions.githubusercontent.com
                subject: https://github.com/acme-co/crossplane-packages/.github/workflows/supplychain.yml@refs/heads/main
          attestations:
            - name: verify attestations
              predicateType: spdxjson
```

`spec.verification.provider` specifies the signature verification provider.
The only supported provider is `Cosign`. `spec.verification.cosign` contains the
configuration for the Cosign provider. The `authorities` field contains the
configuration for the authorities that sign the images. The `attestations` field
contains the configuration for verifying the attestations of the images.

The `ImageConfig` API follows the same API shape as [Policy Controller](https://docs.sigstore.dev/policy-controller/overview/)
from [Sigstore](https://docs.sigstore.dev/). Crossplane initially supports a
subset of the Policy Controller configuration options which can be found in the
[API reference]({{<ref "../api/#ImageConfig-spec-verification-cosign">}})
for the `ImageConfig` resource together with their descriptions.

When multiple authorities are provided, the package manager verifies the
signature against each authority until it finds a valid one. If any of the
authorities' signatures are valid, the package manager accepts the image.
Similarly, when multiple identities or attestations are provided, the package
manager verifies until it finds a valid match and fails if none of them matches.

Matching the image reference to the `ImageConfig` works similarly to the pull
secret configuration, as described in the previous section.

### Checking the signature verification status

When you enable signature verification, the respective controller reports the
verification status as a condition of type `Verified` on the package revision
resources. This condition indicates whether the signature verification was
successful, failed, skipped, or incomplete due to an error.

#### Example conditions

**Verification skipped:** The package manager skipped signature verification for
the package revision because there were no matching `ImageConfig` with signature
verification configuration.

```yaml
  - lastTransitionTime: "2024-10-23T16:38:51Z"
    reason: SignatureVerificationSkipped
    status: "True"
    type: Verified
```

**Verification successful:** The package manager successfully verified the
signature of the image in the package revision.

```yaml
  - lastTransitionTime: "2024-10-23T16:43:05Z"
    message: Signature verification succeeded with ImageConfig named "verify-acme-packages"
    reason: VerificationSucceeded
    status: "True"
    type: Verified
```

**Verification failed:** The package manager failed to verify the signature of
the image in the package revision.

```yaml
  - lastTransitionTime: "2024-10-23T16:42:44Z"
    message: 'Signature verification failed with ImageConfig named "verify-acme-packages":
      [signature keyless validation failed for authority verify acme packages
      for registry1.com/acme-co/configuration-foo:v0.2.0: no signatures found: ]'
    reason: SignatureVerificationFailed
    status: "False"
    type: Verified
```

**Verification incomplete:** The package manager encountered an error while
verifying the signature of the image in the package revision.

```yaml
  - lastTransitionTime: "2024-10-23T16:44:22Z"
    message: 'Error occurred during signature verification cannot get image verification
      config: cannot get cosign verification config: no data found for key "cosign.pub"
      in secret "cosign-public-key"'
    reason: SignatureVerificationIncomplete
    status: "False"
    type: Verified
```

If you can't see this condition on the package revision resource, namely
`ProviderRevision`, `ConfigurationRevision`, or `FunctionRevision`, ensure that
you enable the feature.

## Rewriting image paths

You can use an `ImageConfig` to pull package images from an alternative location
such as a private registry. `spec.rewriteImages` specifies how to rewrite the
paths of matched images.

Only prefix replacement is supported. The prefix specified in
`spec.rewriteImage.prefix` replaces the matched prefix from `matchImages`. For
example, the following `ImageConfig` replaces `xpkg.crossplane.io` with
`registry1.com` for any image with the prefix `xpkg.crossplane.io`.

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: ImageConfig
metadata:
  name: private-registry-rewrite
spec:
  matchImages:
    - prefix: xpkg.crossplane.io
  rewriteImage:
    prefix: registry1.com
```

In this example, installing the provider package
`xpkg.crossplane.io/crossplane-contrib/provider-nop:v0.4.0` will result in the
package manager pulling the provider from
`registry1.com/crossplane-contrib/provider-nop:v0.4.0`.

Rewriting image paths via `ImageConfig` is useful when mirroring packages to a
private registry, because it allows a package and all its dependencies to be
pulled from the same registry. For example, the provider
`xpkg.crossplane.io/crossplane-contrib/provider-aws-s3` has a dependency on
`xpkg.crossplane.io/crossplane-contrib/provider-family-aws`. If you mirror the
packages to your own registry at `registry1.com` and install them without an
`ImageConfig`, the package manager still attempts to pull the dependency from
`xpkg.crossplane.io`. With the preceding `ImageConfig`, the dependency is pulled
from `registry1.com`.

Rewriting an image path with `ImageConfig` doesn't change the `spec.package`
field of the package resource. The rewritten path is recorded in the
`status.resolvedPackage` field. The preceding example results in the following:

```shell
kubectl describe provider crossplane-contrib-provider-family-aws
...
Spec:
  ...
  Package:                        xpkg.crossplane.io/crossplane-contrib/provider-family-aws:v1.22.0
Status:
  ...
  Resolved Package:        registry1.com/crossplane-contrib/provider-family-aws:v1.22.0
```

### Interaction with other operations

{{<hint "tip" >}}
Image rewriting is always done before other `ImageConfig` operations. If you
wish to configure pull secrets or signature verification as well as rewriting,
additional `ImageConfig` resources must match the rewritten image path.
{{< /hint >}}

For example, if you are mirroring packages from `xpkg.crossplane.io` to
`registry1.com` and need to configure pull secrets for `registry1.com`, two
`ImageConfig` resources are necessary:

```yaml
# Rewrite xpkg.crossplane.io -> registry1.com
---
apiVersion: pkg.crossplane.io/v1beta1
kind: ImageConfig
metadata:
  name: private-registry-rewrite
spec:
  matchImages:
    - prefix: xpkg.crossplane.io
  rewriteImage:
    prefix: registry1.com

# Configure pull secrets for registry1.com
---
apiVersion: pkg.crossplane.io/v1beta1
kind: ImageConfig
metadata:
  name: private-registry-auth
spec:
  matchImages:
    - type: Prefix
      prefix: registry1.com
  registry:
    authentication:
      pullSecretRef:
        name: private-registry-credentials
```

## Debugging

When the package manager selects an `ImageConfig` for a package, it throws an
event with the reason `ImageConfigSelection` and the name of the selected
`ImageConfig` and injected pull secret. You can find these events both on the
package and package revision resources. The package manager also updates the
`appliedImageConfigRefs` field in the package status to show the purpose for
which each `ImageConfig` was selected.

For example, the following event and status show that the `ImageConfig` named
`acme-packages` was used to provide a pull secret for the configuration named
`acme-configuration-foo`:

```shell
kubectl describe configuration acme-configuration-foo
...
Status:
  Applied Image Config Refs:
    Name:    acme-packages
    Reason:  SetImagePullSecret
...
Events:
  Type     Reason                Age                From                                              Message
  ----     ------                ----               ----                                              -------
  Normal   ImageConfigSelection  45s                packages/configuration.pkg.crossplane.io          Selected pullSecret "acme-registry-credentials" from ImageConfig "acme-packages" for registry authentication
```

If you can't find the expected event and `appliedImageConfigRefs` entry, ensure
the prefix of the image reference matches the `matchImages` list of any
`ImageConfig` resources in the cluster.

<!-- vale write-good.Passive = YES -->
