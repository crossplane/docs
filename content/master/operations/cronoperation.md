---
title: Cron Operations
weight: 120
state: alpha
alphaVersion: 2.0
description: Run function pipelines on a schedule
---

A `CronOperation` creates [Operations]({{<ref "operation">}}) on a schedule,
like Kubernetes CronJobs. Use CronOperations for recurring operational tasks
such as database backups, certificate rotation, or periodic maintenance.

<!-- vale Google.Headings = NO -->
## How CronOperations work
<!-- vale Google.Headings = YES -->

CronOperations contain a template for an Operation and create new Operations
based on a cron schedule. Each scheduled run creates a new Operation that
executes once to completion.

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: CronOperation
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  concurrencyPolicy: Forbid
  successfulHistoryLimit: 5
  failedHistoryLimit: 3
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: backup
        functionRef:
          name: function-database-backup
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: DatabaseBackupInput
          retentionDays: 7
```

{{<hint "important">}}
CronOperations are an alpha feature. You must enable Operations by adding
`--enable-operations` to Crossplane's arguments.
{{</hint>}}

## Key features

- **Standard cron scheduling syntax** - Uses the same format as Kubernetes CronJobs
- **Configurable concurrency policies** (Allow, Forbid, Replace)
- **Automatic cleanup of old Operations** - Maintains history limits
- **Tracks run history and running operations** - Provides visibility into scheduled runs

## Scheduling

CronOperations use standard cron syntax:

```console {linenos=false,copy-lines="none"}
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

**Common schedule examples:**
- `"0 2 * * *"` - Every day at 2:00 AM
- `"0 0 * * 0"` - Every Sunday at midnight
- `"0 0 1 * *"` - Every month on the first at midnight
- `"*/15 * * * *"` - Every 15 minutes

## Concurrency policies

CronOperations support three concurrency policies:

- **Allow (default)**: Multiple Operations can run simultaneously. Use this 
  when operations don't interfere with each other.
- **Forbid**: New Operations don't start if earlier ones are still running. 
  Use this for operations that can't run concurrently.
- **Replace**: New Operations stop running ones before starting. Use this 
  when you always want the latest operation to run.

## History management

Control the number of completed Operations to keep:

```yaml
spec:
  successfulHistoryLimit: 5  # Keep 5 successful operations
  failedHistoryLimit: 3      # Keep 3 failed operations for debugging
```

This helps balance debugging capabilities with resource usage.

## Common use cases

{{<hint "note">}}
The following examples use hypothetical functions for illustration. At launch,
only function-python supports operations.
{{</hint>}}

### Scheduled database backups

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: CronOperation
metadata:
  name: postgres-backup
spec:
  schedule: "0 3 * * *"  # Daily at 3 AM
  concurrencyPolicy: Forbid  # Don't allow overlapping backups
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: backup
        functionRef:
          name: function-postgres-backup
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: PostgresBackupInput
          instance: production-db
          s3Bucket: db-backups
```

### Scheduled maintenance

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: CronOperation
metadata:
  name: weekly-maintenance
spec:
  schedule: "0 3 * * 0"  # Weekly on Sunday at 3 AM
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: cleanup-logs
        functionRef:
          name: function-log-cleanup
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: LogCleanupInput
          retentionDays: 30
      - step: update-certificates
        functionRef:
          name: function-cert-renewal
```

### Periodic health checks

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: CronOperation
metadata:
  name: health-check
spec:
  schedule: "*/30 * * * *"  # Every 30 minutes
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: check-cluster-health
        functionRef:
          name: function-health-check
        input:
          apiVersion: fn.crossplane.io/v1beta1
          kind: HealthCheckInput
          alertThreshold: 80
```

## Advanced configuration

### Complex scheduling patterns

Advanced cron schedule examples for specific use cases:

```yaml
# Weekdays only at 9 AM (Monday-Friday)
schedule: "0 9 * * 1-5"

# Every 4 hours during business days
schedule: "0 8,12,16 * * 1-5"

# First and last day of each month
schedule: "0 2 1,L * *"

# Every quarter (1st of Jan, Apr, Jul, Oct)
schedule: "0 2 1 1,4,7,10 *"

# Business hours only, every 2 hours
schedule: "0 9-17/2 * * 1-5"
```

### Starting deadline

CronOperations support a `startingDeadlineSeconds` field that controls how 
long to wait after the scheduled time before considering it too late to 
create the Operation:

```yaml
apiVersion: ops.crossplane.io/v1alpha1
kind: CronOperation
metadata:
  name: deadline-example
