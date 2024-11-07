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

<!-- vale write-good.Passive = YES -->