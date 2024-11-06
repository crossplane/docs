---
title: Image Configs
weight: 400
description: "Image Configs is an API for centralized control of the configuration of Crossplane package images."
---

<!-- vale write-good.Passive = NO -->

`ImageConfig` is an API for centralized control over the configuration of
Crossplane package images. It allows you to configure package manager behavior
for images globally, without needing to be referenced by other objects.

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

### Matching image references

`spec.matchImages` is a list of image references that the `ImageConfig` applies
to. Each item in the list specifies the type and configuration of the image
reference to match. The only supported type is `Prefix`, which matches the
prefix of the image reference. No wildcards are supported. The `type` defaults
to `Prefix` and can be omitted.

When there are multiple `ImageConfigs`  matching an image reference, the one
with the longest matching prefix is selected. If there are multiple
`ImageConfigs` with the same longest matching prefix, one of them is selected
arbitrarily. Please note that this situation occurs only if there are
overlapping prefixes in the `matchImages` lists of different `ImageConfig`
resources, which should be avoided.

### Debugging

When the package manager selects an `ImageConfig` for a package, it throws an
event with the reason `ImageConfigSelection` and the name of the selected
`ImageConfig` and injected pull secret. You can find these events both on the
package and package revision resources.

For example, the following event indicates that the `ImageConfig` named
`acme-packages` was selected for the configuration named `acme-configuration-foo`:

```shell
$ kubectl describe configuration acme-configuration-foo
...
Events:
  Type     Reason                Age                From                                              Message
  ----     ------                ----               ----                                              -------
  Normal   ImageConfigSelection  45s                packages/configuration.pkg.crossplane.io          Selected pullSecret "acme-registry-credentials" from ImageConfig "acme-packages" for registry authentication
```

If you can't find the expected event, ensure the prefix of the image reference
matches the `matchImages` list of any `ImageConfig` resources in the cluster.

## Configuring signature verification

{{<hint "important" >}}
Signature verification is an alpha feature and needs to be enabled with the
`--enable-signature-verification` feature flag.
{{< /hint >}}

You can use `ImageConfig` to configure signature verification for images. When
signature verification is enabled, the package manager verifies the signature of
each image before pulling it. If the signature isn't valid, the package manager
rejects the package deployment.

In the following example, the `ImageConfig` resource named `verify-acme-packages`
is configured to verify the signature of images with the prefixes
`registry1.com/acme-co/configuration-foo` and
`registry1.com/acme-co/configuration-bar`.

In the example below, the `ImageConfig` resource named `verify-acme-packages` is
set up to verify the signatures of images with the prefixes
`registry1.com/acme-co/configuration-foo` and `registry1.com/acme-co/configuration-bar`.

```yaml
apiVersion: pkg.crossplane.io/v1alpha1
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
            url: https://fulcio.sigstore.dev
            identities:
              - issuer: https://token.actions.githubusercontent.com
                subjectRegExp: https://github.com/acme-co/crossplane-packages/*
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
[API reference](https://docs.crossplane.io/master/api/#ImageConfig-spec-verification-cosign)
for the `ImageConfig` resource together with their descriptions.

When multiple authorities are provided, the package manager verifies the
signature against each authority until it finds a valid one. If any of the
authorities' signatures are valid, the package manager accepts the image.
Similarly, when multiple identities or attestations are provided, the package
manager verifies until it finds a valid match and fails if none of them matches.

Matching the image reference to the `ImageConfig` works similarly to the pull
secret configuration, as described in the previous section.

### Checking the signature verification status

When signature verification is enabled, the respective controller reports the
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
the feature is enabled.

<!-- vale write-good.Passive = YES -->