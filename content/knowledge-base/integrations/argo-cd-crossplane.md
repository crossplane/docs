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
 
To configure Argo CD for Annotation resource tracking and Health Status, edit the `argocd-cm`

`ConfigMap` in the `argocd` `Namespace`. Add `application.resourceTrackingMethod: annotation`

to the data section as below:

```yaml
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

        if obj.status == nil or obj.status.conditions == nil then
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

        if obj.status == nil or obj.status.conditions == nil then
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
```

On the next Argo CD sync, Crossplane `Claims` and `Composite Resources` will

be considered synchronized with status and will not trigger auto-pruning.

Set the environment variable `ARGOCD_K8S_CLIENT_QPS` to `300` for improved compatibility with a large number of CRDs.
