---
title: Docs Update May 2023
date: 2023-05-01
---

Docs updates in May includes a hint to join the Crossplane Slack channel on the 
[home]({{<ref "/">}}) page, updates the supports Kubernetes versions and 
includes a major rewrite to the [Providers]({{<ref "concepts/providers">}}) page.

<!--more-->

## Changelog

* [5ccd9b1](https://github.com/crossplane/docs/commit/5ccd9b1b830c566cbae816dce10b4b4811a5beca) - (HEAD -> flat-docs, origin/master, origin/HEAD, mr-update, master) Corrects statement about UXP to Up CLI. Resolves #331 (#445)
* [77a5ec7](https://github.com/crossplane/docs/commit/77a5ec7e71dadae992861efad40a8239559fb1bd) - Updates GCP quickstarts to match v1.11's three-part guide (#446)
* [a300834](https://github.com/crossplane/docs/commit/a300834a38faf06fa71611e9754fe36d55a360fa) - Adds @phisco and @lsviben as Reviewers to sync with c/c OWNERS (#447)
* [a555d50](https://github.com/crossplane/docs/commit/a555d50330702412b93bbb9c0ef29248889451ef) - Merge pull request #443 from plumbis/slack-201
* [a5c6a7c](https://github.com/crossplane/docs/commit/a5c6a7c9a367af226584e81078a6f66f4c429bf4) - (origin/slack-201, slack-201) Make the popover clickable
* [e723578](https://github.com/crossplane/docs/commit/e7235781c75eeaa778d1dac6c96ae3fcc3ffdc26) - Exclude tooltip styles from purgecss
* [ae2a5b8](https://github.com/crossplane/docs/commit/ae2a5b86da3d99b82a055f4a3df8bc773706e913) - Create a Join the slack popover on the homepage
* [0ebb281](https://github.com/crossplane/docs/commit/0ebb281dc16a2791796b4a29d7b6900cdf28384e) - Create a popper.js element for slack notification
* [32415fb](https://github.com/crossplane/docs/commit/32415fbb30e179c3e5ffb2fcdee393e27c5fc9e2) - create a unique navbar cache for the homepage
* [fb5c5a8](https://github.com/crossplane/docs/commit/fb5c5a8ea592e963768caeb81ff8d7be10aeac6c) - (crossplane-cli) add search to the home page. (#421)
* [7e0181b](https://github.com/crossplane/docs/commit/7e0181b2bd7ef19dffd774f927893bd50f3d7e3e) - (search-test, mobile-nav-fix) Merge pull request #438 from plumbis/support-versions-4049
* [ada46d6](https://github.com/crossplane/docs/commit/ada46d6b6361e7d41edcd630ce13096fc24fa45d) - (origin/support-versions-4049, support-versions-4049) Update k8s version to say 'actively supported'
* [53e59a9](https://github.com/crossplane/docs/commit/53e59a90373c259bc0e399e0367798b83ac0eb96) - add information about supported k8s versions (#437)
* [5d6ef67](https://github.com/crossplane/docs/commit/5d6ef67fe724cddc973160d40cd83d11228bf273) - (search-fix) Backport Providers update to release versions (#436)
* [e0d8974](https://github.com/crossplane/docs/commit/e0d897441c669b48071b9fe46bc3707a4ddb7352) - Fix XRD/CRD mixup (#435)
* [a5311b4](https://github.com/crossplane/docs/commit/a5311b4bdebd9da7bb9ce47c1339cb8fd35f73e1) - fix vale command (#431)
* [a43dd01](https://github.com/crossplane/docs/commit/a43dd013e08201a1358974121adf9bf12d9f428f) - Merge pull request #434 from okgolove/feature/concepts-fix-typo
* [01c1182](https://github.com/crossplane/docs/commit/01c1182871ccbb32af44417afc5bea00ec0a18fa) - feat: fix typo in concepts doc
* [4f213f5](https://github.com/crossplane/docs/commit/4f213f50e754edb0480090930045a9b0c24ce770) - Concepts: Provider rewrite (#420)
* [980736c](https://github.com/crossplane/docs/commit/980736c846d7d66400e026f5ee9c96e87c9d76e0) - Merge pull request #433 from plumbis/safari-fix
* [e101744](https://github.com/crossplane/docs/commit/e1017449ef5256529ed7bcb8217a65d9bed58432) - (origin/safari-fix, safari-fix) add LightningCSS options for browser support. Fixes Safari rendering problems
* [98751f1](https://github.com/crossplane/docs/commit/98751f192a7466e414c97661dea4c7ea586f59a3) - add a section for troubleshooting composition (#430)
* [2fb64eb](https://github.com/crossplane/docs/commit/2fb64eb948e73be8a36cae9443e2ff122171ba4a) - Document Management Policies (#407)
* [857152d](https://github.com/crossplane/docs/commit/857152daf6024486b5ab7dd18aa3a356ea603219) - Document patching a composed resource from itself (#426)