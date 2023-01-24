---
title: AWS Quickstart Part 2
weight: 120
tocHidden: true
---

{{< hint "important" >}}
This guide is part 2 of a series. Follow **[part 1]({{<ref "provider-aws" >}})** 
to install Crossplane and connect your Kubernetes cluster to AWS.
{{< /hint >}}

This section creates a _Composition_, _Custom Resource Definition_ and _Claim_
to create a custom Kubernetes API to create AWS resources. 

## Prerequisites
* Complete [quickstart part 1]({{<ref "provider-aws" >}}) connecting Kubernetes
  to AWS.
* an AWS account with permissions to create EC2 compute instances


## Create a Composition
[Part 1]({{<ref "provider-aws" >}}) created a single _managed resource_.
A _Composition_ is a template to create multiple _managed resource_ at the same
time.

In this example we will create 