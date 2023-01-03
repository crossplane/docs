---
title: Updated Files
tochidden: true
---

## /api-docs

[/api-docs]({{<ref "../v1.10/api-docs">}}) directory is deleted. `crossplane.md` is just a redirect to doc.crds.dev

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| _index.md | _deleted_ | 
| crds/ | _deleted_ | 
| crds/meta.pkg.crossplane.io_configurations.yaml | _deleted_  | 
| crds/meta.pkg.crossplane.io_providers.yaml | _deleted_  | 
| crossplane.md | _deleted_ | 
{{< /table >}}

## /cloud-providers
`/cloud-providers` directory is deleted, guides are moved into `Getting Started` directory.

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| [/aws/aws-provider.md]({{<ref "../v1.10/cloud-providers/aws/aws-provider/">}}) |  [Getting Started / Provider-AWS]({{<ref "getting-started/provider-aws/">}})| 
| [/azure/azure-provider.md]({{<ref "../v1.10/cloud-providers/azure/azure-provider/">}}) | [Getting Started / Provider-Azure]({{<ref "getting-started/provider-azure/">}}) | 
| [/gcp/gcp-provider.md]({{<ref "../v1.10/cloud-providers/gcp/gcp-provider/">}}) | [Getting Started / Provider-GCP]({{<ref "getting-started/provider-gcp/">}}) | 

{{< /table >}}

## /concepts

`/concepts/` directory is maintained.

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| [_index.md]({{<ref "../v1.10/concepts/">}}) | [Concepts]({{<ref "v1.11/concepts/">}}) | 
| [composition.md]({{<ref "../v1.10/concepts/composition">}}) | [Concepts / Composite Resources]({{<ref "v1.11/concepts/composition">}}) | 
| [managed-resources.md]({{<ref "../v1.10/concepts/managed-resources">}}) | [Concepts / Managed Resources]({{<ref "v1.11/concepts/managed-resources">}}) | 
| [packages.md]({{<ref "../v1.10/concepts/packages">}}) | [Concepts / Crossplane Packages]({{<ref "v1.11/concepts/packages">}}) | 
| [providers.md]({{<ref "../v1.10/concepts/providers">}}) | [Concepts / Providers]({{<ref "v1.11/concepts/providers">}}) | 
| [terminology.md]({{<ref "../v1.10/concepts/terminology">}}) | _deleted_. Content moved to a new [Getting Started / Crossplane Intro]({{<ref "v1.11/getting-started/introduction">}}) chapter.| 
{{< /table >}}

## /contributing

`/contributing` directory is moved to a top-level [Developer Guide]({{<ref "/contribute" >}}).

The new "Developer Guide" provides a `Crossplane` and `Documentation` section containing topics relevant to each. 

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| [_index.md]({{< ref "../v1.10/contributing/" >}}) | [Developer Guide]({{<ref "/contribute/" >}}) |
| [adding_external_secret_store_support.md]({{< ref "../v1.10/contributing/" >}}) | [Developer Guide / Crossplane / Adding Secret Stores]({{<ref "/contribute/coding/add-secret-store" >}}) |
| [docs.md]({{< ref "../v1.10/contributing/" >}}) | [Developer Guide / Docs]({{<ref "/contribute/docs" >}}) |
| [observability_developer_guide.md]({{< ref "../v1.10/contributing/" >}}) | [Developer Guide / Crossplane / Logging and Observability]({{<ref "/contribute/coding/observability" >}}) |
| [provider_development_guide.md]({{< ref "../v1.10/contributing/" >}}) | [Developer Guide / Crossplane / Creating Providers]({{<ref "/contribute/coding/provider" >}}) |
| [release-process.md]({{< ref "../v1.10/contributing/" >}}) | [Developer Guide / Crossplane / Release Process]({{<ref "/contribute/coding/release-process" >}}) |
{{< /table >}}

## /faqs
`/faqs` directory is deleted. Content will be moved into www.crossplane.io/community

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| [_index.md]({{< ref "../v1.10/faqs/" >}}) | _deleted_ | 
| [related_projects.md]({{< ref "../v1.10/faqs/related_projects" >}}) | _deleted_ | 
{{< /table >}}

