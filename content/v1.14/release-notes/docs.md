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

## December 1, 2023

### New features 🎉
* Added [API documentation]({{<ref "../api">}}) for Crossplane core types. 

## November 30, 2023

### New features 🎉
* Added RSS support for Crossplane release notes. 

## November 1, 2023

### New content 🎉
* Created the v1.14 release documentation.  
* New [CLI]({{<ref "../cli">}}) documentation.  
* New [release notes]({{<ref "../release-notes">}}) section.  
* [Usages]({{<ref "../concepts/usages">}}) Crossplane type.
  
### Updated content 🏗️

* Rewritten [packages]({{<ref "../concepts/packages">}}) section focused on Crossplane configuration packages.
* Expanded [providers]({{<ref "../concepts/providers">}}) content related to using Provider packages.
* Major updates to [Composition Functions]({{<ref "../concepts/composition-functions" >}}), moving them to `v1beta1`.


### Removed content 🗑️ 
* Removed end of support v1.11 documentation. Content archived on GitHub.
