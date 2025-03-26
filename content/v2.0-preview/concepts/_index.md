---
title: Concepts
weight: 50
description: Understand Crossplane's core components
---

Crossplane extends Kubernetes allowing it to create and manage
resources external to the Kubernetes cluster. Crossplane enables platform 
engineers to create custom APIs and abstractions combining both native 
Kubernetes resources and cloud resources under a single control plane. 

With custom APIs, the platform users, like developers, don't need to know 
any details about the underlying resources or requirements. 

The platform users only need to know the details exposed by the platform, like
`big` or `small` or `US` or `EU`. Platform users don't need to know any details
about the underlying provider like instance type or region names. 

Crossplane uses multiple core components to manage the various elements of
building and managing external resources through Kubernetes. 

* [**The Crossplane pods**]({{<ref "./pods">}}) include the core Crossplane pod and
  Crossplane RBAC manager pod. Together these pods manage all Crossplane
  components and resources. 

* [**Providers**]({{<ref "./providers">}}) connect Kubernetes to any external
  provider, like AWS, Azure or GCP. Providers translate Kubernetes native
  manifests and API calls into external API calls. Providers are responsible for
  creating, deleting and managing the lifecycle of their resources.

* [**Managed resources**]({{<ref "./managed-resources">}}) are Kubernetes objects
  representing things the Provider created outside of Kubernetes. Creating a
  managed resource in Kubernetes requires a Provider to create a resource.
  Deleting a managed resource requires a Provider to delete the associated
  external resource.

* [**Compositions**]({{<ref "./compositions">}}) are a template of managed
  resources. Compositions describe more complex deployments, combining multiple
  managed resources and any resource customizations, like the size of a database
  or the cloud provider region.

* [**Composite Resource Definitions**]({{<ref "./composite-resource-definitions">}})
  represent a custom API, created by platform engineers and consumed by
  developers or end users. Composite resource definitions use an OpenAPIv3
  schema to further extend Kubernetes with custom API endpoints, revisions and
  more. 

* [**Composite Resources**]({{<ref "./composite-resources">}}) represent all the
  objects created by a user calling the custom API. Every time a user access the
  custom API Crossplane creates a single Composite Resource and links all
  the related managed resources to it. 

* [**EnvironmentConfigs**]({{<ref "./environment-configs">}}) are an in-memory
  data store, like a Kubernetes ConfigMap. EnvironmentConfigs are useful for
  custom resource mapping or storing and retrieving data across Composite
  Resources. 

* [**Usages**]({{<ref "./usages">}}) defining critical resources or custom
  dependency mappings. Usages can prevent Crossplane from deleting or can
  ensure that a parent resource waits for Crossplane to delete all child 
  resources first. 

* [**Packages**]({{<ref "./packages">}}) are a convenient way to package up an
  entire custom platform and define any other Crossplane related requirements.
  Packages define how to install Providers, custom APIs or composition functions.

* [**ImageConfigs**]({{<ref "./image-configs">}}) are for centralized control
  of the configuration of Crossplane package images.