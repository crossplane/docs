---
title: Metrics
weight: 60
description: "Track Crossplane operations with metrics"
---

Crossplane produces [Prometheus style metrics](https://prometheus.io/docs/introduction/overview/#what-are-metrics) for effective monitoring and alerting in your environment.
These metrics are essential for helping to identify and resolve potential issues.
This page offers explanations of all these metrics gathered from Crossplane.
Understanding these metrics helps you maintain the health and performance of your resources.
Please note that this document focuses on Crossplane specific metrics and doesn't cover standard Go metrics.

To enable the export of metrics it's necessary to configure the `--set metrics.enabled=true` option in the [helm chart](https://github.com/crossplane/crossplane/blob/main/cluster/charts/crossplane/README.md#configuration).
```yaml {label="value",copy-lines="none"}
metrics:
  enabled: true
```

These Prometheus annotations expose the metrics:
```yaml {label="deployment",copy-lines="none"}
prometheus.io/path: /metrics
prometheus.io/port: "8080"
prometheus.io/scrape: "true"
```

## Crossplane core metrics

The Crossplane pod emits these metrics.

{{< table "table table-hover table-striped table-sm">}}
| Metric Name | Description |
| --- | --- |
| {{<hover label="function_run_function_request_total" line="1">}}function_run_function_request_total{{</hover>}} | Total number of RunFunctionRequests sent |
| {{<hover label="function_run_function_response_total" line="2">}}function_run_function_response_total{{</hover>}} | Total number of RunFunctionResponses received |
| {{<hover label="function_run_function_seconds" line="3">}}function_run_function_seconds{{</hover>}} | Histogram of RunFunctionResponse latency (seconds) |
| {{<hover label="function_run_function_response_cache_hits_total" line="4">}}function_run_function_response_cache_hits_total{{</hover>}} | Total number of RunFunctionResponse cache hits |
| {{<hover label="function_run_function_response_cache_misses_total" line="5">}}function_run_function_response_cache_misses_total{{</hover>}} | Total number of RunFunctionResponse cache misses |
| {{<hover label="function_run_function_response_cache_errors_total" line="6">}}function_run_function_response_cache_errors_total{{</hover>}} | Total number of RunFunctionResponse cache errors |
| {{<hover label="function_run_function_response_cache_writes_total" line="7">}}function_run_function_response_cache_writes_total{{</hover>}} | Total number of RunFunctionResponse cache writes |
| {{<hover label="function_run_function_response_cache_deletes_total" line="8">}}function_run_function_response_cache_deletes_total{{</hover>}} | Total number of RunFunctionResponse cache deletes |
| {{<hover label="function_run_function_response_cache_bytes_written_total" line="9">}}function_run_function_response_cache_bytes_written_total{{</hover>}} | Total number of RunFunctionResponse bytes written to cache |
| {{<hover label="function_run_function_response_cache_bytes_deleted_total" line="10">}}function_run_function_response_cache_bytes_deleted_total{{</hover>}} | Total number of RunFunctionResponse bytes deleted from cache |
| {{<hover label="function_run_function_response_cache_read_seconds" line="11">}}function_run_function_response_cache_read_seconds{{</hover>}} | Histogram of cache read latency (seconds) |
| {{<hover label="function_run_function_response_cache_write_seconds" line="12">}}function_run_function_response_cache_write_seconds{{</hover>}} | Histogram of cache write latency (seconds) |
| {{<hover label="engine_controllers_started_total" line="13">}}engine_controllers_started_total{{</hover>}} | Total number of controllers started |
| {{<hover label="engine_controllers_stopped_total" line="14">}}engine_controllers_stopped_total{{</hover>}} | Total number of controllers stopped |
| {{<hover label="engine_watches_started_total" line="15">}}engine_watches_started_total{{</hover>}} | Total number of watches started |
| {{<hover label="engine_watches_stopped_total" line="16">}}engine_watches_stopped_total{{</hover>}} | Total number of watches stopped |
{{</table >}}

### Circuit breaker metrics

<!-- vale Crossplane.Spelling = NO -->
<!-- vale write-good.Passive = NO -->
The circuit breaker prevents reconciliation thrashing by monitoring and rate-limiting watch events per Composite Resource (XR). Crossplane core emits these metrics to help you identify and respond to excessive reconciliation activity.
<!-- vale write-good.Passive = YES -->
<!-- vale Crossplane.Spelling = YES -->

{{< table "table table-hover table-striped table-sm">}}
| Metric Name | Description |
| --- | --- |
| {{<hover label="circuit_breaker_opens_total" line="1">}}circuit_breaker_opens_total{{</hover>}} | Number of times the XR circuit breaker transitioned from closed to open |
| {{<hover label="circuit_breaker_closes_total" line="2">}}circuit_breaker_closes_total{{</hover>}} | Number of times the XR circuit breaker transitioned from open to closed |
| {{<hover label="circuit_breaker_events_total" line="3">}}circuit_breaker_events_total{{</hover>}} | Number of XR watch events handled by the circuit breaker, labeled by outcome |
{{</table >}}

All circuit breaker metrics include a `controller` label formatted as `composite/<plural>.<group>` (for example, `composite/xpostgresqlinstances.example.com`), providing visibility per XRD without creating high cardinality from individual XR instances.

<!-- vale Google.Headings = NO -->
<!-- vale Crossplane.Spelling = NO -->
#### circuit_breaker_opens_total
<!-- vale Crossplane.Spelling = YES -->
<!-- vale Google.Headings = YES -->

Tracks when a circuit breaker transitions from closed to open state. An increase indicates an XR is receiving excessive watch events and has triggered throttling.

**Use this metric to:**
- Alert on XRs experiencing reconciliation thrashing
- Identify which XRD types are prone to excessive watch events
- Track the frequency of circuit breaker activations

<!-- vale Crossplane.Spelling = NO -->
**Example PromQL queries:**
<!-- vale Crossplane.Spelling = YES -->
```promql
# Rate of circuit breaker opens over 5 minutes
rate(circuit_breaker_opens_total[5m])

# Count of circuit breaker opens by controller
sum by (controller) (circuit_breaker_opens_total)
```

<!-- vale Google.Headings = NO -->
<!-- vale Crossplane.Spelling = NO -->
#### circuit_breaker_closes_total
<!-- vale Crossplane.Spelling = YES -->
<!-- vale Google.Headings = YES -->

Tracks when a circuit breaker transitions from open to closed state. This indicates an XR has recovered from excessive watch events and returned to normal operation.

**Use this metric to:**
<!-- vale write-good.TooWordy = NO -->
- Monitor recovery from reconciliation thrashing
<!-- vale write-good.TooWordy = YES -->
<!-- vale Crossplane.Spelling = NO -->
- Verify circuit breakers are closing after cooldown periods
<!-- vale Crossplane.Spelling = YES -->
- Track circuit breaker lifecycle

<!-- vale Google.Headings = NO -->
<!-- vale Crossplane.Spelling = NO -->
#### circuit_breaker_events_total
<!-- vale Crossplane.Spelling = YES -->
<!-- vale Google.Headings = YES -->

Tracks all watch events processed by the circuit breaker, labeled by `result`:
<!-- vale write-good.Passive = NO -->
- `Allowed`: Normal operation when circuit is closed - events proceed to reconciliation
<!-- vale write-good.Passive = YES -->
- `Dropped`: Events blocked when circuit is fully open - indicates active throttling
<!-- vale Crossplane.Spelling = NO -->
- `HalfOpenAllowed`: Limited probe events when circuit is half-open - circuit is testing for recovery
<!-- vale Crossplane.Spelling = YES -->

**Use this metric to:**
- Track the volume of watch events per XR type
- Detect when the circuit drops events (active throttling)
- Alert on high dropped event rates indicating potential issues
- Understand reconciliation pressure on specific controllers

<!-- vale Crossplane.Spelling = NO -->
**Example PromQL queries:**
<!-- vale Crossplane.Spelling = YES -->
```promql
# Rate of dropped events (active throttling), aggregated per controller
sum by (controller) (
  rate(circuit_breaker_events_total{result="Dropped"}[5m])
)

# Percentage of events being dropped
sum by (controller) (rate(circuit_breaker_events_total{result="Dropped"}[5m]))
/
sum by (controller) (rate(circuit_breaker_events_total[5m])) * 100

# Number of replicas per controller currently dropping events
count by (controller) (
  rate(circuit_breaker_events_total{result="Dropped"}[5m]) > 0
)

# Estimated number of circuit breaker opens over 5 minutes
sum by (controller) (
  increase(circuit_breaker_opens_total[5m])
)

# Alert condition: controllers under high watch pressure (severe overload)
sum by (controller) (
  rate(circuit_breaker_events_total{result="Dropped"}[5m])
) > 1
```

**Recommended alerts:**
```yaml
# Alert when circuit breaker is consistently dropping events
- alert: CircuitBreakerDropRatioHigh
  expr: |
    (
      sum by (controller)(rate(circuit_breaker_events_total{result="Dropped"}[5m]))
      /
      sum by (controller)(rate(circuit_breaker_events_total[5m]))
    ) > 0.2
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High circuit breaker drop ratio for {{ $labels.controller }}"
    description: "More than 20% of events are being dropped by the circuit breaker for {{ $labels.controller }}, indicating sustained overload."

# Alert when circuit breaker opens frequently
- alert: CircuitBreakerFrequentOpens
  expr: |
    sum by (controller) (
      rate(circuit_breaker_opens_total[5m])
    ) * 3600 > 6
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "Frequent circuit breaker opens for {{ $labels.controller }}"
    description: "Circuit breaker for {{ $labels.controller }} is opening more than 6 times per hour, indicating reconciliation thrashing."
```

For more information on the circuit breaker feature and configuration, see [Troubleshooting - Circuit breaker]({{< ref "troubleshoot-crossplane#circuit-breaker-for-reconciliation-thrashing" >}}).

## Provider metrics

Crossplane providers emit these metrics. All providers built with crossplane-runtime emit the `crossplane_managed_resource_*` metrics.

Providers expose metrics on the `metrics` port (default `8080`). To scrape these metrics, configure a `PodMonitor` or add Prometheus annotations to the provider's `DeploymentRuntimeConfig`.

{{< table "table table-hover table-striped table-sm">}}
| Metric Name | Description |
| --- | --- |
| {{<hover label="crossplane_managed_resource_exists" line="1">}}crossplane_managed_resource_exists{{</hover>}} | The number of managed resources that exist |
| {{<hover label="crossplane_managed_resource_ready" line="2">}}crossplane_managed_resource_ready{{</hover>}} | The number of managed resources in `Ready=True` state |
| {{<hover label="crossplane_managed_resource_synced" line="3">}}crossplane_managed_resource_synced{{</hover>}} | The number of managed resources in `Synced=True` state |
| {{<hover label="crossplane_managed_resource_deletion_seconds" line="4">}}crossplane_managed_resource_deletion_seconds{{</hover>}} | The time it took to delete a managed resource |
| {{<hover label="crossplane_managed_resource_first_time_to_readiness_seconds" line="5">}}crossplane_managed_resource_first_time_to_readiness_seconds{{</hover>}} | The time it took for a managed resource to become ready first time after creation |
| {{<hover label="crossplane_managed_resource_first_time_to_reconcile_seconds" line="6">}}crossplane_managed_resource_first_time_to_reconcile_seconds{{</hover>}} | The time it took to detect a managed resource by the controller |
| {{<hover label="crossplane_managed_resource_drift_seconds" line="7">}}crossplane_managed_resource_drift_seconds{{</hover>}} | Time elapsed after the last successful reconcile when detecting an out-of-sync resource |
{{</table >}}

## Upjet provider metrics

These metrics are only emitted by Upjet-based providers (such as [provider-upjet-aws](https://github.com/crossplane-contrib/provider-upjet-aws), [provider-upjet-azure](https://github.com/crossplane-contrib/provider-upjet-azure), [provider-upjet-gcp](https://github.com/crossplane-contrib/provider-upjet-gcp)).

{{< table "table table-hover table-striped table-sm">}}
| Metric Name | Description |
| --- | --- |
| {{<hover label="upjet_resource_ext_api_duration" line="1">}}upjet_resource_ext_api_duration{{</hover>}} | Measures in seconds how long it takes a Cloud SDK call to complete |
| {{<hover label="upjet_resource_external_api_calls_total" line="2">}}upjet_resource_external_api_calls_total{{</hover>}} | The number of external API calls to cloud providers, with labels describing the endpoints and resources |
| {{<hover label="upjet_resource_reconcile_delay_seconds" line="3">}}upjet_resource_reconcile_delay_seconds{{</hover>}} | Measures in seconds how long the reconciles for a resource delay from the configured poll periods |
| {{<hover label="upjet_resource_ttr" line="4">}}upjet_resource_ttr{{</hover>}} | Measures in seconds the time-to-readiness (TTR) for managed resources |
| {{<hover label="upjet_resource_cli_duration" line="5">}}upjet_resource_cli_duration{{</hover>}} | Measures in seconds how long it takes a Terraform CLI invocation to complete |
| {{<hover label="upjet_resource_active_cli_invocations" line="6">}}upjet_resource_active_cli_invocations{{</hover>}} | The number of active (running) Terraform CLI invocations |
| {{<hover label="upjet_resource_running_processes" line="7">}}upjet_resource_running_processes{{</hover>}} | The number of running Terraform CLI and Terraform provider processes |
{{</table >}}

## Controller-runtime and Kubernetes client metrics

These metrics come from the controller-runtime framework and Kubernetes client libraries. Both Crossplane and providers emit these metrics.

{{< table "table table-hover table-striped table-sm">}}
| Metric Name | Description |
| --- | --- |
| {{<hover label="certwatcher_read_certificate_errors_total" line="1">}}certwatcher_read_certificate_errors_total{{</hover>}} | Total number of certificate read errors |
| {{<hover label="certwatcher_read_certificate_total" line="2">}}certwatcher_read_certificate_total{{</hover>}} | Total number of certificate reads |
| {{<hover label="controller_runtime_active_workers" line="3">}}controller_runtime_active_workers{{</hover>}} | Number of workers (threads processing jobs from the work queue) per controller |
| {{<hover label="controller_runtime_max_concurrent_reconciles" line="4">}}controller_runtime_max_concurrent_reconciles{{</hover>}} | Maximum number of concurrent reconciles per controller |
| {{<hover label="controller_runtime_reconcile_errors_total" line="5">}}controller_runtime_reconcile_errors_total{{</hover>}} | Total number of reconciliation errors per controller. Sharp or continuous rising of this metric indicates a problem. |
| {{<hover label="controller_runtime_reconcile_time_seconds" line="6">}}controller_runtime_reconcile_time_seconds{{</hover>}} | Histogram of time per reconciliation per controller |
| {{<hover label="controller_runtime_reconcile_total" line="7">}}controller_runtime_reconcile_total{{</hover>}} | Total number of reconciliations per controller |
| {{<hover label="controller_runtime_webhook_latency_seconds" line="8">}}controller_runtime_webhook_latency_seconds{{</hover>}} | Histogram of the latency of processing admission requests |
| {{<hover label="controller_runtime_webhook_requests_in_flight" line="9">}}controller_runtime_webhook_requests_in_flight{{</hover>}} | Current number of admission requests served |
| {{<hover label="controller_runtime_webhook_requests_total" line="10">}}controller_runtime_webhook_requests_total{{</hover>}} | Total number of admission requests by HTTP status code |
| {{<hover label="rest_client_requests_total" line="11">}}rest_client_requests_total{{</hover>}} | Number of HTTP requests, partitioned by status code, method, and host |
| {{<hover label="workqueue_adds_total" line="12">}}workqueue_adds_total{{</hover>}} | Total number of adds handled by `workqueue` |
| {{<hover label="workqueue_depth" line="13">}}workqueue_depth{{</hover>}} | Current depth of `workqueue` |
| {{<hover label="workqueue_longest_running_processor_seconds" line="14">}}workqueue_longest_running_processor_seconds{{</hover>}} | How long the longest running processor for `workqueue` has been running |
| {{<hover label="workqueue_queue_duration_seconds" line="15">}}workqueue_queue_duration_seconds{{</hover>}} | Histogram of time an item stays in `workqueue` before processing starts |
| {{<hover label="workqueue_retries_total" line="16">}}workqueue_retries_total{{</hover>}} | Total number of retries handled by `workqueue` |
| {{<hover label="workqueue_unfinished_work_seconds" line="17">}}workqueue_unfinished_work_seconds{{</hover>}} | Seconds of work in progress not yet observed by `work_duration`. Large values suggest stuck threads. |
| {{<hover label="workqueue_work_duration_seconds" line="18">}}workqueue_work_duration_seconds{{</hover>}} | Histogram of time to process an item from `workqueue` (from start to completion) |
{{</table >}}
