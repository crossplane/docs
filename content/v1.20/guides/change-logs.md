---
title: Change Logs
weight: 210
description: "Change logs help you audit all changes made to your resources"
state: alpha
alphaVersion: "1.17"
---

The "change logs" feature is designed to help users of Crossplane Providers to
understand what changes a provider is making to the resources it's managing.
Whenever a provider creates, updates, or deletes a managed resource, an entry
explaining the details of the change is recorded in the provider's change log.

Change logs are important for awareness of the changes that a provider is
making to its managed resources. Due to the nature of Crossplane's active
reconciliation, it's possible for a provider to make changes to managed
resources without any user interaction. Consider the scenario when someone
updates a resource outside of Crossplane, for example via the AWS console or
`gcloud` CLI. When Crossplane detects this configuration drift it will
enforce its source of truth to eventually correct this unexpected change
without any user interaction.

With Crossplane acting continuously and autonomously to update critical
infrastructure, it's vital for users to have insight into the operations being
performed, so they can build and maintain a strong sense of confidence and trust
in their control planes. Change logs provide details about all changes the
provider makes, so users can remain aware of any changes, even when they aren't
explicitly expecting any.

{{<hint "tip">}} Change logs help you understand all the changes a provider is
making to your resources, even when changes weren't explicitly requested, for
example as a result of Crossplane's automatic correction of configuration drift.
{{</hint>}}

## Enabling Change Logs

{{<hint "important" >}} Change logs are an alpha feature and must be explicitly
enabled for each provider through the use of a `DeploymentRuntimeConfig`.
{{</hint >}}

To enable change logs for a provider, use a `DeploymentRuntimeConfig` to
configure each provider pod that should start producing change logs. The
`DeploymentRuntimeConfig` has a few important configuration details:

1. A command line argument to the provider container that enables the change
   logs feature, for example `--enable-changelogs`.