spec:
  schedule: "0 9 * * 1-5"  # Weekdays at 9 AM
  startingDeadlineSeconds: 900  # 15 minutes
  operationTemplate:
    spec:
      mode: Pipeline
      pipeline:
      - step: morning-tasks
        functionRef:
          name: function-morning-tasks
```

If the Operation can't start in 15 minutes of 9 AM (due to 
controller downtime, resource constraints, etc.), the scheduled run is 
skipped.

Skip operations for:
- **Time-sensitive operations** - Skip operations that become meaningless if delayed
- **Resource protection** - Prevent backup Operations piling up during outages
- **SLA compliance** - Ensure operations run in acceptable time windows

### Time zone considerations

{{<hint "important">}}
CronOperations use the cluster's local time zone, same as Kubernetes CronJobs.
To ensure consistent scheduling across different environments, consider:

1. **Standardize cluster time zones** - Use UTC in production clusters
2. **Document time zone assumptions** - Note expected time zone in comments
3. **Account for DST changes** - Be aware that some schedules may skip or repeat during transitions
{{</hint>}}

## Status and monitoring

CronOperations provide status information about scheduling:

```yaml
status:
  conditions:
  - type: Synced
    status: "True"
    reason: ReconcileSuccess
  - type: Scheduling
    status: "True"
    reason: ScheduleActive
  lastScheduleTime: "2024-01-15T10:00:00Z"
  lastSuccessfulTime: "2024-01-15T10:02:30Z"
  runningOperationRefs:
  - name: daily-backup-1705305600
```

**Key status fields:**
- **Conditions**: Standard Crossplane conditions (Synced) and CronOperation-specific conditions:
  - **Scheduling**: `True` when the CronOperation is actively scheduling operations, `False` when paused or has wrong schedule syntax
- **`lastScheduleTime`**: When the CronOperation last created an Operation
- **`lastSuccessfulTime`**: When an Operation last completed successfully
- **`runningOperationRefs`**: Running Operations

### Events

CronOperations emit events for important activities:
- `CreateOperation` (Warning) - Scheduled operation creation failures
- `GarbageCollectOperations` (Warning) - Garbage collection failures
- `ReplaceRunningOperation` (Warning) - Running operation deletion failures
- `InvalidSchedule` (Warning) - Cron schedule parsing errors

<!-- vale write-good.TooWordy = NO -->
### Monitoring
<!-- vale write-good.TooWordy = YES -->

<!-- vale write-good.TooWordy = NO -->
Watch CronOperations using:
<!-- vale write-good.TooWordy = YES -->

```shell
# Check CronOperation status
kubectl get cronoperation my-cronop

# View recent Operations created by the CronOperation
kubectl get operations -l crossplane.io/cronoperation=my-cronop

# Check events
kubectl get events --field-selector involvedObject.name=my-cronop
```

## Best practices

### Scheduling considerations

1. **Consider time zones** - CronOperations use the host's local time 
   (same as Kubernetes CronJobs)
1. **Plan for long-running operations** - Ensure operations complete before 
   next scheduled run
1. **Set reasonable history limits** - Balance debugging needs with cluster 
   resource usage

### Concurrency policies

1. **Choose appropriate concurrency policies**:
   - **Forbid** for backups, maintenance, or operations that must complete 
     alone
   - **Replace** for health checks or monitoring where latest data is most 
     important
   - **Allow** for independent tasks that can run simultaneously

For general Operations best practices including function development and 
operational considerations, see [Operation best practices]({{<ref "operation#best-practices">}}).

## Troubleshooting

<!-- vale Google.Headings = NO -->
### CronOperation not creating Operations
<!-- vale Google.Headings = YES -->

1. Check the cron schedule syntax
1. Verify the CronOperation has `Synced=True` condition
1. Look for events indicating schedule parsing errors

### Operations failing often

1. Check Operation events and logs
1. Verify function capabilities include `operation`
1. Review retry limits and adjust as needed

### Resource cleanup issues

1. Verify you set history limits appropriately
1. Check for events about garbage collection failures

## Next steps

- Learn about [Operation]({{<ref "operation">}}) for one-time operational tasks
- Learn about [WatchOperation]({{<ref "watchoperation">}}) for reactive operations
- [Get started with Operations]({{<ref "../get-started/get-started-with-operations">}}) to try scheduling your first operation