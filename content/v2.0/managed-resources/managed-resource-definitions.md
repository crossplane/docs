---
title: Managed Resource Definitions
weight: 15
state: alpha
alphaVersion: 2.0
description: ManagedResourceDefinitions enable selective activation of provider
  resources and reduce CRD overhead
---

{{<hint "important">}}
Crossplane v2.0+ enables managed resource definitions by default. This
automatically converts provider CRDs to MRDs during installation. To disable
this
behavior, set `--enable-custom-to-managed-resource-conversion=false` when
installing Crossplane.
{{</hint>}}

A `ManagedResourceDefinition` (MRD) is a lightweight abstraction over
Kubernetes CustomResourceDefinitions (CRDs) that enables selective activation of
managed resources. MRDs solve the problem of providers installing hundreds of
CRDs when you only need one or two, reducing API server overhead and improving
cluster performance.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## The CRD scaling problem
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

Large Crossplane providers can install 100+ managed resource CRDs. Each CRD
consumes about 3 MiB of API server memory and creates API endpoints that affect
cluster performance:

- **Memory pressure**: Large providers can consume 300+ MiB of API server
  memory
- **Slower kubectl operations**: Commands like `kubectl get managed` must query
  all custom resource endpoints
- **Increased API server load**: More CRDs mean more API endpoints to serve
- **Unnecessary resource overhead**: Most users only need a subset of provider
  resources

MRDs address this by allowing providers to ship resource definitions that only
become active CRDs when explicitly needed.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## How MRDs work
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

An MRD contains the same schema as a CRD but adds two key fields:

- **`connectionDetails`**: Documents what connection secrets the resource
  provides
- **`state`**: Controls whether the underlying CRD exists (`Active` or
  `Inactive`)

When an MRD's state is `Inactive`, no CRD exists in the cluster. When
activated, Crossplane creates the corresponding CRD and the provider can start
managing instances of that resource.

```yaml
apiVersion: apiextensions.crossplane.io/v1alpha1
kind: ManagedResourceDefinition
metadata:
  name: buckets.s3.aws.m.crossplane.io
spec:
  group: s3.aws.m.crossplane.io
  names:
    kind: Bucket
    plural: buckets
  scope: Cluster
  versions:
  - name: v1alpha1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              forProvider:
                type: object
                properties:
                  region:
                    type: string
                  versioning:
                    type: boolean
  connectionDetails:
  - name: bucket-name
    description: The name of the created S3 bucket
  - name: region  
    description: The AWS region where the bucket was created
  state: Inactive  # Default state - no CRD created yet
```

## Key characteristics

- **Selective activation**: Only create CRDs for resources you actually need
- **Performance benefits**: Inactive MRDs consume minimal cluster resources
- **Connection details documentation**: Schema for documenting available
  connection secrets
- **One-way state transition**: MRDs can go from `Inactive` to `Active` but not
  back

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## MRD states
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

### Inactive state

When `state: Inactive` (the default):

- No CRD exists in the cluster
- No API endpoints exist
- The provider doesn't start a controller for this resource
- Minimal memory and CPU overhead

```yaml
spec:
  state: Inactive  # Default for all MRDs
```

### Active state

When `state: Active`:

- Crossplane creates the corresponding CRD
- API endpoints become available for the resource
- The provider starts a controller to manage instances
- Full capability like traditional managed resources

```yaml
spec:
  state: Active  # CRD will be created
```

{{<hint "important">}}
MRD state transitions are one-way only. Once an MRD becomes `Active`, it can't
return to `Inactive`. This prevents accidental deletion of CRDs that may have
existing resources.
{{</hint>}}

## Connection details documentation

MRDs can document what connection details a managed resource provides. This
helps users understand what data is available in connection secrets without
having to create test resources.

```yaml
spec:
  connectionDetails:
  - name: endpoint
    description: The RDS instance endpoint for database connections
  - name: port
    description: The port number for database connections  
  - name: username
    description: The master username for database access
  - name: password
    description: The auto-generated master password
```

{{<hint "note">}}
<!-- vale write-good.Passive = NO -->
<!-- vale gitlab.CurrentStatus = NO -->
<!-- vale write-good.Weasel = NO -->
Connection details are currently a schema-only feature. Most providers
don't yet populate the `connectionDetails` field in their MRDs, but the structure
is available for future implementation.
<!-- vale write-good.Weasel = YES -->
<!-- vale gitlab.CurrentStatus = YES -->
<!-- vale write-good.Passive = YES -->
{{</hint>}}

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## Working with MRDs
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### Viewing MRDs
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

List all MRDs in your cluster:

```shell
kubectl get managedresourcedefinitions
```

View MRD details:

