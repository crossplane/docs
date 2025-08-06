---
title: WatchOperation
weight: 130
state: alpha
alphaVersion: 2.0
description: WatchOperations create Operations when watched resources change
---

A `WatchOperation` creates [Operations]({{<ref "operation">}}) when watched
Kubernetes resources change. Use WatchOperations for reactive operational
workflows such as backing up databases before deletion, validating
configurations after updates, or triggering alerts when resources fail.

<!-- vale Google.Headings = NO -->
## How WatchOperations work
<!-- vale Google.Headings = YES -->

WatchOperations watch specific Kubernetes resources and create new Operations
whenever those resources change. The changed resource is automatically injected
into the Operation for the function to process.

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: config-validator
spec:
  watch:
    apiVersion: v1
    kind: ConfigMap
    matchLabels:
      validate: "true"
  concurrencyPolicy: Allow
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: validate
        functionRef:
          name: function-config-validator
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: ConfigValidatorInput
          rules:
          - required: ["database.url", "database.port"]
          - format: "email"
            field: "notification.email"
      - step: notify
        functionRef:
          name: function-slack-notifier
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: SlackNotifierInput
          channel: "#alerts"
          severity: "warning"
```

{{<hint "important">}}
WatchOperations are an alpha feature. You must enable Operations by adding
`--enable-operations` to Crossplane's arguments.
{{</hint>}}

## Key features

- **Watches any Kubernetes resource type** - Not limited to Crossplane resources
- **Supports namespace and label filtering** - Target specific resources
- **Automatically injects changed resources** - Functions receive the triggering resource
- **Configurable concurrency policies** - Control operation creation

## Resource watching

WatchOperations can watch any Kubernetes resource with flexible filtering:

### Watch all resources of a type

```yaml
spec:
  watch:
    apiVersion: apps/v1
    kind: Deployment
```

### Watch resources in a specific namespace

```yaml
spec:
  watch:
    apiVersion: v1
    kind: ConfigMap
    namespace: production
```

### Watch resources with specific labels

```yaml
spec:
  watch:
    apiVersion: example.org/v1
    kind: Database
    matchLabels:
      backup: "enabled"
      environment: "production"
```

### Watch cluster-scoped resources

```yaml
spec:
  watch:
    apiVersion: v1
    kind: Node
    matchLabels:
      node-role.kubernetes.io/worker: ""
```

## Resource injection

When a WatchOperation creates an Operation, it automatically injects the 
changed
<!-- vale write-good.TooWordy = NO -->
resource using the special requirement name 
`ops.crossplane.io/watched-resource`.
<!-- vale write-good.TooWordy = YES -->
Functions can access this resource without explicitly requesting it.

For example, when a ConfigMap with label `validate: "true"` changes, the 
WatchOperation creates an Operation like this:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: Operation
metadata:
  name: config-validator-abc123
spec:
  mode: Pipeline
  pipeline:
  - step: validate
    functionRef:
      name: function-config-validator
    requirements:
      requiredResources:
      - requirementName: ops.crossplane.io/watched-resource
        apiVersion: v1
        kind: ConfigMap
        name: my-config
        namespace: default
    # ... other pipeline steps from operationTemplate
```

The watched resource is automatically available to functions in 
`req.required_resources` under the special name 
`ops.crossplane.io/watched-resource`.

## Concurrency policies

WatchOperations support the same concurrency policies as CronOperations:

- **Allow (default)**: Multiple Operations can run simultaneously. Use this 
  when operations don't interfere with each other.
- **Forbid**: New Operations don't start if previous ones are still running. 
  Use this for operations that can't run concurrently.
- **Replace**: New Operations stop running ones before starting. Use this 
  when you always want the latest operation to run.

## Common use cases

{{<hint "note">}}
The following examples use hypothetical functions for illustration. At launch,
only function-python supports operations.
{{</hint>}}

### Configuration validation

Validate ConfigMaps when they change:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: config-validator
spec:
  watch:
    apiVersion: v1
    kind: ConfigMap
    matchLabels:
      validate: "true"
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: validate-config
        functionRef:
          name: function-config-validator
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: ConfigValidatorInput
          rules:
          - required: ["database.host", "database.port"]
          - format: "email"
            field: "notification.email"
