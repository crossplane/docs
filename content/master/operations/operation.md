---
title: Operation
weight: 110
state: alpha
alphaVersion: 2.0
description: Operations run function pipelines once to completion for operational tasks
---

An `Operation` runs a function pipeline once to completion to perform operational
tasks that don't fit the typical resource creation pattern. Unlike compositions
that continuously reconcile desired state, Operations focus on tasks like
backups, rolling upgrades, configuration validation, and scheduled maintenance.

## How operations work

Operations are like Kubernetes Jobs - they run once to completion rather than
continuously reconciling. Like compositions, Operations use function pipelines
to implement their logic, but they're designed for operational workflows
instead of resource composition.

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: backup-database
spec:
  mode: Pipeline
  pipeline:
  - step: create-backup
    functionRef:
      name: function-database-backup
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: DatabaseBackupInput
      database: production-db
      retentionDays: 30
```

When you create this Operation, Crossplane:

1. **Validates** the operation and its function dependencies
2. **Executes** the function pipeline step by step
3. **Applies** any resources the functions create or change
4. **Updates** the Operation status with results and completion state

{{<hint "important">}}
Operations are an alpha feature. You must enable them by adding
`--enable-operations` to Crossplane's arguments.
{{</hint>}}

## Key characteristics

- **Runs once to completion** (like Kubernetes Jobs)
- **Uses function pipelines** (like Compositions)
- **Can create or change any Kubernetes resources**
- **Provides detailed status and output from each step**
- **Supports retry on failure with configurable limits**

## Operation functions vs composition functions

Operations and compositions both use function pipelines, but with important
differences:

**Composition Functions:**
- **Purpose**: Create and maintain resources
- **Lifecycle**: Continuous reconciliation
- **Input**: Observed composite resources
- **Output**: Desired composed resources  
- **Ownership**: Creates owner references

**Operation Functions:**
- **Purpose**: Perform operational tasks
- **Lifecycle**: Run once to completion
- **Input**: Required resources only
- **Output**: Any Kubernetes resources
- **Ownership**: Force applies without owners

Functions can support both modes by declaring the appropriate capabilities in
their package metadata. Function authors declare this in the `crossplane.yaml`
file when building the function package:

```yaml
apiVersion: meta.pkg.crossplane.io/v1
kind: Function
metadata:
  name: my-function
spec:
  capabilities:
  - composition
  - operation
```

This allows Crossplane to know which modes the function supports and avoid
trying to use a composition-only function for operations.

## Common use cases

{{<hint "note">}}
The following examples use hypothetical functions for illustration. At launch,
only function-python supports operations.
{{</hint>}}

### Rolling upgrades

Use Operations for controlled rolling upgrades:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: cluster-upgrade
spec:
  mode: Pipeline
  pipeline:
  - step: rolling-upgrade
    functionRef:
      name: function-cluster-upgrade
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: ClusterUpgradeInput
      targetVersion: "1.28"
      batches: [0.25, 0.5, 1.0]  # 25%, 50%, then 100%
      healthChecks: [Synced, Ready]
```

### One-time maintenance

Use Operations for specific maintenance tasks:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: certificate-rotation
spec:
  mode: Pipeline
  pipeline:
  - step: rotate-certificates
    functionRef:
      name: function-cert-rotation
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: CertRotationInput
      targetCertificates:
        matchLabels:
          rotate: "true"
```

## Advanced configuration

### Retry behavior

Operations automatically retry when they fail. Configure the retry limit to 
control how often attempts occur:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: resilient-operation
spec:
  retryLimit: 10  # Try up to 10 times before giving up (default: 5)
  mode: Pipeline
  pipeline:
  - step: flaky-task
    functionRef:
      name: function-flaky-task
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: FlakyTaskInput
      # Task that might fail due to temporary issues
      timeout: "30s"
```

**Retry behavior:**
- Each retry resets the entire pipeline - if step 2 of 3 fails, the retry 
  starts from step 1
- Operations use exponential backoff: 1&nbsp;s, 2&nbsp;s, 4&nbsp;s, 8&nbsp;s, 16&nbsp;s, 32&nbsp;s, then 60&nbsp;s 
  max
- Operations track the number of failures in `status.failures`
- After reaching `retryLimit`, the Operation becomes 
  `Succeeded=False`

### Credentials

Operations can provide credentials to functions through Secrets:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: secure-backup
spec:
  mode: Pipeline
  pipeline:
  - step: backup-with-credentials
    functionRef:
      name: function-backup
    credentials:
    - name: backup-creds
      source: Secret
      secretRef:
        namespace: crossplane-system
        name: backup-credentials
        key: api-key
    - name: database-creds
      source: Secret
      secretRef:
        namespace: crossplane-system
        name: database-credentials
        key: connection-string
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: BackupInput
      destination: s3://my-backup-bucket
