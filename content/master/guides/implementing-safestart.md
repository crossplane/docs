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
- Users get all ~200 AWS resources even if they need only 5
- Higher memory usage and slower API server responses

**With safe-start:**
- All resources become MRDs that are inactive by default
- Users activate only needed resources through policies
- Lower resource overhead and better performance

## Prerequisites

Before implementing safe-start, ensure you have:

* Provider built with Crossplane v2.0+ runtime
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

### Step 2: Enhance managed resource definition generation

Update your MRD generation to include connection details documentation:

{{< tabs >}}
{{< tab "Go Controller Runtime" >}}
```go
// In your MRD generation code
type ManagedResourceDefinition struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    
    Spec   ManagedResourceDefinitionSpec   `json:"spec"`
    Status ManagedResourceDefinitionStatus `json:"status,omitempty"`
}

type ManagedResourceDefinitionSpec struct {
    // Standard CRD fields
    Group   string `json:"group"`
    Names   Names  `json:"names"`
    Scope   string `json:"scope"`
    
    // safe-start-specific fields
    ConnectionDetails []ConnectionDetail `json:"connectionDetails,omitempty"`
    State             ResourceState      `json:"state,omitempty"`
}

type ConnectionDetail struct {
    Name        string `json:"name"`
    Description string `json:"description"`
    Type        string `json:"type"`
    FromConnectionSecretKey string `json:"fromConnectionSecretKey,omitempty"`
}
```
{{< /tab >}}

{{< tab "Terrajet/Upjet Provider" >}}
```go
// In your provider configuration
func GetProvider() *ujconfig.Provider {
    pc := ujconfig.NewProvider([]byte(providerSchema), resourcePrefix, modulePath,
        ujconfig.WithIncludeList(ExternalNameConfigured()),
        ujconfig.WithDefaultResourceOptions(
            ExternalNameConfigurations(),
            safe-startConfiguration(), // Add safe-start config
        ))
    
    // Configure safe-start for specific resources
    for _, configure := range []func(provider *ujconfig.Provider){
        configureConnectionDetails,
        configureMRDDocumentation,
    } {
        configure(pc)
    }
    
    return pc
}

func configureConnectionDetails(p *ujconfig.Provider) {
    // Example: RDS Instance connection details
    p.AddResourceConfigurator("aws_db_instance", func(r *ujconfig.Resource) {
        r.ConnectionDetails = map[string]ujconfig.ConnectionDetail{
            "endpoint": {
                Description: "The RDS instance endpoint",
                Type:        "string",
                FromConnectionSecretKey: "endpoint",
            },
            "port": {
                Description: "The port on which the DB accepts connections",
                Type:        "integer", 
                FromConnectionSecretKey: "port",
            },
            "username": {
                Description: "The master username for the database",
                Type:        "string",
                FromConnectionSecretKey: "username", 
            },
            "password": {
                Description: "The master password for the database",
                Type:        "string",
                FromConnectionSecretKey: "password",
            },
        }
    })
}
```
{{< /tab >}}
{{< /tabs >}}

### Step 3: Update RBAC Permissions

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
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apiextensions.crossplane.io"] 
  resources: ["managedresourcedefinitions"]
  verbs: ["get", "list", "watch", "update", "patch"]
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
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apiextensions.crossplane.io"] 
  resources: ["managedresourcedefinitions"]
  verbs: ["get", "list", "watch", "update", "patch"]
```

### Step 4: Implement managed resource definition controller logic

Add controller logic to handle MRD activation and CRD lifecycle:

```go
package controller

import (
    "context"
    
    apiextv1 "k8s.io/apiextensions-apiserver/pkg/apis/apiextensions/v1"
    "sigs.k8s.io/controller-runtime/pkg/reconcile"
    
    xpv1alpha1 "github.com/crossplane/crossplane/apis/apiextensions/v1alpha1"
)

// MRDReconciler handles MRD activation
type MRDReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *MRDReconciler) Reconcile(ctx context.Context, req reconcile.Request) (reconcile.Result, error) {
    mrd := &xpv1alpha1.ManagedResourceDefinition{}
    if err := r.Get(ctx, req.NamespacedName, mrd); err != nil {
        return reconcile.Result{}, client.IgnoreNotFound(err)
    }
    
    // Check if MRD should be active
    if mrd.Spec.State != nil && *mrd.Spec.State == xpv1alpha1.ResourceStateActive {
        return r.ensureCRDExists(ctx, mrd)
    }
    
    // If inactive, ensure CRD is removed
    return r.ensureCRDRemoved(ctx, mrd)
}

