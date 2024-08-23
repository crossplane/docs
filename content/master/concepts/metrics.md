---
title: Metrics
weight: 60
description: "Metrics are essential for monitoring Crossplane's operations, helping to quickly identify and resolve potential issues."
---

This page offers explanations of various metrics gathered from Crossplane, which are essential for effective monitoring and alerting within your Crossplane environment. 
Understanding these metrics will help you maintain the health and performance of your resources, ensuring that any issues can be quickly identified and addressed. 
Please note that this document focuses exclusively on Crossplane-specific metrics and does not cover standard Go metrics.


{{<table "table table-sm" >}}
| Metric Name | Description | Further Explanation |
| --- | --- | --- |
| {{<hover label="certwatcher_read_certificate_errors_total" line="1">}}certwatcher_read_certificate_errors_total{{</hover>}} | Total number of certificate read errors |  |
| {{<hover label="certwatcher_read_certificate_total" line="2">}}certwatcher_read_certificate_total{{</hover>}} | Total number of certificate reads |  |
| {{<hover label="composition_run_function_seconds_bucket" line="3">}}composition_run_function_seconds_bucket{{</hover>}} | Histogram of RunFunctionResponse latency (seconds) |  |
| {{<hover label="controller_runtime_active_workers" line="4">}}controller_runtime_active_workers{{</hover>}} | Number of currently used workers per controller | The number of threads that currently process jobs from the work queue. |
| {{<hover label="controller_runtime_max_concurrent_reconciles" line="5">}}controller_runtime_max_concurrent_reconciles{{</hover>}} | Maximum number of concurrent reconciles per controller | Describes how many reconciles can happen in parallel. |
| {{<hover label="controller_runtime_reconcile_errors_total" line="6">}}controller_runtime_reconcile_errors_total{{</hover>}} | Total number of reconciliation errors per controller | A counter that counts reconcile errors. Sharp or non-stop rising of this metric might be a problem. |
| {{<hover label="controller_runtime_reconcile_time_seconds_bucket" line="7">}}controller_runtime_reconcile_time_seconds_bucket{{</hover>}} | Length of time per reconciliation per controller |  |
| {{<hover label="controller_runtime_reconcile_total" line="8">}}controller_runtime_reconcile_total{{</hover>}} | Total number of reconciliations per controller |  |
| {{<hover label="controller_runtime_webhook_latency_seconds_bucket" line="9">}}controller_runtime_webhook_latency_seconds_bucket{{</hover>}} | Histogram of the latency of processing admission requests |  |
| {{<hover label="controller_runtime_webhook_requests_in_flight" line="10">}}controller_runtime_webhook_requests_in_flight{{</hover>}} | Current number of admission requests being served |  |
| {{<hover label="controller_runtime_webhook_requests_total" line="11">}}controller_runtime_webhook_requests_total{{</hover>}} | Total number of admission requests by HTTP status code |  |
| {{<hover label="rest_client_requests_total" line="12">}}rest_client_requests_total{{</hover>}} | Number of HTTP requests, partitioned by status code, method, and host |  |
| {{<hover label="workqueue_adds_total" line="13">}}workqueue_adds_total{{</hover>}} | Total number of adds handled by workqueue |  |
| {{<hover label="workqueue_depth" line="14">}}workqueue_depth{{</hover>}} | Current depth of workqueue |  |
| {{<hover label="workqueue_longest_running_processor_seconds" line="15">}}workqueue_longest_running_processor_seconds{{</hover>}} | How many seconds has the longest running processor for workqueue been running |  |
| {{<hover label="workqueue_queue_duration_seconds_bucket" line="16">}}workqueue_queue_duration_seconds_bucket{{</hover>}} | How long in seconds an item stays in workqueue before being requested | The time it takes from the moment a job is added to the workqueue until the processing of this job starts. |
| {{<hover label="workqueue_retries_total" line="17">}}workqueue_retries_total{{</hover>}} | Total number of retries handled by workqueue |  |
| {{<hover label="workqueue_unfinished_work_seconds" line="18">}}workqueue_unfinished_work_seconds{{</hover>}} | How many seconds of work has been done that is in progress and hasn't been observed by work_duration. Large values indicate stuck threads. |  |
| {{<hover label="workqueue_work_duration_seconds_bucket" line="19">}}workqueue_work_duration_seconds_bucket{{</hover>}} | How long in seconds processing an item from workqueue takes | The time it takes from the moment the job is picked up until it is finished (either successfully or with an error). |
| {{<hover label="crossplane_managed_resource_exists" line="20">}}crossplane_managed_resource_exists{{</hover>}} | The number of managed resources that exist |  |
| {{<hover label="crossplane_managed_resource_ready" line="21">}}crossplane_managed_resource_ready{{</hover>}} | The number of managed resources in Ready=True state |  |
| {{<hover label="crossplane_managed_resource_synced" line="22">}}crossplane_managed_resource_synced{{</hover>}} | The number of managed resources in Synced=True state |  |
| {{<hover label="upjet_resource_ext_api_duration_bucket" line="23">}}upjet_resource_ext_api_duration_bucket{{</hover>}} | Measures in seconds how long it takes a Cloud SDK call to complete |  |
| {{<hover label="upjet_resource_external_api_calls_total" line="24">}}upjet_resource_external_api_calls_total{{</hover>}} | The number of external API calls | The number of calls to cloud providers, with labels describing which endpoints resources have been queried. |
| {{<hover label="upjet_resource_reconcile_delay_seconds_bucket" line="25">}}upjet_resource_reconcile_delay_seconds_bucket{{</hover>}} | Measures in seconds how long the reconciles for a resource have been delayed from the configured poll periods |  |
| {{<hover label="crossplane_managed_resource_deletion_seconds_bucket" line="26">}}crossplane_managed_resource_deletion_seconds_bucket{{</hover>}} | The time it took for a managed resource to be deleted |  |
| {{<hover label="crossplane_managed_resource_first_time_to_readiness_seconds_bucket" line="27">}}crossplane_managed_resource_first_time_to_readiness_seconds_bucket{{</hover>}} | The time it took for a managed resource to become ready first time after creation |  |
| {{<hover label="crossplane_managed_resource_first_time_to_reconcile_seconds_bucket" line="28">}}crossplane_managed_resource_first_time_to_reconcile_seconds_bucket{{</hover>}} | The time it took for a managed resource to be detected by the controller |  |
| {{<hover label="upjet_resource_ttr_bucket" line="29">}}upjet_resource_ttr_bucket{{</hover>}} | Measures in seconds the time-to-readiness (TTR) for managed resources |  |
{{< /table >}}
