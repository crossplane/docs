---
title: Configuring Crossplane with Argo CD
weight: 270
description: "Deploy Crossplane resources with GitOps"
---

[Argo CD](https://argoproj.github.io/cd/) and [Crossplane](https://crossplane.io)
are a great combination. Argo CD provides GitOps while Crossplane turns any Kubernetes
cluster into a Universal Control Plane for all your resources. Configuration details are
required in order for the two to work together properly.
This doc will help you understand these requirements. It is recommended to use
Argo CD version 2.4.8 or later with Crossplane.

Argo CD synchronizes Kubernetes resource manifests stored in a Git repository
with those running in a Kubernetes cluster (GitOps). Argo CD has different ways to configure
how it tracks resources. With Crossplane, you need to configure Argo CD
to use Annotation based resource tracking. See the [Argo CD docs](https://argo-cd.readthedocs.io/en/latest/user-guide/resource_tracking/) for additional detail.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
### Configuring Argo CD with Crossplane
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

#### Set resource tracking method

In order for Argo CD to track Application resources that contain Crossplane related objects, configure it
to use the annotation mechanism.

To configure it, edit the `argocd-cm` `ConfigMap` in the `argocd` `Namespace` as such:
```yaml
apiVersion: v1
kind: ConfigMap
data:
  application.resourceTrackingMethod: annotation
```

#### Set health status

Argo CD has a built-in health assessment for Kubernetes resources. The community directly supports some checks
in Argo's [repository](https://github.com/argoproj/argo-cd/tree/master/resource_customizations). For example the `Provider`
from `pkg.crossplane.io` already exists which means there no further configuration needed.

Argo CD also enable customising these checks per instance, and that's the mechanism used to provide support
of Provider's CRDs.

To configure it, edit the `argocd-cm` `ConfigMap` in the `argocd` `Namespace`.
{{<hint "note">}}
{{<hover label="argocfg" line="22">}} ProviderConfig{{</hover>}} may have no status or a `status.users` field.
{{</hint>}}
```yaml {label="argocfg"}
apiVersion: v1
kind: ConfigMap
data:
  application.resourceTrackingMethod: annotation
  resource.customizations: |
    "*.upbound.io/*":
      health.lua: |
        health_status = {
          status = "Progressing",
          message = "Provisioning ..."
        }

        local function contains (table, val)
          for i, v in ipairs(table) do
            if v == val then
              return true
            end
          end
          return false
        end

        local has_no_status = {
          "ClusterProviderConfig",
          "ProviderConfig",
          "ProviderConfigUsage"
        }

        if obj.status == nil or next(obj.status) == nil and contains(has_no_status, obj.kind) then
          health_status.status = "Healthy"
          health_status.message = "Resource is up-to-date."
          return health_status
        end

        if obj.status == nil or next(obj.status) == nil or obj.status.conditions == nil then
          if (obj.kind == "ProviderConfig" or obj.kind == "ClusterProviderConfig") and obj.status.users ~= nil then
            health_status.status = "Healthy"
            health_status.message = "Resource is in use."
            return health_status
          end
          return health_status
        end

        for i, condition in ipairs(obj.status.conditions) do
          if condition.type == "LastAsyncOperation" then
            if condition.status == "False" then
              health_status.status = "Degraded"
              health_status.message = condition.message
              return health_status
            end
          end

          if condition.type == "Synced" then
            if condition.status == "False" then
              health_status.status = "Degraded"
              health_status.message = condition.message
              return health_status
            end
          end

          if condition.type == "Ready" then
            if condition.status == "True" then
              health_status.status = "Healthy"
              health_status.message = "Resource is up-to-date."
            end
          end
        end

        return health_status

    "*.crossplane.io/*":
      health.lua: |
        health_status = {
          status = "Progressing",
          message = "Provisioning ..."
        }

        local function contains (table, val)
          for i, v in ipairs(table) do
            if v == val then
              return true
            end
          end
          return false
        end

        local has_no_status = {
          "Composition",
          "CompositionRevision",
          "DeploymentRuntimeConfig",
          "ClusterProviderConfig",
          "ProviderConfig",
          "ProviderConfigUsage"
        }
        if obj.status == nil or next(obj.status) == nil and contains(has_no_status, obj.kind) then
            health_status.status = "Healthy"
            health_status.message = "Resource is up-to-date."
          return health_status
        end

        if obj.status == nil or next(obj.status) == nil or obj.status.conditions == nil then
          if (obj.kind == "ProviderConfig" or obj.kind == "ClusterProviderConfig") and obj.status.users ~= nil then
            health_status.status = "Healthy"
            health_status.message = "Resource is in use."
            return health_status
          end
          return health_status
        end

        for i, condition in ipairs(obj.status.conditions) do
          if condition.type == "LastAsyncOperation" then
            if condition.status == "False" then
              health_status.status = "Degraded"
              health_status.message = condition.message
              return health_status
            end
          end

          if condition.type == "Synced" then
            if condition.status == "False" then
              health_status.status = "Degraded"
              health_status.message = condition.message
              return health_status
            end
          end

          if contains({"Ready", "Healthy", "Offered", "Established", "ValidPipeline", "RevisionHealthy"}, condition.type) then
            if condition.status == "True" then
              health_status.status = "Healthy"
              health_status.message = "Resource is up-to-date."
            end
          end
        end

        return health_status
```

#### Set resource exclusion

Crossplane providers generate a `ProviderConfigUsage` for each managed resource (MR) they handle. This resource
enables representing the relationship between MR and a ProviderConfig so that the controller can use it as a finalizer when you delete a
ProviderConfig. End users of Crossplane don't need to interact with this resource.

A growing number of resources and types can impact Argo CD UI reactivity. To help keep this number low, Crossplane
recommend hiding all `ProviderConfigUsage` resources from Argo CD UI.

To configure resource exclusion edit the `argocd-cm` `ConfigMap` in the `argocd` `Namespace` as such:
```yaml
apiVersion: v1
kind: ConfigMap
data:
    resource.exclusions: |
      - apiGroups:
        - "*"
        kinds:
        - ProviderConfigUsage
```

The use of `"*"` as apiGroups enables the mechanism for all Crossplane Providers.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.HeadingAcronyms = NO -->
#### Increase Kubernetes client QPS
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.HeadingAcronyms = YES -->

As the number of CRDs grow on a control plane it increases the amount of queries Argo CD Application Controller
needs to send to the Kubernetes API. If this is the case you can increase the rate limits of the Argo CD Kubernetes client.

Set the environment variable `ARGOCD_K8S_CLIENT_QPS` to `300` for improved compatibility with multiple CRDs.

The default value of `ARGOCD_K8S_CLIENT_QPS` is 50, modifying the value also updates `ARGOCD_K8S_CLIENT_BURST` as it
is default to `ARGOCD_K8S_CLIENT_QPS` x 2.

#### Cross-namespace resource hierarchy

Argo CD versions before v3.3.0 have a limitation displaying namespaced resources owned by cluster-scoped resources in the application tree. This affects Crossplane deployments where cluster-scoped resources like `ProviderRevision` create namespaced children like `Deployment` and `Service` resources.

##### The issue

When viewing a Crossplane application in Argo CD versions before v3.3.0, cluster-scoped resources and their cluster-scoped children appear correctly, but namespaced children don't appear in the resource tree.

For example:
- ✅ `ProviderRevision` (cluster-scoped parent) appears
- ✅ `ClusterRole` (cluster-scoped child) appears  
- ❌ `Deployment` (namespaced child) is missing from the tree

This occurs because the gitops-engine's hierarchy traversal only processes resources within the same namespace, preventing cross-namespace parent-child relationships from being discovered.

{{<hint "important">}}
The missing resources are still deployed and managed by Argo CD. They just don't appear in the UI tree visualization.
{{</hint>}}

##### Example

```yaml
# This cluster-scoped parent appears in Argo CD
apiVersion: pkg.crossplane.io/v1
kind: ProviderRevision
metadata:
  name: provider-aws-s3-96df8f51090d

---
# This namespaced child is missing from the Argo CD tree
apiVersion: apps/v1
kind: Deployment
metadata:
  name: provider-aws-s3-96df8f51090d
  namespace: crossplane-system
  ownerReferences:
  - apiVersion: pkg.crossplane.io/v1
    kind: ProviderRevision
    name: provider-aws-s3-96df8f51090d
    controller: true
```

##### Resolution

This issue is fixed in Argo CD v3.3.0 and later. Upgrade to Argo CD v3.3.0 or later for full Crossplane resource visibility in the application tree.

After upgrading, verify the fix by expanding a `Provider` or `ProviderRevision` resource in the Argo CD UI and confirming that namespaced children like `Deployment` and `Service` resources now appear.

##### Workaround for older versions

If you can't upgrade to v3.3.0 immediately, use `kubectl` to verify namespaced resources:

```bash
# List all resources owned by a ProviderRevision
kubectl get all -n crossplane-system -l pkg.crossplane.io/revision=provider-aws-s3-96df8f51090d

# Check Deployments created by Providers
kubectl get deployments -n crossplane-system
```

GitOps synchronization, health status reporting, and automatic reconciliation continue to work correctly. Only the visual representation in the Argo CD UI is affected.

For more details, see [Argo CD issue #24379](https://github.com/argoproj/argo-cd/issues/24379) and [PR #24847](https://github.com/argoproj/argo-cd/pull/24847).
