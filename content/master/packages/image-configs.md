---
title: Image Configs
weight: 400
description: "Centralized control of package image configuration"
---

<!-- vale write-good.Passive = NO -->

`ImageConfig` is an API for centralized control over the configuration of
Crossplane package images. It allows you to configure package manager behavior
for images globally, without other objects needing to reference it.

## Matching image references

`spec.matchImages` is a list of image references that the `ImageConfig` applies
to. Each item in the list specifies the type and configuration of the image
reference to match. The only supported type is `Prefix`, which matches the
prefix of the image reference. Crossplane doesn't support wildcards. The `type`
defaults to `Prefix` and you can omit it.

When there are multiple `ImageConfigs` matching an image reference, Crossplane
selects the one with the longest matching prefix. If there are multiple
`ImageConfigs` with the same longest matching prefix, Crossplane selects one of
them arbitrarily. This situation occurs only if there are
overlapping prefixes in the `matchImages` lists of different `ImageConfig`
resources. Avoid this situation.

## Configuring a pull secret

You can use `ImageConfig` to inject a pull secret into the Crossplane package
manager registry client. The secret applies whenever the client interacts with
the registry, such as for dependency resolution or image pulls.

In the following example, the `ImageConfig` resource named `acme-packages`
injects the pull secret named `acme-registry-credentials`. This applies whenever
the client interacts with the registry for images with the prefix
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
to inject into the registry client. The secret must be of type
`kubernetes.io/dockerconfigjson` and must be in the Crossplane installation
namespace, typically `crossplane-system`. One can create the secret using the
following command:

```shell
kubectl -n crossplane-system create secret docker-registry acme-registry-credentials --docker-server=registry1.com --docker-username=<user> --docker-password=<password>
```

## Configuring signature verification

{{<hint "important" >}}
Signature verification is an alpha feature. Enable it with the
`--enable-signature-verification` feature flag.
{{< /hint >}}

You can use `ImageConfig` to configure signature verification for images. When
you enable signature verification, the package manager verifies the signature of
each image before pulling it. If the signature isn't valid, the package manager
rejects the package deployment.

The following example shows the `ImageConfig` resource `verify-acme-packages`.
It configures signature verification for images with these prefixes:
`registry1.com/acme-co/configuration-foo` and
`registry1.com/acme-co/configuration-bar`.


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
from [Sigstore](https://docs.sigstore.dev/). Crossplane initially supports a subset of the Policy Controller configuration
options.
Find these options in the
[API reference]({{<ref "../api/#ImageConfig-spec-verification-cosign">}})
for the `ImageConfig` resource.

When you provide multiple authorities, the package manager verifies the
signature against each authority until it finds a valid one. If any of the
authorities' signatures are valid, the package manager accepts the image.
Similarly, when you provide multiple identities or attestations, the package
manager verifies until it finds a valid match and fails if none of them matches.

Matching the image reference to the `ImageConfig` works similarly to the pull
secret configuration, as described in the previous section.

### Checking the signature verification status

When you enable signature verification, the controller reports the verification
status as a `Verified` condition on package revision resources.
This condition shows whether verification was successful, failed, skipped or
incomplete due to an error.

#### Example conditions

<!-- vale gitlab.SentenceLength = NO -->
**Verification skipped:** The controller skipped signature verification. There
were no matching `ImageConfig` with signature verification configuration.

```yaml
  - lastTransitionTime: "2024-10-23T16:38:51Z"
    reason: SignatureVerificationSkipped
    status: "True"
    type: Verified
```

**Verification successful**

Image signature verified.

```yaml
  - lastTransitionTime: "2024-10-23T16:43:05Z"
    message: Signature verification succeeded with ImageConfig named "verify-acme-packages"
    reason: VerificationSucceeded
    status: "True"
    type: Verified
```

**Verification failed:** Signature verification failed for the image.

```yaml
  - lastTransitionTime: "2024-10-23T16:42:44Z"
    message: 'Signature verification failed with ImageConfig named "verify-acme-packages":
      [signature keyless validation failed for authority verify acme packages
      for registry1.com/acme-co/configuration-foo:v0.2.0: no signatures found: ]'
    reason: SignatureVerificationFailed
    status: "False"
    type: Verified
```

**Verification incomplete:** An error occurred during signature verification.

```yaml
  - lastTransitionTime: "2024-10-23T16:44:22Z"
    message: 'Error occurred during signature verification cannot get image verification
      config: cannot get cosign verification config: no data found for key "cosign.pub"
      in secret "cosign-public-key"'
    reason: SignatureVerificationIncomplete
    status: "False"
    type: Verified
```
<!-- vale gitlab.SentenceLength = YES -->

If you can't see this condition on the package revision resource, namely
`ProviderRevision`, `ConfigurationRevision`, or `FunctionRevision`, ensure that
you enable the feature.

## Rewriting image paths

You can use an `ImageConfig` to pull package images from an alternative location
such as a private registry. `spec.rewriteImages` specifies how to rewrite the
paths of matched images.

Crossplane only supports prefix replacement. Specify the replacement prefix in
`spec.rewriteImage.prefix`. This replaces the matched prefix from `matchImages`.

For example, the following `ImageConfig` replaces `xpkg.crossplane.io` with
`registry1.com` for any image with that prefix.

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
private registry. It allows you to pull a package and all its dependencies from
the same registry. For example, the provider
`xpkg.crossplane.io/crossplane-contrib/provider-aws-s3` has a dependency on
`xpkg.crossplane.io/crossplane-contrib/provider-family-aws`. If you mirror packages to `registry1.com` and install them without an
`ImageConfig`, the package manager still pulls the dependency from
`xpkg.crossplane.io`.
With the preceding `ImageConfig`, the package manager pulls the dependency from
`registry1.com`.

Rewriting an image path with `ImageConfig` doesn't change `spec.package`.
Instead, the rewritten path appears in `status.resolvedPackage`.

Example output:
<!-- vale gitlab.SentenceLength = NO --><!-- vale gitlab.SentenceLength = YES -->

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
Image rewriting is always done before other `ImageConfig` operations.
If you also configure pull secrets or signature verification, those
`ImageConfig` resources must match the rewritten image path.
{{< /hint >}}

For example, if you mirror packages from `xpkg.crossplane.io` to
`registry1.com` and need pull secrets, create two `ImageConfig` resources:

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
event with the reason `ImageConfigSelection`. The event includes the name of the
selected `ImageConfig` and injected pull secret. Find these events on package
and package revision resources. The package manager also updates the
`appliedImageConfigRefs` field in the package status to show the purpose for
which it selected each `ImageConfig`.

For example, the following event and status show the selected `ImageConfig`.
The `ImageConfig` named `acme-packages` provided a pull secret for the
configuration `acme-configuration-foo`:

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

If you can't find the expected event and `appliedImageConfigRefs` entry, check
your configuration. Ensure the prefix of the image reference matches the
`matchImages` list of any `ImageConfig` resources in the cluster.

<!-- vale write-good.Passive = YES -->
