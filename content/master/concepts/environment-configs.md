---
title: Environment Configurations
weight: 90
---

Introduced in v1.11
https://github.com/crossplane/crossplane/pull/3007

{{< hint "note" >}}
EnvironmentConfigs are similar to 
[Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
but support more complex data and are only for Crossplane related objects.
{{< /hint >}}

We are using it successfully as-is.

> Some clarity around the patch ordering in documentation and validation that a patch is just not going to work rather than having it fail silently would be great beta criteria. For example if attempting to patch a composed resource and then trying to use that same field elsewhere as if it were a composite field maybe a validatingAdmissionWebhook could deny it as invalid?

> I agree with that. Documentation should be adjusted accordingly. We were facing the same issue as mentioned above when we were trying to use the CombineFromComposite patch type with a value from a status field that was patched by the FromEnvironmentFieldPath before. There's a comment on this in the docs of FromEnvironmentFieldPath, but it's still confusing since it fails silently. So, I agree with the above. Having some sort of validation would be a good feature.

### environment
**environmentconfigs example in yaml is wrong**
https://github.com/crossplane/docs/issues/380

```
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
```

Docs issue: https://github.com/crossplane/docs/issues/305

Document https://github.com/crossplane/crossplane/issues/3454
issue:
https://github.com/crossplane/crossplane/issues/3770#issuecomment-1454932400

Patch ordering:
https://github.com/crossplane/crossplane/issues/3454

Multiple label select
https://github.com/crossplane/crossplane/pull/3931
https://github.com/crossplane/crossplane/issues/4070


Environments that don't exist fail. 
https://github.com/crossplane/crossplane/issues/3723

Updating the Environment in a Composition won't push down to an XR
https://github.com/crossplane/crossplane/issues/3941

Can't add to a package
https://github.com/crossplane/crossplane/issues/3865
discussion: https://github.com/crossplane/crossplane/pull/3955#pullrequestreview-1377419076

Propagate status from MR to Environmetn
https://github.com/crossplane/crossplane/issues/3926#issuecomment-1579565660


Schema validation
https://github.com/crossplane/crossplane/pull/3937