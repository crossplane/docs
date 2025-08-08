---
title: Implementing safe-start in Providers
weight: 160
description: Guide for provider developers to implement safe-start capability
---

This guide shows provider developers how to implement safe-start capability in 
their Crossplane providers. safe-start enables selective resource activation 
through Managed Resource Definitions (MRDs), improving performance and resource 
management.

{{< hint "important" >}}
safe-start requires Crossplane v2.0+ and involves significant provider changes. 
Plan for breaking changes and thorough testing before implementing.
{{< /hint >}}

## What safe-start provides

safe-start transforms how your provider handles resource installation:

**Without safe-start:**
- All resources become MRDs that are automatically active and create CRDs
- Users get all ~100 resources even if they need only 5
- Higher memory usage and slower API server responses

**With safe-start:**
- All resources become MRDs that are inactive by default
- Users activate only needed resources through policies
- Lower resource overhead and better performance

## Prerequisites

Before implementing safe-start, ensure you have:

* Provider built with `crossplane-runtime` v2.0+
* Understanding of [MRDs and activation policies]({{< ref "mrd-activation-policies" >}})
* Test environment with Crossplane v2.0+
* CI/CD pipeline that can build and test provider changes

## Implementation steps

### Step 1: Update Provider Metadata

Declare safe-start capability in your provider package metadata:

```yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-example
spec:
  package: registry.example.com/provider-example:v1.0.0
  capabilities:
  - safe-start
```

{{< hint "tip" >}}
Crossplane supports flexible capability matching. `safe-start`, `safestart`, 
and `safe-start` are all recognized as the same capability.
{{< /hint >}}

### Step 2: Update RBAC Permissions

safe-start providers need extra permissions to manage CRDs dynamically. Crossplane's RBAC manager automatically provides these permissions when you install safe-start providers.

{{< hint "note" >}}
Manual RBAC configuration is only required if you disable Crossplane's RBAC manager (with `--args=--disable-rbac-manager`).
{{< /hint >}}

**Automatically provided permissions:**
```yaml
# Crossplane RBAC manager grants these permissions automatically
# safe-start permissions
- apiGroups: ["apiextensions.k8s.io"]
  resources: ["customresourcedefinitions"]
  verbs: ["get", "list", "watch"]
```

**Manual configuration (only if you disable RBAC manager):**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: provider-example-system
rules:
# Existing provider permissions
- apiGroups: [""]
  resources: ["events"]
  verbs: ["create", "update", "patch"]
- apiGroups: ["example.crossplane.io"]
  resources: ["*"]
  verbs: ["*"]

# safe-start permissions
- apiGroups: ["apiextensions.k8s.io"]
  resources: ["customresourcedefinitions"]
  verbs: ["get", "list", "watch"]
```

## Testing safe-start implementation

### Integration testing

Test safe-start behavior in a real cluster:

```shell
#!/bin/bash
set -e

echo "Starting safe-start integration test..."

# Install Crossplane v2.0
kubectl create namespace crossplane-system
helm install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --version v2.0.0 \
  --wait

# Install provider with safe-start
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-example
spec:
  package: registry.example.com/provider-example:latest
EOF

# Wait for provider installation
kubectl wait --for=condition=Healthy provider/provider-example --timeout=300s

# Verify MRDs created but inactive
echo "Checking MRD states..."
MRD_COUNT=$(kubectl get mrds --no-headers | wc -l)
INACTIVE_COUNT=$(kubectl get mrds -o jsonpath='{.items[*].spec.state}' | grep -o "Inactive" | wc -l)

if [ "$MRD_COUNT" -eq "$INACTIVE_COUNT" ]; then
    echo "✓ All MRDs are inactive as expected"
else
    echo "✗ Some MRDs are unexpectedly active"
    exit 1
fi

# Test activation policy
kubectl apply -f - <<EOF  
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: test-policy
spec:
  activations:
  - "databases.rds.aws.example.io"
EOF

# Wait for activation
sleep 10

# Verify activation worked
ACTIVE_COUNT=$(kubectl get mrd databases.rds.aws.example.io -o jsonpath='{.spec.state}' | grep -o "Active" | wc -l)
if [ "$ACTIVE_COUNT" -eq "1" ]; then
    echo "✓ MRD activation successful"
else
    echo "✗ MRD activation failed"
    exit 1
fi

# Test resource creation
kubectl apply -f - <<EOF
apiVersion: rds.aws.example.io/v1alpha1
kind: Database
metadata:
  name: test-db
  namespace: default
spec:
  forProvider:
    engine: postgres
    region: us-east-1
EOF

# Verify resource creation
kubectl wait --for=condition=Ready database/test-db --timeout=300s --namespace default

echo "✓ safe-start integration test passed"
```

## Migration considerations

### For existing users

When you add safe-start to an existing provider:

**Breaking change considerations:**
- Existing installations continue to work (backward compatibility)
- New installations have inactive MRDs by default
- Users need activation policies for new installations

**Migration strategy:**
```yaml
# Provide migration documentation like:
# For users upgrading to safe-start-enabled provider v2.0:

# 1. Existing resources continue working unchanged
# 2. For new installations, create activation policy:
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: legacy-compatibility
spec:
  activations:
  - "*.aws.example.io"  # Activate all resources (legacy behavior)
```

## Troubleshooting

### Common Issues

**MRDs not activating:**
```shell
# Check activation policy exists and matches
kubectl get mrap
kubectl describe mrap my-policy

# Verify MRD exists  
kubectl get mrd my-resource.provider.example.io
kubectl describe mrd my-resource.provider.example.io
```

**CRDs not created:**
```shell
# Check MRD controller logs
kubectl logs -n crossplane-system deployment/provider-example

# Verify RBAC permissions
kubectl auth can-i create customresourcedefinitions --as=system:serviceaccount:crossplane-system:provider-example
```

**Resource creation fails:**
```shell
# Verify MRD is active
kubectl get mrd my-resource.provider.example.io -o jsonpath='{.spec.state}'

# Check if CRD exists
kubectl get crd my-resource.provider.example.io

# Look for controller errors
kubectl describe my-resource my-instance
```

## Best practices

### Performance optimization
- Start with inactive MRDs for providers with >20 resources
- Document recommended activation patterns for common use cases
- Provide environment-specific activation policy examples

### User experience
- Include helpful error messages when resources aren't activated
- Provide clear migration guides for existing users
- Document connection details

### Testing strategy  
- Test both with and without safe-start in CI
- Verify activation/deactivation cycles work
- Test resource creation after activation
