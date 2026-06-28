---
title: Change Provider Registries
weight: 415
description: "Change from one provider to a compatible provider in a different registry"
---

When you change a provider's OCI reference to a different registry, Crossplane 
updates the provider itself with a new revision. Crossplane treats any 
**dependencies it automatically installs** (like family providers) as entirely 
separate packages. These require careful coordination.

This problem affects:

* **Providers with family dependencies**: Most cloud providers depend on a 
  family provider (like `provider-gcp-compute` depending on `provider-family-gcp`)
* **Providers installed as Configuration dependencies**: When a Configuration 
  package lists providers as dependencies

**Single providers without dependencies change automatically** - no manual 
intervention needed.

The most common conflict occurs with **family provider dependencies**. For 
example, when changing `provider-gcp-compute` from Upbound to Crossplane 
Contrib, both versions depend on different family providers:

* Old: `xpkg.upbound.io/upbound/provider-gcp-compute` → depends on `upbound/provider-family-gcp`
* New: `xpkg.crossplane.io/crossplane-contrib/provider-gcp-compute` → depends on `crossplane-contrib/provider-family-gcp`

This creates two active family providers competing for the same resources, 
causing errors like:

```console
cannot establish control of object: providerconfigusages.gcp.upbound.io is already controlled by ProviderRevision upbound-provider-family-gcp-f0aa3640a6a9
```

## Prerequisites

Before changing providers, ensure:

* Crossplane v2.0 or later
* `kubectl` access to your cluster
* Understanding of your current provider setup
* Time for testing and validation
* Backup of critical resources

{{<hint "tip">}}
Test this change in a staging environment first. The process is safe but 
requires careful verification at each step.
{{</hint>}}

## Why manual coordination works best

Crossplane names package dependencies using OCI repository paths. It uses the
pattern `<org>-<repo>`. When you change from `upbound/provider-gcp-compute` to
`crossplane-contrib/provider-gcp-compute`, Crossplane sees these as separate
providers and creates both:

* `upbound-provider-family-gcp` (old, still active)
* `crossplane-contrib-provider-family-gcp` (new, requires ownership coordination)

Both family providers manage the same CRDs and MRDs, requiring careful 
coordination of ownership transfer. 

Crossplane takes this approach because determining package equivalence is 
complex. For example, an older Upbound provider version might differ from a 
newer Crossplane Contrib version - with more CRDs, different controller 
behavior, or updated APIs. Automatically replacing dependencies could break 
existing resources or introduce unexpected behavior.

Manual coordination gives you explicit control to transition ownership 
from old to new providers with full visibility into each step.

## Process overview

The manual process follows this safe sequence:

1. **Update provider package** - Change the provider's OCI reference
2. **Identify conflicts** - Find which family provider has conflicts
3. **Set manual activation** - Prevent the old family provider from staying active
4. **Deactivate old revision** - Stop the old family provider from managing resources
5. **Verify transition** - Ensure the new family provider manages all resources
6. **Clean up** - Remove the old family provider

This deliberate approach gives you full control over the timing and 
validation, prevents orphaning resources, and provides clear rollback 
points.

## Step-by-step process

This example changes from Upbound's GCP Compute provider to the Crossplane 
community version, which demonstrates the family provider dependency issue:

* **From**: `xpkg.upbound.io/upbound/provider-gcp-compute:v1.14.1`
* **To**: `xpkg.crossplane.io/crossplane-contrib/provider-gcp-compute:v2.0.0`

This change requires coordinating multiple package dependencies because each 
version depends on a different family provider.

### Step 1: Inventory current providers

Check your current provider setup:

```shell
kubectl get providers
```

```console
NAME                        INSTALLED   HEALTHY   PACKAGE                                                   AGE
upbound-provider-family-gcp True        True      xpkg.upbound.io/upbound/provider-family-gcp:v1.14.1     30d
provider-gcp-compute        True        True      xpkg.upbound.io/upbound/provider-gcp-compute:v1.14.1    30d
```

List managed resources to understand what the provider manages:

```shell
kubectl get managed
```

```console
NAME                                           READY   SYNCED   EXTERNAL-NAME           AGE
address.compute.gcp.upbound.io/my-address     True    True     my-address-abc123       5d
```

### Step 2: Update the provider package

Edit the existing provider to change its package reference:

