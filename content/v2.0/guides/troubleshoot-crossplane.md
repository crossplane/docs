---
title: Troubleshoot Crossplane
weight: 306
---
## Requested resource not found

If you use the Crossplane CLI to install a `Provider` or
`Configuration` (for example, `crossplane xpkg install provider
xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v1.21.1`) and get `the server
could not find the requested resource` error, more often than not, that's an
indicator that your Crossplane CLI needs updating. In other words
Crossplane graduated some API from alpha to beta or stable and the old
plugin isn't aware of this change.


## Resource status and conditions

Most Crossplane resources have a `status` section that can represent the current
state of that particular resource. Running `kubectl describe` against a
Crossplane resource frequently gives insightful information about its
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
availability of the resource - whether it's creating, deleting, available,
unavailable, binding, etc.

## Resource events

Most Crossplane resources emit _events_ when something interesting happens. You
can see the events associated with a resource by running `kubectl describe` -
for example, `kubectl describe cloudsqlinstance my-db`. You can also see all events in a
particular namespace by running `kubectl get events`.

```console
Events:
  Type     Reason                   Age                From                                                   Message
  ----     ------                   ----               ----                                                   -------
  Warning  CannotConnectToProvider  16s (x4 over 46s)  managed/postgresqlserver.database.azure.crossplane.io  cannot get referenced ProviderConfig: ProviderConfig.azure.crossplane.io "default" not found
```

> Note that Kubernetes namespaces events, while most Crossplane resources (XRs, etc)
> are cluster scoped. Crossplane emits events for cluster scoped resources to
> the 'default' namespace.

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
## Crossplane Logs
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

The next place to look to get more information or investigate a failure would be
in the Crossplane pod logs, which should be running in the `crossplane-system`
namespace. To get the current Crossplane logs, run the following:

```shell
kubectl -n crossplane-system logs -lapp=crossplane
```

> Note that Crossplane emits minimal logs by default - events are typically the best
> place to look for information about what Crossplane is doing. You may need to
> restart Crossplane with the `--debug` flag if you can't find what you're
> looking for.

## Provider logs

Remember that providers provide much of Crossplane's features. You
can use `kubectl logs` to view provider logs too. By convention, they also emit
minimal logs by default.

```shell
kubectl -n crossplane-system logs <name-of-provider-pod>
```

All providers maintained by the Crossplane community mirror Crossplane's support
of the `--debug` flag. The easiest way to set flags on a provider is to create a
`DeploymentRuntimeConfig` and reference it from the `Provider`:

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: DeploymentRuntimeConfig
metadata:
  name: debug-config
spec:
  deploymentTemplate:
    spec:
      selector: {}
      template:
        spec:
          containers:
          - name: package-runtime
            args: 
            - --debug
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-aws:v0.33.0
  runtimeConfigRef:
    apiVersion: pkg.crossplane.io/v1beta1
    kind: DeploymentRuntimeConfig
    name: debug-config
```

> Note that you can add a reference to a `DeploymentRuntimeConfig` to an already
> installed `Provider` and it updates its `Deployment` accordingly.

## Pausing Crossplane

Sometimes, for example when you encounter a bug, it can be useful to pause
Crossplane if you want to stop it from actively attempting to manage your
resources. To pause Crossplane without deleting all its resources, run the
following command to scale down its deployment:

```shell
kubectl -n crossplane-system scale --replicas=0 deployment/crossplane
```

After you have been able to rectify the problem or smooth things out, you can
unpause Crossplane by scaling its deployment back up:

```shell
kubectl -n crossplane-system scale --replicas=1 deployment/crossplane
```

## Pausing Providers

You can also pause Providers when troubleshooting an issue or orchestrating a
complex migration of resources. Creating and referencing a `DeploymentRuntimeConfig` is
the easiest way to scale down a provider, and you can change the `DeploymentRuntimeConfig` or remove the reference to scale it back up:

```yaml
apiVersion: pkg.crossplane.io/v1beta1
kind: DeploymentRuntimeConfig
metadata:
  name: scale-config
spec:
  deploymentTemplate:
    spec:
      selector: {}
      replicas: 0
      template: {}
---
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-aws:v0.33.0
  runtimeConfigRef:
    apiVersion: pkg.crossplane.io/v1beta1
    kind: DeploymentRuntimeConfig
    name: scale-config
```

> Note that you can add a reference to a `DeploymentRuntimeConfig` to an already
> installed `Provider` and it updates its `Deployment` accordingly.

## Deleting when a resource hangs

The resources that Crossplane manages are automatically cleaned up so as not
to leave anything running behind. Crossplane accomplishes this by using finalizers, but
in certain scenarios the finalizer can prevent the Kubernetes object from
getting deleted.

To deal with this, patch the object to remove its
finalizer, which then allows Kubernetes to delete it. Note that this
doesn't necessarily delete the external resource that Crossplane was managing, so
you want to go to your cloud provider's console and look there for any
lingering resources to clean up.

In general, you can remove a finalizer from an object with this command:

```shell
kubectl patch <resource-type> <resource-name> -p '{"metadata":{"finalizers": []}}' --type=merge
```

For example, for a `CloudSQLInstance` managed resource (`database.gcp.crossplane.io`) named
`my-db`, you can remove its finalizer with:

```shell
kubectl patch cloudsqlinstance my-db -p '{"metadata":{"finalizers": []}}' --type=merge
```

## Tips, tricks, and troubleshooting

This section covers some common tips, tricks, and troubleshooting steps
for working with Composite Resources. If you're trying to track down why your
Composite Resources aren't working the [Troubleshooting][trouble-ref] page also
has some useful information.

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
[Crossplane package]: {{<ref "../packages/configurations/">}}
[Handling Crossplane Package Dependency]: #handling-crossplane-package-dependency
[semver spec]: https://github.com/Masterminds/semver#basic-comparisons


