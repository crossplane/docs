---
title: Change Logs
weight: 210
description: "Change logs help you audit all changes made to your resources"
state: alpha
alphaVersion: "1.17"
---

The change logs feature helps users of Crossplane Providers understand what
changes a provider makes to the resources it manages. Whenever a provider
creates, updates, or deletes a managed resource, the provider records an entry
explaining the details of the change in its change log.

Change logs are important for awareness of the changes that a provider is
making to its managed resources. Due to the nature of Crossplane's active
reconciliation, it's possible for a provider to make changes to managed
resources without any user interaction. Consider the scenario when someone
updates a resource outside of Crossplane, for example via the AWS console or
`gcloud` CLI. When Crossplane detects this configuration drift, it
enforces the declared state and corrects the unexpected change
without any user interaction.

Crossplane acts continuously and autonomously to update critical
infrastructure.
Users need insight into the operations the provider performs to build and
maintain confidence and trust in their control planes.
Change logs provide details about all changes the provider makes.
This keeps users aware of any changes, even when they aren't explicitly
expecting any.

{{<hint "tip">}} Change logs help you understand all the changes a provider is
making to your resources.
This includes changes that weren't explicitly requested, such as Crossplane's
automatic correction of configuration drift.
{{</hint>}}

## Enabling change logs

{{<hint "important" >}} Change logs are an alpha feature and must be explicitly
enabled for each provider through the use of a `DeploymentRuntimeConfig`.
{{</hint >}}

To enable change logs for a provider, use a `DeploymentRuntimeConfig` to
configure each provider pod that should start producing change logs. The
`DeploymentRuntimeConfig` has several important configuration details:

1. A command line argument to the provider container that enables the change
   logs feature, for example `--enable-changelogs`.
1. A [side car container](https://github.com/crossplane/changelogs-sidecar) that
   collects change events and produces change log entries to the provider's pod
   logs.
1. A shared volume mounted to both the provider and sidecar containers that
   enables communication of change events between the two containers.

### Prerequisites

This guide assumes you have a control plane with [Crossplane installed]({{<ref "../get-started/install">}}).

It also assumes you have the [`jq` tool installed](https://jqlang.org/download/),
to perform lightweight querying and filtering of the content in the change logs.

The only other prerequisite for enabling change logs is provider support for the
change logs feature. Support for change logs is optional, and not all providers
in the Crossplane ecosystem have added it yet.

{{<hint "tip">}} Not all providers support the change logs feature. Check with
your provider of choice to confirm it has added support for change logs.
{{</hint>}}

This guide walks through a full example of generating change logs with
[`provider-kubernetes`](https://github.com/crossplane-contrib/provider-kubernetes).

### Create a `DeploymentRuntimeConfig`

Create a `DeploymentRuntimeConfig` that enables change logs for
the provider when it's installed by performing the following configuration
steps:

1. Set the {{<hover label="drc" line="15">}}--enable-changelogs{{</hover>}} flag on the provider.
1. Add the {{<hover label="drc" line="19">}}sidecar container{{</hover>}} to the provider pod.
1. Declare a {{<hover label="drc" line="24">}}shared volume{{</hover>}} and mount it in the {{<hover label="drc" line="16">}}provider
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

To allow the provider to create Kubernetes resources in the control
plane, grant the appropriate permissions. This guide only creates a
`ConfigMap`, so it only requires permissions for that resource type.

{{<hint "important">}} This guide grants specific permissions to the provider
for example purposes. This approach isn't intended to be representative of a
production environment. See more examples for configuring `provider-kubernetes` in its
[examples directory](https://github.com/crossplane-contrib/provider-kubernetes/tree/main/examples/namespaced/provider).
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

After installing and configuring the provider with change logs enabled, create
a resource that generates change log entries.
These entries reflect the actions the control plane takes.

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

Confirm that the change logs include the resource creation operation.
Examine the pod logs for `provider-kubernetes`, specifically the
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
when the change operation occurred. Because each entry is a structured `JSON`
object, you can filter and query them to find any subset of information that
interests you:
```shell {label="changelogs-output-scoped",copy-lines="1-2"}
kubectl -n crossplane-system logs -l pkg.crossplane.io/provider=provider-kubernetes -c changelogs-sidecar \
  | jq '.timestamp + " " + .provider + " " + .kind + " " + .name + " " + .operation'
"2025-04-25T08:23:34Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_CREATE"
```

### Full lifecycle operations

Update and delete operations also generate corresponding change log entries.

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

Check the change logs again to verify that they include both the update and delete operations and capture the
object's full lifecycle:
```shell {label="changelogs-output-final",copy-lines="1-2"}
kubectl -n crossplane-system logs -l pkg.crossplane.io/provider=provider-kubernetes -c changelogs-sidecar \
  | jq '.timestamp + " " + .provider + " " + .kind + " " + .name + " " + .operation'
"2025-04-25T08:23:34Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_CREATE"
"2025-04-25T08:24:21Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_UPDATE"
"2025-04-25T08:24:25Z provider-kubernetes:v0.18.0 Object configmap-for-changelogs OPERATION_TYPE_DELETE"
```