```shell
kubectl patch provider provider-gcp-compute --type=merge \
  -p='{"spec":{"package":"xpkg.crossplane.io/crossplane-contrib/provider-gcp-compute:v2.0.0"}}'
```

This creates a new family provider dependency. Check what providers exist:

```shell
kubectl get providers
```

```console
NAME                                     INSTALLED   HEALTHY   PACKAGE                                                             AGE
crossplane-contrib-provider-family-gcp   True        False     xpkg.crossplane.io/crossplane-contrib/provider-family-gcp:v2.0.0    2m
upbound-provider-family-gcp              True        True      xpkg.upbound.io/upbound/provider-family-gcp:v1.14.1                30d
provider-gcp-compute                     True        True      xpkg.crossplane.io/crossplane-contrib/provider-gcp-compute:v2.0.0   2m
```

Notice the new family provider is `HEALTHY=False` due to the ownership conflict.

### Step 3: Set old family provider to manual activation

Prevent the old family provider from automatically activating its revisions:

```shell
kubectl patch provider upbound-provider-family-gcp --type=merge \
  -p='{"spec":{"revisionActivationPolicy":"Manual"}}'
```

Verify the change:

```shell
kubectl get provider upbound-provider-family-gcp -o yaml | grep revisionActivationPolicy
```

```console
  revisionActivationPolicy: Manual
```

### Step 4: Deactivate old family provider revision

Find the current revision of the old family provider:

```shell
kubectl get providerrevisions | grep upbound-provider-family-gcp
```

```console
NAME                                    HEALTHY   REVISION   IMAGE                                                     STATE    DEP-FOUND   DEP-INSTALLED   AGE
upbound-provider-family-gcp-f0aa3640a6a9 True      1          xpkg.upbound.io/upbound/provider-family-gcp:v1.14.1     Active   0           0               30d
```

Set the old family provider revision to inactive:

```shell
kubectl patch providerrevision upbound-provider-family-gcp-f0aa3640a6a9 --type=merge \
  -p='{"spec":{"desiredState":"Inactive"}}'
```

### Step 5: Verify the new family provider becomes healthy

Check that the new family provider can now establish control:

```shell
kubectl get providers
```

```console
NAME                                     INSTALLED   HEALTHY   PACKAGE                                                             AGE
crossplane-contrib-provider-family-gcp   True        True      xpkg.crossplane.io/crossplane-contrib/provider-family-gcp:v2.0.0    5m
upbound-provider-family-gcp              True        True      xpkg.upbound.io/upbound/provider-family-gcp:v1.14.1                30d
provider-gcp-compute                     True        True      xpkg.crossplane.io/crossplane-contrib/provider-gcp-compute:v2.0.0   5m
```

Verify the old family provider revision is inactive:

```shell
kubectl get providerrevisions | grep upbound-provider-family-gcp
```

```console
NAME                                    HEALTHY   REVISION   IMAGE                                                     STATE      DEP-FOUND   DEP-INSTALLED   AGE
upbound-provider-family-gcp-f0aa3640a6a9 True      1          xpkg.upbound.io/upbound/provider-family-gcp:v1.14.1     Inactive   0           0               30d
```

Check that managed resources are still healthy:

```shell
kubectl get managed
```

```console
NAME                                           READY   SYNCED   EXTERNAL-NAME           AGE
address.compute.gcp.upbound.io/my-address     True    True     my-address-abc123       5d
```

### Step 6: Delete the old family provider

After verifying everything works, remove the old family provider:

```shell
kubectl delete provider upbound-provider-family-gcp
```

### Step 7: Final verification

Confirm only the new providers remain:

```shell
kubectl get providers
```

```console
NAME                                     INSTALLED   HEALTHY   PACKAGE                                                             AGE
crossplane-contrib-provider-family-gcp   True        True      xpkg.crossplane.io/crossplane-contrib/provider-family-gcp:v2.0.0    10m
provider-gcp-compute                     True        True      xpkg.crossplane.io/crossplane-contrib/provider-gcp-compute:v2.0.0   10m
```

Verify managed resources are still healthy:

```shell
kubectl get managed
```

```console
NAME                                           READY   SYNCED   EXTERNAL-NAME           AGE
address.compute.gcp.upbound.io/my-address     True    True     my-address-abc123       5d
```

## Other common scenarios

### Providers without dependencies

