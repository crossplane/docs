---
title: Troubleshoot Crossplane
weight: 306
---
## Requested Resource Not Found

If you use the Crossplane CLI to install a `Provider` or
`Configuration` (e.g. `crossplane install provider
xpkg.upbound.io/crossplane-contrib/provider-aws:v0.33.0`) and get `the server
could not find the requested resource` error, more often than not, that is an
indicator that the Crossplane CLI you're using is outdated. In other words
some Crossplane API has been graduated from alpha to beta or stable and the old
plugin is not aware of this change.


## Resource Status and Conditions

Most Crossplane resources have a `status` section that can represent the current
state of that particular resource. Running `kubectl describe` against a
Crossplane resource will frequently give insightful information about its
condition. For example, to determine the status of a GCP `CloudSQLInstance`
managed resource use `kubectl describe` for the resource.

```shell {copy-lines="1"}
kubectl describe cloudsqlinstance my-db
Status:
  Conditions:
    Last Transition Time:  2019-09-16T13:46:42Z
    Reason:                Creating
    Status:                False
    Type:                  Ready
```

Most Crossplane resources set the `Ready` condition. `Ready` represents the
availability of the resource - whether it is creating, deleting, available,
unavailable, binding, etc.

## Resource Events

Most Crossplane resources emit _events_ when something interesting happens. You
can see the events associated with a resource by running `kubectl describe` -
e.g. `kubectl describe cloudsqlinstance my-db`. You can also see all events in a
particular namespace by running `kubectl get events`.

```console
Events:
  Type     Reason                   Age                From                                                   Message
  ----     ------                   ----               ----                                                   -------
  Warning  CannotConnectToProvider  16s (x4 over 46s)  managed/postgresqlserver.database.azure.crossplane.io  cannot get referenced ProviderConfig: ProviderConfig.azure.crossplane.io "default" not found
```

> Note that events are namespaced, while many Crossplane resources (XRs, etc)
> are cluster scoped. Crossplane emits events for cluster scoped resources to
> the 'default' namespace.

## Crossplane Logs

The next place to look to get more information or investigate a failure would be
in the Crossplane pod logs, which should be running in the `crossplane-system`
namespace. To get the current Crossplane logs, run the following:

```shell
kubectl -n crossplane-system logs -lapp=crossplane
```

> Note that Crossplane emits few logs by default - events are typically the best
> place to look for information about what Crossplane is doing. You may need to
> restart Crossplane with the `--debug` flag if you can't find what you're
> looking for.

## Provider Logs

Remember that much of Crossplane's functionality is provided by providers. You
can use `kubectl logs` to view provider logs too. By convention, they also emit
few logs by default.

```shell
kubectl -n crossplane-system logs <name-of-provider-pod>
```

All providers maintained by the Crossplane community mirror Crossplane's support
of the `--debug` flag. The easiest way to set flags on a provider is to create a
`ControllerConfig` and reference it from the `Provider`:

```yaml
apiVersion: pkg.crossplane.io/v1alpha1
kind: ControllerConfig
metadata:
  name: debug-config
spec:
  args:
    - --debug
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.33.0
  controllerConfigRef:
    name: debug-config
```

> Note that a reference to a `ControllerConfig` can be added to an already
> installed `Provider` and it will update its `Deployment` accordingly.

## Compositions and composite resource definition

### General troubleshooting steps

Crossplane and its providers log most error messages to resources' event fields. Whenever your Composite Resources aren't getting provisioned, follow the following steps:

1. Get the events for the root resource using `kubectl describe` or `kubectl get event`
2. If there are errors in the events, address them.
3. If there are no errors, follow its sub-resources.

    `kubectl get <KIND> <NAME> -o=jsonpath='{.spec.resourceRef}{" "}{.spec.resourceRefs}' | jq`
4. Repeat this process for each resource returned.

{{< hint "note" >}}
The rest of this section show you how to debug issues related to compositions without using external tooling. 
If you are using ArgoCD or FluxCD with UI, you can visualize object relationships in the UI. 
You can also use the kube-lineage plugin to visualize object relationships in your terminal.
{{< /hint >}}

### Examples

#### Composition
<!-- vale Google.WordList = NO --> 
You deployed an example application using a claim. Kind = `ExampleApp`. Name = `example-application`.


The example application never reaches available state as shown below.