func (r *MRDReconciler) ensureCRDExists(ctx context.Context, mrd *xpv1alpha1.ManagedResourceDefinition) (reconcile.Result, error) {
    crd := &apiextv1.CustomResourceDefinition{}
    crdName := mrd.Spec.Names.Plural + "." + mrd.Spec.Group
    
    err := r.Get(ctx, types.NamespacedName{Name: crdName}, crd)
    if client.IgnoreNotFound(err) != nil {
        return reconcile.Result{}, err
    }
    
    if err != nil { // CRD doesn't exist
        return r.createCRD(ctx, mrd)
    }
    
    // CRD exists, ensure it's up to date
    return r.updateCRD(ctx, mrd, crd)
}

func (r *MRDReconciler) createCRD(ctx context.Context, mrd *xpv1alpha1.ManagedResourceDefinition) (reconcile.Result, error) {
    crd := &apiextv1.CustomResourceDefinition{
        ObjectMeta: metav1.ObjectMeta{
            Name: mrd.Spec.Names.Plural + "." + mrd.Spec.Group,
            OwnerReferences: []metav1.OwnerReference{{
                APIVersion: mrd.APIVersion,
                Kind:       mrd.Kind,
                Name:       mrd.Name,
                UID:        mrd.UID,
                Controller: pointer.Bool(true),
            }},
        },
        Spec: mrd.Spec.CustomResourceDefinitionSpec,
    }
    
    return reconcile.Result{}, r.Create(ctx, crd)
}
```

### Step 5: Update build and continuous integration processes

Update your build process to generate MRDs alongside CRDs:

{{< tabs >}}
{{< tab "Makefile" >}}
```makefile
# Update your Makefile to generate both CRDs and MRDs
.PHONY: generate
generate: controller-gen
	$(CONTROLLER_GEN) object:headerFile="hack/boilerplate.go.txt" paths="./..."
	$(CONTROLLER_GEN) crd:allowDangerousTypes=true paths="./..." output:crd:artifacts:config=package/crds
	$(CONTROLLER_GEN) mrd:allowDangerousTypes=true paths="./..." output:mrd:artifacts:config=package/mrds

# Add MRD generation tool
MRD_GEN = $(shell pwd)/bin/mrd-gen
.PHONY: mrd-gen
mrd-gen: ## Download mrd-gen locally if necessary.
	$(call go-get-tool,$(MRD_GEN),sigs.k8s.io/controller-tools/cmd/controller-gen@v0.13.0)

