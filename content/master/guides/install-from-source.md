---
title: Install Crossplane from source code
weight: 510
description: "Build and install Crossplane from source code into a control plane"
---

Building Crossplane from the source code gives you complete control over the
build and installation process.

You build the Crossplane container image and Helm chart directly from the source
code.
Then push the image to your own registry and install to your Kubernetes cluster.

{{< hint "important" >}}
Installing Crossplane from source is an advanced installation path for users who
require complete control over the build and deployment process. Most users
should follow the [standard installation instructions]({{<ref "../get-started/install.md">}})
{{< /hint >}}

This approach is useful when you want to:
- Control the entire build and deployment pipeline
- Use your own container registry and cluster
- Deploy to offline or restricted environments
- Build from a specific commit or branch

### Prerequisites

Building Crossplane from source requires:

- [Docker](https://docs.docker.com/get-docker/)
- [Earthly](https://earthly.dev/get-earthly) version `v0.8.16` or later
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured for your target cluster
- An actively [supported Kubernetes version](https://kubernetes.io/releases/patch-releases/#support-period)
- [Helm](https://helm.sh/docs/intro/install/) version `v3.2.0` or later
- Access to a container registry (Docker Hub, GHCR, Harbor, or any OCI compliant
  registry)

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

### Build the artifacts

Build Crossplane binaries, container image, and Helm chart for multi-platform architectures:

```shell {copy-lines="all"}
earthly +multiplatform-build \
  --CROSSPLANE_REPO=${REGISTRY}/crossplane \
  --CROSSPLANE_VERSION=${VERSION}
```

Earthly creates the container image locally and saves the binaries under
`_output/bin` and the Helm chart under `_output/charts/`.

### Push the image to your registry

<!-- vale write-good.Passive = NO -->
Log in to your registry of choice and push the Crossplane image from the
previous steps.
<!-- vale write-good.Passive = YES -->

{{< hint "tip" >}}
Ensure you log into your registry before attempting to `push`.
{{< /hint >}}

```shell {copy-lines="all"}
docker push ${REGISTRY}/crossplane:${VERSION}
```

### Install Crossplane with the custom image

Locate the built Helm chart in the `_output/charts/` directory.

```shell {copy-lines="all"}
CHART_PATH="_output/charts/crossplane-${VERSION#v}.tgz"
```

Install Crossplane to your cluster using the custom image.

```shell {copy-lines="all"}
helm install crossplane ${CHART_PATH} \
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

### Optional: Build the Crossplane CLI

The `crossplane` CLI provides commands for managing Crossplane resources. You
can optionally build this binary from source code for your local machine and use
it to manage your control plane.

Build the CLI for your local machine.

```shell {copy-lines="all"}
earthly +build --CROSSPLANE_VERSION=${VERSION}
```

Earthly creates the CLI binary in `_output/bin/<OS>_<ARCH>/`. Copy it to your
system path.

For macOS ARM64:
```shell {copy-lines="all"}
sudo cp _output/bin/darwin_arm64/crank /usr/local/bin/crossplane
chmod +x /usr/local/bin/crossplane
```

For Linux AMD64:
```shell {copy-lines="all"}
sudo cp _output/bin/linux_amd64/crank /usr/local/bin/crossplane
chmod +x /usr/local/bin/crossplane
```

Verify the installation.

```shell {copy-lines="1"}
crossplane version
v2.0.0-yourtag
```