1. View the claim.

    ```bash
    kubectl describe exampleapp example-application

    Status:
    Conditions:
        Last Transition Time:  2022-03-01T22:57:38Z
        Reason:                Composite resource claim is waiting for composite resource to become Ready
        Status:                False
        Type:                  Ready
    Events:                    <none>
    ```

2. If the claim doesn't have errors, inspect the `.spec.resourceRef` field of the claim.

    ```bash
    kubectl get exampleapp example-application -o=jsonpath='{.spec.resourceRef}{" "}{.spec.resourceRefs}' | jq

    {
      "apiVersion": "awsblueprints.io/v1alpha1",
      "kind": "XExampleApp",
      "name": "example-application-xqlsz"
    }
    ```
3. In the preceding output, you see the cluster scoped resource for this claim. Kind = `XExampleApp` name = `example-application-xqlsz`
4. View the cluster scoped resource's events.

    ```bash
    kubectl describe xexampleapp example-application-xqlsz

    Events:
    Type     Reason                   Age               From                                                             Message
    ----     ------                   ----              ----                                                             -------
    Normal   PublishConnectionSecret  9s (x2 over 10s)  defined/compositeresourcedefinition.apiextensions.crossplane.io  Successfully published connection details
    Normal   SelectComposition        6s (x6 over 11s)  defined/compositeresourcedefinition.apiextensions.crossplane.io  Successfully selected composition
    Warning  ComposeResources         6s (x6 over 10s)  defined/compositeresourcedefinition.apiextensions.crossplane.io  can't render composed resource from resource template at index 3: can't use dry-run create to name composed resource: an empty namespace may not be set during creation
    Normal   ComposeResources         6s (x6 over 10s)  defined/compositeresourcedefinition.apiextensions.crossplane.io  Successfully composed resources
    ```
5. You see errors in the events. it's complaining about not specifying namespace in its compositions. For this particular kind of error, you can get its sub-resources and check which one isn't created.

    ```bash
    kubectl get xexampleapp example-application-xqlsz -o=jsonpath='{.spec.resourceRef}{" "}{.spec.resourceRefs}' | jq
    
    [
        {
            "apiVersion": "awsblueprints.io/v1alpha1",
            "kind": "XDynamoDBTable",
            "name": "example-application-xqlsz-6j9nm"
        },
        {
            "apiVersion": "awsblueprints.io/v1alpha1",
            "kind": "XIAMPolicy",
            "name": "example-application-xqlsz-lp9wt"
        },
        {
            "apiVersion": "awsblueprints.io/v1alpha1",
            "kind": "XIAMPolicy",
            "name": "example-application-xqlsz-btwkn"
        },
        {
            "apiVersion": "awsblueprints.io/v1alpha1",
            "kind": "IRSA"
        }
    ]
    ```
6. Notice the last element in the array doesn't have a name. When a resource in composition fails validation, the resource object isn't created and doesn't have a name. For this particular issue, you must specify the namespace for the IRSA resource.

#### Composite resource definition

Debugging Composite Resource Definition (XRD) is like debugging Compositions.

1. Get the XRD

    ```bash
    kubectl get xrd testing.awsblueprints.io

    NAME                       ESTABLISHED   OFFERED   AGE
    testing.awsblueprints.io                           66s
    ```
2. Notice its status it not established. You describe this XRD to get its events.

    ```bash
    kubectl describe xrd testing.awsblueprints.io

    Events:
    Type     Reason              Age                    From                                                             Message
    ----     ------              ----                   ----                                                             -------
    Normal   ApplyClusterRoles   3m19s (x3 over 3m19s)  rbac/compositeresourcedefinition.apiextensions.crossplane.io     Applied RBAC ClusterRoles
    Normal   RenderCRD           18s (x9 over 3m19s)    defined/compositeresourcedefinition.apiextensions.crossplane.io  Rendered composite resource CustomResourceDefinition
    Warning  EstablishComposite  18s (x9 over 3m19s)    defined/compositeresourcedefinition.apiextensions.crossplane.io  can't apply rendered composite resource CustomResourceDefinition: can't create object: CustomResourceDefinition.apiextensions.k8s.io "testing.awsblueprints.io" is invalid: metadata.name: Invalid value: "testing.awsblueprints.io": must be spec.names.plural+"."+spec.group
    ```
3. You see in the events that Crossplane can't generate corresponding CRDs for this XRD. In this case, ensure the name is `spec.names.plural+"."+spec.group`

