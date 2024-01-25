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
| `-x`         | `--include-full-xr`          | Include a direct copy of the input XR's spec and metadata fields in the rendered output.   |
| `-o`         | `--observed-resources=<directory or file>`               | Provide artificial managed resource data to the function.                                                    |
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

#### Include the full composite resource in the output

Composition functions can only modify the `status` field of a composite 
resource. Therefore, the `crossplane beta render` command only prints the
`status` field with `metadata.name`. With the `--include-full-xr` flag 
the command prints the full composite resource, including the `spec` 
and `metadata` fields.

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

```yaml {label="or"}
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


### beta trace

Use the `crossplane beta trace` command to display a visual relationship of
Crossplane objects. The `trace` command supports claims, compositions or
managed resources. 

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
| `-s`         | `--show-connection-secrets` | Print any connection secret names. Doesn't print the secret values.                |
<!-- vale Crossplane.Spelling = YES -->
{{< /table >}}

#### Output options

By default `crossplane beta trace` prints directly to the terminal, limiting the
"Ready" condition and "Status" messages to 64 characters.

The following an example output a "cluster" claim from the AWS reference 
platform, which includes multiple Compositions and composed resources: 

```shell {copy-lines="1"}
crossplane beta trace cluster.aws.platformref.upbound.io platform-ref-aws
NAME                                                              SYNCED   READY   STATUS
Cluster/platform-ref-aws (default)                                True     True    Available
└─ XCluster/platform-ref-aws-mlnwb                                True     True    Available
   ├─ XNetwork/platform-ref-aws-mlnwb-6nvkx                       True     True    Available
   │  ├─ VPC/platform-ref-aws-mlnwb-ckblr                         True     True    Available
   │  ├─ InternetGateway/platform-ref-aws-mlnwb-r7w47             True     True    Available
   │  ├─ Subnet/platform-ref-aws-mlnwb-lhr4h                      True     True    Available
   │  ├─ Subnet/platform-ref-aws-mlnwb-bss4b                      True     True    Available
   │  ├─ Subnet/platform-ref-aws-mlnwb-fzbxx                      True     True    Available
   │  ├─ Subnet/platform-ref-aws-mlnwb-vxbf4                      True     True    Available
   │  ├─ RouteTable/platform-ref-aws-mlnwb-cs9nl                  True     True    Available
   │  ├─ Route/platform-ref-aws-mlnwb-vpxdg                       True     True    Available
   │  ├─ MainRouteTableAssociation/platform-ref-aws-mlnwb-sngx5   True     True    Available
   │  ├─ RouteTableAssociation/platform-ref-aws-mlnwb-hprsp       True     True    Available
   │  ├─ RouteTableAssociation/platform-ref-aws-mlnwb-shb8f       True     True    Available
   │  ├─ RouteTableAssociation/platform-ref-aws-mlnwb-hvb2h       True     True    Available
   │  ├─ RouteTableAssociation/platform-ref-aws-mlnwb-m58vl       True     True    Available
   │  ├─ SecurityGroup/platform-ref-aws-mlnwb-xxbl2               True     True    Available
   │  ├─ SecurityGroupRule/platform-ref-aws-mlnwb-7qt56           True     True    Available
   │  └─ SecurityGroupRule/platform-ref-aws-mlnwb-szgxp           True     True    Available
   ├─ XEKS/platform-ref-aws-mlnwb-fqjzz                           True     True    Available
   │  ├─ Role/platform-ref-aws-mlnwb-gmpqv                        True     True    Available
   │  ├─ RolePolicyAttachment/platform-ref-aws-mlnwb-t6rct        True     True    Available
   │  ├─ Cluster/platform-ref-aws-mlnwb-crrt8                     True     True    Available
   │  ├─ ClusterAuth/platform-ref-aws-mlnwb-dgn6f                 True     True    Available
   │  ├─ Role/platform-ref-aws-mlnwb-tdnx4                        True     True    Available
   │  ├─ RolePolicyAttachment/platform-ref-aws-mlnwb-qzljh        True     True    Available
   │  ├─ RolePolicyAttachment/platform-ref-aws-mlnwb-l64q2        True     True    Available
   │  ├─ RolePolicyAttachment/platform-ref-aws-mlnwb-xn2px        True     True    Available
   │  ├─ NodeGroup/platform-ref-aws-mlnwb-4sfss                   True     True    Available
   │  ├─ OpenIDConnectProvider/platform-ref-aws-mlnwb-h26xx       True     True    Available
   │  └─ ProviderConfig/platform-ref-aws                          -        -
   └─ XServices/platform-ref-aws-mlnwb-bgndx                      True     True    Available
      ├─ Release/platform-ref-aws-mlnwb-bcj7r                     True     True    Available
      └─ Release/platform-ref-aws-mlnwb-7hfkv                     True     True    Available
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

### beta xpkg init

The `crossplane beta xpkg init` command populates the current directory with 
files to build a package. 

Provide a name to use for the package and the package template to start from 
with the command  
`crossplane beta xpkg init <name> <template>`

The `<name>` input isn't used. Crossplane reserves the `<name>` for future releases.

The `<template>` value may be one of four well known templates:
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
| `-d`         | `--directory`           | The directory to create and load the template files into. Uses the current directory by default. |
| `-r`         | `--run-init-script`     | Run the init.sh script without prompting, if it exists.                                                        |
<!-- vale Crossplane.Spelling = YES -->
{{< /table >}}

