---
title: Docs Changelog
weight: 999
---

Changes and notable docs updates.

<!---
new: 🎉
changed/fixed: 🏗️
removed: 🗑️
moved: 🗺️
-->

## March 14, 2024

### Removed content 🗑️

Removed information on installing Crossplane 
[Providers]({{<ref "../concepts/providers#install-offline">}}) and 
[Packages]({{<ref "../concepts/packages#install-offline">}}) offline using
the local package cache. Installing via the local package cache isn't intended
to be user facing and the recommended offline install method is with a private
registry. 

## February 22, 2024

### Updated content 🏗️

* New [Crossplane upgrade]({{<ref "../software/upgrade">}}) documentation.
* Added notes to the [managed resources]({{<ref "../concepts/managed-resources" >}}) 
  page that Crossplane can't delete paused resources.
* Upgrade the AWS quickstart to use the new "no fork" Upjet provider version 1.1.0
* Add links to the quickstart guides to the different authentication methods for
  the provider.
* Expanded `crossplane beta validate` [command reference]({{<ref "../cli/command-reference#beta-validate">}}). 
* Documentation for the new [server side apply]({{<ref "../concepts/server-side-apply" >}}) alpha feature. 


### 🔨 Docs fixes
<!-- vale Google.WordList = NO -->
<!-- allow "check" --> 
* Fixed [an issue](https://github.com/crossplane/docs/pull/718) where mermaid 
  diagrams didn't display the right colors across light and dark modes. 
* Added support for a "[you are here](https://github.com/crossplane/docs/pull/716)" 
  feature for doc page table of contents.
* Fixed the color of check marks (✔️) in dark mode. 
<!-- vale Google.WordList = YES -->

## February 15, 2024

<!-- ### New features 🎉 -->

### Updated content 🏗️

* New content for [v1.15.0 release]({{<ref "./1.15.0.md" >}}).

### Removed content 🗑️ 
* Removed end of support v1.12 documentation. Content 
[archived on GitHub](https://github.com/crossplane/docs/releases/tag/v1.12-archive).

### 🔨 Docs fixes
* Fixed issues related to displaying tables in dark mode.