1. A [side car container](https://github.com/crossplane/changelogs-sidecar) that
   collects change events and produces change log entries to the provider's pod
   logs.
1. A shared volume mounted to both the provider and sidecar containers that
   enables communication of change events between the two containers.

### Prerequisites

This guide assumes you have a control plane with [Crossplane installed]({{<ref "../software/install">}}).

It also assumes you have the [`jq` tool installed](https://jqlang.org/download/),
to perform lightweight querying and filtering of the content in the change logs.

The only other prerequisite for enabling change logs is that the provider must
have added support for the change logs feature. This is optional and not all
providers in the Crossplane ecosystem have added this support yet.

{{<hint "tip">}} Not all providers support the change logs feature. Check with
your provider of choice to confirm it has added support for change logs.
{{</hint>}}

This guide walks through a full example of generating change logs with
[`provider-kubernetes`](https://github.com/crossplane-contrib/provider-kubernetes).

### Create a `DeploymentRuntimeConfig`

Create a `DeploymentRuntimeConfig` that will enable change logs for
the provider when it's installed by performing the necessary configuration
steps:

1. The {{<hover label="drc" line="15">}}--enable-changelogs{{</hover>}} flag is
   set on the provider.
1. The {{<hover label="drc" line="19">}}sidecar container{{</hover>}} is added
   to the provider pod.
1. A {{<hover label="drc" line="24">}}shared volume{{</hover>}} is declared and
   then mounted in the {{<hover label="drc" line="16">}}provider
   container{{</hover>}} and the {{<hover label="drc" line="21">}}sidecar
   container{{</hover>}}.

```yaml {label="drc",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1beta1
kind: DeploymentRuntimeConfig
metadata:
  name: enable-changelogs
spec:
  deploymentTemplate:
    spec:
      selector: {}
      template:
        spec:
          containers:
          - name: package-runtime
            args:
            - --enable-changelogs
            volumeMounts:
            - name: changelogs-vol
              mountPath: /var/run/changelogs
          - name: changelogs-sidecar
            image: xpkg.crossplane.io/crossplane/changelogs-sidecar:v0.0.1
            volumeMounts:
            - name: changelogs-vol
              mountPath: /var/run/changelogs
          volumes:
          - name: changelogs-vol
            emptyDir: {}
  serviceAccountTemplate:
    metadata:
      name: provider-kubernetes
EOF
```

### Install the provider

Install the {{<hover label="provider" line="7">}}provider{{</hover>}} and
instruct it to use the {{<hover label="provider" line="8">}}DeploymentRuntimeConfig{{</hover>}}
that was just created.

```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-kubernetes
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-kubernetes:v0.18.0
  runtimeConfigRef:
    apiVersion: pkg.crossplane.io/v1beta1
    kind: DeploymentRuntimeConfig
    name: enable-changelogs
EOF
```

### Configure permissions

In order for the provider to create Kubernetes resources within the control
plane, it must be granted the appropriate permissions. This guide only creates a
`ConfigMap`, so only permissions for that resource type are needed.

{{<hint "important">}} This guide grants specific permissions to the provider
for example purposes. This approach isn't intended to be representative of a
production environment. More examples on configuring `provider-kubernetes` can
be found in its [examples directory](https://github.com/crossplane-contrib/provider-kubernetes/tree/main/examples/provider).
{{</hint>}}

```yaml {label="rbac",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: configmap-edit
rules:
  - apiGroups:
      - ""
    resources:
      - configmaps
    verbs:
      - "*"
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: provider-kubernetes-configmap-edit
subjects:
  - kind: ServiceAccount
    name: provider-kubernetes
    namespace: crossplane-system
roleRef:
  kind: ClusterRole
  name: configmap-edit
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: kubernetes.crossplane.io/v1alpha1
kind: ProviderConfig
metadata:
  name: default
spec:
  credentials:
    source: InjectedIdentity
EOF
```

### Create a resource

Now that the provider is installed and configured with change logs enabled,
create a resource that will generate change logs entries reflecting the actions
the control plane is taking.

```yaml {label="provider",copy-lines="all"}
cat <<EOF | kubectl apply -f -
apiVersion: kubernetes.crossplane.io/v1alpha2
kind: Object
metadata:
  name: configmap-for-changelogs
spec:
  forProvider:
    manifest:
      apiVersion: v1
      kind: ConfigMap
      metadata:
        namespace: default
        name: configmap-for-changelogs
      data:
        key-1: cool-value-1
EOF
```

### Examine the change logs

Check to see that the resource creation operation was recorded in the change
logs. Examine the pod logs for `provider-kubernetes`, specifically at the
`changelogs-sidecar` container:
```shell {label="changelogs-output-full",copy-lines="1"}
kubectl -n crossplane-system logs -l pkg.crossplane.io/provider=provider-kubernetes -c changelogs-sidecar | jq
{
  "timestamp": "2025-04-25T08:23:34Z",
  "provider": "provider-kubernetes:v0.18.0",
  "apiVersion": "kubernetes.crossplane.io/v1alpha2",
  "kind": "Object",
  "name": "configmap-for-changelogs",
  "externalName": "configmap-for-changelogs",
  "operation": "OPERATION_TYPE_CREATE",
  "snapshot": {
  ...(omitted for brevity)...
```

Each change log entry contains rich information about the state of the resource
when the change operation occurred. Since each entry is a structured `JSON`
object, they can be filtered and queried to find any subset of information you
are interested in:
```shell {label="changelogs-output-scoped",copy-lines="1-2"}
kubectl -n crossplane-system logs -l pkg.crossplane.io/provider=provider-kubernetes -c changelogs-sidecar \
  | jq '.timestamp + " " + .provider + " " + .kind + " " + .name + " " + .operation'
"2025-04-25T08:23:34Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_CREATE"
```

### Full lifecycle operations

In addition to change log entries that record the creation of resources, update
and delete operations will also generate corresponding change log entries.

Update the resource by patching its data field `key-1` with a new value
`cooler-value-2`:
```shell {label="object-patch",copy-lines="1-2"}
kubectl patch object configmap-for-changelogs --type=json \
  -p='[{"op": "replace", "path": "/spec/forProvider/manifest/data/key-1", "value": "cooler-value-2"}]'
object.kubernetes.crossplane.io/configmap-for-changelogs patched
```

Then, delete the object entirely:
```shell {label="object-delete",copy-lines="1"}
kubectl delete object configmap-for-changelogs
object.kubernetes.crossplane.io "configmap-for-changelogs" deleted
```

Check the change logs again to verify that both the update and delete operations
were recorded, and the full lifecycle of the object has been captured in the
change logs:
```shell {label="changelogs-output-final",copy-lines="1-2"}
kubectl -n crossplane-system logs -l pkg.crossplane.io/provider=provider-kubernetes -c changelogs-sidecar \
  | jq '.timestamp + " " + .provider + " " + .kind + " " + .name + " " + .operation'
"2025-04-25T08:23:34Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_CREATE"
"2025-04-25T08:24:21Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_UPDATE"
"2025-04-25T08:24:25Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_DELETE"
```