---
title: Multi-Tenant Crossplane
weight: 240
---

This guide describes how to use Crossplane effectively in multi-tenant
environments by using Kubernetes primitives and compatible policy
enforcement projects in the cloud native ecosystem.

## Summary

Infrastructure operators in multi-tenant Crossplane environments typically
use composition and Kubernetes RBAC to define lightweight, standardized
policies that dictate what level of self-service developers have when
requesting infrastructure. Crossplane achieves this self-service by exposing
abstract resource types at the namespace scope, defining `Roles` for teams and
individuals in that namespace, and patching the `spec.providerConfigRef` of
the underlying managed resources so that they use a specific `ProviderConfig`
and credentials when provisioned from each namespace. Larger organizations, or
those with more complex environments, may choose to incorporate third-party
policy engines, or scale to multiple Crossplane clusters. The following sections
describe each of these scenarios in greater detail.

- [Summary](#summary)
- [Background](#background)
  - [Cluster-scoped managed resources](#cluster-scoped-managed-resources)
  - [Namespace-scoped claims](#namespace-scoped-claims)
- [Single cluster multi-tenancy](#single-cluster-multi-tenancy)
  - [Composition as an Isolation Mechanism](#composition-as-an-isolation-mechanism)
  - [Namespaces as an Isolation Mechanism](#namespaces-as-an-isolation-mechanism)
  - [Policy enforcement with Open Policy Agent](#policy-enforcement-with-open-policy-agent)
- [Multi-cluster multi-tenancy](#multi-cluster-multi-tenancy)
  - [Reproducible platforms with configuration packages](#reproducible-platforms-with-configuration-packages)
  - [Control plane of control planes](#control-plane-of-control-planes)

## Background

Crossplane runs in multi-tenant environments where multiple teams consume the
services and abstractions that infrastructure operators provide in the cluster.
Two major design patterns in the Crossplane ecosystem enable this capability.

### Cluster-scoped managed resources

Typically, Crossplane providers, which supply granular [managed resources] that
reflect an external API, authenticate by using a `ProviderConfig` object that
points to a credentials source (such as a Kubernetes `Secret`, the `Pod`
file system, or an environment variable). Then, every managed resource references
a `ProviderConfig` that points to credentials with permissions to
manage that resource type.

For example, the following `ProviderConfig` for `provider-aws` points to a
Kubernetes `Secret` with AWS credentials.

```yaml
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: cool-aws-creds
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: aws-creds
      key: creds
```

If a user wants these credentials to provision an
`RDSInstance`, they reference the `ProviderConfig` in the object manifest:

```yaml
apiVersion: database.aws.crossplane.io/v1beta1
kind: RDSInstance
metadata:
  name: rdsmysql
spec:
  forProvider:
    region: us-east-1
    dbInstanceClass: db.t3.medium
    masterUsername: masteruser
    allocatedStorage: 20
    engine: mysql
    engineVersion: "5.6.35"
    skipFinalSnapshotBeforeDeletion: true
  providerConfigRef:
    name: cool-aws-creds # name of ProviderConfig above
  writeConnectionSecretToRef:
    namespace: crossplane-system
    name: aws-rdsmysql-conn
```

Because both the `ProviderConfig` and all managed resources are cluster-scoped,
the RDS controller in `provider-aws` resolves this reference by fetching the
`ProviderConfig`, obtaining the credentials it points to, and using those
credentials to reconcile the `RDSInstance`. This means that anyone with
[RBAC] to manage `RDSInstance` objects can use any credentials to do so.
In practice, Crossplane assumes that only folks acting as infrastructure
administrators or platform builders interact directly with cluster-scoped
resources.

### Namespace-scoped claims

While managed resources exist at the cluster scope, composite resources, which
a **CompositeResourceDefinition (XRD)** defines, may exist at either
the cluster or namespace scope. Platform builders define XRDs and
**Compositions** that specify what granular managed resources Crossplane
creates in response to creating an instance of the XRD. The
[Composition] documentation has more information about
this architecture.

Every XRD exists at the cluster scope, but only those with `spec.claimNames`
defined have a namespace scoped variant.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: CompositeResourceDefinition
metadata:
  name: xmysqlinstances.example.org
spec:
  group: example.org
  names:
    kind: XMySQLInstance
    plural: xmysqlinstances
  claimNames:
    kind: MySQLInstance
    plural: mysqlinstances
...
```

When you create the preceding example, Crossplane produces two
[CustomResourceDefinitions]:
1. A cluster-scoped type with `kind: XMySQLInstance`. Crossplane calls this a
   **Composite Resource (XR)**.
2. A namespace scoped type with `kind: MySQLInstance`. Crossplane calls this a
   **Claim (XRC)**.

Platform builders may choose to define an arbitrary number of Compositions that
map to these types, meaning that creating a `MySQLInstance` in a given namespace
can result in the creations of any set of managed resources at the cluster
scope. For instance, creating a `MySQLInstance` could result in the creation of
the `RDSInstance` defined preceding.

## Single cluster multi-tenancy

Depending on the size and scope of an organization, platform teams may choose to
run one central Crossplane control plane, or one for each team
or business unit. This section focuses on servicing multiple teams in
a single cluster, which may or may not be one of multiple other Crossplane clusters in
the organization.

### Composition as an Isolation Mechanism

While managed resources always reflect every field that the underlying provider
API exposes, XRDs can have any schema that a platform builder chooses. The
fields in the XRD schema can then map onto fields in the underlying
managed resource defined in a Composition, essentially exposing those fields as
configurable to the consumer of the XR or XRC.

This feature serves as a lightweight policy mechanism by only giving the
consumer the ability to customize the underlying resources to the extent the
platform builder desires. For instance, in the preceding examples, a platform
builder may choose to define a `spec.location` field in the schema of the
`XMySQLInstance` that's an enum with options `east` and `west`. In the
Composition, those fields could map to the `RDSInstance` `spec.region` field,
making the value either `us-east-1` or `us-west-1`. If the Composition defined
no other patches for the `RDSInstance`, giving a user the ability (using RBAC)
to create a `XMySQLInstance` / `MySQLInstance` would be akin to giving the
ability to create a specifically configured `RDSInstance`, where they can only
decide the region where it lives and they're restricted to two options.

This model is in contrast to most infrastructure as code tools where the end
user must have provider credentials to create the underlying resources that
the abstraction renders. Crossplane takes a different approach, defining
various credentials in the cluster (using the `ProviderConfig`), then giving
only the provider controllers the ability to use those credentials and
provision infrastructure on the users behalf. This creates a consistent
permission model, even when using different providers with differing IAM
models, by standardizing on Kubernetes RBAC.

### Namespaces as an Isolation Mechanism

While the ability to define abstract schemas and patches to concrete resource
types using composition is powerful, support for defining Claim types at the
namespace scope enhances this capability further by enabling RBAC to apply
with namespace restrictions. Most users in a cluster don't have access
to cluster-scoped resources as they're considered only relevant to
infrastructure admins by both Kubernetes and Crossplane.

Building on the `XMySQLInstance` / `MySQLInstance` example, a platform
builder may choose to define permissions on `MySQLInstance` at the namespace
scope using a `Role`. This allows for giving users the ability to create and
manage `MySQLInstances` in their given namespace, but not the ability to see
those defined in other namespaces.

Furthermore, because the `metadata.namespace` is a field on the XRC, patching
configures managed resources based on the namespace in which the
corresponding XRC exists. Namespace-scoped patching is useful if a platform
builder wants to set specific credentials or a set of credentials that users
in a given namespace can use when provisioning infrastructure using an XRC.
You can do this today by creating one or more `ProviderConfig` objects that
include the name of the namespace in the `ProviderConfig` name. For example, if
any `MySQLInstance` created in the `team-1` namespace should use specific AWS
credentials when the provider controller creates the underlying `RDSInstance`,
the platform builder could:

1. Define a `ProviderConfig` with name `team-1`.

```yaml
apiVersion: aws.crossplane.io/v1beta1
kind: ProviderConfig
metadata:
  name: team-1
spec:
  credentials:
    source: Secret
    secretRef:
      namespace: crossplane-system
      name: team-1-creds
      key: creds
```

2. Define a `Composition` that patches the namespace of the Claim reference in the XR
   to the `providerConfigRef` of the `RDSInstance`.

```yaml
...
resources:
- base:
    apiVersion: database.aws.crossplane.io/v1beta1
    kind: RDSInstance
    spec:
      forProvider:
      ...
  patches:
  - fromFieldPath: spec.claimRef.namespace
    toFieldPath: spec.providerConfigRef.name
    policy:
      fromFieldPath: Required
```

This results in the `RDSInstance` using the `ProviderConfig` of whatever
namespace held the corresponding `MySQLInstance` at creation time.

> Note that this model only allows for a single `ProviderConfig` per
> namespace. Future Crossplane releases should allow for defining a set
> of `ProviderConfig` that you can pick from using [Multiple Source Field
> patching].

<!-- vale Google.Headings = NO -->
### Policy enforcement with Open Policy Agent
<!-- vale Google.Headings = YES -->

In some Crossplane deployment models, only using composition and RBAC to define
policy isn't flexible enough. Because Crossplane brings
management of external infrastructure to the Kubernetes API, it's well suited
to integrate with other projects in the cloud native ecosystem. Organizations
and individuals that need a more robust policy engine, or just prefer a more
general language for defining policy, often turn to [Open Policy Agent].
OPA allows platform builders to write custom logic in [Rego], a domain specific
language. Writing policy in this manner allows for not only incorporating the
information available in the specific resource that OPA evaluates, but also using
other state represented in the cluster. Crossplane users typically install OPA
[Gatekeeper] to make policy management as streamlined as possible.

> Watch a live demo of using OPA with Crossplane [here].

## Multi-cluster multi-tenancy

Organizations that deploy Crossplane across multiple clusters typically take
advantage of two major features that make managing multiple control planes much
simpler.

### Reproducible platforms with configuration packages

[Configuration packages] allow platform builders to package their XRDs and
Compositions into [OCI images] that distribute via any OCI compliant
image registry. These packages can also declare dependencies on providers,
meaning that a single package can declare all the granular managed resources,
the controllers that must deploy to reconcile them, and the abstract types
that expose the underlying resources using composition.

Organizations with several Crossplane deployments use Configuration packages to
<!-- vale alex.Condescending = NO -->
reproduce their platform in each cluster. This can be as simple as installing
<!-- vale alex.Condescending = YES -->
Crossplane with the flag to automatically install a Configuration package
alongside it.

```
helm install crossplane --namespace crossplane-system crossplane-stable/crossplane --set configuration.packages='{"registry.upbound.io/xp/getting-started-with-aws:latest"}'
```

### Control plane of control planes

Taking the multi-cluster multi-tenancy model one step further, some
organizations opt to manage their multiple Crossplane clusters using a single
central Crossplane control plane. This requires setting up the central cluster,
then using a provider to spin up new clusters (such as an [EKS Cluster] using
[provider-aws]), then using [provider-helm] to install Crossplane into the new
remote cluster, bundling a common Configuration package into each
install using the preceding method.

This advanced pattern allows for full management of Crossplane clusters using
Crossplane itself, and is a scalable solution to providing
dedicated control planes to multiple tenants in a single organization.


<!-- Named Links -->
[managed resources]: {{<ref "../concepts/managed-resources" >}}
[RBAC]: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
[Composition]: {{<ref "../concepts/compositions" >}}
[CustomResourceDefinitions]: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
[Open Policy Agent]: https://www.openpolicyagent.org/
[Rego]: https://www.openpolicyagent.org/docs/latest/policy-language/
[Gatekeeper]: https://open-policy-agent.github.io/gatekeeper/website/docs/
[here]: https://youtu.be/TaF0_syejXc
[Multiple Source Field patching]: https://github.com/crossplane/crossplane/pull/2093
[Configuration packages]: {{<ref "../concepts/packages" >}}
[OCI images]: https://github.com/opencontainers/image-spec
[EKS Cluster]: https://github.com/crossplane-contrib/provider-upjet-aws/blob/main/examples/eks/v1beta2/cluster.yaml
[provider-aws]: https://github.com/crossplane-contrib/provider-upjet-aws
[provider-helm]: https://github.com/crossplane-contrib/provider-helm
[Open Service Broker API]: https://github.com/openservicebrokerapi/servicebroker
[Crossplane Service Broker]: https://github.com/vshn/crossplane-service-broker
[Cloudfoundry]: https://www.cloudfoundry.org/
[Kubernetes Service Catalog]: https://github.com/kubernetes-sigs/service-catalog
[vshn/application-catalog-demo]: https://github.com/vshn/application-catalog-demo
