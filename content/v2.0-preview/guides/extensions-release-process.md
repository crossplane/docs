---
title: Releasing Crossplane Extensions
weight: 80
description: "Configuring build pipelines for Crossplane extensions with GitHub
Actions"
---

## Distributing Crossplane extensions

Crossplane provides a packaging specification for extending a Crossplane
instance with APIs and business logic for composing resources.

Building a Crossplane extension involves creating OCI images in the [xpkg]
format. Authors and maintainers of Crossplane extensions must push their
packages to an OCI registry before users can reference and use them.

The release process for Crossplane extensions grew organically in the community
and developed its own conventions and common configurations. Authors of these
extensions should follow this guide to enable automation for building
and pushing their packages as part of their git workflow.

This guide provides step-by-step instructions for configuring automated
CI pipelines in GitHub Actions for pushing your Crossplane extensions to
`xpkg.crossplane.io`, the main registry that the Crossplane community
uses today.

{{< hint "tip" >}}
For more information about Crossplane packages, review the
[xpkg concepts]({{<ref "../packages" >}}).
{{< /hint >}}

## Typical workflow

A typical GitHub workflow definition to build and release an extension
contains the following steps:

1. Fetching the source repository
2. Authenticating to a remote registry
3. Building and packaging artifacts
4. Pushing (publishing) the artifact

{{< hint "warning" >}}
The supplied credentials for the remote registry require read and write access
as upload requests to the registry specify `push` authorization scope.
{{< /hint >}}

## Quickstart: Releasing a Provider to `xpkg.crossplane.io`

### Prerequisites