```

### Database backup on deletion

Backup databases before they're deleted:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: backup-on-deletion
spec:
  watch:
    apiVersion: rds.aws.crossplane.io/v1alpha1
    kind: Instance
    # Note: Watching for deletion requires function logic
    # to check deletion timestamp
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: create-backup
        functionRef:
          name: function-rds-backup
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: RDSBackupInput
          retentionDays: 30
```

### Resource failure alerting

Alert when resources enter a failed state:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: failure-alerts
spec:
  watch:
    apiVersion: example.org/v1
    kind: App
    matchLabels:
      alert: "enabled"
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: check-status
        functionRef:
          name: function-status-checker
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: StatusCheckerInput
          alertConditions:
          - type: "Ready"
            status: "False"
      - step: send-alert
        functionRef:
          name: function-alertmanager
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: AlertInput
          severity: "critical"
```

## Advanced configuration

### Advanced watch patterns

Complex resource watching with multiple conditions:

```yaml
# Watch Deployments in specific namespaces with multiple label conditions
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: multi-condition-watcher
spec:
  watch:
    apiVersion: apps/v1
    kind: Deployment
    namespace: production  # Only production namespace
    matchLabels:
      app.kubernetes.io/managed-by: "crossplane"
      environment: "prod"
      backup-required: "true"
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: backup-deployment
        functionRef:
          name: function-deployment-backup
```

```yaml
# Watch custom resources across all namespaces
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: database-lifecycle-manager
spec:
  watch:
    apiVersion: database.example.io/v1
    kind: PostgreSQLInstance
    # No namespace specified = watch all namespaces
    matchLabels:
      lifecycle-management: "enabled"
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: lifecycle-check
        functionRef:
          name: function-database-lifecycle
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: DatabaseLifecycleInput
          checkDeletionTimestamp: true
          autoBackup: true
```


### Cross-resource workflows

WatchOperations can watch one resource type and dynamically fetch related 
resources. Here's a WatchOperation that watches Ingresses and manages 
certificates:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: ingress-certificate-manager
spec:
  watch:
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    matchLabels:
      auto-cert: "enabled"
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: manage-certificates
        functionRef:
          name: function-cert-manager
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: CertManagerInput
          issuer: "letsencrypt-prod"
          renewBefore: "720h"  # 30 days
```

The function examines the watched Ingress and dynamically requests related resources:

```python
from crossplane.function import request, response

def operate(req, rsp):
    # Access the watched Ingress resource
    ingress = request.get_required_resource(req, "ops.crossplane.io/watched-resource")
    if not ingress:
        response.set_output(rsp, {"error": "No watched resource found"})
        return
    
    # Extract the service name from the Ingress backend
    rules = ingress.get("spec", {}).get("rules", [])
    if not rules:
        return
        
    backend = rules[0].get("http", {}).get("paths", [{}])[0].get("backend", {})
    service_name = backend.get("service", {}).get("name")
    if not service_name:
        return
        
    ingress_namespace = ingress.get("metadata", {}).get("namespace", "default")
    
    # Always declare what resources we need (requirements must be stable across calls)
    rsp.requirements.resources["related-service"].api_version = "v1"
    rsp.requirements.resources["related-service"].kind = "Service"
    rsp.requirements.resources["related-service"].match_name = service_name
    rsp.requirements.resources["related-service"].namespace = ingress_namespace
    
    # Process the service if Crossplane fetched it after our previous response
    service = request.get_required_resource(req, "related-service")
    if service:
        create_certificate_for_service(ingress, service, rsp)
```

This pattern allows functions to:
1. Examine the watched resource
2. Dynamically determine what other resources you need  
3. Request those resources in the next response
4. Process the more resources in next calls

## Status and monitoring

WatchOperations provide status information about watching:

```yaml
status:
  conditions:
  - type: Synced
    status: "True"
    reason: ReconcileSuccess
  - type: Watching
    status: "True"
    reason: WatchActive
  watchingResources: 12
  runningOperationRefs:
  - name: config-validator-anjda
  - name: config-validator-f0d92
```

**Key status fields:**
- **Conditions**: Standard Crossplane conditions (Synced) and WatchOperation-specific conditions:
  - **Watching**: `True` when the WatchOperation is actively watching resources, `False` when paused or failed
- **`watchingResources`**: Number of resources under watch
- **`runningOperationRefs`**: Running Operations created by this WatchOperation

### Events

