---
title: Managed Resource Activation Policies
weight: 20
state: alpha
alphaVersion: 2.0
description: Choose which provider resources Crossplane activates
---

{{<hint "important">}}
Managed resource activation policies work with
[managed resource definitions]({{<ref "managed-resource-definitions">}}),
which Crossplane v2.0+ enables by default. To disable this behavior, set
`--enable-custom-to-managed-resource-conversion=false` when installing
Crossplane.
{{</hint>}}

A `ManagedResourceActivationPolicy` (MRAP) controls which
[ManagedResourceDefinitions]({{<ref "managed-resource-definitions">}})
become active in your cluster. MRAPs enable selective installation of provider
resources, allowing you to activate only the 10 managed resources you need
instead of the 100+ that a provider ships.

## The selective activation problem

Modern Crossplane providers can ship dozens or hundreds of managed resources,
but most users only need a small subset. Before MRAPs, you got "all or
nothing" - installing a provider meant getting every managed resource it
supported, consuming unnecessary cluster resources.

MRAPs solve this by providing pattern-based activation of
ManagedResourceDefinitions, letting you choose which provider resources to
enable.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## How MRAPs work
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

MRAPs contain activation patterns that match ManagedResourceDefinition names.
When you create or update an MRAP, Crossplane:

1. **Lists all MRDs** in the cluster
2. **Matches MRD names** against the activation patterns
3. **Activates matching MRDs** by setting their `state` to `Active`
4. **Updates the MRAP status** with the list of activated resources

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: aws-core-resources
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io      # Modern v2 style S3 buckets
  - instances.rds.aws.m.crossplane.io   # Modern v2 style RDS instances
  - "*.ec2.aws.m.crossplane.io"         # All modern v2 style EC2 resources
```

When you apply this MRAP, Crossplane activates the specified S3 Bucket, RDS
Instance, and all EC2 resources, leaving other AWS resources inactive.

## Key features

- **Pattern-based matching**: Use wildcards to activate groups of resources
- **Multiple policy support**: Different MRAPs can activate different resource
  sets
- **Status tracking**: See which resources each policy activated
- **Automatic activation**: New MRDs matching existing patterns activate
  automatically

## Pattern matching

### Exact matching

Specify complete MRD names for precise control:

```yaml
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io
  - databases.rds.aws.m.crossplane.io
  - clusters.eks.aws.m.crossplane.io
```

{{<hint "important">}}
Use the **plural** name when using a complete MRD name, aligning with how
Kubernetes expresses the complete names of CRDs.

For example, use `buckets`, as opposed to `bucket`, in `buckets.s3.aws.m.crossplane.io`.
{{</hint>}}

### Wildcard patterns

Use `*` wildcards to match multiple resources:

```yaml
spec:
  activate:
  - "*.s3.aws.m.crossplane.io"      # All S3 resources
  - "*.ec2.aws.m.crossplane.io"     # All EC2 resources
  - "*.rds.aws.m.crossplane.io"     # All RDS databases
```

{{<hint "important">}}
MRAPs use prefix-only wildcards, not full regular expressions. Only `*` at
the beginning of a pattern works (for example, `*.s3.aws.m.crossplane.io`).
Patterns like `s3.*.aws.m.crossplane.io` or `*.s3.*` aren't valid.
{{</hint>}}

{{<hint "tip">}}
You can mix exact names and wildcards for flexible activation:
```yaml
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io        # Exact S3 buckets
  - "*.ec2.aws.m.crossplane.io"           # All EC2 resources
  - clusters.eks.aws.m.crossplane.io      # Exact EKS clusters
```
{{</hint>}}

## Legacy and modern resource versions

Crossplane v2 supports two styles of managed resources:

- **Modern v2 style** (recommended): Use `*.m.crossplane.io` domains for
  namespaced managed resources with better isolation and security
- **Legacy v1 style**: Use `*.crossplane.io` domains for cluster-scoped
  managed resources (maintained for backward compatibility)

### Activating modern resources

Most examples in this guide use modern v2 style resources:

```yaml
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io         # Modern v2 S3 bucket
  - "*.ec2.aws.m.crossplane.io"            # All modern v2 EC2 resources