```

### Multiple pipeline steps

Complex operations can use multiple pipeline steps:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: multi-step-deployment
spec:
  mode: Pipeline
  pipeline:
  - step: validate-config
    functionRef:
      name: function-validator
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: ValidatorInput
      configName: app-config
  - step: backup-current
    functionRef:
      name: function-backup
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: BackupInput
      target: current-deployment
  - step: deploy-new-version
    functionRef:
      name: function-deploy
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: DeployInput
      image: myapp:v2.0.0
      strategy: rollingUpdate
  - step: verify-health
    functionRef:
      name: function-health-check
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: HealthCheckInput
      timeout: 300s
      healthEndpoint: /health
```

### RBAC permissions

If your Operation needs to access resources that Crossplane doesn't have 
permissions for by default, create a ClusterRole that aggregates to 
Crossplane:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: operation-additional-permissions
  labels:
    rbac.crossplane.io/aggregate-to-crossplane: "true"
rules:
# Additional permissions for Operations
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "patch", "update"]
- apiGroups: [""]
  resources: ["persistentvolumes"]
  verbs: ["get", "list"]
# Add other resources your Operations need to access
```

This ClusterRole is automatically aggregated to Crossplane's main 
ClusterRole, giving the Crossplane service account the permissions needed 
for your Operations.

{{<hint "note">}}
The [RBAC manager]({{<ref "../guides/pods#rbac-manager-pod">}}) automatically
grants Crossplane access to Crossplane resources (MRs, XRs, etc.). You 
only need to create more ClusterRoles for other Kubernetes resources 
that your Operations need to access.

For more details on RBAC configuration, see the 
[Compositions RBAC documentation]({{<ref "../composition/compositions#grant-access-to-composed-resources">}}).
{{</hint>}}

### Required resources

Operations can preload resources for functions to access:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: resource-aware-operation
spec:
  mode: Pipeline
  pipeline:
  - step: process-deployment
    functionRef:
      name: function-processor
    requirements:
      requiredResources:
      - requirementName: app-deployment
        apiVersion: apps/v1
        kind: Deployment
        name: my-app
        namespace: production
      - requirementName: app-service
        apiVersion: v1
        kind: Service
        name: my-app-service
        namespace: production
    input:
      apiVersion: fn.crossplane.io/v1beta1
      kind: ProcessorInput
      action: upgrade
```

Functions access these resources through the standard request structure:

```python
from crossplane.function import request, response

def operate(req, rsp):
    # Access required resources
    deployment = request.get_required_resource(req, "app-deployment")
    service = request.get_required_resource(req, "app-service")
    
    if not deployment or not service:
        response.set_output(rsp, {"error": "Required resources not found"})
        return
    
    # Process the resources
    new_replicas = deployment["spec"]["replicas"] * 2
    
    # Return updated resources with full GVK and metadata for server-side apply
    rsp.desired.resources["app-deployment"].resource.update({
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": deployment["metadata"]["name"],
            "namespace": deployment["metadata"]["namespace"]
        },
        "spec": {"replicas": new_replicas}
    })
```

## Status and monitoring

Operations provide rich status information:

```yaml
status:
  conditions:
  - type: Synced
    status: "True"
    reason: ReconcileSuccess
  - type: Succeeded
    status: "True"
    reason: PipelineSuccess
  - type: ValidPipeline
    status: "True"
    reason: ValidPipeline
  failures: 1  # Number of retry attempts
  pipeline:
  - step: create-backup
    output:
      backupId: "backup-20240115-103000"
      size: "2.3GB"
  appliedResourceRefs:
  - apiVersion: "v1"
    kind: "Secret"
    namespace: "production"
    name: "backup-secret"
  - apiVersion: "apps/v1" 
    kind: "Deployment"
    name: "updated-deployment"
```

**Key status fields:**
- **Conditions**: Standard Crossplane conditions (Synced) and Operation-specific conditions:
  - **Succeeded**: `True` when the operation completed successfully, `False` when it failed
  - **ValidPipeline**: `True` when all functions have the required `operation` capability
- **Failures**: Number of times the operation has failed and retried
- **Pipeline**: Output from each function step for tracking progress
- **`AppliedResourceRefs`**: References to all resources the Operation created or modified

### Events

Operations emit Kubernetes events for important activities:
- Function run results and warnings
- Resource apply failures
- Operation lifecycle events (creation, completion, failure)

### Troubleshooting operations

**Select operation status:**

