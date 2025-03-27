---
title: "Welcome"
weight: -1
cascade:
    version: "2.0-preview"
---

Welcome to the Crossplane documentation. Crossplane is a control plane framework
for platform engineering. 

Crossplane lets you build control planes to manage your cloud native software.
It lets you design the APIs and abstractions that your users use to interact
with your control planes.

Crossplane has a rich ecosystem of extensions that make building a control plane
faster and easier. It's built on Kubernetes, so it works with all the Kubernetes
tools you already use.

{{< hint "tip" >}}
**A control plane is software that controls other software.**

Control planes are a core cloud native pattern. The major cloud providers are
all built using control planes.

Control planes expose an API. You use the API to tell the control plane what
software it should configure and how - this is your _desired state_.

A control plane can configure any cloud native software. It could deploy an app,
create a load balancer, or create a GitHub repository.

The control plane configures your software, then monitors it throughout its
lifecycle. If your software ever _drifts_ from your desired state, the control
plane automatically corrects the drift.
{{< /hint >}}


# Using the documentation

Crossplane organizes its documentation into the following sections:

* [Get Started]({{<ref "get-started">}}) explains how to install Crossplane and
  create a control plane.

* [Concepts]({{<ref "concepts">}}) introduces Crossplane's key concepts.

* [Guides]({{<ref "guides">}}) guide you through common use cases, like
  monitoring Crossplane or extending it by writing a composition function.

* [CLI Reference]({{<ref "cli">}}) documents the `crossplane` command-line
  interface that you can use to configure a Crossplane control plane.

* [API Reference]({{<ref "api">}}) documents the APIs that you can use to
  configure a Crossplane control plane.
