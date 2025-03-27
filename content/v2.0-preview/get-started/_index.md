---
title: Get Started
weight: 4
description: Get started with Crossplane.
---

Crossplane has three major components:

* [Composition](#composition)
* [Managed resources](#managed-resources)
* [Package manager](#package-manager)

You can use all the components to build your control plane, or pick only the
ones you need.

# Composition

Composition lets you build custom APIs to control your cloud-native software.

Crossplane extends Kubernetes. You build your custom APIs by using Crossplane to
extend Kubernetes with new custom resources.

To extend Kubernetes without using Crossplane you have to write a Kubernetes
controller. The controller is the software that reacts when a user calls the
custom resource API.

With Crossplane you don't have to write a controller. Instead you configure a
pipeline of functions. The functions tell Crossplane what to do when a user
calls the custom resource API. You can configure the functions using common
languages, including YAML, [KCL](https://www.kcl-lang.io), and
[Python](https://python.org).

You can use composition together with [managed resources](#managed-resources) to
build new custom resource APIs powered by managed resources.

Follow [Get Started with Composition]({{<ref "./get-started-with-composition">}})
to see how composition works.

{{<hint "tip">}}
Not familiar with Kubernetes custom resources and controllers?

Read the Kubernetes documentation on
[custom resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
and [controllers](https://kubernetes.io/docs/concepts/architecture/controller/).

Kubebuilder is a popular project for building Kubernetes controllers. Read the
[Kubebuilder documentation](https://book.kubebuilder.io) to see what's
involved in writing a controller.
{{</hint>}}

# Managed resources

Managed resources (MRs) are ready-made Kubernetes custom resources. 

Each MR extends Kubernetes with the ability to manage a new kind of resource.
For example there's an RDS instance MR that extends Kubernetes with the ability
to manage [AWS RDS](https://aws.amazon.com/rds/) instances.

Crossplane has an extensive library of managed resources you can use to manage
almost any cloud provider, or cloud-native software.

You can use managed resources together with [composition](#composition) to build
new custom resource APIs powered by MRs.

Follow [Get Started with Managed Resources]({{<ref "./get-started-with-managed-resources">}})
to see how managed resources work.

{{<hint "note">}}
Only AWS managed resources support the Crossplane v2 preview.

<!-- vale gitlab.FutureTense = NO -->
Maintainers will update the managed resources for other systems including Azure,
GCP, Terraform, Helm, GitHub, etc to support Crossplane v2 soon.
<!-- vale gitlab.FutureTense = YES -->
{{</hint>}}

# Package manager

The Crossplane package manager lets you install new managed resources and
composition functions.

You can also package any part of a control plane's configuration and install it
using the package manager. This allows you to deploy several control planes with
identical capabilities - for example one control planes per region or per
service.

Read about Crossplane packages in [Concepts]({{<ref "../concepts/packages">}})
to learn about the package manager.