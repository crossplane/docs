---
title: Building a Development Environment
weight: 30
---

<!-- vale off -->
The Crossplane project consists of several repositories under the crossplane and
crossplane-contrib GitHub organisations. Most of these projects use the Upbound
[build submodule]; a library of common Makefiles. Establishing a development
environment typically requires:

1. Forking and cloning the repository you wish to work on.
1. Installing development dependencies.
1. Running `make` to establish the build submodule.

Run `make help` for information on the available Make targets. Useful targets
include:

* `make reviewable` - Run code generation, linters, and unit tests.
* `make e2e` - Run end-to-end tests.
* `make` - Build Crossplane.

Once you've built Crossplane you can deploy it to a Kubernetes cluster of your
choice. [`kind`] (Kubernetes in Docker) is a good choice for development. The
`kind.sh` script contains several utilities to deploy and run a development
build of Crossplane to `kind`:

```bash
# Build Crossplane locally.
make

# See what commands are available.
./cluster/local/kind.sh help

# Start a new kind cluster. Specifying KUBE_IMAGE is optional.
KUBE_IMAGE=kindest/node:v1.23.0 ./cluster/local/kind.sh up

# Use Helm to deploy the local build of Crossplane.
./cluster/local/kind.sh helm-install

# Use Helm to upgrade the local build of Crossplane.
./cluster/local/kind.sh helm-upgrade
```

When iterating rapidly on a change it can be faster to run Crossplane as a local
process, rather than as a pod deployed by Helm to your Kubernetes cluster. Use
Helm to install your local Crossplane build per the above instructions, then:

```bash
# Stop the Helm-deployed Crossplane pod.
kubectl -n crossplane-system scale deploy crossplane --replicas=0

# Run Crossplane locally; it should connect to your kind cluster if said cluster
# is your active kubectl context. You can also go run cmd/crossplane/main.go.
make run
```

<!-- vale on -->
[Slack]: https://slack.crossplane.io/
[code of conduct]: https://github.com/cncf/foundation/blob/master/code-of-conduct.md
[build submodule]: https://github.com/upbound/build/
[`kind`]: https://kind.sigs.k8s.io/
[Crossplane release cycle]: docs/reference/release-cycle.md
[good git commit hygiene]: https://www.futurelearn.com/info/blog/telling-stories-with-your-git-history
[Developer Certificate of Origin]: https://github.com/apps/dco
[code review comments]: https://github.com/golang/go/wiki/CodeReviewComments
[test review comments]: https://github.com/golang/go/wiki/TestComments
[crossplane-runtime]: https://github.com/crossplane/crossplane-runtime
[docs]: docs/
[Effective Go]: https://golang.org/doc/effective_go
[Observability Developer Guide]: docs/contributing/observability_developer_guide.md
[Dave Cheney's blog]: https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis
[`crossplane-runtime/pkg/errors`]: https://pkg.go.dev/github.com/crossplane/crossplane-runtime/pkg/errors
[golangci-lint]: https://golangci-lint.run/