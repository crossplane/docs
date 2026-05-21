---
title: Feature Lifecycle
toc: true
weight: 309
indent: true
description: "Crossplane's feature development process"
---

# Feature lifecycle

Crossplane follows a similar feature lifecycle to [upstream
Kubernetes][kube-features]. Crossplane adds all major new features in alpha. Alpha
features graduate to beta, and then to general
availability (GA). Features that languish at alpha or beta may be subject to
deprecation.

## Alpha features

Alpha features are off by default, and you must enable them by a feature flag, for example
`--enable-composition-revisions`. API types for alpha features use a
`vNalphaN` style API version, like `v1alpha`. **Alpha features are subject to
removal or breaking changes without notice**, and aren't considered ready
for use in production. 

<!-- vale alex.Condescending = NO -->
Sometimes alpha features require Crossplane to add fields to existing beta or GA
API types. In these cases you must mark fields (for instance in their OpenAPI
schema) as alpha and subject to alpha API constraints (or lack thereof).
<!-- vale alex.Condescending = YES -->

All alpha features should have an issue tracking their graduation to beta.

## Beta features

Beta features are on by default, but you may disable them by a feature flag. API
types for beta features use a `vNbetaN` style API version, like
`v1beta1`. Crossplane considers beta features to be well tested, and doesn't
removed without Crossplane marking them deprecated for at least two releases.

The schema and/or semantics of objects may change in incompatible ways in a
later beta or stable release. When this happens, the team provides
instructions for migrating to the next version. This may require deleting,
editing, and recreating API objects. The editing process may require some
thought. This may require downtime for applications that rely on the feature.

<!-- vale alex.Condescending = NO -->
Sometimes beta features require Crossplane to add fields to existing GA API types. In
these cases you must mark fields (for instance in their OpenAPI schema) as beta
and subject to beta API constraints (or lack thereof).
<!-- vale alex.Condescending = YES -->

All beta features should have an issue tracking their graduation to GA.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## GA features
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

GA features are always enabled - you can't disable them. API types pertaining
to GA features use `vN` style API versions, like `v1`. GA features are widely
used and well tested. They guarantee API stability - Crossplane only allows backward
compatible changes.

[kube-features]: https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/#feature-stages