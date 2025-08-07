---
title: Provider Capabilities
weight: 20
description: Understand provider capabilities and how they affect resource behavior
---

Provider capabilities are declarative features that providers can implement to 
change their behavior and integration with Crossplane. Capabilities enable 
providers to opt into new features while maintaining backward compatibility.

## What are provider capabilities

Provider capabilities are metadata declarations in provider packages that tell 
Crossplane how the provider should behave. They're like feature flags 
but you declare them at the package level.

```yaml
# In provider package metadata
apiVersion: meta.pkg.crossplane.io/v1alpha1
kind: Provider
metadata:
  name: provider-aws
spec:
  capabilities:
  - safe-start
  - CustomCapability
```

Crossplane reads these capabilities and modifies its behavior when installing 
and managing the provider.

## Available capabilities

<!-- vale Google.Headings = NO -->
### safe-start
<!-- vale Google.Headings = YES -->

The `safe-start` capability changes how Managed Resource Definitions (MRDs) are 
activated when you install the provider.

**Without safe-start:**
- All resources become MRDs that are automatically active
- Active MRDs create corresponding CRDs
- Compatible with legacy providers and existing workflows

**With safe-start:**
- All resources become MRDs that start in `Inactive` state
- No CRDs until you explicitly activate MRDs
- Reduces initial resource overhead and improves performance

```yaml
spec:
  capabilities:
  - safe-start
```

{{< hint "tip" >}}
safe-start is valuable for large providers like AWS that define 
hundreds of managed resources. It prevents performance issues by avoiding the 
creation of unused CRDs.
{{< /hint >}}

#### When to use safe-start

Use safe-start when:
* Your provider defines over 50 managed resources
* Users typically need only a subset of available resources
* Installation performance and resource usage are concerns
* You want to provide better resource discovery through MRDs

Don't use safe-start when:
* Your provider has under 20 managed resources
* Most users need all available resources
* Backward compatibility with existing installations is critical
* Your users aren't ready to manage resource activation

## Capability matching

Crossplane supports flexible matching for capability names:

* **Exact match**: `safe-start`
* **Case variations**: `SafeStart`, `safestart`, `safe-start`
* **Fuzzy matching**: Handles common spelling variations

This flexibility prevents issues when providers use different naming conventions.

## How capabilities affect installation

The provider installation process changes based on declared capabilities:

```mermaid
flowchart TD
    install[Install Provider Package]
    readCaps[Read Capabilities]
    checkSafe{Has safe-start?}
    activateAll[Activate All MRDs]
    keepInactive[Keep MRDs Inactive]
    createCRDs[Create All CRDs]
    waitPolicy[Wait for Activation Policy]
    
    install --> readCaps
    readCaps --> checkSafe
    checkSafe -->|No| activateAll
    checkSafe -->|Yes| keepInactive
    activateAll --> createCRDs
    keepInactive --> waitPolicy
    
    style keepInactive fill:#c8e6c9
    style waitPolicy fill:#fff3e0
```

## Provider compatibility

### Legacy providers

Providers without any capabilities work as before:
* All MRDs are active by default
* Crossplane creates all CRDs when provider installs
* No changes required for existing compositions or configurations

### Modern providers

Providers with safe-start capability require extra setup:
* Create ManagedResourceActivationPolicy to activate needed resources
* Verify required CRDs exist before creating managed resources  
* Use MRD connection details documentation for resource planning

## Implementing safe-start in providers

safe-start implementation requires several technical changes to provider code and 
build processes. This section provides an overview - see the 
[complete safe-start implementation guide]({{< ref "../guides/implementing-safestart" >}}) 
for detailed instructions.

### Key implementation requirements

**Code changes:**
- Add MRD controller logic to handle activation/deactivation
- Support both namespaced and cluster-scoped resources
- Generate MRDs with connection details documentation
- Implement CRD lifecycle management

**Build process changes:**
- Update Makefile to generate MRDs alongside CRDs
- Change CI/CD to test safe-start behavior
- Include MRDs in provider package artifacts

**RBAC updates:**
safe-start providers need extra permissions to manage CRDs dynamically:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole  
metadata:
  name: my-provider-system