```

### Activating legacy resources

To activate legacy v1 style resources, use patterns without `.m`:

```yaml
spec:
  activate:
  - buckets.s3.aws.crossplane.io           # Legacy v1 S3 bucket
  - "*.ec2.aws.crossplane.io"              # All legacy v1 EC2 resources
```

### Mixed activation

You can activate both modern and legacy resources in the same MRAP:

```yaml
spec:
  activate:
  - "*.aws.m.crossplane.io"                # All modern AWS resources
  - "*.aws.crossplane.io"                  # All legacy AWS resources
```

## Common activation strategies

### Activate everything (default behavior)

The Crossplane Helm chart creates a default MRAP that activates all resources:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: default
spec:
  activate:
  - "*"  # Activate all MRDs
```

You can customize this during installation:

```shell
# Disable default activations entirely
helm install crossplane crossplane-stable/crossplane \
  --set provider.defaultActivations={}

# Or provide custom default activations
helm install crossplane crossplane-stable/crossplane \
  --set provider.defaultActivations={\
    "*.s3.aws.m.crossplane.io","*.ec2.aws.m.crossplane.io"}
```

### Provider-specific activation

Activate all resources from specific providers:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: aws-provider-resources
spec:
  activate:
  - "*.aws.crossplane.io"     # All AWS resources
  - "*.aws.m.crossplane.io"   # All AWS managed resources (v2 style)
```

### Service-specific activation

Activate resources for specific cloud services:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: storage-and-compute
spec:
  activate:
  - "*.s3.aws.m.crossplane.io"         # AWS S3 resources
  - "*.ec2.aws.m.crossplane.io"        # AWS EC2 resources
  - "*.storage.gcp.m.crossplane.io"    # GCP Storage resources
  - "*.compute.gcp.m.crossplane.io"    # GCP Compute resources
```

### Minimal activation

Activate only the resources you know you need:

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: minimal-footprint
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io       # Just S3 buckets
  - instances.ec2.aws.m.crossplane.io    # Just EC2 instances
  - databases.rds.aws.m.crossplane.io    # Just RDS databases
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## Multiple MRAPs
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

You can have multiple MRAPs in your cluster. Crossplane processes all MRAPs
together and activates any MRD that matches at least one pattern.

### Team-based activation

Different teams can manage their own activation policies:

```yaml
# Storage team MRAP
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: storage-team
spec:
  activate:
  - "*.s3.aws.m.crossplane.io"
  - "*.storage.gcp.m.crossplane.io"
---
# Database team MRAP
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: database-team
spec:
  activate:
  - "*.rds.aws.m.crossplane.io"
  - "*.sql.gcp.m.crossplane.io"
```

### Configuration package activation

Configuration packages can include MRAPs to declare their resource dependencies:

```yaml
# In your Configuration package
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceActivationPolicy
metadata:
  name: web-platform-dependencies
spec:
  activate:
  - buckets.s3.aws.m.crossplane.io       # For static assets
  - instances.ec2.aws.m.crossplane.io    # For web servers
  - databases.rds.aws.m.crossplane.io    # For application data
  - certificates.acm.aws.m.crossplane.io # For HTTPS
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## Working with MRAPs
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### Creating MRAPs
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

Apply an MRAP like any Kubernetes resource:

```shell
kubectl apply -f my-activation-policy.yaml
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### Viewing MRAPs
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

List all MRAPs:

```shell
kubectl get managedresourceactivationpolicies
```

View MRAP details and status:

```shell
kubectl describe mrap aws-core-resources
```

### Checking activation status

MRAPs track which resources they've activated:

```yaml
status:
  conditions:
  - type: Healthy
    status: "True"
    reason: Running
  activated:
  - buckets.s3.aws.m.crossplane.io
  - instances.ec2.aws.m.crossplane.io
  - instances.rds.aws.m.crossplane.io
  - securitygroups.ec2.aws.m.crossplane.io
  - subnets.ec2.aws.m.crossplane.io
  - vpcs.ec2.aws.m.crossplane.io
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## MRAP status conditions
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

### Healthy condition

- **`Healthy: True, Reason: Running`**: MRAP works
- **`Healthy: Unknown, Reason: EncounteredErrors`**: Some MRDs failed to
  activate

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## Troubleshooting MRAPs
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### MRAP exists but resources aren't activated
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

<!-- vale Google.Colons = NO -->
**Symptoms**: MRAP shows `activated: []` or missing expected resources
<!-- vale Google.Colons = YES -->

**Causes and solutions:**

1. **Pattern doesn't match MRD names**
   ```shell
   # List available MRDs
   kubectl get mrds

   # Check your pattern matches
   kubectl get mrds -o name | grep "your-pattern"
   ```

2. **MRDs don't exist yet**
   - Install the required provider first
   - Providers create MRDs when they start

3. **Provider doesn't support activation**
   ```shell
   # Check provider capabilities
   kubectl get providerrevision <provider-revision-name> \
     -o jsonpath='{.status.capabilities}'
   # Look for "safe-start"
   ```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### MRAP shows activation errors
<!-- vale Microsoft.HeadingAcronyms = YES -->
<!-- vale Google.Headings = YES -->

<!-- vale Google.Colons = NO -->
**Symptoms**: MRAP has `Healthy: Unknown` status with errors
<!-- vale Google.Colons = YES -->

**Status condition example:**

```yaml
conditions:
- type: Healthy
  status: "Unknown"
  reason: EncounteredErrors
  message: "failed to activate 2 of 5 ManagedResourceDefinitions"
```

**Solution**: select MRAP events for specific failure details:

```shell
kubectl describe mrap <name>
# Look at the Events section for activation errors
```

### Resources activate when you don't expect them to

**Symptoms**: more resources are active than expected

**Cause**: multiple MRAPs with overlapping patterns (this is normal behavior)

**Solution**: review all MRAP patterns to understand which policies are
activating which resources

```shell
# List all MRAP activation patterns
kubectl get mrap \
  -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.activate}{"\n"}{end}'

# Check which MRAPs activated each resource
kubectl get mrap \
  -o jsonpath='{range .items[*]}{.metadata.name}: {.status.activated}{"\n"}{end}'
```

## Best practices

MRAPs are additive - multiple MRAPs can activate the same resource without
conflicts. This enables team-based activation strategies and Configuration
package dependencies.

<!-- vale alex.ProfanityUnlikely = NO -->
1. **Start specific, broaden as needed** - Begin with exact resource names
   (using the plural name for each resource), add wildcards only when beneficial for
   maintainability
2. **Plan for provider evolution** - Design wildcard patterns that
   accommodate new resources as providers add them (for example,
   `*.s3.aws.m.crossplane.io` works for future S3 resources)
3. **Group related resources logically** - Create MRAPs that activate
   resources teams actually use together
4. **Include activation dependencies in Configuration packages** -
   Configuration packages should declare what MRDs they need rather than
   assuming resources are available
5. **Use conservative patterns in shared environments** - Avoid overly broad
   wildcards that activate unnecessary resources when multiple teams share
   providers
<!-- vale alex.ProfanityUnlikely = YES -->

## Next steps

- Learn about
  [ManagedResourceDefinitions]({{<ref "managed-resource-definitions">}})
  to understand what MRAPs activate
- See the
  [disabling unused managed resources guide]({{<ref "../guides/disabling-unused-managed-resources">}})
  for step-by-step implementation
- Check the [API reference]({{<ref "../api">}}) for complete MRAP schema
  documentation
