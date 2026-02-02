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
|            | `--verbose` | Print verbose output.        |

{{< /table >}}

<!-- vale Google.Headings = NO -->
<!-- vale Microsoft.Headings = NO -->
## version
<!-- vale Google.Headings = YES -->
<!-- vale Microsoft.Headings = YES -->

The `crossplane version` command returns the version of Crossplane CLI
and the control plane.

```shell
crossplane version
Client Version: v1.17.0
Server Version: v1.17.0
```

<!-- vale Google.Headings = NO -->
## render
<!-- vale Google.Headings = YES -->

The `crossplane render` command previews the output of a
[composite resource]({{<ref "../composition/composite-resources">}}) after applying
any [composition functions]({{<ref "../composition/compositions">}}).

{{< hint "important" >}}
The `crossplane render` command requires you to use composition functions.
{{< /hint >}}

The `crossplane render` command connects to the locally running Docker
Engine to pull and run composition functions.

{{<hint "important">}}
Running `crossplane render` requires [Docker](https://www.docker.com/).
{{< /hint >}}

Provide a composite resource, composition and composition function YAML
definition with the command to render the output locally.

For example,
`crossplane render xr.yaml composition.yaml function.yaml`

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
apiVersion: s3.aws.m.upbound.io/v1beta1
kind: Bucket
metadata:
  annotations:
    crossplane.io/composition-resource-name: my-bucket
  generateName: test-xrender-
  labels:
    crossplane.io/composite: test-xrender
  namespace: default
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

### Flags

{{< table "table table-sm table-striped">}}

| Short flag   | Long flag                             | Description                                           |
| ------------ | -------------                         | ------------------------------                        |
|              | `--context-files=<key>=<file>,<key>=<file>`    | A comma separated list of files to load for function "contexts." |
|              | `--context-values=<key>=<value>,<key>=<value>` | A comma separated list of key-value pairs to load for function "contexts."                                                    |
| `-r`         | `--include-function-results`          | Include the "results" or events from the function.   |
| `-o`         | `--observed-resources=<directory or file>`  | Provide artificial managed resource data to the function. |
| `-e`         | `--extra-resources=PATH`     |  A YAML file or directory of YAML files specifying extra resources to pass to the Function pipeline. |
|  `-c`        | `--include-context`          | Include the context in the rendered output as a resource of kind: Context. |
| `-x`         | `--include-full-xr`          | Include a copy of the input Composite Resource spec and metadata fields in the rendered output.   |
|              | `--timeout=`                          | Amount of time to wait for a function to finish. (Default 1 minute)       |

{{< /table >}}

The `crossplane render` command relies on standard
[Docker environmental variables](https://docs.docker.com/engine/reference/commandline/cli/#environment-variables)
to connect to the local Docker Engine and run composition functions.

### Provide function context

The `--context-files` and `--context-values` flags can provide data
to a function's `context`.
The context is JSON formatted data.

### Include function results

If a function produces Kubernetes events with statuses use the
`--include-function-results` to print them along with the managed resource
outputs.

### Include the composite resource

Composition functions can only change the `status` field of a composite
resource. By default, the `crossplane render` command only prints the
`status` field with `metadata.name`.

Use `--include-full-xr` to print the full composite resource,
including the `spec` and `metadata` fields.

### Mock managed resources

Provide mocked, or artificial data representing a managed resource with
`--observed-resources`. The `crossplane render` command treats the
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

### Mock extra resources

Extra Resources allow a Composition to request Crossplane Objects on the cluster that aren't
part of the Composition. The `--extra-resources` option points at a directory containing
YAML manifests of resources to mock. Use Extra Resources in combination with a function like
[function-extra-resources](https://github.com/crossplane-contrib/function-extra-resources) or the
built-in support in [function-go-templating](https://github.com/crossplane-contrib/function-go-templating?tab=readme-ov-file#extraresources).

<!-- vale Google.Headings = NO -->
## xpkg
<!-- vale Google.Headings = YES -->

The `crossplane xpkg` commands create, install and update Crossplane
[packages]({{<ref "../packages/configurations">}}) and enable authentication
and publishing of Crossplane packages to a Crossplane package registry.

<!-- vale Google.Headings = NO -->
### xpkg build
<!-- vale Google.Headings = YES -->

Using `crossplane xpkg build` provides automation and simplification to build
Crossplane packages.

The Crossplane CLI combines a directory of YAML files and packages them as
an [OCI container image](https://opencontainers.org/).

The CLI applies the required annotations and values to meet the
[Crossplane XPKG specification](https://github.com/crossplane/crossplane/blob/main/contributing/specifications/xpkg.md).

The `crossplane` CLI supports building
[configuration]({{< ref "../packages/configurations" >}}),
[function]({{<ref "../composition/compositions">}}) and
[provider]({{<ref "../packages/providers" >}}) package types.

#### Flags

{{< table "table table-sm table-striped">}}

| Short flag   | Long flag                            | Description                    |
| ------------ | -------------                        | ------------------------------ |
|              | `--embed-runtime-image=NAME`    |  The image name and tag of an image to include in the package. Only for provider and function packages. |
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

#### Include a runtime image

Functions and Providers require YAML files describing their dependencies and
settings and a container image for their runtime.

Using `--embed-runtime-image` runs a specified image and
includes the image inside the function or provider package.

{{<hint "note" >}}
Images referenced with `--embed-runtime-image` must be in the local Docker
cache.

Use `docker pull` to download a missing image.
{{< /hint >}}

The `--embed-runtime-image-tarball` flag includes a local OCI image tarball
inside the function or provider package.

<!-- vale Google.Headings = NO -->
### xpkg init
<!-- vale Google.Headings = YES -->

The `crossplane xpkg init` command populates the current directory with
files to build a package.

Provide a name to use for the package and the package template to start from
with the command
`crossplane xpkg init <name> <template>`

The `<name>` input isn't used. Crossplane reserves the `<name>` for future releases.

The `<template>` value may be one of four well known templates:
* `configuration-template` - A template to build a Crossplane [Configuration]({{<ref "../packages/configurations">}}) from the [crossplane/configuration-template](https://github.com/crossplane/configuration-template) repository.
* `function-template-go` - A template to build Crossplane Go [composition functions]({{<ref "../composition/compositions">}}) from the [crossplane/function-template-go](https://github.com/crossplane/function-template-go) repository.
* `function-template-python` - A template to build Crossplane Python [composition functions]({{<ref "../composition/compositions">}}) from the [crossplane/function-template-python](https://github.com/crossplane/function-template-go) repository.
* `provider-template` - A template to build a basic Crossplane provider from the [Crossplane/provider-template](https://github.com/crossplane/provider-template) repository.
* `provider-template-upjet` - A template for building [Upjet](https://github.com/crossplane/upjet) based Crossplane providers from existing Terraform providers. Copies from the [upbound/upjet-provider-template](https://github.com/upbound/upjet-provider-template) repository.

Instead of a well known template the `<template>` value can be a git repository
URL.

<!-- vale Google.Headings = NO -->
#### NOTES.txt
<!-- vale Google.Headings = YES -->

If the template repository contains a `NOTES.txt` file in its root directory,
the `crossplane xpkg init` command prints the contents of the file to the
terminal after populating the directory with the template files. This can be
useful for providing information about the template.

<!-- vale Google.Headings = NO -->
#### init.sh
<!-- vale Google.Headings = YES -->

If the template repository contains an `init.sh` file in its root directory, the
`crossplane xpkg init` command starts a dialog after populating the
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


<!-- vale Google.Headings = NO -->
### xpkg install
<!-- vale Google.Headings = YES -->

Download and install packages into Crossplane with  `crossplane xpkg install`.

By default the `crossplane xpkg install` command uses the Kubernetes
configuration defined in `~/.kube/config`.

Define a custom Kubernetes configuration file location with the environmental
variable `KUBECONFIG`.

Specify the package kind, package file and optionally a name to give the package
inside Crossplane.

`crossplane xpkg install <package-kind> <registry URL package name and tag> [<optional-name>]`

The `<package-kind>` is either a `configuration`, `function` or `provider`.

For example, to install the latest version of the
[AWS S3 provider](https://github.com/crossplane-contrib/provider-upjet-aws):

`crossplane xpkg install provider xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v2.0.0`

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
[manual activation]({{<ref "../packages/configurations#revision-activation-policy" >}}),
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
[package revisions]({{< ref "../packages/configurations#configuration-revisions" >}})
in the package documentation.

<!-- vale Google.Headings = NO -->
### xpkg login
<!-- vale Google.Headings = YES -->

Use `xpkg login` to authenticate to registries that host Crossplane packages.

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

<!-- vale Google.Headings = NO -->
### xpkg logout
<!-- vale Google.Headings = YES -->

Use `crossplane xpkg logout` to invalidate the current `crossplane xpkg login`
session.

{{< hint "note" >}}
Using `crossplane xpkg logout` removes the `session` from the
`~/.crossplane/config.json` file, but doesn't delete the configuration file.
{{< /hint >}}

<!-- vale Google.Headings = NO -->
### xpkg push
<!-- vale Google.Headings = YES -->

Push a Crossplane package file to a package registry.

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

<!-- vale Google.Headings = NO -->
### xpkg update
<!-- vale Google.Headings = YES -->

The `crossplane xpkg update` command downloads and updates an existing package.

By default the `crossplane xpkg update` command uses the Kubernetes
configuration defined in `~/.kube/config`.

Define a custom Kubernetes configuration file location with the environmental
variable `KUBECONFIG`.

Specify the package kind, package file and optionally the name of the package
already installed in Crossplane.

`crossplane xpkg update <package-kind> <registry package name and tag> [<optional-name>]`

For example, to update to the latest version of the
[AWS S3 provider](https://github.com/crossplane-contrib/provider-upjet-aws):

`crossplane xpkg update provider xpkg.crossplane.io/crossplane-contrib/provider-aws-s3:v2.0.0`


<!-- vale Google.Headings = NO -->
## beta
<!-- vale Google.Headings = YES -->

Crossplane `beta` commands are experimental. These commands may change the
flags, options or outputs in future releases.

Crossplane maintainers may promote or remove commands under `beta` in future
releases.


<!-- vale Google.Headings = NO -->
### beta convert
<!-- vale Google.Headings = YES -->

As Crossplane evolves, its APIs and resources may change. To help with the
migration to the new APIs and resources, the `crossplane beta convert` command
converts a Crossplane resource to a new version or kind.

Use the `crossplane beta convert` command to convert a
ControllerConfig to a [DeploymentRuntimeConfig]({{<ref "../packages/providers#runtime-configuration">}})
or a legacy Composition using `mode: Resources` to a
[Composition pipeline function]({{< ref "../composition/compositions" >}}).

Provide the `crossplane beta convert` command the conversion type, the input
file and optionally, an output file. By default the command writes the output to
standard out.

For example, to convert a ControllerConfig to a DeploymentRuntimeConfig use
`crossplane beta convert deployment-runtime`. For example,

`crossplane beta convert deployment-runtime controllerConfig.yaml -o deploymentConfig.yaml`

To convert a legacy Composition using inline patch and transforms to a pipeline
composition, use `crossplane beta convert pipeline-composition`.

{{< hint "important" >}}
The `pipeline-composition` conversion is **only available in CLI version v1.20**.
This conversion is mandatory when migrating to Crossplane v2, as v2 no longer
supports inline patch and transform compositions. Users must use the v1.20 CLI
to perform this conversion during their upgrade process.
{{< /hint >}}

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


<!-- vale Google.Headings = NO -->
### beta top
<!-- vale Google.Headings = YES -->

The command `crossplane beta top` shows CPU and memory usage of Crossplane
related pods.

```shell
crossplane beta top
TYPE         NAMESPACE   NAME                                                                  CPU(cores)   MEMORY
crossplane   default     crossplane-f98f9ddfd-tnm46                                            4m           32Mi
crossplane   default     crossplane-rbac-manager-74ff459b88-94p8p                              4m           14Mi
provider     default     provider-aws-s3-1f1a3fb08cbc-5c49d84447-sggrq                         3m           108Mi
provider     default     crossplane-contrib-provider-family-aws-48b3b5ccf964-76c9686b6-bgg65   2m           89Mi
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


<!-- vale Google.Headings = NO -->
### beta trace
<!-- vale Google.Headings = YES -->

Use the `crossplane beta trace` command to display a visual relationship of
Crossplane objects. The `trace` command supports XRs, compositions,
functions, managed resources or packages.

The command requires a resource type and a resource name.

`crossplane beta trace <resource kind> <resource name>`

For example to view a resource named `my-xr` of type `example.crossplane.io`:
`crossplane beta trace example.crossplane.io my-xr`

The command also accepts Kubernetes CLI style `<kind>/<name>` input.
For example,
`crossplane beta trace example.crossplane.io/my-xr`

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

#### Wide outputs
Print the entire "Ready" or "Status" message if they're longer than
64 characters with `--output=wide`.

For example, the output truncates the "Status" message that's too long.

```shell {copy-lines="1"
crossplane trace cluster.aws.platformref.upbound.io platform-ref-aws
NAME                                                              SYNCED   READY   STATUS
Cluster/platform-ref-aws (default)                                True     False   Unready resources: cluster
```

Use `--output=wide` to see the full message.

```shell {copy-lines="1"
crossplane trace cluster.aws.platformref.upbound.io platform-ref-aws --output=wide
NAME                                                              SYNCED   READY   STATUS
Cluster/platform-ref-aws (default)                                True     False   Unready resources: cluster
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
│  ├─ Provider/upbound-provider-aws-ec2                                            v2.0.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                    v2.0.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v2.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v2.0.0    -           True      Active   HealthyPackageRevision
│  └─ Function/upbound-function-patch-and-transform                                v0.2.1    True        True      -        HealthyPackageRevision
│     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715        v0.2.1    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-database                                v0.5.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-database-3112f0a765c5        v0.5.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-rds                                            v2.0.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-rds-58f96aa9fc4b                    v2.0.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v2.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v2.0.0    -           True      Active   HealthyPackageRevision
│  └─ Configuration/upbound-configuration-aws-network                              v0.7.0    True        True      -        HealthyPackageRevision
│     ├─ ConfigurationRevision/upbound-configuration-aws-network-97be9100cfe1      v0.7.0    -           True      Active   HealthyPackageRevision
│     ├─ Provider/upbound-provider-aws-ec2                                         v2.0.0   True        True      -        HealthyPackageRevision
│     │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                 v2.0.0   -           True      Active   HealthyPackageRevision
│     │  └─ Provider/upbound-provider-family-aws                                   v2.0.0    True        True      -        HealthyPackageRevision
│     │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964           v2.0.0    -           True      Active   HealthyPackageRevision
│     └─ Function/upbound-function-patch-and-transform                             v0.2.1    True        True      -        HealthyPackageRevision
│        └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715     v0.2.1    -           True      Active   HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-eks                                     v0.5.0    True        True      -        HealthyPackageRevision
│  ├─ ConfigurationRevision/upbound-configuration-aws-eks-83c9d65f4a47             v0.5.0    -           True      Active   HealthyPackageRevision
│  ├─ Configuration/upbound-configuration-aws-network                              v0.7.0    True        True      -        HealthyPackageRevision
│  │  ├─ ConfigurationRevision/upbound-configuration-aws-network-97be9100cfe1      v0.7.0    -           True      Active   HealthyPackageRevision
│  │  ├─ Provider/upbound-provider-aws-ec2                                         v2.0.0   True        True      -        HealthyPackageRevision
│  │  │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                 v2.0.0   -           True      Active   HealthyPackageRevision
│  │  │  └─ Provider/upbound-provider-family-aws                                   v2.0.0    True        True      -        HealthyPackageRevision
│  │  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964           v2.0.0    -           True      Active   HealthyPackageRevision
│  │  └─ Function/upbound-function-patch-and-transform                             v0.2.1    True        True      -        HealthyPackageRevision
│  │     └─ FunctionRevision/upbound-function-patch-and-transform-a2f88f8d8715     v0.2.1    -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-helm                                    v0.16.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-helm-b4cc4c2c8db3            v0.16.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/crossplane-contrib-provider-kubernetes                              v0.10.0   True        True      -        HealthyPackageRevision
│  │  └─ ProviderRevision/crossplane-contrib-provider-kubernetes-63506a3443e0      v0.10.0   -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-ec2                                            v2.0.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-ec2-cfeb0cd0f1d2                    v2.0.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v2.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v2.0.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-eks                                            v2.0.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-eks-641a096d79d8                    v2.0.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v2.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v2.0.0    -           True      Active   HealthyPackageRevision
│  ├─ Provider/upbound-provider-aws-iam                                            v2.0.0   True        True      -        HealthyPackageRevision
│  │  ├─ ProviderRevision/upbound-provider-aws-iam-438eac423037                    v2.0.0   -           True      Active   HealthyPackageRevision
│  │  └─ Provider/upbound-provider-family-aws                                      v2.0.0    True        True      -        HealthyPackageRevision
│  │     └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v2.0.0    -           True      Active   HealthyPackageRevision
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
│  └─ Provider/upbound-provider-aws-ec2                                            v2.0.0    True        True      -          HealthyPackageRevision
│     ├─ ProviderRevision/upbound-provider-aws-ec2-5cfd948d082f                    v2.0.0    -           True      Active     HealthyPackageRevision
│     └─ Provider/upbound-provider-family-aws                                      v2.0.0    True        True      -          HealthyPackageRevision
│        └─ ProviderRevision/upbound-provider-family-aws-48b3b5ccf964              v2.0.0    -           True      Active     HealthyPackageRevision
# Removed for brevity
```

To hide all revisions use `--show-package-revision none`.

```shell
crossplane beta trace configuration platform-ref-aws --show-package-revisions none
NAME                                                       VERSION   INSTALLED   HEALTHY   STATE   STATUS
Configuration/platform-ref-aws                             v0.9.0    True        True      -       HealthyPackageRevision
├─ Configuration/upbound-configuration-aws-network         v0.2.0    True        True      -       HealthyPackageRevision
│  └─ Provider/upbound-provider-aws-ec2                    v2.0.0    True        True      -       HealthyPackageRevision
│     └─ Provider/upbound-provider-family-aws              v2.0.0    True        True      -       HealthyPackageRevision
# Removed for brevity
```

<!-- vale Google.Headings = NO -->
### beta validate
<!-- vale Google.Headings = YES -->

The `crossplane beta validate` command validates
[compositions]({{<ref "../composition/compositions">}}) against provider or XRD
schemas using the Kubernetes API server's validation library
with extra validation such as checking for unknown fields,
a common source of difficult to debug issues in Crossplane.

The `crossplane beta validate` command supports validating the following
scenarios:

- Validate a managed resource or composite resource
  [against a Provider or XRD schema](#validate-resources-against-a-schema).
- Use the output of `crossplane render` as [validation input](#validate-render-command-output).
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
[Provider AWS IAM](https://github.com/crossplane-contrib/provider-upjet-aws)
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
  name: crossplane-contrib-provider-aws-iam
spec:
  package: xpkg.crossplane.io/crossplane-contrib/provider-aws-iam:v2.0.0
```

Now include the XR or managed resource to validate.

For example, to validate an
{{<hover label="iamAK" line="2">}}AccessKey{{</hover>}} managed resource,
provide a managed resource YAML file.

```yaml {label="iamAK"}
apiVersion: iam.aws.m.upbound.io/v1beta1
kind: AccessKey
metadata:
  namespace: default
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
[✓] iam.aws.m.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-0 validated successfully
Total 1 resources: 0 missing schemas, 1 success case, 0 failure cases
```

#### Validate render command output

You can pipe the output of `crossplane render` into
`crossplane beta validate` to validate complete Crossplane resource pipelines,
including XRs, compositions and composition functions.

Use the `--include-full-xr` command with `crossplane render` and the `-`
option with `crossplane beta validate` to pipe the output from
`crossplane render` to the input of `crossplane beta validate`.

```shell {copy-lines="1"}
crossplane render xr.yaml composition.yaml function.yaml --include-full-xr | crossplane beta validate schemas.yaml -
[x] schema validation error example.crossplane.io/v1beta1, Kind=XR, example : status.conditions[0].lastTransitionTime: Invalid value: "null": status.conditions[0].lastTransitionTime in body must be of type string: "null"
[x] schema validation error example.crossplane.io/v1beta1, Kind=XR, example : spec: Required value
[✓] iam.aws.m.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-0 validated successfully
[✓] iam.aws.m.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-1 validated successfully
[✓] iam.aws.m.upbound.io/v1beta1, Kind=User, test-user-0 validated successfully
[✓] iam.aws.m.upbound.io/v1beta1, Kind=User, test-user-1 validated successfully
Total 5 resources: 0 missing schemas, 4 success cases, 1 failure cases
```

<!-- vale Google.Headings = NO -->
#### Validate Common Expression Language rules
<!-- vale Google.Headings = YES -->

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

The `crossplane render` command can validate a directory of YAML files.

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
[✓] iam.aws.m.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-0 validated successfully
[✓] iam.aws.m.upbound.io/v1beta1, Kind=AccessKey, sample-access-key-1 validated successfully
[✓] iam.aws.m.upbound.io/v1beta1, Kind=User, test-user-0 validated successfully
[✓] iam.aws.m.upbound.io/v1beta1, Kind=User, test-user-1 validated successfully
Total 5 resources: 0 missing schemas, 4 success cases, 1 failure cases
```

### beta lint

The `crossplane beta lint` command checks [composite resource definitions]({{<ref "../concepts/composite-resource-definitions">}})
against a set of best practices. These rules help ensure that your XRDs are well-formed and follow Crossplane's API design guidelines.

{{< hint "note" >}}
The `crossplane beta lint` command performs all checks offline.

A Kubernetes cluster running Crossplane isn't required.
{{< /hint >}}

#### Flags

{{< table "table table-sm table-striped" >}}
| Short flag   | Long flag          | Description                                                              |
| ------------ | ------------------ | ------------------------------------------------------------------------ |
| `-h`         | `--help`           | Show context sensitive help.                                             |
| `-o`         | `--output`         | Output format. Valid values are stdout (default) or json.                |
|              | `--skip-reference` | Skip printing the reference docs to the rule that was violated.          |
{{< /table >}}

#### Rules

##### XRD001 - No boolean fields

Boolean fields are inflexible and cannot be extended. Replace them with enum-based strings so you can introduce additional states later.
See [Kubernetes API conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#primitive-types) 

```yaml {label="Incorrect:"}
# Removed for brevity
properties:
  spec:
    type: object
    properties:
      enabled:
        type: boolean # flagged by XRD001
```

```yaml {label="Best practice:"}
# Removed for brevity
properties:
  enabled:
    type: string
    enum:
      - Enabled
      - Disabled
```

##### XRD002 - Check for required fields

Marking fields as required up front forces every user to provide them and makes future changes risky - this rule flags any `required:`
list in your XRD so you can decide if each field truly needs to be mandatory.

```yaml
# Removed for brevity
properties:
  spec:
    type: object
    properties:
      version:
        type: string
    required: # flagged by XRD002
      - version
```

##### XRD003 - Check for missing descriptions

Every property in your schema should include a description: so that `kubectl explain` and documentation generators can produce helpful output.

```yaml {label="Incorrect:"}
# Removed for brevity
versions:
- name: v1alpha1
  schema:
    openAPIV3Schema:
      type: object
      properties:
        spec:
          type: object
          properties:
            version: # flagged by XRD003
              type: string

```

```yaml {label="Best practice:"}
# Removed for brevity
properties:
  spec:
    type: object
    properties:
      version:
        type: string
        description: |
          The version of the database engine to deploy.
```

#### Ignore rules

If you need to opt out of a specific check for example, a field that you know is safe even though it violates a rule
you can append a `# nolint <RULE_ID>` comment directly above the violating node or line:

```yaml {label="Missing description"}
# Removed for brevity
properties:
  spec:
    type: object
    properties:
      # nolint XRD003
      version:
        type: string
```

```yaml {label="Boolean field"}
# Removed for brevity
properties:
  spec:
    type: object
    properties:
      version:
        # nolint XRD001
        type: boolean
```

#### Example usage

Running the command on an XRD file:

```shell
crossplane beta lint my-xrd.yaml
xdatabases.custom-api.example.org:20 [XRD001] Boolean field detected at path spec.versions[0].schema.openAPIV3Schema.properties.spec.properties.enabled — consider using an enum instead for extensibility. More information: (https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#primitive-types)
xdatabases.custom-api.example.org:25 [XRD002] Required field 'enabled' at path spec.versions[0].schema.openAPIV3Schema.properties.spec.required — consider making it optional with a default.
Found 2 issues: 0 errors, 2 warnings
exit status 2
```

This outputs any violations of the best practices, along with references to the relevant guidelines for fixing them.

To integrate in CI or tooling, output as JSON (--output=json):

```shell
crossplane beta lint my-xrd.yaml --output=json
{
  "summary": {
    "valid": false,
    "total": 3,
    "errors": 0,
    "warnings": 3
  },
  "issues": [
    {
      "id": "XRD001",
      "name": "xdatabases.custom-api.example.org",
      "line": 20,
      "error": false,
      "reference": "https://github.com/kubernetes/community/blob/master/contributors/devel/sig-archi
tecture/api-conventions.md#primitive-types",
      "message": "Boolean field detected at path spec.versions[0].schema.openAPIV3Schema.properties.
spec.properties.enabled — consider using an enum instead for extensibility."
    },
    ...
  ]
}
```
