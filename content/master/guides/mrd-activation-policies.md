---
title: Writing MRD activation policies
weight: 150
description: Learn how to create effective activation policies for managed resources
---

ManagedResourceActivationPolicy (MRAP) provides powerful pattern-based control 
over which Managed Resource Definitions (MRDs) become active in your cluster. 
This guide shows how to write effective activation policies for different 
scenarios.

## Default activation policy

Crossplane automatically creates a default ManagedResourceActivationPolicy when 
installed. Understanding and configuring this default policy is crucial for 
effective MRD management.

### What's the default activation policy

The default MRAP is automatically created by Crossplane and activates managed 
resources according to configurable patterns. By default, it uses a wildcard 
pattern that activates **all** managed resources:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: crossplane-default-activation-policy
spec:
  activations:
  - "*"  # Activates all managed resources
```

{{< hint "important" >}}
The default `"*"` pattern means safe-start providers still create all CRDs, 
defeating the performance benefits. Most users should customize this behavior.
{{< /hint >}}

### Configuring default activation with Helm

Configure the default activation policy during Crossplane installation:

```yaml
# values.yaml for Crossplane Helm installation
provider:
  defaultActivations: 
  - "*"  # Default: activate everything (not recommended for large providers)
```

**Recommended configurations:**

{{< tabs >}}
{{< tab "Production (Selective)" >}}
```yaml
# Recommended: Disable default activation, use targeted policies
provider:
  defaultActivations: null  # or []

# Then create provider-specific MRAPs
# This provides better control and performance
```
{{< /tab >}}

{{< tab "Development (Permissive)" >}}
```yaml
# For development environments where you want broad access
provider:
  defaultActivations:
  - "*.aws.crossplane.io"
  - "*.gcp.crossplane.io" 
  - "*.azure.crossplane.io"
```
{{< /tab >}}

{{< tab "Service-Specific" >}}
```yaml
# Activate only specific service categories
provider:
  defaultActivations:
  - "*.rds.aws.crossplane.io"      # All RDS resources
  - "*.s3.aws.crossplane.io"       # All S3 resources
  - "instances.ec2.aws.crossplane.io"  # Only EC2 instances
```
{{< /tab >}}
{{< /tabs >}}

### Modifying the default policy after installation

You can change the default activation policy directly and changes persist:

```shell
# View current default policy
kubectl get mrap crossplane-default-activation-policy -o yaml

# Delete the default policy and restart Crossplane using Helm
kubectl delete mrap crossplane-default-activation-policy
helm upgrade crossplane crossplane-stable/crossplane \
  --set provider.defaultActivations=null \
  --namespace crossplane-system --reuse-values
kubectl rollout restart deployment/crossplane -n crossplane-system
```

{{< hint "note" >}}
**Changes to the default policy are permanent.** After the default MRAP exists, 
Crossplane doesn't change it. The Helm chart `provider.defaultActivations` 
value is only used when creating the policy if it doesn't already exist.
{{< /hint >}}

### Controlling default activation for new installations

The Helm chart value only affects the **initial creation** of the default policy:

```shell
# This only matters for NEW installations or when the default policy doesn't exist
helm upgrade crossplane crossplane-stable/crossplane \
  --set provider.defaultActivations=null \
  --namespace crossplane-system --reuse-values
```

If you want to reset the default policy to match new Helm values:

```shell
# Delete existing policy so Crossplane recreates it from Helm values
kubectl delete mrap crossplane-default-activation-policy

# Restart Crossplane to recreate the policy with current Helm values
kubectl rollout restart deployment/crossplane -n crossplane-system
```

### Best practices for default activation

**Recommended approach:**
1. **Disable default activation** by setting `provider.defaultActivations: null`
2. **Create targeted MRAPs** for each provider or service category
3. **Use specific patterns** rather than wildcards when possible

```shell
# 1. Install Crossplane with no default activation
helm install crossplane crossplane-stable/crossplane \
  --set provider.defaultActivations=null