- A GitHub repository, for example created from the
[Upjet template](https://github.com/crossplane/upjet-provider-template)

### Steps

1. Create a new YAML file under `.github/workflows`. By convention, name this
file `publish-provider-package.yaml`.
2. Copy the following workflow definition into the file, replacing
`<REPOSITORY NAME>` with the desired name of the repository in the registry.

    ```yaml
    name: Publish Provider Package

    on:
      workflow_dispatch:
        inputs:
          version:
            description: "Version string to use while publishing the package (e.g. v1.0.0-alpha.1)"
            default: ''
            required: false
          go-version:
            description: 'Go version to use if building needs to be done'
            default: '1.23'
            required: false

    jobs:
      publish-provider-package:
        uses: crossplane-contrib/provider-workflows/.github/workflows/publish-provider-non-family.yml@main
        with:
          repository: <REPOSITORY NAME>
          version: ${{ github.event.inputs.version }}
          go-version: ${{ github.event.inputs.go-version }}
          cleanup-disk: true
        secrets:
          GHCR_PAT: ${{ secrets.GITHUB_TOKEN }}
    ```

3. Commit the workflow file to the default branch of the GitHub repository.
4. The workflow should now be available to trigger via the GitHub UI in the
`Actions` tab.
5. Create a release branch with the `release-` prefix in the name in the GitHub UI. For example, `release-0.1`.
6. Tag the desired commit on release branch with a valid semver release tag.
For example, `v0.1.0`. By default, this is the inferred reference pushed to the registry.
7. Manually run the workflow in the GitHub UI, targeting the release branch from step 5.

See [branching conventions](#branching-conventions) for more details on tagging
practices and optionally overriding the inferred git tag version.

## Quickstart: Releasing a Function to `xpkg.crossplane.io`

The template repository for [functions] provides a functional GitHub Action
YAML file that pushes to `xpkg.crossplane.io` without extra configuration.

To build and push a new release to the registry:

1. Cut a release branch with the `release-` prefix in the name in the GitHub UI. For example, `release-0.1`.
2. Tag the desired commit on release branch with a valid semver release tag.
For example, `v0.1.0`. By default, this is the inferred reference pushed to the registry.
3. Manually run the workflow in the GitHub UI, targeting the release branch from step 1.

See [branching conventions](#branching-conventions) for more details on tagging
practices and optionally overriding the inferred git tag version.

## Common Configuration

While the reusable workflows referenced in the quickstart guides are for
convenience, users may choose to write their own custom GitHub Actions.

This and following sections provide more detailed information
about common configuration options and conventions to implement the release
process.

All workflows require references to credentials for a remote registry.
Typically, users configure them as [GitHub Actions Secrets], and the workflow
performs authentication via the`docker/login-action`
[action](http://github.com/docker/login-action).

For example, adding the following step to a pipeline authenticates
the job to `ghcr.io` using the workflow's ephemeral GitHub OIDC token.

```yaml
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}
```

{{< hint "important" >}}
By default, the job's OIDC token don't have permission to write packages
to `ghcr.io`. Permissions are configurable in the GitHub repository's settings
or declared
[explicitly](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token)
in the workflow definition YAML file.
{{< /hint >}}

For other registries, it's still best practice to reference credentials as
custom Secret variables. For example:

```yaml
      - name: Login to Another Registry
        uses: docker/login-action@v3
        with:
          registry: my-registry.io
          username: ${{ env.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
```

## Branching conventions

Repositories for Crossplane extensions follow similar branching conventions
to upstream Crossplane, where the release process assumes the workflow
executing in branches with the `release-*` prefix. `main` is often included,
though a conventional release process would not build and push off of tags on
`main`.

```yaml
on:
  push:
    branches:
      - main
      - release-*
```

For example, when releasing `v0.1.0` of an extension, the conventional
process is to cut a release branch `release-0.1` at the git commit
where it builds from, and tag it as `v0.1.0`.

{{< hint "note" >}}
Some custom workflows may accept an explicit input for the remote reference,
which overrides inferring from a git ref or tag. The [`ci.yml`](https://github.com/crossplane-contrib/function-python/blob/main/.github/workflows/ci.yml)
file for `crossplane-contrib/function-python` is a good example.
{{< /hint >}}

## Configuring workflows for function packages

Function workflow definitions differ based on the base language the
function implementation uses. For example, a Python function requires
a Python environment in the GitHub Action runner:

```yaml
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Setup Hatch
        run: pipx install hatch==1.7.0

      - name: Lint
        run: hatch run lint:check
```

While the template repository provides a working pipeline definition, users may
choose to customize their environment with different tooling.

Functions also require a runtime image of the core business logic to
build and embed into the Function package. The default workflow definition
builds for two platforms: `linux/amd64` and `linux/arm64`.

```yaml
      - name: Build Runtime
        id: image
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/${{ matrix.arch }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          target: image
          build-args:
            PYTHON_VERSION=${{ env.PYTHON_VERSION }}
          outputs: type=docker,dest=runtime-${{ matrix.arch }}.tar
```

## Configuring workflows for provider packages

Providers, unlike Functions, use custom `make` targets in the [build submodule]
for building and pushing Crossplane Provider packages.

Configuring the workflow for a specific registry involves two steps:

1. Updating the registry variables in the top-level `Makefile`.
2. Referencing GitHub Actions Secrets for authorized credentials to the
registry.

### Configure target registry

The provider template repository includes a top-level [`Makefile`](https://github.com/crossplane/upjet-provider-template/blob/main/Makefile).
Edit the following variables to define the target registry:

1. `XPKG_REG_ORGS` - a space-delimited list of target repositories.
2. `XPKG_REG_ORGS_NO_PROMOTE` - for registries that don't use or infer
channel tags.

For example, the following dual-pushes to `xpkg.crossplane.io` as well as
`index.docker.io`:

```make
XPKG_REG_ORGS ?= xpkg.crossplane.io/crossplane-contrib index.docker.io/crossplanecontrib

XPKG_REG_ORGS_NO_PROMOTE ?= xpkg.crossplane.io/crossplane-contrib
```

## Reusable workflows

The [crossplane-contrib/provider-workflows] repository provide reusable
workflow definitions that are callable from a custom CI pipeline.

For example, the following snippet references the callable workflow to
build and push the `provider-kubernetes` package to `xpkg.crossplane.io`:

```yaml
jobs:
  publish-provider-package:
    uses: crossplane-contrib/provider-workflows/.github/workflows/publish-provider-non-family.yml@main
    with:
      repository: provider-kubernetes
      version: ${{ github.event.inputs.version }}
      go-version: ${{ github.event.inputs.go-version }}
      cleanup-disk: true
    secrets:
      GHCR_PAT: ${{ secrets.GITHUB_TOKEN }}
```

{{< hint "tip" >}}
The reusable workflows referenced here publish to `ghcr.io` by default.
Ensure that the default GitHub Actions OIDC token inherits the
`packages: write` permission.
{{< /hint >}}

## Troubleshooting

{{< expand "Why is my workflow is failing with a 404 error code?" >}}
Ensure the target repository exists in the registry. You need to create
it if it doesn't already exist.
{{</expand >}}

{{< expand "Why is my workflow failing with a 401 error code?" >}}
Ensure the credentials used during the registry login step has authorization to
pull and push, and that the `{{ secrets.* }}` variable substitutions match
what's configured in GitHub.
{{</expand >}}

<!-- Named Links -->
[xpkg]: https://github.com/crossplane/crossplane/blob/main/contributing/specifications/xpkg.md
[functions]: https://github.com/crossplane/function-template-go/blob/main/.github/workflows/ci.yml
[GitHub Actions Secrets]: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
[build submodule]: https://github.com/crossplane/build
[crossplane-contrib/provider-workflows]: https://github.com/crossplane-contrib/provider-workflows/blob/main/.github/workflows