rules:
# Standard provider permissions
- apiGroups: [""]
  resources: ["events"]
  verbs: ["create", "update", "patch"]
  
# Additional safe-start permissions
- apiGroups: ["apiextensions.k8s.io"]
  resources: ["customresourcedefinitions"] 
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apiextensions.crossplane.io"]
  resources: ["managedresourcedefinitions"]
  verbs: ["get", "list", "watch", "update", "patch"]
```

### Provider package metadata

Declare safe-start capability in your provider package:

```yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Provider
metadata:
  name: my-provider
spec:
  package: registry.example.com/my-provider:v2.0.0
  capabilities:
  - safe-start
```

### Managed resource definition generation with connection details

Generate MRDs that document connection details for better user experience:

```yaml
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
  
  # Connection details documentation
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
```

### Implementation examples

The [provider-nop safe-start implementation](https://github.com/crossplane-contrib/provider-nop/pull/24) 
demonstrates:
- Adding both namespaced and cluster-scoped resource variants
- MRD controller integration
- Build process updates for safe-start support
- Testing strategies for safe-start behavior

{{< hint "tip" >}}
See the [complete safe-start implementation guide]({{< ref "../guides/implementing-safestart" >}}) 
for step-by-step instructions, code examples, and testing strategies.
{{< /hint >}}

### Migration considerations

When adding safe-start to existing providers:

**Backward compatibility:**
- Existing provider installations continue working unchanged
- New installations start with inactive MRDs
- Provide migration documentation for users

**Version strategy:**
```yaml
# Document version compatibility clearly
# Provider v1.x: Traditional CRD installation  
# Provider v2.0+: safe-start support with MRDs
```

## Best practices

### For provider developers

**Do use safe-start when:**
* Your provider has >50 managed resources
* Resource activation patterns vary by environment
* Performance optimization is important

**Document capabilities:**
* Explain what each capability does
* Provide migration guides for existing users
* Include examples of activation policies

**Test compatibility:**
* Verify behavior with and without capabilities
* Test with different Crossplane versions
* Validate RBAC permissions

### For platform operators

**Plan activation policies:**
```yaml
# Development environment - minimal resources
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: dev-resources
spec:
  activations:
  - "databases.*.example.com"
  - "buckets.*.example.com"

---
# Production environment - comprehensive resources  
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: prod-resources
spec:
  activations:
  - "*.example.com"  # Activate all resources
```

**Track activation status:**
```shell
# Check which MRDs are active
kubectl get mrds -l provider=my-provider

# Verify activation policies
kubectl get mrap -o wide

# Monitor resource usage
kubectl top nodes
```

## Troubleshooting capabilities

### Common issues

**MRDs not activating:**
```shell
# Check if provider has safe-start capability
kubectl get provider my-provider -o yaml | grep -A5 capabilities

# Verify activation policy exists and matches
kubectl get mrap
kubectl describe mrap my-policy
```

**CRDs not created:**
```shell
# Check MRD activation status
kubectl get mrd my-resource.example.com

# Look for controller errors
kubectl logs -n crossplane-system deployment/crossplane
```

**Provider installation fails:**
```shell
# Check provider conditions
kubectl describe provider my-provider

# Look for RBAC issues
kubectl get events --field-selector reason=FailedCreate
```

### Debug commands

```shell
# List all providers and their capabilities
kubectl get providers -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.capabilities[*].name}{"\n"}{end}'

# Check MRD activation across providers
kubectl get mrds --show-labels

# Verify CRD creation matches activation
kubectl get crds | grep example.com | wc -l
kubectl get mrds -l state=Active | wc -l
```

## Relationship to other features

Provider capabilities integrate with:

* **MRDs** - safe-start controls default activation state
* **Activation policies** - Work together to control resource availability  
* **Package manager** - Crossplane reads capabilities during package installation
* **RBAC** - Some capabilities require extra permissions
* **Compositions** - May need updates when capabilities change resource availability

Capabilities provide a foundation for evolving provider behavior while 
maintaining compatibility with existing Crossplane installations.