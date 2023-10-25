---
weight: 400
title: Crossplane CLI
description: "Documentation for the Crossplane command-line interface"
---

The Crossplane CLI helps simplify some development and administration aspects of
Crossplane.

The Crossplane CLI includes:
* tools to build, install, update and push Crossplane Packages
* standalone Composition Function testing and rendering without the need to access a Kubernetes cluster running Crossplane
* visual dependency mapping across Compositions, Composite Resources and Managed Resources

## Installing the CLI

The Crossplane CLI is a single standalone binary with no external dependencies.

{{<hint "note" >}}
Install the Crossplane CLI on a user's computer. 

The Crossplane CLI is independent of Kubernetes and doesn't require a Crossplane
pod.
{{< /hint >}} 

To download the latest version for your CPU architecture with the Crossplane
install script.

```shell
curl -sL "https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh" | sh
```

[The script](https://raw.githubusercontent.com/crossplane/crossplane/master/install.sh)
detects your CPU architecture and downloads the latest stable release.

Manually download a binary from the Crossplane releases repository at 
https://releases.crossplane.io/stable/current/bin

{{<hint "important" >}}
<!-- vale write-good.Passive = NO -->
The CLI is named `crank` in the release repository. Download this file. 
<!-- vale write-good.Passive = YES -->

The `crossplane` binary is the Kubernetes Crossplane pod image.
{{< /hint >}}

Move the binary to a location in your `$PATH`, for example `/usr/local/bin`.