---
title: Crossplane Pods
weight: 1
description: Background on the components installed with Crossplane and their functions.
---

The base Crossplane installation consists of two pods, the `crossplane` pod and
the `rbac-manager` pod. Both pods install in the `crossplane-system`
namespace by default. 


## Crossplane pod

### Init container
Before starting the core Crossplane container an _init_ container runs. The init
container sets parameters related to the core Crossplane container and
installing the core Crossplane 
[Custom Resource Definitions](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions)
(`CRDs`).

{{<hint "tip" >}}
The Kubernetes documentation contains more information about 
[init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/).
{{< /hint >}}

The settings the init container sets include installing Provider or Configuration 
packages with Crossplane, customizing the namespace Crossplane installs in and 
defining webhook configurations. 

The core CRDs installed by the init container include: 
* Composite Resource Definitions, Compositions, Configurations and Providers
* `locks` to manage package dependencies
* `controllerconfigs` to apply settings to installed Providers
* `storeconfigs` for connecting external secret stores like 
[Hashicorp Vault](https://www.vaultproject.io/)

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

#### Reconcile loop

The core container operates on a _reconcile loop_, constantly checking the 
status of deployed resources and correcting any "drift." After checking a 
resource Crossplane waits some time and checks again.

{{<hint "note" >}}
The Crossplane pod only reconciles core Crossplane components, including claims
and composite resources. Providers are responsible for reconciling their managed
resources. 
{{< /hint >}}

Crossplane monitors resources in one of two ways:
1. A Kubernetes _[watch](https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes)_
2. Periodic polling

Crossplane requests that Kubernetes notifies Crossplane of any changes on
objects. This notification tool is a _watch_. 

Watched objects include providers, managed resources and composite resource 
definitions.

For objects that Kubernetes can't provide a watch for, Crossplane
periodically poll the resource to find it's state. The default polling rate is
one minute. Change the polling rate with the `---poll-interval` pod argument.

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
provider environment.
{{< /hint >}}

Crossplane checks all resources, both watched and polled resources, to
confirm they're in the desired state. Crossplane does this every one hour by
default. Use the `--sync-interval` Crossplane pod argument to change this
interval. 

The `--max-reconcile-rate` rate defines two different settings at the same time:

* The global retry rate for checking failed objects.
* The number of threads created to reconcile resources.

Reducing the `--max-reconcile-rate`, or making it smaller, increases the
CPU resources Crossplane uses.

Increasing the `--max-reconcile-rate`, or making it larger, reduces CPU 
resources Crossplane uses, but increases the amount of time until changed 
resources are fully synced. 

{{< hint "important" >}}
Most providers use their own `--max-reconcile-rate`. This determines the
same settings for Providers and their managed resources. 
{{< /hint >}}
##### Reconcile retry rate

When Crossplane checks a resource and it's not in the desired
state they 100 times per second. If the resource is still not in the desired 
state Crossplane checks the `--max-reconcile-rate` times per second. By default,
the `--max-reconcile-rate` value of 10 means checking 10 times per second. 

{{< hint "note" >}}
Kubernetes defines the initial rate of 100 times per second. This isn't
configurable.
{{< /hint >}}

All core Crossplane components share the retry rate. Each Provider
implements their own retry rate. 

##### Number of reconcilers

The second value `--max-reconcile-rate` defines is the number of threads
created to reconcile resources. Each thread manages the reconciliation of a
specific resource. If there are more resources than configured threads,
remaining resources must wait until a new thread is available. 

Changing `--max-reconcile-rate` changes the number of threads Crossplane creates
when more than one resource need reconciliation.

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

<!-- vale Microsoft.HeadingAcronyms = NO -->
<!-- allow 'RBAC' since that's the name -->
### RBAC init container
<!-- vale Microsoft.HeadingAcronyms = YES -->

The RBAC manager requires the `CompositeResourceDefinition` and
`ProviderRevision` resources to be available before starting.

The RBAC manager init container waits for these resources before starting the 
main RBAC manager container. 


<!-- vale Microsoft.HeadingAcronyms = NO -->
<!-- allow 'RBAC' since that's the name -->
### RBAC manager container
<!-- vale Microsoft.HeadingAcronyms = YES -->

The RBAC manager container preforms the following tasks:
* creating and applying RBAC policies to Provider Service Accounts, allowing 
  them to control their managed resources
* allowing the `crossplane` Service Account to create managed resources
* creating and applying policies for Crossplane composite resources

When installing a Provider their service account needs permissions to create and 
manage managed resources. 

When creating composite resources the Crossplane service account needs
permissions for the newly created API endpoints. 

The RBAC manager container manages these functions. 

The RBAC manager pod supports two policy options:
* `All` - The default policy, configures and manages all RBAC capabilities.
* `Basic` - Only manage policies related to Composite resources. 

Use the `Basic` policy option when manually assigning RBAC policies to
Crossplane providers and provider resources. The RBAC manager still creates
cluster roles for composite resources. 

Change from the default `All` to the `Basic` policy with the `-m Basic` pod 
argument.

To control all RBAC roles and policies related to Crossplane resources and
providers, you can disable the RBAC manager. 

Disable the RBAC manager after installation by deleting the
`crossplane-rbac-manager` deployment from the `crossplane-system` namespace.

Disable the RBAC manager before installation by editing the Helm `values.yaml`
file, setting `rbacManager.deploy` to `false`.

{{< hint "note" >}}

Instructions for changing Crossplane pod settings during installation are in the
[Crossplane Install]({{<ref "../software/install">}}) section. 
{{< /hint >}}

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

The full list of configuration options are available in the 
[Crossplane Install]({{<ref "../software/install">}}) section. 

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
