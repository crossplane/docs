---
title: Configuration Packages
description: "Packages combine multiple Crossplane resources into a single, portable, OCI image."
altTitle: "Crossplane Packages"
weight: 200
---

A _Configuration_ package is an 
[OCI container images](https://opencontainers.org/) containing a collection of
[Compositions]({{<ref "./compositions" >}}), 
[Composite Resource Definitions]({{<ref "./composite-resource-definitions" >}})
and any required [Providers]({{<ref "./providers">}}) or 
[Functions]({{<ref "./composition-functions" >}}).

Configuration packages make your Crossplane configuration fully portable. 

{{<hint "important" >}}
Crossplane [Providers]({{<ref "./providers">}}) and 
[Functions]({{<ref "./composition-functions">}}) are also Crossplane packages.  

This document describes how to install and manage configuration packages.  

Refer to the 
[Provider]({{<ref "./providers">}}) and 
[Composition Functions]({{<ref "./composition-functions">}}) chapters for
details on their usage of packages. 
{{< /hint >}}

## Install a Configuration

Install a Configuration with a Crossplane 
{{<hover line="2" label="install">}}Configuration{{</hover>}} object by setting 
the {{<hover line="6" label="install">}}spec.package{{</hover>}} value to the
location of the configuration package.

{{< hint "important" >}}
Beginning with Crossplane version 1.15.0 Crossplane uses the Upbound Marketplace
Crossplane package registry at `xpkg.upbound.io` by default for downloading and
installing packages. 

Specify the full domain name with the `package` or change the default Crossplane
registry with the `--registry` flag on the [Crossplane pod]({{<ref "./pods">}})
{{< /hint >}}

For example to install the 
[Upbound AWS reference platform](https://marketplace.upbound.io/configurations/upbound/platform-ref-aws/v0.6.0), 

```yaml {label="install"}
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: platform-ref-aws
spec:
  package: xpkg.upbound.io/upbound/platform-ref-aws:v0.6.0
```

Crossplane installs the Compositions, Composite Resource Definitions and
Providers listed in the Configuration. 

### Install with Helm

Crossplane supports installing Configurations during an initial Crossplane
installation with the Crossplane Helm chart.

Use the
{{<hover label="helm" line="5" >}}--set configuration.packages{{</hover >}}
argument with `helm install`.

For example, to install the Upbound AWS reference platform,

```shell {label="helm"}
helm install crossplane \
crossplane-stable/crossplane \
--namespace crossplane-system \
--create-namespace \
--set configuration.packages='{xpkg.upbound.io/upbound/platform-ref-aws:v0.6.0}'
```

### Install offline

Installing Crossplane packages offline requires a local container registry like 
[Harbor](https://goharbor.io/) to host the packages. Crossplane only
supports installing packages from a container registry. 

Crossplane doesn't support installing packages directly from Kubernetes
volumes.

### Installation options

Configurations support multiple options to change configuration package related
settings. 


#### Configuration revisions

When installing a newer version of an existing Configuration Crossplane creates
a new configuration revision. 

View the configuration revisions with 
{{<hover label="rev" line="1">}}kubectl get configurationrevisions{{</hover>}}.

```shell {label="rev",copy-lines="1"}
kubectl get configurationrevisions
NAME                            HEALTHY   REVISION   IMAGE                                             STATE      DEP-FOUND   DEP-INSTALLED   AGE
platform-ref-aws-1735d56cd88d   True      2          xpkg.upbound.io/upbound/platform-ref-aws:v0.5.0   Active     2           2               46s
platform-ref-aws-3ac761211893   True      1          xpkg.upbound.io/upbound/platform-ref-aws:v0.4.1   Inactive                               5m13s
```

Only a single revision is active at a time. The active revision determines the
available resources, including Compositions and Composite Resource Definitions. 

By default Crossplane keeps only a single _Inactive_ revision.

Change the number of revisions Crossplane maintains with a Configuration package 
{{<hover label="revHistory" line="6">}}revisionHistoryLimit{{</hover>}}. 

The {{<hover label="revHistory" line="6">}}revisionHistoryLimit{{</hover>}}
field is an integer.  
The default value is `1`.  
Disable storing revisions by setting 
{{<hover label="revHistory" line="6">}}revisionHistoryLimit{{</hover>}} to `0`.

For example, to change the default setting and store 10 revisions use 
{{<hover label="revHistory" line="6">}}revisionHistoryLimit: 10{{</hover>}}.

```yaml {label="revHistory"}
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: platform-ref-aws
spec:
  revisionHistoryLimit: 10
# Removed for brevity
```

#### Configuration package pull policy

Use a {{<hover label="pullpolicy" line="6">}}packagePullPolicy{{</hover>}} to
define when Crossplane should download the Configuration package to the local
Crossplane package cache.

The `packagePullPolicy` options are: 
* `IfNotPresent` - (**default**) Only download the package if it isn't in the cache.
* `Always` - Check for new packages every minute and download any matching
  package that isn't in the cache.
* `Never` - Never download the package. Packages are only installed from the
  local package cache. 

{{<hint "tip" >}}
The Crossplane 
{{<hover label="pullpolicy" line="6">}}packagePullPolicy{{</hover>}} works
like the Kubernetes container image 
[image pull policy](https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy).  

Crossplane supports the use of tags and package digest hashes like
Kubernetes images. 
{{< /hint >}}

For example, to `Always` download a given Configuration package use the 
{{<hover label="pullpolicy" line="6">}}packagePullPolicy: Always{{</hover>}}
configuration. 

```yaml {label="pullpolicy",copy-lines="6"}
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: platform-ref-aws
spec:
  packagePullPolicy: Always
# Removed for brevity
```

#### Revision activation policy

The `Active` package revision
is the package controller actively reconciling resources. 

By default Crossplane sets the most recently installed package revision as 
`Active`.

Control the Configuration upgrade behavior with a
{{<hover label="revision" line="6">}}revisionActivationPolicy{{</hover>}}.

The {{<hover label="revision" line="6">}}revisionActivationPolicy{{</hover>}} 
options are:
* `Automatic` - (**default**) Automatically activate the last installed configuration.
* `Manual` - Don't automatically activate a configuration. 

For example, to change the upgrade behavior to require manual upgrades, set 
{{<hover label="revision" line="6">}}revisionActivationPolicy: Manual{{</hover>}}.

```yaml {label="revision"}
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: platform-ref-aws
spec:
  revisionActivationPolicy: Manual
# Removed for brevity
```


#### Install a Configuration from a private registry

Like Kubernetes uses `imagePullSecrets` to 
[install images from private registries](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/), 
Crossplane uses `packagePullSecrets` to install Configuration packages from a 
private registry. 

Use {{<hover label="pps" line="6">}}packagePullSecrets{{</hover>}} to provide a
Kubernetes secret to use for authentication when downloading a Configuration 
package. 

{{<hint "important" >}}
The Kubernetes secret must be in the same namespace as Crossplane.
{{</hint >}}

The {{<hover label="pps" line="6">}}packagePullSecrets{{</hover>}} is a list of
secrets.

For example, to use the secret named
{{<hover label="pps" line="6">}}example-secret{{</hover>}} configure a 
{{<hover label="pps" line="6">}}packagePullSecrets{{</hover>}}.

```yaml {label="pps"}
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: platform-ref-aws
spec:
  packagePullSecrets: 
    - name: example-secret
# Removed for brevity
```

#### Ignore dependencies

By default Crossplane installs any [dependencies](#manage-dependencies) listed
in a Configuration package. 

Crossplane can ignore a Configuration package's dependencies with 
{{<hover label="pkgDep" line="6" >}}skipDependencyResolution{{</hover>}}.

{{< hint "warning" >}}
Most Configurations include dependencies for the required Providers. 

If a Configuration ignores dependencies, the required Providers must be 
manually installed.
{{< /hint >}}

For example, to disable dependency resolution configure 
{{<hover label="pkgDep" line="6" >}}skipDependencyResolution: true{{</hover>}}.

```yaml {label="pkgDep"}
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: platform-ref-aws
spec:
  skipDependencyResolution: true
# Removed for brevity
```

#### Ignore Crossplane version requirements

A Configuration package may require a specific or minimum Crossplane version 
before installing. By default, Crossplane doesn't install a Configuration if 
the Crossplane version doesn't meet the required version. 

Crossplane can ignore the required version with 
{{<hover label="xpVer" line="6">}}ignoreCrossplaneConstraints{{</hover>}}.

For example, to install a Configuration package into an unsupported Crossplane
version, configure 
{{<hover label="xpVer" line="6">}}ignoreCrossplaneConstraints: true{{</hover>}}.

```yaml {label="xpVer"}
apiVersion: pkg.crossplane.io/v1
kind: Configuration
metadata:
  name: platform-ref-aws
spec:
  ignoreCrossplaneConstraints: true
# Removed for brevity
```


### Verify a Configuration

Verify a Configuration with 
{{<hover label="verify" line="1">}}kubectl get configuration{{</hover >}}.

A working configuration reports `Installed` and `Healthy` as `True`.

```shell {label="verify",copy-lines="1"}
kubectl get configuration
NAME               INSTALLED   HEALTHY   PACKAGE                                           AGE
platform-ref-aws   True        True      xpkg.upbound.io/upbound/platform-ref-aws:v0.6.0   54s
```

### Manage dependencies

Configuration packages may include dependencies on other packages including
Functions, Providers or other Configurations. 

If Crossplane can't meet the dependencies of a Configuration the Configuration
reports `HEALTHY` as `False`. 

For example, this installation of the Upbound AWS reference platform is
`HEALTHY: False`.

```shell {copy-lines="1"}
kubectl get configuration
NAME               INSTALLED   HEALTHY   PACKAGE                                           AGE
platform-ref-aws   True        False     xpkg.upbound.io/upbound/platform-ref-aws:v0.6.0   71s
```

To see more information on why the Configuration isn't `HEALTHY` use 
{{<hover label="depend" line="1">}}kubectl describe configurationrevisions{{</hover>}}.

```yaml {copy-lines="1",label="depend"}
kubectl describe configurationrevision
Name:         platform-ref-aws-a30ad655c769
API Version:  pkg.crossplane.io/v1
Kind:         ConfigurationRevision
# Removed for brevity
Spec:
  Desired State:                  Active
  Image:                          xpkg.upbound.io/upbound/platform-ref-aws:v0.6.0
  Revision:                       1
Status:
  Conditions:
    Last Transition Time:  2023-10-06T20:08:14Z
    Reason:                UnhealthyPackageRevision
    Status:                False
    Type:                  Healthy
  Controller Ref:
    Name:
Events:
  Type     Reason       Age                From                                              Message
  ----     ------       ----               ----                                              -------
  Warning  LintPackage  29s (x2 over 29s)  packages/configurationrevision.pkg.crossplane.io  incompatible Crossplane version: package is not compatible with Crossplane version (v1.12.0)
```

The {{<hover label="depend" line="18">}}Events{{</hover>}} show a 
{{<hover label="depend" line="21">}}Warning{{</hover>}} with a message that the
current version of Crossplane doesn't meet the Configuration package 
requirements.

## Create a Configuration

Crossplane Configuration packages are 
[OCI container images](https://opencontainers.org/) containing one or more YAML
files. 

{{<hint "important" >}}
Configuration packages are fully OCI compliant. Any tool that builds OCI images
can build Configuration packages.  

It's strongly recommended to use the Crossplane command-line tool to
provide error checking and formatting to Crossplane package builds. 

Read the 
[Crossplane package specification](https://github.com/crossplane/crossplane/blob/master/contributing/specifications/xpkg.md) 
for package requirements when building packages with third-party tools.
{{</hint >}}

A Configuration package requires a `crossplane.yaml` file and may include
Composition and CompositeResourceDefinition files. 

<!-- vale Google.Headings = NO -->
### The crossplane.yaml file
<!-- vale Google.Headings = YES -->

To build a Configuration package using the Crossplane CLI, create a file
named 
{{<hover label="cfgMeta" line="1">}}crossplane.yaml{{</hover>}}.  
The 
{{<hover label="cfgMeta" line="1">}}crossplane.yaml{{</hover>}}
file defines the requirements and name of the 
Configuration.

{{<hint "important" >}}
The Crossplane CLI only supports a file named `crossplane.yaml`.
{{< /hint >}}

Configuration package uses the 
{{<hover label="cfgMeta" line="2">}}meta.pkg.crossplane.io{{</hover>}}
Crossplane API group.

Specify any other Configurations, Functions or Providers in the 
{{<hover label="cfgMeta" line="7">}}dependsOn{{</hover>}} list.  
Optionally, you can require a specific or minimum package version with the 
{{<hover label="cfgMeta" line="9">}}version{{</hover>}} option.

You can also define a specific or minimum version of Crossplane for this
Configuration with the 
{{<hover label="cfgMeta" line="11">}}crossplane.version{{</hover>}} option. 

{{<hint "note" >}}
Defining the {{<hover label="cfgMeta" line="10">}}crossplane{{</hover>}} object 
or required versions is optional. 
{{< /hint >}}

```yaml {label="cfgMeta",copy-lines="all"}
$ cat crossplane.yaml
apiVersion: meta.pkg.crossplane.io/v1alpha1
kind: Configuration
metadata:
  name: test-configuration
spec:
  dependsOn:
    - provider: xpkg.upbound.io/crossplane-contrib/provider-aws
      version: ">=v0.36.0"
  crossplane:
    version: ">=v1.12.1-0"
```

### Build the package

Create the package using the 
[Crossplane CLI]({{<ref "../cli">}}) command 
`crossplane xpkg build --package-root=<directory>`.

Where the `<directory>` is the directory containing the `crossplane.yaml` file
and any Composition or CompositeResourceDefinition YAML files.

The CLI recursively searches for `.yml` or `.yaml` files in the directory to
include in the package.

{{<hint "important" >}}
You must ignore any other YAML files with `--ignore=<file_list>`.  
For
example, `crossplane xpkg build --package-root=test-directory --ignore=".tmp/*"`.

Including YAML files that aren't Compositions or CompositeResourceDefinitions, 
including Claims isn't supported.
{{</hint >}}

By default, Crossplane creates an `.xpkg` file of the Configuration name and 
a SHA-256 hash of the package contents.

For example, a {{<hover label="xpkgName" line="2">}}Configuration{{</hover>}}
named {{<hover label="xpkgName" line="4">}}test-configuration{{</hover>}}.  
The
Crossplane CLI builds a package named `test-configuration-e8c244f6bf21.xpkg`.

```yaml {label="xpkgName"}
apiVersion: meta.pkg.crossplane.io/v1alpha1
kind: Configuration
metadata:
  name: test-configuration
# Removed for brevity
```

Specify the output file with `--package-file=<filename>.xpkg` option.

For example, to build a package from a directory named `test-directory` and
generate a package named `test-package.xpkg` in the current working directory,
use the command:

```shell
crossplane xpkg build --package-root=test-directory --package-file=test-package.xpkg
```

```shell
ls -1 ./
test-directory
test-package.xpkg
```