## /getting-started

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| [_index.md]({{<ref "../v1.10/getting-started" >}}) | [Getting Started]({{<ref "getting-started" >}})|
| [create-configuration.md]({{<ref "../v1.10/getting-started/create-configuration" >}}) | _deleted_. Content will be folded into individual Getting Started / Provider-* quick start guides. |
| [install-configure.md]({{<ref "../v1.10/getting-started/install-configure" >}}) | Content will be split between [Install Upgrade Uninstall]({{<ref "software/">}}), new `Concepts / Configurations` chapter |
| [provision-infrastructure.md]({{<ref "../v1.10/getting-started/provision-infrastructure" >}}) | Content will be split between `Concepts` sections and individual Getting Started / Provider-* quick start guides |
{{< /table >}}

## /guides
`/guides` move to the newly created [Knowledge Base]({{<ref "/knowledge-base" >}})

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| [_index.md]({{<ref "../v1.10/guides/" >}}) | [Knowledge Base]({{<ref "/knowledge-base/" >}}) |
| [argo-cd-crossplane.md]({{<ref "../v1.10/guides/argo-cd-crossplane" >}}) | [Knowledge Base / Integrations / Configuring Crossplane with ArgoCD]({{<ref "/knowledge-base/integrations/argo-cd-crossplane" >}}) |
| [composition-revisions.md]({{<ref "../v1.10/guides/composition-revisions" >}}) | [Knowledge Base / Configuration Guides / Composition Revisions]({{<ref "/knowledge-base/guides/composition-revisions" >}}) |
| [multi-tenant.md]({{<ref "../v1.10/guides/multi-tenant" >}}) | [Knowledge Base / Configuration Guides / Multi-Tenant Crossplane]({{<ref "/knowledge-base/guides/multi-tenant" >}}) |
| [self-signed-ca-certs.md]({{<ref "../v1.10/guides/self-signed-ca-certs" >}}) | [Knowledge Base / Configuration Guides / Self-Signed CA Certs]({{<ref "/knowledge-base/guides/self-signed-ca-certs" >}}) |
| [upgrading-to-v0.14.md]({{<ref "../v1.10/guides/upgrading-to-v0.14.md" >}}) | [Knowledge Base / Installing and Upgrading / Upgrading to v0.14]({{<ref "/knowledge-base/install/upgrading-to-v0.14.md" >}}) |
| [upgrading-to-v1.x.md]({{<ref "../v1.10/guides/upgrading-to-v1.x.md" >}}) | [Knowledge Base / Installing and Upgrading / Upgrading to v1.x]({{<ref "/knowledge-base/install/upgrading-to-v1.x.md" >}}) |
| [vault-as-secret-store.md]({{<ref "../v1.10/guides/vault-as-secret-store" >}}) | [Knowledge Base / Integrations / Vault as an External Secret Store]({{<ref "/knowledge-base/integrations/vault-as-secret-store" >}}) |
| [vault-injection.md]({{<ref "../v1.10/guides/vault-injection" >}}) | [Knowledge Base / Integrations / Vault Credential Injection]({{<ref "/knowledge-base/integrations/vault-injection" >}}) |
{{< /table >}}

## /media
`/media` is deleted. Contents are moved closer to the related content. 