# 2. Create provider-specific activation policies
kubectl apply -f - <<EOF
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: aws-core-services
spec:
  activations:
  - "instances.ec2.aws.crossplane.io"
  - "*.rds.aws.crossplane.io"
  - "buckets.s3.aws.crossplane.io"
EOF
```

**Why this approach is better:**
- **Performance**: Only activates resources you actually use
- **Security**: Principle of least privilege for resource access
- **Clarity**: Explicit about which resources are available
- **Maintainability**: Easier to understand and change activation patterns

## Policy basics

Beyond the default policy, you can create custom activation policies that 
specify which MRDs should activate using pattern matching:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: my-policy
spec:
  activations:
  - "exact-match.provider.example.com"
  - "*.wildcard.example.com" 
  - "prefix-*.example.com"
```

{{< hint "note" >}}
Multiple activation policies can exist simultaneously. Their activations are 
combined, so any MRD matched by any policy becomes active.
{{< /hint >}}

## Activation patterns

### Exact matching

Activate specific MRDs by their full name:

```yaml
spec:
  activations:
  - instances.ec2.aws.crossplane.io
  - buckets.s3.aws.crossplane.io
  - databases.rds.aws.crossplane.io
```

Use exact matching when:
* You know which resources you need
* You want fine-grained control over individual resources
* Security policies require explicit resource approval

### Wildcard matching

Use wildcards to activate groups of related resources:

```yaml
spec:
  activations:
  - "*.rds.aws.crossplane.io"        # All RDS resources
  - "*.storage.gcp.crossplane.io"    # All GCP storage resources  
  - "*.compute.azure.crossplane.io"  # All Azure compute resources
```

{{< hint "tip" >}}
Wildcard patterns only support prefix matching. The `*` must be at the 
beginning of the pattern and match one or more DNS label components.
{{< /hint >}}

### Provider-wide activation

Activate all resources from a specific provider:

```yaml
spec:
  activations:
  - "*.aws.crossplane.io"     # All AWS resources
  - "*.gcp.crossplane.io"     # All GCP resources
  - "*.azure.crossplane.io"   # All Azure resources
```

Use provider-wide activation when:
* You're migrating from non-safe-start providers
* Your applications use diverse resources from a single provider
* Development environments need broad resource access

## Environment-based policies

### Development environment

Activate minimal resources for development:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: development-resources
  namespace: development
spec:
  activations:
  # Basic compute
  - instances.ec2.aws.crossplane.io
  - "*.compute.gcp.crossplane.io"
  
  # Storage
  - buckets.s3.aws.crossplane.io
  - "*.storage.azure.crossplane.io"
  
  # Databases
  - "*.rds.aws.crossplane.io"
  - instances.sql.gcp.crossplane.io
```

### Staging environment  

Include resources for integration testing:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: staging-resources
  namespace: staging
spec:
  activations:
  # Everything from development
  - instances.ec2.aws.crossplane.io
  - "*.compute.gcp.crossplane.io"
  - buckets.s3.aws.crossplane.io
  - "*.storage.azure.crossplane.io"
  - "*.rds.aws.crossplane.io"
  - instances.sql.gcp.crossplane.io
  
  # Additional staging needs
  - "*.networking.aws.crossplane.io"
  - "*.iam.aws.crossplane.io"
  - clusters.eks.aws.crossplane.io
  - "*.monitoring.gcp.crossplane.io"
```

### Production environment

Activate all necessary resources:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: production-resources
  namespace: production
spec:
  activations:
  # Broad activation for production flexibility
  - "*.aws.crossplane.io"
  - "*.gcp.crossplane.io"
  - "*.azure.crossplane.io"
