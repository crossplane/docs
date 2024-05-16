---
title: "Overview"
weight: -1
cascade:
    version: "1.16"
---

{{< img src="/media/banner.png" alt="Crossplane Popsicle Truck" size="large" >}}

<br />

Crossplane is an open source Kubernetes extension that transforms your Kubernetes
cluster into a **universal control plane**.

Crossplane lets you manage anything, anywhere, all through standard Kubernetes
APIs. Crossplane can even let you
[order a pizza](https://blog.crossplane.io/providers-101-ordering-pizza-with-kubernetes-and-crossplane/)
directly from Kubernetes. If it has an API, Crossplane can connect to it.

With Crossplane, platform teams can create new abstractions and custom
APIs with the full power of Kubernetes policies, namespaces, role based access
controls and more. Crossplane brings all your non-Kubernetes resources under
one roof.

Custom APIs, created by platform teams, allow security and compliance
enforcement across resources or clouds, without exposing any complexity to the
developers. A single API call can create multiple resources, in multiple clouds
and use Kubernetes as the control plane for everything.

{{< hint "tip" >}}
**What's a control plane?**
<!-- vale Google.WordList = NO -->
Control planes create and manage the lifecycle of resources. Control planes
constantly _check_ that the intended resources exist, _report_ when the intended
state doesn't match reality and _act_ to make things right.

Crossplane extends the Kubernetes control plane to be a **universal control
plane** to check, report and act on any resource, anywhere.
<!-- vale Google.WordList = YES -->
{{< /hint >}}


# Get started
* [Install Crossplane]({{<ref "software/install">}}) in your Kubernetes cluster
* Learn more about how Crossplane works in the
[Crossplane introduction]({{<ref "getting-started/introduction" >}})
* Join the [Crossplane Slack](https://slack.crossplane.io/) and start a
conversation with a community of over 7,000 operators.


Crossplane is a [Cloud Native Compute Foundation](https://www.cncf.io/) project.