#### Providers

You can use install providers in two ways: `configuration.pkg.crossplane.io` and `provider.pkg.crossplane.io`. You can use either one to install providers with no functional differences to providers themselves.
If you define a `configuration.pkg.crossplane.io` object, Crossplane creates a
`provider.pkg.crossplane.io` object and manages it. Refer to [the Packages
documentation]({{<ref "/master/concepts/packages">}})
for more information about Crossplane Packages.

If you are experiencing provider issues, steps below are a good starting point. 

1. Check the status of provider object. 
    ```bash
    kubectl describe provider.pkg.crossplane.io provider-aws

    Status:
        Conditions:
            Last Transition Time:  2022-08-04T16:19:44Z
            Reason:                HealthyPackageRevision
            Status:                True
            Type:                  Healthy
            Last Transition Time:  2022-08-04T16:14:29Z
            Reason:                ActivePackageRevision
            Status:                True
            Type:                  Installed
        Current Identifier:      crossplane/provider-aws:v0.29.0
        Current Revision:        provider-aws-a2e16ca2fc1a
    Events:
        Type    Reason                  Age                      From                                 Message
        ----    ------                  ----                     ----                                 -------
        Normal  InstallPackageRevision  9m49s (x237 over 4d17h)  packages/provider.pkg.crossplane.io  Successfully installed package revision
    ```
    In the output above you see that this provider is healthy. To get more information about this provider, you can dig deeper. The `Current Revision` field let you know of your next object to look at.


2. When you create a provider object, Crossplane creates a `ProviderRevision` object based on the contents of the OCI image. In this example, you're specifying the OCI image to be `crossplane/provider-aws:v0.29.0`. This image contains a YAML file which defines Kubernetes objects such as Deployment, ServiceAccount, and CRDs.
The `ProviderRevision` object creates resources necessary for a provider to function based on the contents of the YAML file. To inspect what's deployed as part of the provider package, you inspect the ProviderRevision object. The `Current Revision` field above indicates which ProviderRevision object this provider uses.

    ```bash
    kubectl get providerrevision provider-aws-a2e16ca2fc1a

    NAME                        HEALTHY   REVISION   IMAGE                             STATE    DEP-FOUND   DEP-INSTALLED   AGE
    provider-aws-a2e16ca2fc1a   True      1          crossplane/provider-aws:v0.29.0   Active                               19d
    ```

    When you describe the object, you find all CRDs managed by this object. 

    ```bash
    kubectl describe providerrevision provider-aws-a2e16ca2fc1a

    Status:
        Controller Ref:
            Name:  provider-aws-a2e16ca2fc1a
        Object Refs:
            API Version:  apiextensions.k8s.io/v1
            Kind:         CustomResourceDefinition
            Name:         natgateways.ec2.aws.crossplane.io
            UID:          5c36d1bc-61b8-44f8-bca0-47e368af87a9
            ....
    Events:
        Type    Reason             Age                    From                                         Message
        ----    ------             ----                   ----                                         -------
        Normal  SyncPackage        22m (x369 over 4d18h)  packages/providerrevision.pkg.crossplane.io  Successfully configured package revision
        Normal  BindClusterRole    15m (x348 over 4d18h)  rbac/providerrevision.pkg.crossplane.io      Bound system ClusterRole to provider ServiceAccount
        Normal  ApplyClusterRoles  15m (x364 over 4d18h)  rbac/providerrevision.pkg.crossplane.io      Applied RBAC ClusterRoles
    ```
    
    The event field also indicates any issues that may have occurred during this process.
    <!-- vale  Google.WordList = YES -->
3. If you don't see any errors in the event field above, you should check if Crossplane provisioned deployments and their status.

    ```bash
    kubectl get deployment -n crossplane-system

    NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
    crossplane                  1/1     1            1           105d
    crossplane-rbac-manager     1/1     1            1           105d
    provider-aws-a2e16ca2fc1a   1/1     1            1           19d

    kubectl get pods -n crossplane-system

    NAME                                         READY   STATUS    RESTARTS   AGE
    crossplane-54db688c8d-qng6b                  2/2     Running   0          4d19h
    crossplane-rbac-manager-5776c9fbf4-wn5rj     1/1     Running   0          4d19h
    provider-aws-a2e16ca2fc1a-776769ccbd-4dqml   1/1     Running   0          4d23h
    ```
    If there are any pods failing, check its logs and remedy the problem.


