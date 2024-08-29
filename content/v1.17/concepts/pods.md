---
title: Crossplane Pods
weight: 1
description: Background on the components installed with Crossplane and their functions.
---

The base Crossplane installation consists of two pods, the `crossplane` pod and
the `crossplane-rbac-manager` pod. Both pods install in the `crossplane-system`
namespace by default. 


## Crossplane pod

### Init container
Before starting the core Crossplane container an _init_ container runs. The init
container installs the core Crossplane 
[Custom Resource Definitions](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions)
(`CRDs`), configures Crossplane webhooks and installs any supplied Providers or
Configurations. 

{{<hint "tip" >}}
The Kubernetes documentation contains more information about 
[init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/).
{{< /hint >}}

The settings the init container sets include installing Provider or Configuration 
packages with Crossplane, customizing the namespace Crossplane installs in and 
defining webhook configurations. 

The core CRDs installed by the init container include: 
* CompositeResourceDefinitions, Compositions, Configurations and Providers
* Locks to manage package dependencies
* DeploymentRuntimeConfigs to apply settings to installed Providers and Functions
* StoreConfigs for connecting external secret stores like 
[HashiCorp Vault](https://www.vaultproject.io/)

{{< hint "note" >}}

The [Install Crossplane]({{< ref "../software/install" >}}) section has more
information about customizing the Crossplane install.
{{< /hint >}}

The status `Init` on the Crossplane pod is the init container running. 

```shell
kubectl get pods -n crossplane-system
NAME                                       READY   STATUS     RESTARTS   AGE
crossplane-9f6d5cd7b-r9j8w                 0/1     Init:0/1   0          6s
```

The init container completes and starts the Crossplane core container 
automatically.

```shell
kubectl get pods -n crossplane-system
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-9f6d5cd7b-r9j8w                 1/1     Running   0          15s
```

### Core container

The main Crossplane container, called the _core_ container, enforces
the desired state of Crossplane resources, manages leader elections and process
webhooks. 

{{<hint "note" >}}
The Crossplane pod only reconciles core Crossplane components, including Claims
and composite resources. Providers are responsible for reconciling their managed
resources. 
{{< /hint >}}

#### Reconcile loop

The core container operates on a _reconcile loop_, constantly checking the 
status of deployed resources and correcting any "drift." After checking a 
resource Crossplane waits some time and checks again.

Crossplane monitors resources through a Kubernetes 
[_watch_](https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes)
or through periodic polling. Some resources may be both watched and polled. 

Crossplane requests that the API server notifies Crossplane of any changes on
objects. This notification tool is a _watch_. 

Watched objects include Providers, managed resources and 
CompositeResourceDefinitions.

For objects that Kubernetes can't provide a watch for, Crossplane
periodically poll the resource to find it's state. The default polling rate is
one minute. Change the polling rate with the `--poll-interval` pod argument.

Reducing the poll-interval value causes Crossplane to poll resources more
frequently. This increases the load of the Crossplane pod and
results in more frequent provider API calls.

<!-- vale write-good.TooWordy = NO -->
<!-- allow "maximum" -->
Increasing the poll-interval causes Crossplane to poll resources less
frequently. This increases the maximum time until Crossplane
discovers changes in the cloud provider that require updating. 
<!-- vale write-good.TooWordy = YES -->

Managed resources use polling.

{{< hint "note" >}}
Managed resources watch for Kubernetes events like deletion or changes to
their `spec`. Managed resources rely on polling to detect changes in the
external system.
{{< /hint >}}

Crossplane double-checks all resources to
confirm they're in the desired state. Crossplane does this every one hour by
default. Use the `--sync-interval` Crossplane pod argument to change this
interval. 

The `--max-reconcile-rate` rate defines the rate, in times per second, 
Crossplane reconciles resources. 

Reducing the `--max-reconcile-rate`, or making it smaller, reduces CPU 
resources Crossplane uses, but increases the amount of time until changed 
resources are fully synced. 

Increasing the `--max-reconcile-rate`, or making it larger, increases the
CPU resources Crossplane uses but allows Crossplane to reconcile all resources
faster. 

{{< hint "important" >}}
Most Providers use their own `--max-reconcile-rate`. This determines the
same settings for Providers and their managed resources. Applying the
`--max-reconcile-rate` to Crossplane only controls the rate for
core Crossplane resources. 
{{< /hint >}}

##### Enable real time Compositions

With real time compositions enabled Crossplane watches every composed resource
with a Kubernetes watch. Crossplane receives events from the
Kubernetes API server when a composed resource changes. For example, when
a provider sets the `Ready` condition to `true`.

{{<hint "important" >}}
Real time compositions are an alpha feature. Alpha features aren't enabled by
default. 
{{< /hint >}}

With real time compositions enabled, Crossplane doesn't use the `--poll-interval`
settings. 

Enable real time compositions support by
[changing the Crossplane pod setting]({{<ref "./pods#change-pod-settings">}})
and enabling  
{{<hover label="deployment" line="12">}}--enable-realtime-compositions{{</hover>}}
argument.

```yaml {label="deployment",copy-lines="12"}
$ kubectl edit deployment crossplane --namespace crossplane-system
apiVersion: apps/v1
kind: Deployment
spec:
# Removed for brevity
  template:
    spec:
      containers:
      - args:
        - core
        - start
        - --enable-realtime-compositions
```

{{<hint "tip" >}}

The [Crossplane install guide]({{<ref "../software/install#feature-flags">}})
describes enabling feature flags like
{{<hover label="deployment" line="12">}}--enable-realtime-compositions{{</hover>}}
with Helm.
{{< /hint >}}

##### Reconcile retry rate

The `--max-reconcile-rate` setting configures the number of times per second
Crossplane or a provider attempts to correct a resource. The default value is 
10 times per second.

All core Crossplane components share the reconcile rate. Each Provider
implements their own max reconcile rate setting. 

##### Number of reconcilers

The second value `--max-reconcile-rate` defines is the number of
resources that Crossplane can reconcile at once. If there are more resources than
the configured `--max-reconcile-rate` the remaining resources must wait until
Crossplane reconciles a an existing resource.

Read the [Change Pod Settings]({{<ref "#change-pod-settings">}}) section for
instructions on applying these settings. 

<!-- vale Microsoft.HeadingAcronyms = NO -->
<!-- allow 'RBAC' since that's the name -->
## RBAC manager pod
<!-- vale Microsoft.HeadingAcronyms = YES -->
The Crossplane RBAC manager pod automates required Kubernetes RBAC permissions
for Crossplane and Crossplane Providers. 

{{<hint "note" >}}
Crossplane installs and enables the RBAC manager by default.
Disabling the RBAC manager requires manual Kubernetes permissions definitions
for proper Crossplane operations. 

The 
[RBAC manager design document](https://github.com/crossplane/crossplane/blob/master/design/design-doc-rbac-manager.md) 
provides more comprehensive details on the Crossplane RBAC requirements.
{{< /hint >}}

### Disable the RBAC manager 

Disable the RBAC manager after installation by deleting the
`crossplane-rbac-manager` deployment from the `crossplane-system` namespace.

Disable the RBAC manager before installation by editing the Helm `values.yaml`
file, setting `rbacManager.deploy` to `false`.

{{< hint "note" >}}

Instructions for changing Crossplane pod settings during installation are in the
[Crossplane Install]({{<ref "../software/install">}}) section. 
{{< /hint >}}

<!-- vale Microsoft.HeadingAcronyms = NO -->
<!-- allow 'RBAC' since that's the name -->
### RBAC init container
<!-- vale Microsoft.HeadingAcronyms = YES -->

The RBAC manager requires the `CompositeResourceDefinition` and
`ProviderRevision` resources to be available before starting.

The RBAC manager init container waits for these resources before starting the 
main RBAC manager container. 

### RBAC manager container

The RBAC manager container preforms the following tasks:
* creating and binding RBAC roles to Provider ServiceAccounts, allowing 
  them to control their managed resources
* allowing the `crossplane` ServiceAccount to create managed resources
* creating ClusterRoles to access Crossplane resources in all namespaces

Use the [ClusterRoles]({{<ref "#crossplane-clusterroles">}}) to grant access to all Crossplane resources in the
cluster.  

#### Crossplane ClusterRoles

The RBAC manager creates four Kubernetes ClusterRoles. These Roles grant 
permissions over cluster wide Crossplane resources. 

<!-- vale Google.Headings = NO -->
<!-- disable heading checking for the role names -->
<!-- vale Google.WordList = NO -->
<!-- allow "admin" -->
##### crossplane-admin
<!-- vale Google.WordList = YES -->
<!-- vale Crossplane.Spelling = NO -->
The `crossplane-admin` ClusterRole has the following permissions:
  * full access to all Crossplane types
  * full access to all secrets and namespaces (even those unrelated to Crossplane)
  * read-only access to all cluster RBAC roles, CustomResourceDefinitions and
    events
  * ability to bind RBAC roles to other entities. 
<!-- vale Crossplane.Spelling = YES -->
View the full RBAC policy with 

```shell
kubectl describe clusterrole crossplane-admin
```

##### crossplane-edit

The `crossplane-edit` ClusterRole has the following permissions:

  * full access to all Crossplane types
  * full access to all secrets (even those unrelated to Crossplane)
  * read-only access to all namespaces and events (even those unrelated to Crossplane).

View the full RBAC policy with 

```shell
kubectl describe clusterrole crossplane-edit
```

##### crossplane-view

The `crossplane-view` ClusterRole has the following permissions:

  * read-only access to all Crossplane types
  * read-only access to all namespaces and events (even those unrelated to Crossplane).

View the full RBAC policy with 

```shell
kubectl describe clusterrole crossplane-view
```

##### crossplane-browse

The `crossplane-browse` ClusterRole has the following permissions:

  * read-only access to Crossplane compositions and XRDs. This allows resource claim
    creators to discover and select an appropriate composition.

View the full RBAC policy with 

```shell
kubectl describe clusterrole crossplane-browse
```

## Leader election

By default only a single Crossplane pod runs in a cluster. If more than one
Crossplane pod runs both pods try to manage Crossplane resources. To prevent
conflicts Crossplane uses a _leader election_ to have a single pod in control at
a time. Other Crossplane pods standby until the leader fails. 

{{< hint "note" >}}
It's possible to run more than one Crossplane or RBAC manager pods for 
redundancy.

Kubernetes restarts any failed Crossplane or RBAC manager pods.
Redundant pods aren't required in most deployments.
{{< /hint >}}

Both the Crossplane pod and the RBAC manager pods support leader elections.

Enable leader elections with the `--leader-election` pod argument.

{{< hint "warning" >}}
<!-- vale write-good.TooWordy = NO -->
<!-- "multiple" -->
<!-- vale write-good.Passive = NO -->
<!-- allow "is unsupported" --> 
Running multiple Crossplane pods without leader election is unsupported.
<!-- vale write-good.Passive = YES -->
<!-- vale write-good.TooWordy = YES -->
{{< /hint >}}


## Change pod settings

Change Crossplane pod settings either before installing Crossplane by editing
the Helm `values.yml` file or after installation by editing the `Deployment`.

The full list of 
[configuration options]({{<ref "../software/install#customize-the-crossplane-helm-chart">}}) 
and 
[feature flags]({{<ref "../software/install#customize-the-crossplane-helm-chart">}}) 
are available in the 
[Crossplane Install]({{<ref "../software/install">}}) 
section. 

{{< hint "note" >}}

Instructions for changing Crossplane pod settings during installation are in the
[Crossplane Install]({{<ref "../software/install">}}) section. 
{{< /hint >}}

### Edit the deployment
{{< hint "note" >}}
These settings apply to both the `crossplane` and `rbac-manager` pods and
`Deployments`.
{{< /hint >}}

To change the settings of an installed Crossplane pod, edit the `crossplane`
deployment in the `crossplane-system` namespace with the command

`kubectl edit deployment crossplane --namespace crossplane-system`

{{< hint "warning" >}}
Updating the Crossplane deployment restarts the Crossplane pod.
{{< /hint >}}

Add Crossplane pod arguments to the 
{{<hover label="args" line="9" >}}spec.template.spec.containers[].args{{< /hover >}}
section of the deployment.

For example, to change the `sync-interval` add 
{{<hover label="args" line="12" >}}--sync-interval=30m{{< /hover >}}.

```yaml {label="args", copy-lines="1"}
kubectl edit deployment crossplane --namespace crossplane-system
apiVersion: apps/v1
kind: Deployment
spec:
# Removed for brevity
  template:
    spec:
      containers:
      - args:
        - core
        - start
        - --sync-interval=30m
```

### Use environmental variables

The core Crossplane pod checks for configured environmental variables at startup
to change default settings. 

The full list of configurable environmental variables are available in the 
[Crossplane Install]({{<ref "../software/install">}}) section.
