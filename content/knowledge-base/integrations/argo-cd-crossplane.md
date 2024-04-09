---  
title: Configuring Crossplane with Argo CD
weight: 270
---  

[Argo CD](https://argoproj.github.io/cd/) and [Crossplane](https://crossplane.io)
are a great combination. Argo CD provides GitOps while Crossplane turns any Kubernetes
cluster into a Universal Control Plane for all of your resources. There are
configuration details required in order for the two to work together properly.
This doc will help you understand these requirements. It is recommended to use
Argo CD version 2.4.8 or later with Crossplane.
 
Argo CD synchronizes Kubernetes resource manifests stored in a Git repository
with those running in a Kubernetes cluster (GitOps). There are different ways to configure 
how Argo CD tracks resources. With Crossplane, you need to configure Argo CD 
to use Annotation based resource tracking. See the [Argo CD docs](https://argo-cd.readthedocs.io/en/latest/user-guide/resource_tracking/) for additional detail.
 
### Configuring Argo CD with Crossplane

#### Set Resource Tracking Method

In order for Argo CD to correctly track Application resources that contain Crossplane related objects it needs
to be configured to use the annotation mechanism.

To configure it, edit the `argocd-cm` `ConfigMap` in the `argocd` `Namespace` as such:
```yaml
apiVersion: v1
kind: ConfigMap
data:
  application.resourceTrackingMethod: annotation
```

#### Set Health Status

Argo CD has a built-in health assessment for Kubernetes resources. Some checks are supported by the community directly
in Argo's [repository](https://github.com/argoproj/argo-cd/tree/master/resource_customizations). For example the `Provider`
from `pkg.crossplane.io` has already been declared which means there no further configuration needed.

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
          "ProviderConfig",
          "ProviderConfigUsage"
        }

        if obj.status == nil or next(obj.status) == nil and contains(has_no_status, obj.kind) then
          health_status.status = "Healthy"
          health_status.message = "Resource is up-to-date."
          return health_status
        end

        if obj.status == nil or next(obj.status) == nil or obj.status.conditions == nil then
          if obj.kind == "ProviderConfig" and obj.status.users ~= nil then
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
          "ControllerConfig",
          "ProviderConfig",
          "ProviderConfigUsage"
        }
        if obj.status == nil or next(obj.status) == nil and contains(has_no_status, obj.kind) then
            health_status.status = "Healthy"
            health_status.message = "Resource is up-to-date."
          return health_status
        end

        if obj.status == nil or next(obj.status) == nil or obj.status.conditions == nil then
          if obj.kind == "ProviderConfig" and obj.status.users ~= nil then
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

          if contains({"Ready", "Healthy", "Offered", "Established"}, condition.type) then
            if condition.status == "True" then
              health_status.status = "Healthy"
              health_status.message = "Resource is up-to-date."
              return health_status
            end
          end
        end

        return health_status
```

#### Set Resource Exclusion

Crossplane providers generates a `ProviderConfigUsage` for each of the managed resource (MR) it handles. This resource
enable representing the relationship between MR and a ProviderConfig so that the controller can use it as finalizer when a
ProviderConfig is deleted. End-users of Crossplane are not expected to interact with this resource.

Argo CD UI reactivity can be impacted as the number of resource and types grow. To help keep this number low we
recommend hiding all `ProviderConfigUsage` resources from Argo CD UI.

To configure resource exclusion  edit the `argocd-cm` `ConfigMap` in the `argocd` `Namespace` as such:
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

The use of `"*"` as apiGroups will enable the mechanism for all Crossplane Providers.

#### Increase K8s Client QPS

As the number of CRDs grow on a control plane it will increase the amount of queries Argo CD Application Controller
needs to send to the Kubernetes API. If this is the case you can increase the rate limits of the Argo CD Kubernetes client.

Set the environment variable `ARGOCD_K8S_CLIENT_QPS` to `300` for improved compatibility with a large number of CRDs.

The default value of `ARGOCD_K8S_CLIENT_QPS` is 50, modifying the value will also update `ARGOCD_K8S_CLIENT_BURST` as it
is default to `ARGOCD_K8S_CLIENT_QPS` x 2.

