---
title: Server-Side Apply
state: alpha
alphaVersion: "1.15"
weight: 300
---

Crossplane can use server-side apply to sync claims with composite resources
(XRs), and to sync composite resources with composed resources.

When Crossplane uses server-side apply, the Kubernetes API server helps sync
resources. Using server-side apply makes syncing more predictable and less
buggy.

{{<hint "tip">}}
Server-side apply is a Kubernetes feature. Read more about server-side apply in
the [Kubernetes documentation](https://kubernetes.io/docs/reference/using-api/server-side-apply/).
{{</hint>}}

## Use server-side apply to sync claims with composite resources

When you create a claim, Crossplane creates a corresponding composite resource.
Crossplane keeps the claim in sync with the composite resource. When you change
the claim, Crossplane reflects those changes on the composite resource.

Read the [claims documentation]({{<ref "./claims">}}) to learn more about claims
and how they relate to composite resources.

Crossplane can use server-side apply to keep the claim in sync with the
composite resource.

Use the `--enable-ssa-claims` feature flag to enable using server-side apply.
Read the [Install Crossplane documentation]({{<ref "../software/install#feature-flags">}})
to learn about feature flags.

If you see fields reappearing after you delete them from a claim's `spec`,
enable server-side apply to fix the problem. Enabling server-side apply also
fixes the problem where Crossplane doesn't delete labels and annotations from
the composite resource when you delete them from the claim.

{{<hint "important">}}
When you enable server-side apply, Crossplane is stricter about how it syncs
a claim with its counterpart composite resource:

- The claim's `metadata` syncs to the composite resource's `metadata`.
- The claim's `spec` syncs to the composite resource's `spec`.
- The composite resource's `status` syncs to the claim's `status`.

When you enable server-side apply Crossplane doesn't sync the composite resource's `metadata`
and `spec` back to the claim's `metadata` and `spec`. It also doesn't sync the
claim's `status` to the composite resource's `status`.
{{</hint>}}

## Use server-side apply to sync claims end-to-end

To get the full benefit of server-side apply, use the `--enable-ssa-claims`
feature flag together with composition functions.

When you use composition functions, Crossplane uses server side apply to sync
composite resources with composed resources. Read more about this in the
[composition functions documentation]({{<ref "./composition-functions#how-composition-functions-work">}}).

```mermaid
graph LR
  A(Claim) -- claim server-side apply --> B(Composite Resource)
  B -- function server-side apply --> C(Composed Resource)
  B -- function server-side apply --> D(Composed Resource)
  B -- function server-side apply --> E(Composed Resource)
```

When you use server-side apply end-to-end there is a clear, predictable
propagation of fields from claim to composed resources, and back:

* `metadata` and `spec` flow forwards, from claim to XR to composed resources.
* `status` flows backwards, from composed resources to XR to claim.

{{<hint "important">}}
When you use composition functions, Crossplane is stricter about how it syncs
composite resources (XRs) with composed resources:

- The XR's `metadata` syncs to the composed resource's `metadata`.
- The XR's `spec` syncs to the composed resource's `spec`.
- The composed resource's `status` syncs to the XR's `status`.

When you use composition functions Crossplane doesn't sync the composed resource's `metadata`
and `spec` back to the XR's `metadata` and `spec`.
{{</hint>}}

When Crossplane uses server-side apply end-to-end to sync claims with composed
resources, it deletes fields from a composed resource's `spec` when you
delete fields from the claim's `spec`.

When Crossplane uses server-side apply end-to-end it's also able to merge claim
fields into complex composed resource fields. Objects and arrays of objects are
examples of complex composed resource fields.

{{<hint "tip">}}
Crossplane can only merge complex fields for resources that use server-side
apply merge strategy OpenAPI extensions. Read about these extensions in the
Kubernetes [server-side apply documentation](https://kubernetes.io/docs/reference/using-api/server-side-apply/#merge-strategy).

If you find that Crossplane isn't merging managed resource fields, raise an
issue against the relevant provider. Ask the provider maintainer to add
server-side apply merge strategy extensions to the managed resource.
{{</hint>}}