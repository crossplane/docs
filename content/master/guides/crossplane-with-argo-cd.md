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

### Configuring Argo CD with Crossplane

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
              return health_status
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
              return health_status
            end
          end
        end

        return health_status
```

#### Set resource exclusion

Crossplane providers generate a `ProviderConfigUsage` for each managed resource
(MR) they handle.
This resource represents the relationship between MR and a ProviderConfig.
The controller uses it as a finalizer when you delete a ProviderConfig.
End users of Crossplane don't need to interact with this resource.

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

#### Increase Kubernetes client QPS

As the number of CRDs grow on a control plane, Argo CD Application Controller
needs to send more queries to the Kubernetes API.
You can increase the rate limits of the Argo CD Kubernetes client to handle
this.

Set the environment variable `ARGOCD_K8S_CLIENT_QPS` to `300` for improved compatibility with multiple CRDs.

The default value of `ARGOCD_K8S_CLIENT_QPS` is 50, modifying the value also updates `ARGOCD_K8S_CLIENT_BURST` as it
is default to `ARGOCD_K8S_CLIENT_QPS` x 2.

