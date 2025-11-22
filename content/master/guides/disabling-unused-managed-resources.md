---
title: Disabling Unused Managed Resources
weight: 85
state: alpha
alphaVersion: 2.0
description: Reduce CRD overhead by disabling unused managed resources
---

{{<hint "important">}}
This guide uses
[managed resource definitions]({{<ref "../managed-resources/managed-resource-definitions">}})
and
[managed resource activation policies]({{<ref "../managed-resources/managed-resource-activation-policies">}}),
which Crossplane v2.0+ enables by default. To disable this behavior, set
`--enable-custom-to-managed-resource-conversion=false` when installing
Crossplane.
{{</hint>}}

Large Crossplane providers can install 100+ managed resource CRDs. This
consumes significant cluster resources even when you only need one or two
resource types. This guide shows how to use
[ManagedResourceDefinitions]({{<ref "../managed-resources/managed-resource-definitions">}})
and
[ManagedResourceActivationPolicies]({{<ref "../managed-resources/managed-resource-activation-policies">}})
to install only the provider resources you need.

## Before you begin

This guide requires:

- Crossplane v2.0+ installed in your cluster
- A provider with `safe-start` capability (this guide uses
  `provider-aws-ec2:v2.0.0`)
- Basic familiarity with Kubernetes and Crossplane concepts

{{<hint "important">}}
ManagedResourceDefinitions and ManagedResourceActivationPolicies are alpha
features in Crossplane v2.0+.
{{</hint>}}

## The problem: Resource overhead

Installing a large cloud provider in Crossplane creates hundreds of CRDs:

```shell
# Before selective activation - provider-aws-ec2 installs ~200 CRDs
kubectl get crds | grep aws.crossplane.io | wc -l
# Output: 200

# Each CRD consumes ~3 MiB of API server memory
# 200 CRDs × 3 MiB = 600 MiB of memory usage
```

Most users only need a small subset of these resources. Selective activation
lets you install just what you need.

## Step 1: Disable automatic activation

The Crossplane Helm chart creates an activation policy by default. This policy
enables all provider resources. To use selective activation, disable this
default behavior.

### Option A: Helm installation

```shell
helm install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --set provider.defaultActivations={}
```

### Option B: Existing installation

Delete the default activation policy:

```shell
kubectl delete managedresourceactivationpolicy default
```

## Step 2: Install your provider

Install your provider as usual. Crossplane automatically converts the
provider's CRDs to ManagedResourceDefinitions:

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-ec2
spec:
  package: xpkg.crossplane.io/provider-aws-ec2:v2.0.0
```

Save this as `provider.yaml` and apply it:

```shell
kubectl apply -f provider.yaml

# Wait for provider to be ready
kubectl wait --for=condition=Healthy provider/provider-aws-ec2 --timeout=5m
```

## Step 3: Verify Crossplane created MRDs

<!-- vale Google.WordList = NO -->
After the provider installs, check the ManagedResourceDefinitions. Crossplane
creates them in an inactive state:
<!-- vale Google.WordList = YES -->

```shell
# List ManagedResourceDefinitions
kubectl get managedresourcedefinitions

# Check their states (should be "Inactive")
kubectl get mrds -o jsonpath='{.items[*].spec.state}' \
  | tr ' ' '\n' | sort | uniq -c
# 200 Inactive
```

Notice that Crossplane didn't create any CRDs yet:

```shell
kubectl get crds | grep ec2.aws.m.crossplane.io
# No output - CRDs don't exist until MRDs are activated
```

## Step 4: Create an activation policy

Create a ManagedResourceActivationPolicy to selectively activate only the
resources you need:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: my-app-resources
spec:
  activate:
  - instances.ec2.aws.m.crossplane.io        # EC2 instances for compute
  - securitygroups.ec2.aws.m.crossplane.io   # Security groups for networking
  - vpcs.ec2.aws.m.crossplane.io             # VPCs for isolation
```

Save this as `activation-policy.yaml` and apply it:

```shell
kubectl apply -f activation-policy.yaml
```

## Step 5: Verify selective activation

<!-- vale Google.WordList = NO -->
Check that Crossplane activated only the specified resources:
<!-- vale Google.WordList = YES -->

```shell
# Check MRD states - only some should be Active now
kubectl get mrds \
  -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.state}{"\n"}{end}' \
  | grep Active
# instances.ec2.aws.m.crossplane.io: Active
# securitygroups.ec2.aws.m.crossplane.io: Active
# vpcs.ec2.aws.m.crossplane.io: Active

# Verify Crossplane created corresponding CRDs
kubectl get crds | grep ec2.aws.m.crossplane.io
# instances.ec2.aws.m.crossplane.io
# securitygroups.ec2.aws.m.crossplane.io
# vpcs.ec2.aws.m.crossplane.io

# Count CRDs from EC2 provider - should match activated MRDs
kubectl get crds | grep ec2.aws.m.crossplane.io | wc -l
# 3 (only the activated resources)
```

## Step 6: Measure the impact

Check the significant reduction in resource overhead:

```shell
# Count CRDs from EC2 provider - should be much lower than 200
kubectl get crds | grep aws.crossplane.io | wc -l
# 3 CRDs (99% reduction from 200)

# Calculate memory savings
echo "197 CRDs saved × 3 MiB = 591 MiB saved (99% reduction)"

# Verify inactive MRDs still exist but consume minimal resources
kubectl get mrds \
  -o jsonpath='{.items[?(@.spec.state=="Inactive")]..metadata.name}' | wc -w
# 197 inactive MRDs (~20 MiB total overhead vs 600 MiB for active CRDs)

# Check total MRDs (active + inactive)
kubectl get mrds | wc -l
# 200 total MRDs (3 active, 197 inactive)
```

Selective activation provides massive resource savings. It maintains full
capability for the resources you use.

## Next steps

- Learn more about
  [ManagedResourceDefinitions]({{<ref "../managed-resources/managed-resource-definitions">}})
  for detailed concepts and troubleshooting
- Explore
  [ManagedResourceActivationPolicies]({{<ref "../managed-resources/managed-resource-activation-policies">}})
  for advanced activation strategies and best practices
- Check the [API reference]({{<ref "../api">}}) for complete schema
  documentation
