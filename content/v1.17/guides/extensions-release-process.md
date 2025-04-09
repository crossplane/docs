---
title: Releasing Crossplane Extensions
weight: 80
description: "Configuring build pipelines for Crossplane extensions with GitHub
Actions"
---

Building a Crossplane extension involves creating OCI images in the [xpkg]
format. Authors and maintainers of Crossplane extensions must push their
packages to an OCI registry before Crossplane can reference and use them.

{{< hint "tip" >}}
For more information about Crossplane packages, review the
[xpkg concepts]({{<ref "../../master/concepts/packages" >}}).
{{< /hint >}}

## Typical workflow

This guide covers configuring a GitHub Action for building Crossplane
providers and functions and pushing them to an OCI registry such as `ghcr.io`.

A typical GitHub workflow definition contains the following steps:

1. Fetching the source repository
2. Authenticating to a remote registry
3. Building and packaging artifacts
4. Pushing (publishing) the artifact

{{< hint "warning" >}}
The supplied credentials for the remote registry require read and write access
as upload requests to the registry specify `push` authorization scope.
{{< /hint >}}

The template GitHub repositories for [providers] and [functions] provide
a functional GitHub Action in `.github/workflows/ci.yml`. The following
sections of this guide cover configuration options and conventions for each.

## Common Configuration

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
      - name: Login to Upbound
        uses: docker/login-action@v3
        if: env.XPKG_ACCESS_ID != ''
        with:
          registry: xpkg.upbound.io
          username: ${{ env.XPKG_ACCESS_ID }}
          password: ${{ secrets.XPKG_TOKEN }}
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
which overrides inferring from a git ref or tag. The [`ci.yml`] file for
`crossplane-contrib/function-python` is a good example.
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

The provider template repository includes a top-level `Makefile`. Edit
the following variables to define the target registry:

1. `XPKG_REG_ORGS` - a space-delimited list of target repositories.
2. `XPKG_REG_ORGS_NO_PROMOTE` - for registries that don't use or infer
channel tags, such as `xpkg.upbound.io`.

For example, the following dual-pushes to `xpkg.upbound.io` as well as
`index.docker.io`:

```make
XPKG_REG_ORGS ?= xpkg.upbound.io/crossplane-contrib index.docker.io/crossplanecontrib

XPKG_REG_ORGS_NO_PROMOTE ?= xpkg.upbound.io/crossplane-contrib
```

## Reusable workflows

The [crossplane-contrib/provider-workflows] repository provide reusable
workflow definitions that are callable from a custom CI pipeline.

For example, the following snippet references the callable workflow to
build and push the `provider-kubernetes` package to both `ghcr.io` and
`xpkg.upbound.io`:

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
      XPKG_UPBOUND_TOKEN: ${{ secrets.XPKG_UPBOUND_TOKEN }}
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
[providers]: https://github.com/crossplane/upjet-provider-template/blob/main/.github/workflows/ci.yml
[GitHub Actions Secrets]: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
[build submodule]: https://github.com/crossplane/build
[`ci.yml`]: https://github.com/crossplane-contrib/function-python/blob/main/.github/workflows/ci.yml
[crossplane-contrib/provider-workflows]: https://github.com/crossplane-contrib/provider-workflows/blob/main/.github/workflows