```shell
kubectl get operation my-operation -o wide
kubectl describe operation my-operation
```

**Common failure scenarios:**

1. **ValidPipeline condition is False** - Function doesn't support operations:
   ```yaml
   conditions:
   - type: ValidPipeline
     status: "False"
     reason: InvalidFunctionCapability
     message: "Function function-name doesn't support operations"
   ```
   *Solution*: use a function that declares `operation` capability.

2. **Succeeded condition is False** - Function run failed:
   ```yaml
   conditions:
   - type: Succeeded
     status: "False" 
     reason: PipelineFailure
     message: "Function returned error: connection timeout"
   ```
   *Solution*: view function logs and fix the underlying issue.

3. **Resource apply failures** - View events for details:
   ```shell
   kubectl get events --field-selector involvedObject.name=my-operation
   ```

**Debug function runs:**

```shell
# View function logs
kubectl logs -n crossplane-system deployment/function-python

# Check operation events
kubectl get events --field-selector involvedObject.kind=Operation

# Inspect operation status in detail
kubectl get operation my-operation -o jsonpath='{.status.pipeline}' | jq '.'
```

## Resource management

Operations can create or change any Kubernetes resources using server-side
apply with force ownership. This means:

**What Operations can do:**
- Create new resources of any kind
- Change existing resources by taking ownership of specific fields
- Apply changes that may conflict with other controllers

**What Operations can't do:**
- Delete resources (current limitation of alpha implementation)
- Establish owner references (resources aren't garbage collected)
- Continuously maintain desired state (they run once)

{{<hint "important">}}
Use caution with Operations that change resources managed by other controllers.
Operations force ownership when applying changes, which can cause conflicts.
{{</hint>}}

## Test an operation

You can preview the output of any Operation using the Crossplane CLI. You
don't need a Crossplane control plane to do this. The Crossplane CLI uses Docker
Engine to run functions.

{{<hint "tip">}}
See the [Crossplane CLI docs]({{<ref "../cli">}}) to
learn how to install and use the Crossplane CLI.
{{< /hint >}}

{{<hint "important">}}
Running `crossplane alpha render op` requires [Docker](https://www.docker.com).
{{< /hint >}}

Provide an operation, composition functions, and any required resources to render
the output locally.

```shell
crossplane alpha render op operation.yaml functions.yaml --required-resources=ingress.yaml
```

`crossplane alpha render op` prints the Operation status and any resources the
operation functions created or modified. It shows what would happen if you
applied the Operation to a cluster.

```yaml
---
# Operation status showing function results
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: ingress-cert-monitor
status:
  conditions:
  - type: Succeeded
    status: "True"
    reason: PipelineSuccess
  pipeline:
  - step: check-ingress-certificate
    output:
      certificateExpires: "Sep 29 08:34:02 2025 GMT"
      daysUntilExpiry: 53
      hostname: google.com
      ingressName: example-app
      status: ok
---
# Modified Ingress resource with certificate annotations
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-monitor.crossplane.io/expires: Sep 29 08:34:02 2025 GMT
    cert-monitor.crossplane.io/days-until-expiry: "53"
    cert-monitor.crossplane.io/status: ok
  name: example-app
  namespace: default
spec:
  # ... ingress spec unchanged
```

Use `--required-resources` to provide resources that your operation functions
need access to. You can specify multiple files or use glob patterns:

```shell
# Multiple specific files
crossplane alpha render op operation.yaml functions.yaml \
  --required-resources=deployment.yaml,service.yaml,configmap.yaml

# Glob pattern for all YAML files in a directory
crossplane alpha render op operation.yaml functions.yaml \
  --required-resources="resources/*.yaml"
```

{{<hint "tip">}}
Use the `crossplane alpha render op` command to test your Operations locally
before deploying them to a cluster. The command helps validate function logic 
and required resource access patterns.
{{</hint>}}

## Best practices

### Operation-specific practices

1. **Plan for rollback** - Design operations to be reversible when possible,
   because Operations don't auto rollback like Compositions
1. **Make operations idempotent** - Operations should be safe to retry if they
   fail partway through
1. **Use required resources** - Prepopulate functions with needed resources for
   efficiency rather than requesting them during running

### Function development

1. **Declare capabilities** - Explicitly declare `operation` capability in
   function metadata to enable Operations support
1. **Return meaningful output** - Use the output field to track what the
   operation accomplished for monitoring and debugging

## Next steps

- [Get started with Operations]({{<ref "../get-started/get-started-with-operations">}}) to create your first Operation
- Learn about [CronOperation]({{<ref "cronoperation">}}) for scheduled operations
- Learn about [WatchOperation]({{<ref "watchoperation">}}) for reactive operations