```

## Service-based policies

### Database services

Create policies focused on specific service categories:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: database-services
spec:
  activations:
  # Relational databases
  - "*.rds.aws.crossplane.io"
  - instances.sql.gcp.crossplane.io
  - servers.postgresql.azure.crossplane.io
  - servers.mysql.azure.crossplane.io
  
  # NoSQL databases  
  - tables.dynamodb.aws.crossplane.io
  - instances.spanner.gcp.crossplane.io
  - accounts.cosmosdb.azure.crossplane.io
  
  # Caching
  - clusters.elasticache.aws.crossplane.io
  - instances.memorystore.gcp.crossplane.io
  - caches.redis.azure.crossplane.io
```

### Networking services

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: networking-services
spec:
  activations:
  # Core networking
  - vpcs.ec2.aws.crossplane.io
  - subnets.ec2.aws.crossplane.io  
  - networks.compute.gcp.crossplane.io
  - subnetworks.compute.gcp.crossplane.io
  - virtualnetworks.network.azure.crossplane.io
  
  # Load balancing
  - "*.elbv2.aws.crossplane.io"
  - "*.compute.gcp.crossplane.io"
  - loadbalancers.network.azure.crossplane.io
  
  # DNS and routing
  - "*.route53.aws.crossplane.io"
  - "*.dns.gcp.crossplane.io" 
  - zones.dns.azure.crossplane.io
```

## Team-based policies

### Platform team

Broad access for platform engineering:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: platform-team-resources
spec:
  activations:
  # Infrastructure management
  - "*.iam.aws.crossplane.io"
  - "*.iam.gcp.crossplane.io"
  - "*.authorization.azure.crossplane.io"
  
  # Networking and security
  - "*.ec2.aws.crossplane.io"
  - "*.compute.gcp.crossplane.io"
  - "*.network.azure.crossplane.io"
  
  # Monitoring and logging
  - "*.cloudwatch.aws.crossplane.io"
  - "*.monitoring.gcp.crossplane.io"
  - "*.insights.azure.crossplane.io"
```

### App team

Resources needed by app developers:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: app-team-resources
spec:
  activations:
  # Compute resources
  - instances.ec2.aws.crossplane.io
  - clusters.eks.aws.crossplane.io
  - clusters.gke.gcp.crossplane.io
  
  # Storage
  - buckets.s3.aws.crossplane.io
  - buckets.storage.gcp.crossplane.io
  - accounts.storage.azure.crossplane.io
  
  # Databases (read-only access through compositions)
  - "*.rds.aws.crossplane.io"
  - instances.sql.gcp.crossplane.io
```

## Dynamic activation patterns

### Conditional activation

Use multiple policies to create conditional resource activation:

```yaml
# Base resources always active
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: base-resources
spec:
  activations:
  - instances.ec2.aws.crossplane.io
  - buckets.s3.aws.crossplane.io

---
# Optional resources for advanced features
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: advanced-resources
spec:
  activations:
  - clusters.eks.aws.crossplane.io
  - "*.lambda.aws.crossplane.io"
```

You can delete the `advanced-resources` policy to deactivate optional 
resources while keeping base capability.

### Feature flag patterns

Use labels and naming to create feature flag-like behavior:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: feature-ml-services
  labels:
    feature: machine-learning
    environment: production
spec:
  activations:
  - "*.sagemaker.aws.crossplane.io"
  - "*.ml.gcp.crossplane.io"
  - "*.cognitiveservices.azure.crossplane.io"
```

## Validation and testing

### Check activation status

Verify your policies work:

```shell
# List all activation policies
kubectl get mrap

# Check specific policy status
kubectl describe mrap my-policy

# See which MRDs are currently active
kubectl get mrds --field-selector spec.state=Active

# Count active MRDs by provider
kubectl get mrds -l crossplane.io/provider=provider-aws --field-selector spec.state=Active | wc -l
```

### Test resource creation

Verify activated resources work:

```shell
# Try creating a managed resource
kubectl apply -f - <<EOF
apiVersion: s3.aws.crossplane.io/v1alpha1
kind: Bucket
metadata:
  name: test-activation
spec:
  forProvider:
    region: us-east-1
EOF

# Check if the resource was created successfully
kubectl get bucket test-activation
kubectl describe bucket test-activation
```

### Policy debugging

Common issues and solutions:

```shell
# Check if MRD exists but isn't active
kubectl get mrd my-resource.provider.example.com
kubectl describe mrd my-resource.provider.example.com

# Verify policy is matching  
kubectl get mrap my-policy -o yaml | grep -A20 status

# Look for controller errors
kubectl logs -n crossplane-system deployment/crossplane | grep -i mrd
```

## Performance considerations

### Activation overhead

Each activation creates a CRD, which has resource overhead:

```yaml
# Efficient - activates exactly what's needed
spec:
  activations:
  - instances.ec2.aws.crossplane.io
  - buckets.s3.aws.crossplane.io

# Less efficient - activates everything
spec:
  activations:
  - "*.aws.crossplane.io"  # Could be 200+ resources
```

### Policy consolidation

Multiple small policies vs. large policies:

{{< tabs >}}
{{< tab "Multiple Small Policies (Recommended)" >}}
```yaml
# Easier to manage and understand
---
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: compute-resources
spec:
  activations:
  - "*.ec2.aws.crossplane.io"
  - "*.compute.gcp.crossplane.io"

---
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: storage-resources  
spec:
  activations:
  - "*.s3.aws.crossplane.io"
  - "*.storage.gcp.crossplane.io"
```
{{< /tab >}}

{{< tab "Single Large Policy" >}}
```yaml
# Harder to manage but fewer resources
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: all-resources
spec:
  activations:
  - "*.ec2.aws.crossplane.io"
  - "*.compute.gcp.crossplane.io"
  - "*.s3.aws.crossplane.io"
  - "*.storage.gcp.crossplane.io"
  # ... many more activations
```
{{< /tab >}}
{{< /tabs >}}

## Policy lifecycle management

<!-- vale Google.Headings = NO -->
### GitOps workflow
<!-- vale Google.Headings = YES -->

Store activation policies in Git for proper change management:

```yaml
# clusters/production/activation-policies/
production-compute.yaml
production-storage.yaml  
production-networking.yaml

# clusters/staging/activation-policies/
staging-core.yaml
staging-experimental.yaml

# clusters/development/activation-policies/
development-minimal.yaml
```

### Versioning strategies

Use metadata to track policy versions:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: production-resources
  labels:
    version: "v2.1.0"
    environment: production
    team: platform-engineering
  annotations:
    policy.crossplane.io/description: "Production resource activation policy"
    policy.crossplane.io/last-updated: "2024-01-15"
    policy.crossplane.io/approved-by: "platform-team"
spec:
  activations:
  - "*.aws.crossplane.io"
```

## Integration with compositions

### Composition compatibility

Compositions work with both active and inactive MRDs, but resource creation 
only succeeds when MRDs are active:

```yaml
# This composition can exist regardless of MRD state
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: webapp-stack
spec:
  compositeTypeRef:
    apiVersion: platform.example.com/v1alpha1
    kind: WebApp
  resources:
  - name: database
    base:
      apiVersion: rds.aws.crossplane.io/v1alpha1
      kind: DBInstance
      # This only works if RDS MRDs are active
  - name: storage  
    base:
      apiVersion: s3.aws.crossplane.io/v1alpha1
      kind: Bucket
      # This only works if S3 MRDs are active
```

### Activation dependencies

Document activation requirements in compositions:

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: ml-pipeline
  annotations:
    composition.crossplane.io/required-mrds: |
      - "*.sagemaker.aws.crossplane.io"
      - "*.s3.aws.crossplane.io"  
      - "*.iam.aws.crossplane.io"
spec:
  # ... composition definition
```

This helps operators understand which activation policies you need for 
specific compositions to work.