## Pausing Crossplane

Sometimes, for example when you encounter a bug, it can be useful to pause
Crossplane if you want to stop it from actively attempting to manage your
resources. To pause Crossplane without deleting all of its resources, run the
following command to simply scale down its deployment:

```bash
kubectl -n crossplane-system scale --replicas=0 deployment/crossplane
```

Once you have been able to rectify the problem or smooth things out, you can
unpause Crossplane simply by scaling its deployment back up:

```bash
kubectl -n crossplane-system scale --replicas=1 deployment/crossplane
```

## Pausing Providers

Providers can also be paused when troubleshooting an issue or orchestrating a
complex migration of resources. Creating and referencing a `ControllerConfig` is
the easiest way to scale down a provider, and the `ControllerConfig` can be
modified or the reference can be removed to scale it back up:

```yaml
apiVersion: pkg.crossplane.io/v1alpha1
kind: ControllerConfig
metadata:
  name: scale-config
spec:
  replicas: 0
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.upbound.io/crossplane-contrib/provider-aws:v0.33.0
  controllerConfigRef:
    name: scale-config
```

> Note that a reference to a `ControllerConfig` can be added to an already
> installed `Provider` and it will update its `Deployment` accordingly.

## Deleting When a Resource Hangs

The resources that Crossplane manages will automatically be cleaned up so as not
to leave anything running behind. This is accomplished by using finalizers, but
in certain scenarios the finalizer can prevent the Kubernetes object from
getting deleted.

To deal with this, we essentially want to patch the object to remove its
finalizer, which will then allow it to be deleted completely. Note that this
won't necessarily delete the external resource that Crossplane was managing, so
you will want to go to your cloud provider's console and look there for any
lingering resources to clean up.

In general, a finalizer can be removed from an object with this command:

```shell
kubectl patch <resource-type> <resource-name> -p '{"metadata":{"finalizers": []}}' --type=merge
```

For example, for a `CloudSQLInstance` managed resource (`database.gcp.crossplane.io`) named
`my-db`, you can remove its finalizer with:

```shell
kubectl patch cloudsqlinstance my-db -p '{"metadata":{"finalizers": []}}' --type=merge
```

## Tips, Tricks, and Troubleshooting

In this section we'll cover some common tips, tricks, and troubleshooting steps
for working with Composite Resources. If you're trying to track down why your
Composite Resources aren't working the [Troubleshooting][trouble-ref] page also
has some useful information.

### Troubleshooting Claims and XRs

Crossplane relies heavily on status conditions and events for troubleshooting.
You can see both using `kubectl describe` - for example:

```console
# Describe the PostgreSQLInstance claim named my-db
kubectl describe postgresqlinstance.database.example.org my-db
```

Per Kubernetes convention, Crossplane keeps errors close to the place they
happen. This means that if your claim is not becoming ready due to an issue with
your `Composition` or with a composed resource you'll need to "follow the
references" to find out why. Your claim will only tell you that the XR is not
yet ready.

To follow the references:

1. Find your XR by running `kubectl describe` on your claim and looking for its
   "Resource Ref" (aka `spec.resourceRef`).
1. Run `kubectl describe` on your XR. This is where you'll find out about issues
   with the `Composition` you're using, if any.
1. If there are no issues but your XR doesn't seem to be becoming ready, take a
   look for the "Resource Refs" (or `spec.resourceRefs`) to find your composed
   resources.
1. Run `kubectl describe` on each referenced composed resource to determine
   whether it is ready and what issues, if any, it is encountering.




<!-- Named Links -->
[Requested Resource Not Found]: #requested-resource-not-found
[install Crossplane CLI]: "../getting-started/install-configure"
[Resource Status and Conditions]: #resource-status-and-conditions
[Resource Events]: #resource-events
[Crossplane Logs]: #crossplane-logs
[Provider Logs]: #provider-logs
[Pausing Crossplane]: #pausing-crossplane
[Pausing Providers]: #pausing-providers
[Deleting When a Resource Hangs]: #deleting-when-a-resource-hangs
[Installing Crossplane Package]: #installing-crossplane-package
[Crossplane package]: /master/concepts/packages/
[Handling Crossplane Package Dependency]: #handling-crossplane-package-dependency
[semver spec]: https://github.com/Masterminds/semver#basic-comparisons


