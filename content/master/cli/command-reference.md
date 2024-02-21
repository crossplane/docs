---
weight: 50
title: Command Reference
description: "Command reference for the Crossplane CLI"
---


<!-- vale Google.Headings = NO -->
The `crossplane` CLI provides utilities to make using Crossplane easier. 

Read the [Crossplane CLI overview]({{<ref "../cli">}}) page for information on 
installing `crossplane`.

## Global flags
The following flags are available for all commands.

{{< table "table table-sm table-striped">}}
| Short flag | Long flag   | Description                  |
|------------|-------------|------------------------------|
| `-h`       | `--help`    | Show context sensitive help. |
| `-v`       | `--version` | Print version and exit.      |
|            | `--verbose` | Print verbose output.        |
{{< /table >}}

## xpkg

The `crossplane xpkg` commands create, install and update Crossplane
[packages]({{<ref "../concepts/packages">}}) as well as enable authentication
and publishing of Crossplane packages to a Crossplane package registry. 

### xpkg build

Using `crossplane xpkg build` provides automation and simplification to build 
Crossplane packages.  

The Crossplane CLI combines a directory of YAML files and packages them as 
an [OCI container image](https://opencontainers.org/).  

The CLI applies the required annotations and values to meet the 
[Crossplane XPKG specification](https://github.com/crossplane/crossplane/blob/master/contributing/specifications/xpkg.md).

The `crossplane` CLI supports building 
[configuration]({{< ref "../concepts/packages" >}}),
[function]({{<ref "../concepts/composition-functions">}}) and 
[provider]({{<ref "../concepts/providers" >}}) package types. 


#### Flags
{{< table "table table-sm table-striped">}}
| Short flag   | Long flag                            | Description                    |
| ------------ | -------------                        | ------------------------------ |
|              | `--embed-runtime-image-name=NAME`    |  The image name and tag of an image to include in the package. Only for provider and function packages. |
|              | `--embed-runtime-image-tarball=PATH` |  The filename of an image to include in the package. Only for provider and function packages.                              |
| `-e`         | `--examples-root="./examples"`       |  The path to a directory of examples related to the package.                               |
|              | `--ignore=PATH,...`                  |  List of files and directories to ignore.                              |
| `-o`         | `--package-file=PATH`                |  Directory and filename of the created package.                             |
| `-f`         | `--package-root="."`                 |  Directory to search for YAML files.                              |
{{< /table >}}

The `crossplane xpkg build` command recursively looks in the directory set by 
`--package-root` and attempts to combine any files ending in `.yml` or `.yaml` 
into a package.

All YAML files must be valid Kubernetes manifests with `apiVersion`, `kind`, 
`metadata` and `spec` fields. 

#### Ignore files

Use `--ignore` to provide a list of files and directories to ignore.  

For example,  
`crossplane xpkg build --ignore="./test/*,kind-config.yaml"`

#### Set the package name

`crossplane` automatically names the new package a combination of the 
`metadata.name` and a hash of the package contents and saves the contents 
in the same location as `--package-root`. Define a specific location and 
filename with `--package-file` or `-o`.  

For example,  
`crossplane xpkg build -o /home/crossplane/example.xpkg`.


#### Include examples

Include YAML files demonstrating how to use the package with `--examples-root`. 

[Upbound Marketplace](https://marketplace.upbound.io/) uses files included with 
`--examples-root` as documentation for published packages.

#### Include a runtime image

Functions and Providers require YAML files describing their dependencies and 
settings as well as a container image for their runtime.

Using `--embed-runtime-image-name` runs a specified image and 
includes the image inside the function or provider package.

{{<hint "note" >}}
Images referenced with `--embed-runtime-image-name` must be in the local Docker 
cache.  

Use `docker pull` to download a missing image.
{{< /hint >}}

The `--embed-runtime-image-tarball` flag includes a local OCI image tarball 
inside the function or provider package.


### xpkg install

Download and install packages into Crossplane with  `crossplane xpkg install`.

By default the `crossplane xpkg install` command uses the Kubernetes 
configuration defined in `~/.kube/config`.  

Define a custom Kubernetes configuration file location with the environmental 
variable `KUBECONFIG`.

Specify the package kind, package file and optionally a name to give the package 
inside Crossplane.

`crossplane xpkg install <package-kind> <registry URL package name and tag> [<optional-name>]`

The `<package-kind>` is either a `configuration`, `function` or `provider`.

For example, to install version 0.42.0 of the 
[AWS S3 provider](https://marketplace.upbound.io/providers/upbound/provider-aws-s3/v0.42.0):

`crossplane xpkg install provider xpkg.upbound.io/upbound/provider-aws-s3:v0.42.0`

#### Flags
{{< table "table table-sm table-striped">}}
| Short flag   | Long flag                                        | Description                                                                                     |
| ------------ | -------------                                    | ------------------------------                                                                  |
|              | `--runtime-config=<runtime config name>`         | Install the package with a runtime configuration.                                               |
| `-m`         | `--manual-activation`                            | Set the `revisionActiviationPolicy` to `Manual`.                                                |
|              | `--package-pull-secrets=<list of secrets>`       | A comma-separated list of Kubernetes secrets to use for authenticating to the package registry. |
| `-r`         | `--revision-history-limit=<number of revisions>` | Set the `revisionHistoryLimit`. Defaults to `1`.                                                |
| `-w`         | `--wait=<number of seconds>`                     | Number of seconds to wait for a package to install.                                             |

{{< /table >}}

#### Wait for package install

When installing a package the `crossplane xpkg install` command doesn't wait for
the package to download and install. View any download or installation problems 
by inspecting the `configuration` with `kubectl describe configuration`.

Use `--wait` to have the `crossplane xpkg install` command to wait for a 
package to have the condition `HEALTHY` before continuing. The command 
returns an error if the `wait` time expires before the package is `HEALTHY`.

#### Require manual package activation

Set the package to require 
[manual activation]({{<ref "../concepts/packages#revision-activation-policy" >}}), 
preventing an automatic upgrade of a package with `--manual-activation`

#### Authenticate to a private registry

To authenticate to a private package registry use `--package-pull-secrets` and 
provide a list of Kubernetes Secret objects. 

{{<hint "important" >}}
The secrets must be in the same namespace as the Crossplane pod. 
{{< /hint >}}

#### Customize the number of stored package versions

By default Crossplane only stores a single inactive package in the local package
cache. 

Store more inactive copies of a package with `--revision-history-limit`. 

Read more about 
[package revisions]({{< ref "../concepts/packages#configuration-revisions" >}}) 
in the package documentation. 

### xpkg login

Use `xpkg login` to authenticate to `xpkg.upbound.io`, the 
[Upbound Marketplace](https://marketplace.upbound.io/) container registry.

[Register with the Upbound Marketplace](https://accounts.upbound.io/register) 
to push packages and create private repositories. 

#### Flags

{{< table "table table-sm table-striped">}}
| Short flag   | Long flag                            | Description                    |
| ------------ | -------------                        | ------------------------------ |
| `-u` | `--username=<username>`    | Username to use for authentication. | 
| `-p` | `--password=<password>`    | Password to use for authentication. | 
| `-t` | `--token=<token string>`   | User token string to use for authentication. | 
| `-a` | `--account=<organization>` | Specify an Upbound organization during authentication. |
{{< /table >}}


#### Authentication options

The `crossplane xpkg login` command can use a username and password or Upbound API token.

By default, `crossplane xpkg login` without arguments, prompts for a username
and password. 

Provide a username and password with the `--username` and `--password` flags or
set the environmental variable `UP_USER` for a username or `UP_PASSWORD` for the
password. 

Use an Upbound user token instead of a username and password with `--token` or 
the `UP_TOKEN` environmental variable. 

{{< hint "important" >}}
The `--token` or `UP_TOKEN` environmental variables take precedence over a 
username and password.
{{< /hint >}}

Using `-` as the input for `--password` or `--token` reads the input from stdin.  
For example, `crossplane xpkg login --password -`.

After logging in the Crossplane CLI creates a `profile` in 
`.crossplane/config.json` to cache unprivileged account information. 

{{<hint "note" >}}
The `session` field of `config.json` file is a session cookie identifier. 

The `session` value isn't used for authentication. This isn't a `token`.
{{< /hint >}}

#### Authenticate with a registered Upbound organization

Authenticate to a registered organization in the Upbound Marketplace with the 
`--account` option, along with the username and password or token. 

For example, 
`crossplane xpkg login --account=Upbound --username=my-user --password -`.

### xpkg logout

Use `crossplane xpkg logout` to invalidate the current `crossplane xpkg login` 
session.

{{< hint "note" >}}
Using `crossplane xpkg logout` removes the `session` from the 
`~/.crossplane/config.json` file, but doesn't delete the configuration file.
{{< /hint >}}

### xpkg push

Push a Crossplane package file to a package registry. 

The Crossplane CLI pushes images to the 
[Upbound Marketplace](https://marketplace.upbound.io/) at `xpkg.upbound.io` by 
default.

{{< hint "note" >}}
Pushing a package may require authentication with 
[`crossplane xpkg login`](#xpkg-login)
{{< /hint >}}

Specify the organization, package name and tag with  
`crossplane xpkg push <package>`

By default the command looks in the current directory for a single `.xpkg` file 
to push. 

To push multiple files or to specify a specific `.xpkg` file use the `-f` flag.

For example, to push a local package named `my-package` to 
`crossplane-docs/my-package:v0.14.0` use:

`crossplane xpkg push -f my-package.xpkg crossplane-docs/my-package:v0.14.0`

To push to another package registry, like [DockerHub](https://hub.docker.com/) 
provide the full URL along with the package name. 

For example, to push a local package named `my-package` to 
DockerHub organization `crossplane-docs/my-package:v0.14.0` use:
`crossplane xpkg push -f my-package.xpkg index.docker.io/crossplane-docs/my-package:v0.14.0`.


#### Flags

{{< table "table table-sm table-striped">}}
| Short flag   | Long flag              | Description                                   |
| ------------ | -------------          | ------------------------------                |
| `-f`         | `--package-files=PATH` | A comma-separated list of xpkg files to push. |
{{< /table >}}

### xpkg update

The `crossplane xpkg update` command downloads and updates an existing package.

By default the `crossplane xpkg update` command uses the Kubernetes 
configuration defined in `~/.kube/config`.  

Define a custom Kubernetes configuration file location with the environmental 
variable `KUBECONFIG`.

Specify the package kind, package file and optionally the name of the package 
already installed in Crossplane.

`crossplane xpkg update <package-kind> <registry package name and tag> [<optional-name>]`

The package file must be an organization, image and tag on the `xpkg.upbound.io`
registry on [Upbound Marketplace](https://marketplace.upbound.io/).

For example, to update to version 0.42.0 of the 
[AWS S3 provider](https://marketplace.upbound.io/providers/upbound/provider-aws-s3/v0.42.0):

`crossplane xpkg update provider xpkg.upbound.io/upbound/provider-aws-s3:v0.42.0`


## beta

Crossplane `beta` commands are experimental. These commands may change the 
flags, options or outputs in future releases. 

Crossplane maintainers may promote or remove commands under `beta` in future 
releases.


### beta convert

As Crossplane evolves, its APIs and resources may change. To help with the 
migration to the new APIs and resources, the `crossplane beta convert` command
converts a Crossplane resource to a new version or kind.

Use the `crossplane beta convert` command to convert an existing
[ControllerConfig]({{<ref "../concepts/providers#controller-configuration">}})
to a [DeploymentRuntimeConfig]({{<ref "../concepts/providers#runtime-configuration">}}) 
or a Composition using [patch and transforms]({{<ref "../concepts/patch-and-transform">}}) 
to a 
[Composition pipeline function]({{< ref "../concepts/compositions#use-composition-functions" >}}).

Provide the `crossplane beta convert` command the conversion type, the input
file and optionally, an output file. By default the command writes the output to
standard out. 

For example, to convert a ControllerConfig to a DeploymentRuntimeConfig use 
`crossplane beta convert deployment-runtime`. For example,

`crossplane beta convert deployment-runtime controllerConfig.yaml -o deploymentConfig.yaml`

To convert a Composition using patch and transforms to a pipeline function, use
`crossplane beta convert pipeline-composition`.  

Optionally, use the `-f` flag to provide the name of the function.  
By default the function name is "function-patch-and-transform."

`crossplane beta convert pipeline-composition oldComposition.yaml -o newComposition.yaml -f patchFunctionName`


#### Flags
{{< table "table table-sm table-striped">}}
| Short flag   | Long flag       | Description                                                                                |
| ------------ | --------------- | ------------------------------                                                             |
| `-o`         | `--output-file` | The output YAML file to write. Outputs to stdout by default.  |
| `-f`         | `--function-name` | The name of the new function. Defaults to `function-patch-and-transform`. |
<!-- vale Crossplane.Spelling = YES -->
{{< /table >}}


### beta render 

The `crossplane beta render` command previews the output of a 
[composite resource]({{<ref "../concepts/composite-resources">}}) after applying 
any [composition functions]({{<ref "../concepts/composition-functions">}}).

{{< hint "important" >}}
The `crossplane beta render` command doesn't apply 
[patch and transform composition patches]({{<ref "../concepts/patch-and-transform">}}).

The command only supports function "patch and transforms."
{{< /hint >}}

The `crossplane beta render` command connects to the locally running Docker 
Engine to pull and run composition functions. 

{{<hint "important">}} 
Running `crossplane beta render` requires [Docker](https://www.docker.com/).
{{< /hint >}}

Provide a composite resource, composition and composition function YAML 
definition with the command to render the output locally. 

For example, 
`crossplane beta render xr.yaml composition.yaml function.yaml`

The output includes the original composite resource followed by the generated 
managed resources. 

{{<expand "An example render output" >}}
```yaml
---
apiVersion: nopexample.org/v1
kind: XBucket
metadata:
  name: test-xrender
status:
  bucketRegion: us-east-2
---
apiVersion: s3.aws.upbound.io/v1beta1
kind: Bucket
metadata:
  annotations:
    crossplane.io/composition-resource-name: my-bucket
  generateName: test-xrender-
  labels:
    crossplane.io/composite: test-xrender
  ownerReferences:
  - apiVersion: nopexample.org/v1
    blockOwnerDeletion: true
    controller: true
    kind: XBucket
    name: test-xrender
    uid: ""
spec:
  forProvider:
    region: us-east-2
```
{{< /expand >}}

#### Flags

{{< table "table table-sm table-striped">}}
| Short flag   | Long flag                             | Description                                           |
| ------------ | -------------                         | ------------------------------                        |
|              | `--context-files=<key>=<file>,<key>=<file>`    | A comma separated list of files to load for function "contexts." |
|              | `--context-values=<key>=<value>,<key>=<value>` | A comma separated list of key-value pairs to load for function "contexts."                                                    |
| `-r`         | `--include-function-results`          | Include the "results" or events from the function.   |
| `-o`         | `--observed-resources=<directory or file>`               |
Provide artificial managed resource data to the function.
|
| `-x`         | `--include-full-xr`          | Include a copy of the input Composite Resource spec and metadata fields in the rendered output.   |
|              | `--timeout=`                          | Amount of time to wait for a function to finish.                    |
{{< /table >}}

The `crossplane beta render` command relies on standard 
[Docker environmental variables](https://docs.docker.com/engine/reference/commandline/cli/#environment-variables) 
to connect to the local Docker engine and run composition functions. 


#### Provide function context

The `--context-files` and `--context-values` flags can provide data 
to a function's `context`.  
The context is JSON formatted data.

#### Include function results

If a function produces Kubernetes events with statuses use the 
`--include-function-results` to print them along with the managed resource 
outputs. 

#### Include the composite resource 

Composition functions can only change the `status` field of a composite 
resource. By default, the `crossplane beta render` command only prints the
`status` field with `metadata.name`.  

Use `--include-full-xr` to print the full composite resource, 
including the `spec` and `metadata` fields.

#### Mock managed resources

Provide mocked, or artificial data representing a managed resource with 
`--observed-resources`. The `crossplane beta render` command treats the 
provided inputs as if they were resources in a Crossplane cluster. 

A function can reference and manipulate the included resource as part of 
running the function.

The `observed-resources` may be a single YAML file with multiple resources or a 
directory of YAML files representing multiple resources.

Inside the YAML file include an 
{{<hover label="apiVersion" line="1">}}apiVersion{{</hover>}},
{{<hover label="apiVersion" line="2">}}kind{{</hover>}},
{{<hover label="apiVersion" line="3">}}metadata{{</hover>}} and
{{<hover label="apiVersion" line="7">}}spec{{</hover>}}.

```yaml {label="apiVersion"}
apiVersion: example.org/v1alpha1
kind: ComposedResource
metadata:
  name: test-render-b
  annotations:
    crossplane.io/composition-resource-name: resource-b
spec:
  coolerField: "I'm cooler!"
```

The schema of the resource isn't validated and may contain any data.

### beta top

The command `crossplane beta top` shows CPU and memory usage of Crossplane
related pods. 

```shell
crossplane beta top 
TYPE         NAMESPACE   NAME                                                       CPU(cores)   MEMORY
crossplane   default     crossplane-f98f9ddfd-tnm46                                 4m           32Mi
crossplane   default     crossplane-rbac-manager-74ff459b88-94p8p                   4m           14Mi
provider     default     provider-aws-s3-1f1a3fb08cbc-5c49d84447-sggrq              3m           108Mi
provider     default     upbound-provider-family-aws-48b3b5ccf964-76c9686b6-bgg65   2m           89Mi
```

{{<hint "important" >}}
Using `crossplane beta top` requires the Kubernetes 
[metrics server](https://github.com/kubernetes-sigs/metrics-server) enabled on 
the cluster running Crossplane before using `crossplane beta top`. 

Follow the installation instructions on the 
[metrics-server GitHub page](https://github.com/kubernetes-sigs/metrics-server#installation).
{{< /hint >}}



#### Flags
{{< table "table table-sm table-striped">}}
<!-- vale Crossplane.Spelling = NO -->
<!-- vale flags `dot` as an error but only the trailing tick. -->
| Short flag   | Long flag                   | Description                                                                        |
| ------------ | -------------               | ------------------------------                                                     |
| `-n`         | `--namespace`               | The namespace where the Crossplane pod runs. Default is `crossplane-system`.                                                    |
| `-s`         | `--summary`                 | Print a summary of all Crossplane pods along with the output.                |
|              | `--verbose`                 | Print verbose logging information with the output.                                                     |
<!-- vale Crossplane.Spelling = YES -->
{{< /table >}}

The Kubernetes metrics server may take some time to collect data for the
`crossplane beta top` command. Before the metrics server is ready, 
running the `top` command may produce an error, for example,

`crossplane: error: error adding metrics to pod, check if metrics-server is running or wait until metrics are available for the pod: the server is currently unable to handle the request (get pods.metrics.k8s.io crossplane-contrib-provider-helm-b4cc4c2c8db3-6d787f9686-qzmz2)`


### beta trace

Use the `crossplane beta trace` command to display a visual relationship of
Crossplane objects. The `trace` command supports claims, compositions, 
functions, managed resources or packages. 

The command requires a resource type and a resource name.  

`crossplane beta trace <resource kind> <resource name>`

For example to view a resource named `my-claim` of type `example.crossplane.io`:  
`crossplane beta trace example.crossplane.io my-claim`

The command also accepts Kubernetes CLI style `<kind>/<name>` input.  
For example,  
`crossplane beta trace example.crossplane.io/my-claim`

By default the `crossplane beta trace` command uses the Kubernetes 
configuration defined in `~/.kube/config`.  

Define a custom Kubernetes configuration file location with the environmental 
variable `KUBECONFIG`.

#### Flags
{{< table "table table-sm table-striped">}}
<!-- vale Crossplane.Spelling = NO -->
<!-- vale flags `dot` as an error but only the trailing tick. -->
| Short flag   | Long flag                   | Description                                                                        |
| ------------ | -------------               | ------------------------------                                                     |
| `-n`         | `--namespace`               | The namespace of the resource.                                                     |
| `-o`         | `--output=`                 | Change the graph output with `wide`, `json`, or `dot` for a [Graphviz dot](https://graphviz.org/docs/layouts/dot/) output. |
|              | `--show-connection-secrets` | Print any connection secret names. Doesn't print the secret values.                |
|              | `--show-package-dependencies <filter>` | Show package dependencies. Options are `all` to show every dependency, `unique` to only print a package once or `none` to not print any dependencies. By default the `trace` command uses `--show-package-dependencies unique`.                |
|              | `--show-package-revisions <output>`    | Print package revision versions. Options are `active`, showing only the active revisions, `all` showing all revisions or `none` to print not print any revisions.                 |
|              | `--show-package-runtime-configs` | Print DeploymentRuntimeConfig dependencies.                |
<!-- vale Crossplane.Spelling = YES -->
{{< /table >}}

#### Output options

By default `crossplane beta trace` prints directly to the terminal, limiting the
"Ready" condition and "Status" messages to 64 characters.

The following an example output a "cluster" claim from the AWS reference 
platform, which includes multiple Compositions and composed resources: 

```shell {copy-lines="1"}
crossplane beta trace cluster.aws.platformref.upbound.io platform-ref-aws
NAME                                                                               VERSION   INSTALLED   HEALTHY   STATE    STATUS
Configuration/platform-ref-aws                                                     v0.9.0    True        True      -        HealthyPackageRevision
├─ ConfigurationRevision/platform-ref-aws-9ad7b5db2899                             v0.9.0    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-network                                 v0.7.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-network-97be9100cfe1         v0.7.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-ec2                                            v0.47.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                    v0.47.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v1.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v1.0.0    -           True      Active   HealthyPackageRevision
│  └─ Function/upbound-function-patch-and-transform                                v0.2.1    True        True      -        HealthyPackageRevision
│     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715        v0.2.1    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-database                                v0.5.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-database-3112f0a765c5        v0.5.0    -           True      Active   HealthyPackageRevision
│  └─ Provider/upbound-provider-aws-rds                                            v0.47.0   True        True      -        HealthyPackageRevision
│     └─ ProviderRevision/upbound-provider-aws-rds-58f96aa9fc4b                    v0.47.0   -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-eks                                     v0.5.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-eks-83c9d65f4a47             v0.5.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-helm                                    v0.16.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-helm-b4cc4c2c8db3            v0.16.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-kubernetes                              v0.10.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-kubernetes-63506a3443e0      v0.10.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-eks                                            v0.47.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/upbound-provider-aws-eks-641a096d79d8                    v0.47.0   -           True      Active   HealthyPackageRevision
│  └─ Provider/upbound-provider-aws-iam                                            v0.47.0   True        True      -        HealthyPackageRevision
│     └─ ProviderRevision/upbound-provider-aws-iam-438eac423037                    v0.47.0   -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-app                                         v0.2.0    True        True      -        HealthyPackageRevision
│  └─ ConfigurationRevision/upbound-configuration-app-5d95726dba8c                 v0.2.0    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-observability-oss                           v0.2.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-observability-oss-a51529457ad7   v0.2.0    -           True      Active   HealthyPackageRevision
│  └─ Provider/grafana-provider-grafana                                            v0.8.0    True        True      -        HealthyPackageRevision
│     └─ ProviderRevision/grafana-provider-grafana-ac529c8ce1c6                    v0.8.0    -           True      Active   HealthyPackageRevision
└─ Configuration/upbound-configuration-gitops-flux                                 v0.2.0    True        True      -        HealthyPackageRevision
   └─ ConfigurationRevision/upbound-configuration-gitops-flux-2e80ec62738d         v0.2.0    -           True      Active   HealthyPackageRevision
```

#### Wide outputs
Print the entire "Ready" or "Status" message if they're longer than 
64 characters with `--output=wide`. 

For example, the output truncates the "Status" message that's too long. 

```shell {copy-lines="1"
crossplane trace cluster.aws.platformref.upbound.io platform-ref-aws
NAME                                                              SYNCED   READY   STATUS
Cluster/platform-ref-aws (default)                                True     False   Waiting: ...resource claim is waiting for composite resource to become Ready
```

Use `--output=wide` to see the full message.

```shell {copy-lines="1"
crossplane trace cluster.aws.platformref.upbound.io platform-ref-aws --output=wide
NAME                                                              SYNCED   READY   STATUS
Cluster/platform-ref-aws (default)                                True     False   Waiting: Composite resource claim is waiting for composite resource to become Ready
```

#### Graphviz dot file output

Use the `--output=dot` to print out a textual 
[Graphviz dot](https://graphviz.org/docs/layouts/dot/) output. 

Save the output and export it or the output directly to Graphviz `dot` to 
render an image. 

For example, to save the output as a `graph.png` file use 
`dot -Tpng -o graph.png`.

`crossplane beta trace cluster.aws.platformref.upbound.io platform-ref-aws -o dot | dot -Tpng -o graph.png`

#### Print connection secrets

Use `-s` to print any connection secret names along with the other resources.

{{<hint "important">}}
The `crossplane beta trace` command doesn't print secret values.
{{< /hint >}}

The output includes both the secret name along with the secret's namespace.

```shell
crossplane beta trace configuration platform-ref-aws -s
NAME                                                                        SYNCED   READY   STATUS
Cluster/platform-ref-aws (default)                                          True     True    Available
└─ XCluster/platform-ref-aws-mlnwb                                          True     True    Available
   ├─ XNetwork/platform-ref-aws-mlnwb-6nvkx                                 True     True    Available
   │  ├─ SecurityGroupRule/platform-ref-aws-mlnwb-szgxp                     True     True    Available
   │  └─ Secret/3f11c30b-dd94-4f5b-aff7-10fe4318ab1f (upbound-system)       -        -
   ├─ XEKS/platform-ref-aws-mlnwb-fqjzz                                     True     True    Available
   │  ├─ OpenIDConnectProvider/platform-ref-aws-mlnwb-h26xx                 True     True    Available
   │  └─ Secret/9666eccd-929c-4452-8658-c8c881aee137-eks (upbound-system)   -        -
   ├─ XServices/platform-ref-aws-mlnwb-bgndx                                True     True    Available
   │  ├─ Release/platform-ref-aws-mlnwb-7hfkv                               True     True    Available
   │  └─ Secret/d0955929-892d-40c3-b0e0-a8cabda55895 (upbound-system)       -        -
   └─ Secret/9666eccd-929c-4452-8658-c8c881aee137 (upbound-system)          -        -
```

#### Print package dependencies

Use the `--show-package-dependencies` flag to include more information about
package dependencies.

By default `crossplane beta trace` uses `--show-package-dependencies unique` to
include a required package only once in the output.

Use `--show-package-dependencies all` to see every package requiring the same
dependency. 

```shell
crossplane beta trace configuration platform-ref-aws --show-package-dependencies all
NAME                                                                               VERSION   INSTALLED   HEALTHY   STATE    STATUS
Configuration/platform-ref-aws                                                     v0.9.0    True        True      -        HealthyPackageRevision
├─ ConfigurationRevision/platform-ref-aws-9ad7b5db2899                             v0.9.0    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-network                                 v0.7.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-network-97be9100cfe1         v0.7.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-ec2                                            v0.47.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                    v0.47.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v1.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v1.0.0    -           True      Active   HealthyPackageRevision
│  └─ Function/upbound-function-patch-and-transform                                v0.2.1    True        True      -        HealthyPackageRevision
│     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715        v0.2.1    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-database                                v0.5.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-database-3112f0a765c5        v0.5.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-rds                                            v0.47.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-rds-58f96aa9fc4b                    v0.47.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v1.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v1.0.0    -           True      Active   HealthyPackageRevision
│  └─ Configuration/upbound-configuration-aws-network                              v0.7.0    True        True      -        HealthyPackageRevision
│     ├─ ConfigurationRevision/upbound-configuration-aws-network-97be9100cfe1      v0.7.0    -           True      Active   HealthyPackageRevision
│     ├─ Provider/upbound-provider-aws-ec2                                         v0.47.0   True        True      -        HealthyPackageRevision
│     │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                 v0.47.0   -           True      Active   HealthyPackageRevision
│     │  └─ Provider/upbound-provider-family-aws                                   v1.0.0    True        True      -        HealthyPackageRevision
│     │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964           v1.0.0    -           True      Active   HealthyPackageRevision
│     └─ Function/upbound-function-patch-and-transform                             v0.2.1    True        True      -        HealthyPackageRevision
│        └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715     v0.2.1    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-eks                                     v0.5.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-eks-83c9d65f4a47             v0.5.0    -           True      Active   HealthyPackageRevision
│  ├─ Configuration/upbound-configuration-aws-network                              v0.7.0    True        True      -        HealthyPackageRevision
│  │  ├─ ConfigurationRevision/upbound-configuration-aws-network-97be9100cfe1      v0.7.0    -           True      Active   HealthyPackageRevision
│  │  ├─ Provider/upbound-provider-aws-ec2                                         v0.47.0   True        True      -        HealthyPackageRevision
│  │  │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                 v0.47.0   -           True      Active   HealthyPackageRevision
│  │  │  └─ Provider/upbound-provider-family-aws                                   v1.0.0    True        True      -        HealthyPackageRevision
│  │  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964           v1.0.0    -           True      Active   HealthyPackageRevision
│  │  └─ Function/upbound-function-patch-and-transform                             v0.2.1    True        True      -        HealthyPackageRevision
│  │     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715     v0.2.1    -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-helm                                    v0.16.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-helm-b4cc4c2c8db3            v0.16.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-kubernetes                              v0.10.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-kubernetes-63506a3443e0      v0.10.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-ec2                                            v0.47.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                    v0.47.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v1.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v1.0.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-eks                                            v0.47.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-eks-641a096d79d8                    v0.47.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v1.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v1.0.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-iam                                            v0.47.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-iam-438eac423037                    v0.47.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v1.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v1.0.0    -           True      Active   HealthyPackageRevision
│  └─ Function/upbound-function-patch-and-transform                                v0.2.1    True        True      -        HealthyPackageRevision
│     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715        v0.2.1    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-app                                         v0.2.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-app-5d95726dba8c                 v0.2.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-helm                                    v0.16.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-helm-b4cc4c2c8db3            v0.16.0   -           True      Active   HealthyPackageRevision
│  └─ Function/upbound-function-patch-and-transform                                v0.2.1    True        True      -        HealthyPackageRevision
│     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715        v0.2.1    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-observability-oss                           v0.2.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-observability-oss-a51529457ad7   v0.2.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-helm                                    v0.16.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-helm-b4cc4c2c8db3            v0.16.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-kubernetes                              v0.10.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-kubernetes-63506a3443e0      v0.10.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/grafana-provider-grafana                                            v0.8.0    True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/grafana-provider-grafana-ac529c8ce1c6                    v0.8.0    -           True      Active   HealthyPackageRevision
│  └─ Function/upbound-function-patch-and-transform                                v0.2.1    True        True      -        HealthyPackageRevision
│     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715        v0.2.1    -           True      Active   HealthyPackageRevision
└─ Configuration/upbound-configuration-gitops-flux                                 v0.2.0    True        True      -        HealthyPackageRevision
   ├─ ConfigurationRevision/upbound-configuration-gitops-flux-2e80ec62738d         v0.2.0    -           True      Active   HealthyPackageRevision
   ├─ Provider/crossplane-contrib-provider-helm                                    v0.16.0   True        True      -        HealthyPackageRevision
   │  └─ ProviderRevision/crossplane-contrib-provider-helm-b4cc4c2c8db3            v0.16.0   -           True      Active   HealthyPackageRevision
   └─ Function/upbound-function-patch-and-transform                                v0.2.1    True        True      -        HealthyPackageRevision
      └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715        v0.2.1    -           True      Active   HealthyPackageRevision
```

Use `--show-package-dependencies none` to hide all dependencies.

```shell
crossplane beta trace configuration platform-ref-aws --show-package-dependencies none
NAME                                                     VERSION   INSTALLED   HEALTHY   STATE    STATUS
Configuration/platform-ref-aws                           v0.9.0    True        True      -        HealthyPackageRevision
└─ ConfigurationRevision/platform-ref-aws-9ad7b5db2899   v0.9.0    -           True      Active   HealthyPackageRevision
```

#### Print package revisions

By default the `crossplane beta trace` command only shows the package revisions
actively in use. To view both active and inactive revisions use
`--show-package-revisions all`.

```shell
crossplane beta trace configuration platform-ref-aws --show-package-revisions all
NAME                                                                               VERSION   INSTALLED   HEALTHY   STATE      STATUS
Configuration/platform-ref-aws                                                     v0.9.0    True        True      -          HealthyPackageRevision
├─ ConfigurationRevision/platform-ref-aws-ad01153c1179                             v0.8.0    -           True      Inactive   HealthyPackageRevision
├─ ConfigurationRevision/platform-ref-aws-9ad7b5db2899                             v0.9.0    -           True      Active     HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-network                                 v0.2.0    True        True      -          HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-network-288fcd1b88dd         v0.2.0    -           True      Active     HealthyPackageRevision
│  └─ Provider/upbound-provider-aws-ec2                                            v1.0.0    True        True      -          HealthyPackageRevision
│     ├─ ProviderRevision/upbound-provider-aws-ec2-5cfd948d082f                    v1.0.0    -           True      Active     HealthyPackageRevision
│     └─ Provider/upbound-provider-family-aws                                      v1.0.0    True        True      -          HealthyPackageRevision
│        └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v1.0.0    -           True      Active     HealthyPackageRevision
# Removed for brevity
```

To hide all revisions use `--show-package-revision none`.

```shell
crossplane beta trace configuration platform-ref-aws --show-package-revisions none
NAME                                                       VERSION   INSTALLED   HEALTHY   STATE   STATUS
Configuration/platform-ref-aws                             v0.9.0    True        True      -       HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-network         v0.2.0    True        True      -       HealthyPackageRevision
│  └─ Provider/upbound-provider-aws-ec2                    v1.0.0    True        True      -       HealthyPackageRevision
│     └─ Provider/upbound-provider-family-aws              v1.0.0    True        True      -       HealthyPackageRevision
# Removed for brevity
```

### beta validate

The `crossplane beta validate` command validates 
[compositions]({{<ref "../concepts/compositions">}}) against provider or XRD 
schemas using the Kubernetes API server's validation library.

The `crossplane beta validate` command supports validating the following 
scenarios:

- Validate a managed resource or composite resource 
  [against a Provider or XRD schema](#validate-resources-against-a-schema). 
- Use the output of `crossplane beta render` as [validation input](#validate-render-command-output). 
- Validate an [XRD against Kubernetes Common Expression Language](#validate-common-expression-language-rules) 
  (CEL) rules.
- Validate resources against a [directory of schemas](#validate-against-a-directory-of-schemas).


{{< hint "note" >}}
The `crossplane beta validate` command performs all validation offline. 

A Kubernetes cluster running Crossplane isn't required. 
{{< /hint >}}

#### Flags

{{< table "table table-sm table-striped" >}}
| Short flag   | Long flag                | Description                                           |
| ------------ | ------------------------ | ----------------------------------------------------- |
| `-h`         | `--help`                 | Show context sensitive help.                          |
| `-v`         | `--version`              | Print version and quit.                               |
|              | `--cache-dir=".crossplane/cache"` | Specify the absolute path to the cache directory to store downloaded schemas. |
|              | `--clean-cache`          | Clean the cache directory before downloading package schemas. |
|              | `--skip-success-results` | Skip printing success results.                        |
|              | `--verbose`              | Print verbose logging statements.                     |
{{< /table >}}

#### Validate resources against a schema

The `crossplane beta validate` command can validate an XR and one or more 
managed resources against a provider's schema. 

{{<hint "important" >}}
When validating against a provider the `crossplane beta validate` command
downloads the provider package to the `--cache-dir` directory. By default
Crossplane uses `.crossplane` as the `--cache-dir` location.

Access to a Kubernetes cluster or Crossplane pod isn't required.  
Validation requires the ability to download the provider package.
{{< /hint >}}

The `crossplane beta validate` command downloads and caches the schema CRD files
in the `--cache-dir` directory. By default the Crossplane CLI uses
`.crossplane/cache` as the cache location.

To clear the cache and download the CRD files again use the `--clean-cache` flag.

To validate a managed resource against a provider,
first, create a provider manifest file. For example, to validate an IAM role
from Provider AWS, use the 
[Provider AWS IAM](https://marketplace.upbound.io/providers/upbound/provider-aws-iam/v1.0.0) 
manifest.

{{<hint "tip" >}}
To validate a 
"[family provider](https://blog.upbound.io/new-provider-families)" use the
provider manifests of the resources to validate.
{{< /hint >}}

```yaml
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-iam
spec:
  package: xpkg.upbound.io/upbound/provider-aws-iam:v1.0.0
```

Now include the XR or managed resource to validate.

For example, to validate an 
{{<hover label="iamAK" line="2">}}AccessKey{{</hover>}} managed resource,
provide a managed resource YAML file. 

```yaml {label="iamAK"}
apiVersion: iam.aws.upbound.io/v1beta1
kind: AccessKey
metadata:
  name: sample-access-key-0
spec:
  forProvider:
    userSelector:
      matchLabels:
        example-name: test-user-0
```

Run the `crossplane beta validate` command providing the provider and managed
resource YAML files as input. 

```shell
crossplane beta validate provider.yaml managedResource.yaml
[✓] iam.aws.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-0 validated successfully
Total 1 resources: 0 missing schemas, 1 success case, 0 failure cases
```


#### Validate render command output

You can pipe the output of `crossplane beta render` into 
`crossplane beta validate` to validate complete Crossplane resource pipelines,
including XRs, compositions and composition functions. 

Use the `--include-full-xr` command with `crossplane beta render` and the `-` 
option with `crossplane beta validate` to pipe the output from 
`crossplane beta render` to the input of `crossplane beta validate`. 

```shell {copy-lines="1"}
crossplane beta render xr.yaml composition.yaml function.yaml --include-full-xr | crossplane beta validate schemas.yaml -
[x] schema validation error example.crossplane.io/v1beta1, Kind=XR, example : status.conditions[0].lastTransitionTime: Invalid value: "null": status.conditions[0].lastTransitionTime in body must be of type string: "null"
[x] schema validation error example.crossplane.io/v1beta1, Kind=XR, example : spec: Required value
[✓] iam.aws.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-0 validated successfully
[✓] iam.aws.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-1 validated successfully
[✓] iam.aws.upbound.io/v1beta1, Kind=User, test-user-0 validated successfully
[✓] iam.aws.upbound.io/v1beta1, Kind=User, test-user-1 validated successfully
Total 5 resources: 0 missing schemas, 4 success cases, 1 failure cases
```


#### Validate Common Expression Language rules
XRDs can define [validation rules](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#validation-rules) expressed in the Common Expression Language 
([CEL](https://kubernetes.io/docs/reference/using-api/cel/)).


Apply a CEL rule with the 
{{<hover label="celXRD" line="12" >}}x-kubernetes-validations{{</hover>}} key
inside the schema {{<hover label="celXRD" line="10" >}}spec{{</hover>}} object of an XRD.

```yaml {label="celXRD"}
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: myXR.crossplane.io
spec:
# Removed for brevity
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              x-kubernetes-validations:
              - rule: "self.minReplicas <= self.replicas && self.replicas <= self.maxReplicas"
                message: "replicas should be in between minReplicas and maxReplicas."
              properties:
                minReplicas:
                  type: integer
                maxReplicas:
                  type: integer
                replicas: 
                  type: integer
# Removed for brevity
```

The rule in this example checks that the vale of the
{{<hover label="celXR" line="6">}}replicas{{</hover>}} field of an XR is between
the {{<hover label="celXR" line="7">}}minReplicas{{</hover>}} and 
{{<hover label="celXR" line="8">}}maxReplicas{{</hover>}} values.

```yaml {label="celXR"}
apiVersion: example.crossplane.io/v1beta1
kind: XR
metadata:
  name: example
spec:
  replicas: 49
  minReplicas: 1
  maxReplicas: 30
```

Running `crossplane beta validate` with the example XRD and XR produces an
error.

```shell
`crossplane beta validate xrd.yaml xr.yaml
[x] CEL validation error example.crossplane.io/v1beta1, Kind=XR, example : spec: Invalid value: "object": replicas should be in between minReplicas and maxReplicas.
Total 1 resources: 0 missing schemas, 0 success cases, 1 failure cases
```


#### Validate against a directory of schemas

The `crossplane beta render` command can validate a directory of YAML files. 

The command only processes `.yaml` and `.yml` files, while ignoring all other
file types.

With a directory of files, provide the directory and resource to validate. 

For example, using a directory named 
{{<hover label="validateDir" line="2">}}schemas{{</hover>}} containing the XRD
and Provider schemas.

```shell {label="validateDir"}
tree
schemas
|-- platform-ref-aws.yaml
|-- providers
|   |-- a.txt
|   `-- provider-aws-iam.yaml
`-- xrds
    `-- xrd.yaml
```

Provide the directory name and a resource YAML file to the 
`crossplane beta validate` command. 

```shell
crossplane beta validate schema resources.yaml
[x] schema validation error example.crossplane.io/v1beta1, Kind=XR, example : status.conditions[0].lastTransitionTime: Invalid value: "null": status.conditions[0].lastTransitionTime in body must be of type string: "null"
[x] CEL validation error example.crossplane.io/v1beta1, Kind=XR, example : spec: Invalid value: "object": no such key: minReplicas evaluating rule: replicas should be greater than or equal to minReplicas.
[✓] iam.aws.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-0 validated successfully
[✓] iam.aws.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-1 validated successfully
[✓] iam.aws.upbound.io/v1beta1, Kind=User, test-user-0 validated successfully
[✓] iam.aws.upbound.io/v1beta1, Kind=User, test-user-1 validated successfully
Total 5 resources: 0 missing schemas, 4 success cases, 1 failure cases
```

### beta xpkg init

The `crossplane beta xpkg init` command populates the current directory with 
files to build a package. 

Provide a name to use for the package and the package template to start from 
with the command  
`crossplane beta xpkg init <name> <template>`

The `<name>` input isn't used. Crossplane reserves the `<name>` for future releases.

The `<template>` value may be one of four well known templates:
* `configuration-template` - A template to build a Crossplane [Configuration]({{<ref "../concepts/packages">}}) from the [crossplane/configuration-template](https://github.com/crossplane/configuration-template) repository.
* `function-template-go` - A template to build Crossplane Go [composition functions]({{<ref "../concepts/composition-functions">}}) from the [crossplane/function-template-go](https://github.com/crossplane/function-template-go) repository.
* `function-template-python` - A template to build Crossplane Python [composition functions]({{<ref "../concepts/composition-functions">}}) from the [crossplane/function-template-python](https://github.com/crossplane/function-template-go) repository.
* `provider-template` - A template to build a basic Crossplane provider from the [Crossplane/provider-template](https://github.com/crossplane/provider-template) repository.
* `provider-template-upjet` - A template for building [Upjet](https://github.com/crossplane/upjet) based Crossplane providers from existing Terraform providers. Copies from the [upbound/upjet-provider-template](https://github.com/upbound/upjet-provider-template) repository.

Instead of a well known template the `<template>` value can be a git repository 
URL.

#### NOTES.txt

If the template repository contains a `NOTES.txt` file in its root directory,
the `crossplane beta xpkg init` command prints the contents of the file to the
terminal after populating the directory with the template files. This can be
useful for providing information about the template.

#### init.sh

If the template repository contains an `init.sh` file in its root directory, the
`crossplane beta xpkg init` command starts a dialog after populating the
directory with the template files. The dialog prompts the user if they want
to view or run the script. Use the initialization script to automatically
personalize the template.

#### Flags
{{< table "table table-sm table-striped">}}
| Short flag   | Long flag               | Description                                                                                      |
| ------------ | ----------------------- | ------------------------------                                                                   |
| `-b`         | `--ref-name`            | The branch or tag to clone from the template repository.                                         |
| `-d`         | `--directory`           | The directory to create and load the template files into. Uses the current directory by default. |
| `-r`         | `--run-init-script`     | Run the init.sh script without prompting, if it exists.                                                        |
<!-- vale Crossplane.Spelling = YES -->
{{< /table >}}



