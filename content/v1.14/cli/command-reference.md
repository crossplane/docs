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

The Crossplane CLI creates a 
single YAML file from a directory of YAML files and combines them as an 
[OCI container image](https://opencontainers.org/).  

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
|              | `--embed-runtime-image-name=NAME`    |  The image name and tag of a container to include in the package. Only for provider and function packages. |
|              | `--embed-runtime-image-tarball=PATH` |  The filename of a container to include in the package. Only for provider and function packages.                              |
| `-e`         | `--examples-root="./examples"`       |  The path to a directory of examples related to the package.                               |
|              | `--ignore=PATH,...`                  |  List of files and directories to ignore.                              |
| `-o`         | `--output=PATH`                      |  Directory and filename of the created package.                             |
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
filename with `--output` or `-o`.  

For example,  
`crossplane xpkg build -o /home/crossplane/example.xpkg`.


#### Include examples

Include YAML files demonstrating how to use the package with `--examples-root`. 

[Upbound Marketplace](https://marketplace.upbound.io/) uses files included with 
`--examples-root` as documentation for published packages.

#### Include a runtime image

Functions and Providers require YAML files describing their dependencies and 
settings as well as a container image for the function or provider controller.

Using `--embed-runtime-image-name` downloads a specified container image and 
includes the image inside the function or provider package. Use the 

The `--embed-runtime-image-tarball` flag includes a local OCI image tarball 
inside the function or provider package.


### xpkg install

Download and install Crossplane packages with  `crossplane xpkg install`.
Crossplane packages.  

By default the `crossplane xpkg install` command uses the Kubernetes 
configuration defined in `~/.kube/config`.  

Define a custom Kubernetes configuration file location with the environmental 
variable `KUBECONFIG`.

#### Flags
{{< table "table table-sm table-striped">}}
| Short flag   | Long flag                            | Description                    |
| ------------ | -------------                        | ------------------------------ |
|    | `--runtime-config=<runtime config name>`    | Install the package with a runtime configuration. | 
| `-m` | `--manual-activation`      | Set the `revisionActiviationPolicy` to `Manual`.  | 
|    | `--package-pull-secrets=<list of secrets>` | A comma-seperated list of Kubernetes secrets to use for authenticating to the package registry. |  
| `-r` | `--revision-history-limit=<number of revisions>` | Set the `revisionHistoryLimit`. Defaults to `1`. | 
| `-w` | `--wait=<number of seconds>`                | Number of seconds to wait for a package to install. | 

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
[manual activation]({{<ref "../concepts/packages#upgrade-policy" >}}), 
preventing an automatic upgrade of a package with `--manual-activation`

#### Authenticate to a private registry

To authenticate to a private package registry use `--package-pull-secrets` and 
provide a list of Kubernetes Secret objects. 

The secrets must be in the same namespace as the Crossplane pod. 

#### Customize the number of stored package versions

By default Crossplane only stores a single inactive package in the local package
cache. 

Store more inactive copies of a package with `--revision-history-limit`. 

Read more about 
[package revisions]({{< ref "../concepts/packages#configuration-revisions" >}}) 
in the package documentation. 

### xpkg login

Use `xpkg login` to authenticate to the 
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

The `crossplane xkpg login` command can use a username and password or Upbound API token.

Provide a username and password with the `--username` and `--password` flags or
set the environmental variable `UP_USER` for a username or `UP_PASSWORD` for the
password. 

Use an Upbound user token instead of a username and password with `--token` or 
the `UP_TOKEN` environmental variable. 

{{< hint "important" >}}
The `--token` or `UP_TOKEN` environmental variables take precedence over a 
username and password.
{{< /hint >}}

Using `-` as the input for `--password` or `--token` hides the input.  
For example, `crossplane xpkg login --password -`.

#### Authenticate with an Upbound organization

Authenticate to a registered organization in the Upbound Marketplace with the 
`--account` option, along with the username and password or token. 

For example, `crossplane xpkg login --account=Upbound --username=my-user --password -`.

### xpkg logout

### xpkg push

### xpkg update