```shell
kubectl describe mrd buckets.s3.aws.m.crossplane.io
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### Checking MRD status
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

MRDs provide status information about their lifecycle:

```yaml
status:
  conditions:
  - type: Established
    status: "False"
    reason: InactiveManagedResource
    message: "ManagedResourceDefinition is inactive"
```

**Status conditions:**

- **`Established: False, Reason: InactiveManagedResource`**: MRD is inactive,
  no CRD created
- **`Established: Unknown, Reason: PendingManagedResource`**: Crossplane is
  creating the CRD  
- **`Established: True, Reason: EstablishedManagedResource`**: CRD exists and
  is ready
- **`Healthy: True, Reason: Running`**: MRD controller operating
- **`Healthy: Unknown, Reason: EncounteredErrors`**: MRD controller
  experiencing issues

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### Manually activating MRDs
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

You can manually activate an MRD by changing its state:

```shell
kubectl patch mrd buckets.s3.aws.m.crossplane.io --type='merge' \
  -p='{"spec":{"state":"Active"}}'
```

The recommended approach is to use
[ManagedResourceActivationPolicies]({{<ref "managed-resource-activation-policies">}})
for systematic activation.

## How providers work with MRDs

Crossplane v2.0+ automatically converts all provider CRDs to MRDs during
package installation, regardless of the provider's age or original format. The
provider's `safe-start` capability determines the default MRD state:

### Providers with `safe-start` capability
- MRDs start with `state: Inactive` by default
- Support selective activation via
  [ManagedResourceActivationPolicies]({{<ref "managed-resource-activation-policies">}})
- Reduced resource overhead for unused resources
- Provider can start without all CRDs being active

```yaml
# Provider package metadata
apiVersion: meta.pkg.crossplane.io/v1
kind: Provider
spec:
  capabilities:
  - safe-start
```

{{<hint "tip">}}
Crossplane uses fuzzy matching for capabilities, so `safe-start`,
`safe_start`, `safestart`, and `SafeStart` all match the `safe-start`
capability.
{{</hint>}}

### Providers without `safe-start` capability
- MRDs start with `state: Active` by default (legacy behavior)
- All CRDs become available for backward compatibility
- Full resource overhead like traditional providers


<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
## Troubleshooting MRDs
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### MRD exists but no CRD appears
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

<!-- vale Google.Colons = NO -->
**Symptoms**: MRD is present but `kubectl get <resource>` shows "no
resources found"

**Cause**: MRD is in `Inactive` state

**Solution**: Activate the MRD using an
[ManagedResourceActivationPolicy]({{<ref "managed-resource-activation-policies">}})
or manually patch the state
<!-- vale Google.Colons = YES -->

```shell
# Check MRD state
kubectl get mrd <name> -o jsonpath='{.spec.state}'

# Activate if needed
kubectl patch mrd <name> --type='merge' -p='{"spec":{"state":"Active"}}'
```

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### MRD activation fails
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

<!-- vale Google.Colons = NO -->
**Symptoms**: MRD state is `Active` but `Established` condition remains `False`

**Cause**: CRD creation failed due to schema issues or conflicts

**Solution**: Check MRD events and status for error details
<!-- vale Google.Colons = YES -->

```shell
kubectl describe mrd <name>
```

**Other status conditions for troubleshooting:**
- **`Established: False, Reason: BlockedManagedResourceActivationPolicy`**:
  Blocked by activation policy issues
- **`Established: False, Reason: TerminatingManagedResource`**: Crossplane is
  deleting the MRD

**Common events you might see:**
- `Normal CreateCustomResourceDefinition` - CRD successfully created
- `Normal UpdateCustomResourceDefinition` - CRD successfully updated  
- `Warning CreateCustomResourceDefinition` - CRD creation failed
- `Warning UpdateCustomResourceDefinition` - CRD update failed
- `Warning Reconcile` - General reconciliation errors

Common issues:
- Malformed OpenAPI schema in the MRD
- CRD name conflicts with existing resources
- Insufficient RBAC permissions for Crossplane

### Provider doesn't support activation

<!-- vale Google.Colons = NO -->
**Symptoms**: Provider starts all controllers regardless of MRD states

**Cause**: Provider doesn't implement late activation support

**Solution**: Check provider capabilities and use a compatible provider version
<!-- vale Google.Colons = YES -->

```shell
# Check if provider supports late activation
kubectl get providerrevision <provider-revision-name> \
  -o jsonpath='{.status.capabilities}'
```

Look for the `safe-start` capability.

## Next steps

- Learn about
  [ManagedResourceActivationPolicies]({{<ref "managed-resource-activation-policies">}})
  for systematic resource activation
- See the
  [disabling unused managed resources guide]({{<ref "../guides/disabling-unused-managed-resources">}})
  for practical implementation
- Check the [API reference]({{<ref "../api">}}) for complete MRD schema
  documentation