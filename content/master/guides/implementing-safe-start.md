---
title: Implementing safe-start in Providers  
weight: 90
state: alpha
alphaVersion: 2.0
description: Guide for provider developers to add safe-start capability for
  selective resource activation
---

This guide shows provider developers how to implement safe-start capability in
their Crossplane providers. safe-start enables
[disabling unused managed resources]({{<ref "disabling-unused-managed-resources">}})
through ManagedResourceDefinitions, improving performance and reducing resource
overhead.

{{<hint "important">}}
safe-start requires Crossplane v2.0+ and crossplane-runtime v2.0+.
Implementing safe-start involves code changes that affect provider startup
behavior.
{{</hint>}}

## What safe-start provides

safe-start changes how your provider handles CRD installation:

**Without safe-start:**
- Providers create all managed resource CRDs when installed
- Users get all resources even if they only need one or two
- Higher memory usage and API server load

**With safe-start:**
- Providers create ManagedResourceDefinitions but CRDs only when activated
- Users activate only needed resources through ManagedResourceActivationPolicies
- Significant reduction in cluster resource overhead

## Prerequisites

Before implementing safe-start:

- Provider built with crossplane-runtime v2.0+
- Understanding of
  [ManagedResourceDefinitions]({{<ref "../managed-resources/managed-resource-definitions">}})
- Test environment with Crossplane v2.0+

## Implementation steps

### Step 1: Declare safe-start capability

Add safe-start to your provider package metadata:

```yaml
# package/crossplane.yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-example
spec:
  capabilities:
  - safe-start
```

### Step 2: Add required imports

Update your main.go imports (see
[crossplane-runtime godoc](https://pkg.go.dev/github.com/crossplane/crossplane-runtime/v2)
for full API reference):

```go
import (
    // existing imports...
    
    "k8s.io/apimachinery/pkg/runtime/schema"
    apiextensionsv1 "k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1"
    
    "github.com/crossplane/crossplane-runtime/v2/pkg/controller"
    "github.com/crossplane/crossplane-runtime/v2/pkg/gate"
    "github.com/crossplane/crossplane-runtime/v2/pkg/reconciler/customresourcesgate"
)
```

### Step 3: Initialize the gate

Add gate initialization in your main function:

```go
func main() {
    // existing setup code...
    
    o := controller.Options{
        // existing options...
        Gate: new(gate.Gate[schema.GroupVersionKind]),
    }
    
    // Add CustomResourceDefinition to scheme for gate controller
    if err := apiextensionsv1.AddToScheme(mgr.GetScheme()); err != nil {
        panic(err)
    }
    
    // Setup controllers
    if err := yourprovider.Setup(mgr, o); err != nil {
        panic(err)
    }
        
    // Setup the CRD gate controller  
    if err := customresourcesgate.Setup(mgr, o); err != nil {
        panic(err)
    }
        
    // start manager...
}
```

### Step 4: Use gated controller setup

Create a gated setup function for each managed resource controller:

```go
// SetupGated registers controller setup with the gate, waiting for the
// required CRD
func SetupGated(mgr ctrl.Manager, o controller.Options) error {
    o.Gate.Register(func() {
        if err := Setup(mgr, o); err != nil {
            panic(err)
        }
    }, v1alpha1.MyResourceGroupVersionKind)
    return nil
}

// Setup is your existing controller setup function (unchanged)
func Setup(mgr ctrl.Manager, o controller.Options) error {
    // existing controller setup code...
}
```

### Step 5: Update controller registration

Change your controller setup to use the gated versions:

```go
// internal/controller/controller.go
func Setup(mgr ctrl.Manager, o controller.Options) error {
    for _, setup := range []func(ctrl.Manager, controller.Options) error{
        myresource.SetupGated,  // Changed from myresource.Setup
        // other gated setups...
    } {
        if err := setup(mgr, o); err != nil {
            return err
        }
    }
    return nil
}
```

## Implementation details

The safe-start implementation uses a "gate" pattern:

1. **Gate initialization**: Creates a gate that tracks CRD readiness
2. **Controller registration**: Controllers register with the gate, specifying
   which CRDs they need
3. **CRD monitoring**: The `customresourcesgate` controller watches for CRD
   creation/deletion
4. **Delayed startup**: Controllers only start when their required CRDs
   become active

## Testing your implementation

Test safe-start behavior with this basic workflow:

```shell
# Install Crossplane v2.0+
helm install crossplane crossplane-stable/crossplane \
  --namespace crossplane-system \
  --set provider.defaultActivations={}

# Install your provider  
kubectl apply -f provider.yaml

# Check that MRDs are created but inactive
kubectl get mrds
# All should show STATE: Inactive

# No CRDs should exist yet
kubectl get crds | grep yourprovider.io
# Should return no results

# Create activation policy
kubectl apply -f - <<EOF
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: test-activation
spec:
  activate:
  - "myresource.yourprovider.io"
EOF

# Verify activation worked
kubectl get mrd myresource.yourprovider.io
# Should show STATE: Active

# CRD should now exist
kubectl get crd myresource.yourprovider.io
```

## Troubleshooting

### Controllers never start
**Cause**: gate waits for CRDs that never become active.

<!-- vale Google.WordList = NO -->
**Solution**: check that Crossplane activated MRDs and created CRDs:
<!-- vale Google.WordList = YES -->
```shell
kubectl get mrds -o wide
kubectl describe mrap <activation-policy-name>
```

<!-- vale Google.Headings = NO -->
### CRDs don't appear
<!-- vale Google.Headings = YES -->
<!-- vale Google.Colons = NO -->
**Cause**: MRDs might not activate or activation policy doesn't match.
<!-- vale Google.Colons = YES -->

**Solution**: verify activation policy patterns match MRD names:
```shell
kubectl get mrds
kubectl get mrap -o yaml
```

## Migration considerations

When adding safe-start to existing providers:

- **Existing installations**: Continue working as expected (no CRD changes)
- **New installations**: Start with inactive MRDs, require activation policies

## Next steps

- Test your safe-start implementation with different activation patterns
- Update provider documentation to explain activation requirements  
- Consider the user experience for providers that now require activation
  policies

Learn more about the user experience in
[disabling unused managed resources]({{<ref "disabling-unused-managed-resources">}}).