WatchOperations emit events for important activities:
- `EstablishWatched` (Warning) - Watch establishment failures
- `TerminateWatched` (Warning) - Watch termination failures
- `GarbageCollectOperations` (Warning) - Operation cleanup failures
- `CreateOperation` (Warning) - Operation creation failures
- `ReplaceRunningOperation` (Warning) - Operation replacement failures

<!-- vale write-good.TooWordy = NO -->
### Monitoring
<!-- vale write-good.TooWordy = YES -->

<!-- vale write-good.TooWordy = NO -->
Monitor WatchOperations using:
<!-- vale write-good.TooWordy = YES -->

```shell
# Check WatchOperation status
kubectl get watchoperation my-watchop

# View recent Operations created by the WatchOperation
kubectl get operations -l crossplane.io/watchoperation=my-watchop

# Check watched resource count
kubectl describe watchoperation my-watchop

# Check events
kubectl get events --field-selector involvedObject.name=my-watchop
```


## Best practices

### Resource selection

1. **Use specific label selectors** - Prevent unnecessary Operations with 
   precise filtering
1. **Avoid high-churn resources** - Be careful watching frequently changing 
   resources
1. **Start small** - Begin with narrow selectors and expand as needed

### Event handling

1. **Implement event filtering** - Check generation, deletion timestamp, 
   and status conditions
   to avoid processing irrelevant changes
<!-- vale write-good.TooWordy = NO -->
1. **Monitor operation volume** - Popular resources can create numerous 
   Operations
<!-- vale write-good.TooWordy = YES -->

### Concurrency policies

1. **Choose appropriate concurrency policies**:
   - **Allow** for independent processing that can run in parallel
   - **Forbid** for operations that must complete before processing new 
     changes  
   - **Replace** for status-checking or monitoring where only latest state 
     matters

### History management

Like CronOperations, WatchOperations automatically clean up completed Operations:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: WatchOperation
metadata:
  name: config-validator
spec:
  watch:
    apiVersion: v1
    kind: ConfigMap
  successfulHistoryLimit: 10  # Keep 10 successful Operations (default: 3)
  failedHistoryLimit: 5       # Keep 5 failed Operations (default: 1)
  operationTemplate:
    # Operation template here
```

### Watched resource injection

<!-- vale write-good.TooWordy = NO -->
WatchOperations automatically inject the changed resource into the created 
Operation using a special requirement name 
`ops.crossplane.io/watched-resource`:
<!-- vale write-good.TooWordy = YES -->

```python
from crossplane.function import request, response

def operate(req, rsp):
    # Access the resource that triggered this Operation
    watched_resource = request.get_required_resource(req, "ops.crossplane.io/watched-resource")
    if not watched_resource:
        response.set_output(rsp, {"error": "No watched resource found"})
        return
    
    # Process based on the watched resource
    if watched_resource["kind"] == "ConfigMap":
        config_data = watched_resource["data"]
        # Validate configuration...
```

The watched resource is available in the function's `required_resources` map 
without needing to declare it in the Operation template.

For general Operations best practices including function development and 
operational considerations, see [Operation best practices]({{<ref "operation#best-practices">}}).

## Troubleshooting

<!-- vale Google.Headings = NO -->
### WatchOperation not creating Operations
<!-- vale Google.Headings = YES -->

1. Verify the WatchOperation has `Watching=True` condition
1. Check that watched resources exist and match the selector
1. Ensure resources are actually changing
1. Look for events indicating watch establishment failures

<!-- vale Google.Headings = NO -->
<!-- vale write-good.Weasel = NO -->
### Too many Operations created
<!-- vale write-good.Weasel = YES -->
<!-- vale Google.Headings = YES -->

1. Refine label selectors to match fewer resources
1. Consider using `Forbid` or `Replace` concurrency policy
1. Check if resources are changing more frequently than expected
1. Review function logic to ensure it's not causing resource updates

### Operations failing to process watched resources

1. Verify function capabilities include `operation`
1. Check that functions handle the `ops.crossplane.io/watched-resource`
1. Review function logs for processing errors
1. Ensure functions can handle the specific resource types under watch

## Next steps

- Learn about [Operation]({{<ref "operation">}}) for one-time operational tasks
- Learn about [CronOperation]({{<ref "cronoperation">}}) for scheduled operations
- [Get started with Operations]({{<ref "../get-started/get-started-with-operations">}}) to create your first reactive operation