For providers that don't depend on other packages (like `provider-helm`, 
`provider-kubernetes`, or standalone providers), the change happens automatically:

1. Update the provider's `spec.package`
2. Crossplane creates a new revision with the new package
3. The old revision automatically becomes inactive
4. No conflicts occur because there are no dependencies

Examples of providers that typically change automatically:

* `provider-helm`
* `provider-kubernetes` 
* `provider-sql`

{{<hint "tip">}}
<!-- vale Google.WordList = NO -->
You can check which providers have dependencies by inspecting the package lock:
<!-- vale Google.WordList = YES -->

```shell
kubectl get lock lock -o yaml
```

Look for providers with non-empty `dependencies` arrays. For example:
```yaml
- name: provider-gcp-compute-a41e4ba551fc
  dependencies:
  - constraints: '>= 0.0.0'
    package: xpkg.crossplane.io/crossplane-contrib/provider-family-gcp
    type: Provider
```

Providers with empty `dependencies: []` change automatically.
{{</hint>}}

### Configuration package dependencies

When changing providers that are dependencies of Configuration packages, the 
same conflicts can occur. The Configuration creates provider dependencies based 
on OCI references, so changing registries creates duplicate providers.

To change providers in this scenario:
1. Update the Configuration's package OCI reference
2. Follow the same manual coordination steps for any conflicted providers
3. Verify all providers the Configuration depends on are healthy

### Rollback procedure

If you need to rollback during the process:

1. **Before deleting the old provider (step 6)**: Reactivate the old family 
   provider revision:
   ```shell
   kubectl patch providerrevision upbound-provider-family-gcp-f0aa3640a6a9 --type=merge \
     -p='{"spec":{"desiredState":"Active"}}'
   ```
   
   Then deactivate the new family provider revision and delete the new provider.

2. **After deleting the old provider**: You must recreate the old provider 
   because Crossplane automatically deletes all revisions when you delete a 
   provider. Create this manifest:
   
   ```yaml
   apiVersion: pkg.crossplane.io/v1
   kind: Provider
   metadata:
     name: upbound-provider-family-gcp
   spec:
     package: xpkg.upbound.io/upbound/provider-family-gcp:v1.14.1
   ```
   
   Save as `rollback-provider.yaml` and apply:
   ```shell
   kubectl apply -f rollback-provider.yaml
   ```
   
   Then follow the process in reverse to switch back.

## Troubleshooting

### New family provider stays unhealthy

If the new family provider remains `HEALTHY=False` after deactivating the old one:

1. Check the provider revision status:
   ```shell
   kubectl get providerrevisions | grep crossplane-contrib-provider-family
   ```

2. Look for ownership conflict errors in the provider logs:
   ```shell
   kubectl logs -n crossplane-system -l pkg.crossplane.io/provider=crossplane-contrib-provider-family-gcp
   ```

3. Verify the old revision is truly inactive:
   ```shell
   kubectl describe providerrevision upbound-provider-family-gcp-f0aa3640a6a9
   ```

### Ownership conflicts persist

If you see persistent ownership conflicts:

```console
cannot establish control of object: providerconfigusages.gcp.upbound.io is already controlled by ProviderRevision upbound-provider-family-gcp-f0aa3640a6a9
```

<!-- vale Google.WordList = NO -->
This means the old revision is still active. Double-check:
<!-- vale Google.WordList = YES -->

1. The old provider has `revisionActivationPolicy: Manual`
2. The old revision has `desiredState: Inactive`
3. Wait a moment for the change to propagate

### Provider doesn't deactivate

If the old provider revision doesn't become inactive:

<!-- vale Google.WordList = NO -->
1. Check for active managed resources preventing deactivation
<!-- vale Google.WordList = YES -->
2. Verify the patch command succeeded
3. Check provider logs for errors:
<!-- vale Google.WordList = YES -->
   ```shell
   kubectl logs -n crossplane-system -l pkg.crossplane.io/provider=upbound-provider-family-gcp
   ```

## Next steps

After successfully changing providers:

* Update any documentation referencing the old provider
* Consider changing to v2 namespaced resources if using Crossplane v2
* Review other providers for potential registry changes
* Share your experience with the Crossplane community

For more information:
* [Provider documentation]({{<ref "../packages/providers">}})
* [Troubleshooting guide]({{<ref "troubleshoot-crossplane">}})
* [Crossplane community](https://crossplane.io/community/)
