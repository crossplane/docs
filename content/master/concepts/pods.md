---
title: Crossplane Pods
weight: 1
description: Background on the components installed with Crossplane and their functions.
---

The base Crossplane installation consists of two Pods, the `crossplane` pod and
the `rbac-manager` pod. Both pods install in the `crossplane-system`
namespace by default. 


## Crossplane pod

### Init pod
Before starting the core Crossplane pod an _init_ Pod runs. The init pod is
responsible for setting parameters related to the core Crossplane pod and
installing the core Crossplane 
[Custom Resource Definitions](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions)
(`CRDs`).

The settings the init pod sets include installing Provider or Configuration 
packages with Crossplane, customizing the namespace Crossplane installs in and 
defining webhook configurations. 

The core CRDs installed by the init pod include: 
* Composite Resource Definitions, Compositions, Configurations and Providers
* `locks` to manage package dependencies
* `controllerconfigs` to apply settings to installed Providers
* `storeconfigs` for connecting external secret stores like 
[Hashicorp Vault](https://www.vaultproject.io/)

{{< hint "note" >}}

The [Install Crossplane]({{< ref "../software/install" >}}) section has more
information about customizing the Crossplane install.
{{< /hint >}}

The init pod completes and starts the Crossplane core pod. 

### Core pod

The main Crossplane pod, called the _core_ pod, enforces
the desired state of Crossplane resources, manages leader elections and process
webhooks. 

#### Reconcile loop

The core pod operates on a _reconcile loop_, constantly checking the status of
deployed resources and correcting any "drift." After checking a resource
Crossplane waits some time and checks again.

{{<hint "note" >}}
The Crossplane pod only reconciles core Crossplane components, including Claims
and Composite Resources. Providers are responsible for reconciling their managed
resources. 
{{< /hint >}}

Crossplane monitors resources in one of two ways:
1. A Kubernetes _[watch](https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes)_
2. Periodic polling

Crossplane requests that Kubernetes notifies Crossplane of any changes on
objects. This notification tool is a _watch_. 

Watched objects include Providers and Composite Resource Definitions.

For objects that Kubernetes can't provide a watch for, Crossplane
periodically poll the resource to find it's state. The default polling rate is
one minute. Change the polling rate with the `---poll-interval` pod argument.

Managed resources use polling.

Crossplane checks all resources, both watched and polled resources, to
confirm they're in the desired state. Crossplane does this every one hour by
default. Use the `--sync-interval` Crossplane pod argument to change this
interval. 

The most that Crossplane acts on objects is the 
`--max-reconcile-rate` rate. This rate is 10 times per second by default.


<!-- vale Microsoft.HeadingAcronyms = NO -->
<!-- allow 'RBAC' since that's the name -->
## RBAC manager pod
<!-- vale Microsoft.HeadingAcronyms = YES -->
The Crossplane RBAC manager pod automates required Kubernetes RBAC permissions
for Crossplane and Crossplane Providers. 

{{<hint "note" >}}
Crossplane installs and enables the RBAC manager by default. You can disable the
RBAC manager pod.  
Disabling the RBAC manager requires manual Kubernetes permissions definitions
for proper Crossplane operations. 

The 
[RBAC manager design document](https://github.com/crossplane/crossplane/blob/master/design/design-doc-rbac-manager.md) 
provides more comprehensive details on the Crossplane RBAC requirements.
{{< /hint >}}

<!-- vale Microsoft.HeadingAcronyms = NO -->
<!-- allow 'RBAC' since that's the name -->
### RBAC init pod
<!-- vale Microsoft.HeadingAcronyms = YES -->

The RBAC manager requires the `CompositeResourceDefinition` and
`ProviderRevision` resources to be available before starting.

The RBAC manager init pod waits for these resources before starting the main 
RBAC manager pod. 


<!-- vale Microsoft.HeadingAcronyms = NO -->
<!-- allow 'RBAC' since that's the name -->
### RBAC manager pod
<!-- vale Microsoft.HeadingAcronyms = YES -->

The RBAC manager pod preforms the following tasks:
* creating and applying RBAC policies to Provider Service Accounts, allowing 
  them to control their managed resources
* allowing the `crossplane` Service Account to create managed resources
* creating and applying policies for Crossplane Composite Resources

When installing a Provider their service account needs permissions to create and 
manage managed resources. 

When creating Composite Resources the Crossplane service account needs
permissions for the newly created API endpoints. 

The RBAC manager pod manages these functions. 

The RBAC manager pod supports two policy options:
* `All` - The default policy, configures and manages all RBAC capabilities.
* `Basic` - Only manage policies related to Composite resources. 

Change from the default `All` to the `Basic` policy with the `-m Basic` pod 
argument.

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

{{<hint "important" >}}
Leader election applies to both the Crossplane pod and the RBAC manager pod.
{{< /hint >}}

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

Changing Crossplane pod settings either before installing Crossplane by editing
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
{{<hover label="args" line="7" >}}spec.template.spec.containers[].args{{< /hover >}}
section of the deployment.

For example, to change the `sync-interval` add 
{{<hover label="args" line="10" >}}--sync-interval=30m{{< /hover >}}.

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
