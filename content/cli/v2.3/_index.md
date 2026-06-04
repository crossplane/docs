---
weight: 50
title: CLI Overview
description: "Command-line tools for Crossplane development"
cascade:
    version: "2.3"
---

The Crossplane CLI helps simplify some development and administration aspects of
Crossplane.

The Crossplane CLI includes commands for:

* building, installing, updating and pushing Crossplane Packages
* building platforms using Crossplane Projects
* testing and rendering standalone Composition Functions without the need to
  access a Kubernetes cluster running Crossplane
* troubleshooting Crossplane Compositions, Composite Resources and Managed
  Resources

## Installing the CLI

The Crossplane CLI is a single standalone binary with no external
dependencies. Some commands, such as `crossplane composition render` and
`crossplane project build`, do require a Docker compatible container runtime.

{{<hint "note" >}}
Install the Crossplane CLI on a user's computer.

Most Crossplane CLI commands are independent of Kubernetes and
don't require access to a Crossplane pod.
{{< /hint >}}

You can download the latest version using the install script:

```shell
curl -sfL "https://cli.crossplane.io/install.sh" | sh
```

[The script](https://raw.githubusercontent.com/crossplane/cli/main/install.sh)
detects your operating system and CPU architecture and downloads the appropriate
binary to the current directory. Note that it doesn't attempt to place the
binary in your shell's `$PATH`, so you may want to move it.

{{<expand "Manually install the Crossplane CLI" >}}

If you don't want to run shell script you can manually download a binary from
the Crossplane releases repository at
https://cli.crossplane.io/stable/current/bin

Move the binary to a location in your `$PATH`, for example `/usr/local/bin`.
{{< /expand >}}

### Download other CLI versions

You can download different Crossplane CLI versions or different release branches
with the `XP_CHANNEL` and `XP_VERSION` environmental variables.

By default the CLI installs from the `XP_CHANNEL` named `stable` and the
`XP_VERSION` of `current`, matching the most recent stable release.

For example, to install CLI version `v2.3.0` add `XP_VERSION=v2.3.0` to the
download script curl command:

```shell
curl -sfL "https://cli.crossplane.io/install.sh" | XP_VERSION=v2.3.0 sh
```

To install the latest build from the `main` branch, use the `master` channel by
adding `XP_CHANNEL=master`:

```shell
curl -sfL "https://cli.crossplane.io/install.sh" | XP_CHANNEL=master sh
```
