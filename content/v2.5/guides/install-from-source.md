---
title: Install Crossplane from source code
weight: 510
description: "Build and install Crossplane from source code into a control plane"
---

Building Crossplane from the source code gives you complete control over the
build and installation process.

You build the Crossplane container image and Helm chart directly from the source
code, push the image to your own registry, and install to your Kubernetes
cluster.

{{< hint "important" >}}
Installing Crossplane from source is an advanced installation path for users who
require complete control over the build and deployment process. Most users
should follow the [standard installation instructions]({{<ref "../get-started/install.md">}}).
{{< /hint >}}

This approach is useful when you want to:
- Control the entire build and deployment pipeline
- Use your own container registry and cluster
- Deploy to offline or restricted environments
- Build from a specific commit or branch

### Prerequisites

Building Crossplane from source requires:

- [Nix](https://nixos.org/download/) with [flakes enabled](https://wiki.nixos.org/wiki/Flakes#Enable_flakes_permanently_for_the_current_user)
- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured for your target cluster
- An actively [supported Kubernetes version](https://kubernetes.io/releases/patch-releases/#support-period)
- [Helm](https://helm.sh/docs/intro/install/) version `v3.2.0` or later
- Access to a container registry (Docker Hub, GHCR, Harbor, or any OCI compliant
  registry)

Crossplane uses [Nix](https://nixos.org/) for its build system. Nix produces
reproducible, sandboxed builds without requiring a system Go toolchain or other
language-specific dependencies.

{{< hint "tip" >}}
If you can't install Nix, the Crossplane repository includes a `./nix.sh`
wrapper that runs Nix inside a Docker container. Anywhere this guide uses
`nix <command>`, substitute `./nix.sh <command>`. The wrapper has some
limitations around credential handling and build artifact persistence, so
installing Nix natively is the recommended path.
{{< /hint >}}

### Clone the Crossplane repository

Clone the Crossplane repository and optionally checkout a specific release.

```shell {copy-lines="all"}
git clone https://github.com/crossplane/crossplane.git
cd crossplane
```

{{< hint "tip" >}}
To build a specific release, checkout the release tag before building.

```shell
git checkout v2.0.2
```
{{< /hint >}}

### Determine artifacts destination

<!-- vale gitlab.FutureTense = NO -->
Identify the registry and version tag where you will push your built
software artifacts and save them in environment variables:
<!-- vale gitlab.FutureTense = YES -->

```shell {copy-lines="all"}
export REGISTRY="your-registry.com/your-org"; \
  export VERSION="v2.0.0-yourtag"
```

`${VERSION}` should follow the format `vMAJOR.MINOR.PATCH[-suffix]`, for example
`v2.0.0-yourtag`.

The build embeds `${VERSION}` into the Crossplane binary and uses it as the
container image tag and Helm chart version. Nix's sandboxed builds only read
from files tracked by git, so you must write `${VERSION}` into `flake.nix`
before building:

```shell {copy-lines="all"}
sed -i "s|buildVersion = null;|buildVersion = \"${VERSION}\";|" flake.nix
```

{{< hint "tip" >}}
On macOS, use `sed -i ''` instead of `sed -i`:

```shell
sed -i '' "s|buildVersion = null;|buildVersion = \"${VERSION}\";|" flake.nix
```
{{< /hint >}}

### Build the artifacts

Build Crossplane binaries, container images, and Helm chart for all supported
platforms:

```shell {copy-lines="all"}
nix build
```

<!-- vale write-good.Weasel = NO -->
The first run downloads the build toolchain and takes a few minutes. Later
runs reuse the Nix store cache and complete in seconds.
<!-- vale write-good.Weasel = YES -->

The build output is under `./result/`:

- `result/bin/<os>_<arch>/` contains the `crossplane` and `crank` binaries for
  each supported platform.
- `result/charts/crossplane-<version>.tgz` is the Helm chart.
- `result/images/linux_<arch>/image.tar.gz` is the container image tarball for
  each supported Linux architecture.

The build doesn't load images into your local Docker daemon. The push step
loads the image tarballs in `result/images/` automatically.

### Push the image to your registry

{{< hint "important" >}}
If your registry requires authentication, log in with `docker login` before
pushing.
{{< /hint >}}

Push the per-architecture images and assemble a multi-arch manifest with a
single command:

```shell {copy-lines="all"}
nix run .#push-images -- ${REGISTRY}/crossplane
```

{{< hint "note" >}}
If your host Docker uses a credential helper (for example
Docker Desktop on macOS), the helper isn't available on the sandboxed
`PATH` used by `nix run .#push-images`. Bypass the helper for the login
and push by writing auth directly to a temporary Docker configuration:

```shell
export DOCKER_CONFIG=$(mktemp -d)
cat > $DOCKER_CONFIG/config.json <<EOF
{"credHelpers":{"${REGISTRY%%/*}":""}}
EOF
docker login ${REGISTRY%%/*}
nix run .#push-images -- ${REGISTRY}/crossplane
unset DOCKER_CONFIG
```
{{< /hint >}}

This loads each per-architecture image tarball, tags it with
`${REGISTRY}/crossplane:${VERSION}-<arch>`, pushes each, and then creates and
pushes a multi-arch manifest at `${REGISTRY}/crossplane:${VERSION}`.

### Install Crossplane with the custom image

Install Crossplane to your cluster using the built Helm chart and your custom
image:

```shell {copy-lines="all"}
helm install crossplane result/charts/crossplane-${VERSION#v}.tgz \
  --namespace crossplane-system \
  --create-namespace \
  --set image.repository=${REGISTRY}/crossplane \
  --set image.tag=${VERSION} \
  --set image.pullPolicy=IfNotPresent
```

{{< hint "important" >}} If your registry requires authentication, create an
`imagePullSecret` before installing.

```shell
kubectl create secret docker-registry regcred \
  --docker-server=${REGISTRY} \
  --docker-username=<username> \
  --docker-password=<password> \
  --namespace crossplane-system
```

Add the secret reference to the `helm install` command.

```shell
--set imagePullSecrets[0].name=regcred
```
{{< /hint >}}

### Verify the installation

View the installed Crossplane pods with `kubectl get pods`.

```shell {copy-lines="1"}
kubectl get pods -n crossplane-system
NAME                                       READY   STATUS    RESTARTS   AGE
crossplane-5644774bd4-zvcwc                1/1     Running   0          72s
crossplane-rbac-manager-84dc89c564-b9x6q   1/1     Running   0          72s
```

Verify the Crossplane deployment is using your custom image.

```shell {copy-lines="1"}
kubectl get deployment crossplane -n crossplane-system -o jsonpath='{.spec.template.spec.containers[0].image}'
your-registry.com/your-org/crossplane:v2.0.0-yourtag
```

### Optional: Install the Crossplane CLI

The `crossplane` CLI provides commands for managing Crossplane resources. The
build in the previous steps already produced the CLI binary (named `crank`) for
all supported platforms under `result/bin/`. Copy the binary for your system to
your path.

For macOS ARM64:
```shell {copy-lines="all"}
sudo cp result/bin/darwin_arm64/crank /usr/local/bin/crossplane
chmod +x /usr/local/bin/crossplane
```

For Linux AMD64:
```shell {copy-lines="all"}
sudo cp result/bin/linux_amd64/crank /usr/local/bin/crossplane
chmod +x /usr/local/bin/crossplane
```

Verify the installation.

```shell {copy-lines="1"}
crossplane version
v2.0.0-yourtag
```

### Clean up the working tree

The earlier `sed` step modified `flake.nix`, a file that git tracks. After all
build, push, and install steps are complete, revert the change to keep your
working tree clean:

```shell {copy-lines="all"}
git checkout flake.nix
```

Reverting this file before completing the push or install steps causes Nix to
rebuild the flake with `buildVersion = null`, which produces a different
version that doesn't match the artifacts you already built.
