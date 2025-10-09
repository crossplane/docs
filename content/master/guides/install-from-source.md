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
This is an advanced installation path for users who
require complete control over the build and deployment process. Most users
should follow the [standard installation instructions]({{<ref "../get-started/install.md">}})
{{< /hint >}}

This approach is useful when you want to:
- Control the entire build and deployment pipeline
- Use your own container registry and cluster
- Deploy to air-gapped or restricted environments
- Build from a specific commit or branch

### Prerequisites

Building Crossplane from source requires:

- [Docker](https://docs.docker.com/get-docker/)
- [Earthly](https://earthly.dev/get-earthly) version `v0.8.16` or later
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured for your target cluster
- An actively [supported Kubernetes version](https://kubernetes.io/releases/patch-releases/#support-period)
- [Helm](https://helm.sh/docs/intro/install/) version `v3.2.0` or later
- Access to a container registry (Docker Hub, GHCR, Harbor, or any OCI-compliant
  registry)

### Clone the Crossplane repository

Clone the Crossplane repository and optionally check out a specific release.

```shell {copy-lines="all"}
git clone https://github.com/crossplane/crossplane.git
cd crossplane
```

{{< hint "tip" >}}
To build a specific release, check out the release tag before building.

```shell
git checkout v2.0.2
```
{{< /hint >}}

### Determine your cluster architecture

Identify your cluster's CPU architecture before building. Crossplane must be
built for the same architecture as your cluster nodes. Here is one possible way to check the
architecture of your cluster:

```shell {copy-lines="1"}
kubectl get nodes -o jsonpath='{.items[0].status.nodeInfo.architecture}'
arm64
```

Save this architecture in an environment variable:

```shell
export CLUSTER_ARCH=<your cluster arch>
```

### Determine artifacts destination

Identify the registry and version tag where you will be pushing your built
software artifacts and save them in environment variables:

```shell {copy-lines="all"}
export REGISTRY="your-registry.com/your-org"; \
  export VERSION="v2.0.0-yourtag"
```

### Build the artifacts

Build Crossplane binaries for your cluster's architecture:

```shell {copy-lines="all"}
earthly --platform=linux/${CLUSTER_ARCH} +go-build --CROSSPLANE_VERSION=${VERSION}
```

Build the Crossplane container image:

```shell {copy-lines="all"}
earthly --platform=linux/${CLUSTER_ARCH} +image \
  --CROSSPLANE_REPO=${REGISTRY}/crossplane \
  --CROSSPLANE_VERSION=${VERSION}
```

Build the Helm chart:
```shell {copy-lines="all"}
earthly +helm-build --CROSSPLANE_VERSION=${VERSION}
```

Earthly creates the container image locally and saves the binaries and Helm
chart under `_output/bin` and `_output/charts/` respectively.

### Push the image to your registry

Log in to your registry of choice and push the Crossplane image that we built in the previous steps.

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

The `crossplane` CLI provides additional commands for managing Crossplane
resources. You can optionally build this binary from source code for your local
machine and use it to manage your control plane.

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