# Update package generation to include MRDs
.PHONY: build-package
build-package: generate
	mkdir -p package/
	cp package/crds/*.yaml package/
	cp package/mrds/*.yaml package/
	echo "# Package metadata with safe-start capability" > package/provider.yaml
	echo "apiVersion: meta.pkg.crossplane.io/v1" >> package/provider.yaml
	echo "kind: Provider" >> package/provider.yaml
	echo "spec:" >> package/provider.yaml
	echo "  capabilities:" >> package/provider.yaml
	echo "  - safe-start" >> package/provider.yaml
```
{{< /tab >}}

{{< tab "GitHub Actions" >}}
```yaml
name: Build and Test safe-start Provider

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-safestart:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.21'
        
    - name: Run Tests
      run: make test
      
    - name: Generate MRDs
      run: make generate
      
    - name: Verify MRD Generation
      run: |
        if [ ! -d "package/mrds" ]; then
          echo "MRD generation failed"
          exit 1
        fi
        echo "Generated MRDs:"
        ls -la package/mrds/
        
    - name: Test safe-start Integration
      run: |
        # Start local cluster
        make kind-up
        make install-crossplane-v2
        
        # Install provider with safe-start
        make install-provider
        
        # Verify MRDs created but inactive
        kubectl get mrds
        kubectl get mrds -o jsonpath='{.items[*].spec.state}' | grep -q "Inactive"
        
        # Test activation policy
        kubectl apply -f examples/activation-policy.yaml
        
        # Verify resources activate
        sleep 30
        kubectl get mrds -o jsonpath='{.items[*].spec.state}' | grep -q "Active"
        
        # Test resource creation
        kubectl apply -f examples/example-resource.yaml
        kubectl wait --for=condition=Ready --timeout=300s -f examples/example-resource.yaml
```
{{< /tab >}}
{{< /tabs >}}

### Step 6: Add connection details documentation

Document connection details in your MRDs to help users understand resource 
capabilities:

```yaml
# Example generated MRD with connection details
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceDefinition
metadata:
  name: databases.rds.aws.example.io
spec:
  group: rds.aws.example.io
  names:
    kind: Database
    plural: databases
  scope: Namespaced
  
  # safe-start-specific fields
  connectionDetails:
  - name: endpoint
    description: "The RDS instance connection endpoint"
    type: string
    fromConnectionSecretKey: endpoint
  - name: port  
    description: "The port number for database connections"
    type: integer
    fromConnectionSecretKey: port
  - name: username
    description: "The master username for the database"
    type: string
    fromConnectionSecretKey: username
  - name: password
    description: "The master password for the database"
    type: string
    fromConnectionSecretKey: password
  - name: ca_certificate
    description: "The CA certificate for SSL connections"
    type: string
    fromConnectionSecretKey: ca_certificate
    
  # Standard CRD specification  
  versions:
  - name: v1alpha1
    served: true
    storage: true
    # ... rest of CRD spec
```

## Testing safe-start implementation

### Unit testing

Test your MRD generation and controller logic:

```go
func TestMRDGeneration(t *testing.T) {
    // Test MRD generation with correct connection details
    mrd := generateMRDForResource("Database")
    
    assert.Equal(t, "databases.rds.aws.example.io", mrd.Name)
    assert.NotEmpty(t, mrd.Spec.ConnectionDetails)
    
    // Verify specific connection details
    endpointDetail := findConnectionDetail(mrd, "endpoint")
    assert.NotNil(t, endpointDetail)
    assert.Equal(t, "string", endpointDetail.Type)
    assert.Contains(t, endpointDetail.Description, "endpoint")
}

func TestMRDActivation(t *testing.T) {
    // Test MRD activation creates CRD
    ctx := context.Background()
    mrd := &v1alpha1.ManagedResourceDefinition{
        Spec: v1alpha1.ManagedResourceDefinitionSpec{
            State: &[]v1alpha1.ResourceState{v1alpha1.ResourceStateActive}[0],
        },
    }
    
    reconciler := &MRDReconciler{Client: fakeClient}
    result, err := reconciler.Reconcile(ctx, reconcile.Request{})
    
    assert.NoError(t, err)
    assert.False(t, result.Requeue)
    
    // Verify CRD creation
    crd := &apiextv1.CustomResourceDefinition{}
    err = fakeClient.Get(ctx, types.NamespacedName{Name: "databases.rds.aws.example.io"}, crd)
    assert.NoError(t, err)
}
```

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
  capabilities:
  - safe-start
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

### Version compatibility matrix

Document version compatibility:

| Provider Version | Crossplane Version | safe-start Support | Notes |
|------------------|-------------------|------------------|-------|
| v1.x            | v1.x - v2.x       | No               | Legacy CRD-only mode |  
| v2.0            | v2.0+             | Yes              | Full safe-start support |
| v2.1            | v2.0+             | Yes              | Enhanced MRD features |

## Documentation requirements

Update your provider documentation to include:

<!-- vale Google.Headings = NO -->
### README updates
<!-- vale Google.Headings = YES -->

```markdown
# Provider Example

## safe-start Support

This provider supports safe-start capability, which provides:
- Selective resource activation
- Improved performance for large providers  
- Connection details documentation

### Quick Start with safe-start

1. Install the provider:
```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-example
spec:
  package: registry.example.com/provider-example:v2.0.0
```

2. Create activation policy:
```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1  
kind: ManagedResourceActivationPolicy
metadata:
  name: example-resources
spec:
  activations:
  - "databases.rds.aws.example.io"
  - "*.s3.aws.example.io"
```

3. Create resources - only activated resources work.
```

### Connection Details Documentation

Document what connection details each resource provides:

```markdown
## Connection Details Reference

### Database (`databases.rds.aws.example.io`)
- `endpoint` (string): RDS instance connection endpoint
- `port` (integer): Database connection port  
- `username` (string): Master database username
- `password` (string): Master database password
- `ca_certificate` (string): CA certificate for SSL connections

### Storage Bucket (`buckets.s3.aws.example.io`) 
- `bucket_name` (string): The S3 bucket name
- `region` (string): AWS region where bucket is located
- `arn` (string): Full ARN of the S3 bucket
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

safe-start provides significant value for large providers and improves the 
 Crossplane user experience. Following this guide helps ensure your 
implementation is robust, well-documented, and user-friendly.