{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| README.md | _deleted_ | 
| banner.png | _deleted_ | 
| composition-claims-and-xrs.svg | Moved to `/concepts/media/` | 
| composition-how-it-works.svg | Moved to `/concepts/media/` |
| composition-xrs-and-mrs.svg | Moved to `/concepts/media/` |
| logo.svg | _deleted_ | 
{{< /table >}}

## /reference
{{< table "table table-sm" >}}
| Filename | Updated location| 
| --- | --- | 
| [_index.md]({{<ref "../v1.10/reference" >}}) | _deleted_ |
| [composition.md]({{<ref "../v1.10/reference/composition" >}}) | contend combined into [Concepts / Composite Resources]({{<ref "concepts/composition" >}}) |
| [configure.md]({{<ref "../v1.10/reference/configure" >}}) | Content will be folded into individual Getting Started / Provider-* quick start guides. |
| [feature-lifecycle.md]({{<ref "../v1.10/reference" >}}) | [Knowledge Base / Configuration Guides / Feature Lifecycle]({{<ref "/knowledge-base/guides/feature-lifecycle" >}}) |
| [install.md]({{<ref "../v1.10/reference" >}}) | [Install, Uninstall, Upgrade / Install]({{<ref "software/install" >}}) |
| [learn_more.md]({{<ref "../v1.10/reference" >}}) | Content divided between www.crossplane.io/community and [Knowledge Base / Configuration Guides / Learn More]({{<ref "/knowledge-base/guides/learn_more" >}}) |
| [release-cycle.md]({{<ref "../v1.10/reference" >}}) | [Knowledge Base / Configuration Guides / Release Cycle]({{<ref "/knowledge-base/guides/release-cycle" >}}) |
| [troubleshoot.md]({{<ref "../v1.10/reference" >}}) | [Knowledge Base / Configuration Guides / Troubleshoot]({{<ref "/knowledge-base/guides/troubleshoot" >}}) |
| [uninstall.md]({{<ref "../v1.10/reference" >}}) | [Install, Uninstall, Upgrade / Install]({{<ref "software/uninstall" >}}) |
| [xpkg.md]({{<ref "../v1.10/reference" >}}) | Content combined into [Concepts / Crossplane Packages]({{<ref "concepts/packages/" >}}) |

## /snippets
The `/snippets` directory will be deleted. Any included files will live closer to the content. 

{{< expand "tree output" >}}
``` shell
$ tree content/v1.10
content/v1.10
├── README.md
├── _index.md
├── api-docs
│   ├── _index.md
│   ├── crds
│   │   ├── meta.pkg.crossplane.io_configurations.yaml
│   │   └── meta.pkg.crossplane.io_providers.yaml
│   └── crossplane.md
├── cloud-providers
│   ├── aws
│   │   └── aws-provider.md
│   ├── azure
│   │   └── azure-provider.md
│   └── gcp
│       └── gcp-provider.md
├── concepts
│   ├── _index.md
│   ├── composition.md
│   ├── managed-resources.md
│   ├── packages.md
│   ├── providers.md
│   └── terminology.md
├── contributing
│   ├── _index.md
│   ├── adding_external_secret_store_support.md
│   ├── docs.md
│   ├── observability_developer_guide.md
│   ├── provider_development_guide.md
│   └── release-process.md
├── faqs
│   ├── _index.md
│   └── related_projects.md
├── getting-started
│   ├── _index.md
│   ├── create-configuration.md
│   ├── install-configure.md
│   └── provision-infrastructure.md
├── guides
│   ├── _index.md
│   ├── argo-cd-crossplane.md
│   ├── composition-revisions.md
│   ├── multi-tenant.md
│   ├── self-signed-ca-certs.md
│   ├── upgrading-to-v0.14.md
│   ├── upgrading-to-v1.x.md
│   ├── vault-as-secret-store.md
│   └── vault-injection.md
├── media
│   ├── README.md
│   ├── banner.png
│   ├── composition-claims-and-xrs.svg
│   ├── composition-how-it-works.svg
│   ├── composition-xrs-and-mrs.svg
│   └── logo.svg
├── reference
│   ├── _index.md
│   ├── composition.md
│   ├── configure.md
│   ├── feature-lifecycle.md
│   ├── install.md
│   ├── learn_more.md
│   ├── release-cycle.md
│   ├── troubleshoot.md
│   ├── uninstall.md
│   └── xpkg.md
└── snippets
    ├── compose
    │   ├── claim-aws-new.yaml
    │   ├── claim-aws.yaml
    │   ├── claim-azure.yaml
    │   ├── claim-gcp.yaml
    │   └── pod.yaml
    ├── configure
    │   ├── aws
    │   │   ├── providerconfig.yaml
    │   │   └── setup.sh
    │   ├── azure
    │   │   └── providerconfig.yaml
    │   └── gcp
    │       └── credentials.sh
    ├── package
    │   ├── aws
    │   │   ├── composition.yaml
    │   │   ├── crossplane.yaml
    │   │   └── definition.yaml
    │   ├── aws-with-vpc
    │   │   ├── composition.yaml
    │   │   ├── crossplane.yaml
    │   │   └── definition.yaml
    │   ├── azure
    │   │   ├── composition.yaml
    │   │   ├── crossplane.yaml
    │   │   └── definition.yaml
    │   ├── definition.yaml
    │   └── gcp
    │       ├── composition.yaml
    │       ├── crossplane.yaml
    │       └── definition.yaml
    └── provision
        ├── aws.yaml
        ├── azure.yaml
        └── gcp.yaml
```
{{< /expand >}}