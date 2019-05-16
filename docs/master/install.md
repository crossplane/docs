---
title: Install
toc: true
weight: 320
indent: true
---
# Installing GitLab-Controller

GitLab-Controller can be easily installed into any existing Kubernetes cluster using the regularly published Helm chart.
The Helm chart contains all the custom resources and controllers needed to deploy and configure GitLab-Controller.

## Pre-requisites

* [Kubernetes cluster](https://kubernetes.io/docs/setup/)
  * For example [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/), minimum version `v0.28+`
* [Helm](https://docs.helm.sh/using_helm/), minimum version `v2.9.1+`.
* [Crossplane](https://github.com/crossplaneio/crossplane), `v0.2.0+`

## Installation

Helm charts for GitLab-Controller are currently published to the `alpha` and `master` channels.
In the future, `beta` and `stable` will also be available.

### Alpha

The alpha channel is the most recent release of GitLab-Controller that is considered ready for testing by the community.

```console
helm repo add crossplane-alpha https://charts.crossplane.io/alpha
helm install --name gitlab-controller --namespace crossplane-system crossplane-alpha/gitlab-controller
```

### Master

The `master` channel contains the latest commits, with all automated tests passing.
`master` is subject to instability, incompatibility, and features may be added or removed without much prior notice.
It is recommended to use one of the more stable channels, but if you want the absolute newest GitLab-Controller 
installed, then you can use the `master` channel.

To install the Helm chart from master, you will need to pass the specific version returned by the `search` command:

```console
helm repo add crossplane-master https://charts.crossplane.io/master/
helm search gitlab-controller
helm install --name gitlab-controller --namespace crossplane-system crossplane-master/gitlab-controller --version <version>
```

For example:

```console
helm install --name gitlab-controller --namespace crossplane-system crossplane-master/gitlab-controlelr --version 0.0.0-249.637ccf9
```

## Uninstalling the Chart

To uninstall/delete the `gitlab-controller` application:

```console
helm delete --purge gitlab-controller
```

That command removes all Kubernetes components associated with GitLab-Controller, 
including all the custom resources and controllers.

## Configuration

The following tables lists the configurable parameters of the GitLab-Controller chart and their default values.

| Parameter                 | Description                                                     | Default                                                |
| ------------------------- | --------------------------------------------------------------- | ------------------------------------------------------ |
| `image.repository`        | Image                                                           | `crossplane/gitlab-controller`                                |
| `image.tag`               | Image tag                                                       | `master`                                               |
| `image.pullPolicy`        | Image pull policy                                               | `Always`                                               |
| `imagePullSecrets`        | Names of image pull secrets to use                              | `dockerhub`                                            |
| `replicas`                | The number of replicas to run for the GitLab-Controller operator       | `1`                                                    |
| `deploymentStrategy`      | The deployment strategy for the GitLab-Controller operator             | `RollingUpdate`                                        |

### Command Line

You can pass the settings with helm command line parameters.
Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`.
For example, the following command will install GitLab-Controller with an image pull policy of `IfNotPresent`.

```console
helm install --name gitlab-controller --namespace crossplane-system crossplane-alpha/gitlab-controller --set image.pullPolicy=IfNotPresent
```

### Settings File

Alternatively, a yaml file that specifies the values for the above parameters (`values.yaml`) can be provided while installing the chart.

```console
helm install --name gitlab-controller --namespace crossplane-system crossplane-alpha/gitlab-controller -f values.yaml
```

Here are the sample settings to get you started.

```yaml
replicas: 1

deploymentStrategy: RollingUpdate

image:
  repository: crossplane/gitlab-controller
  tag: master
  pullPolicy: Always

imagePullSecrets:
- dockerhub
```
