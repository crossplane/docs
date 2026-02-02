---
name: New Release
title: "Release Crossplane version... "
about: Cut a Crossplane release
labels: release
---

- [ ] Update the `$LATEST_VER` parameter in [netlify_build.sh](https://github.com/crossplane/docs/blob/master/netlify_build.sh#L3)
- [ ] Update `params.latest` in [config.yaml](https://github.com/crossplane/docs/blob/master/config.yaml#L93)
- [ ] Copy Crossplane [cluster/crds](https://github.com/crossplane/crossplane/tree/main/cluster/crds) contents to `/content/master/api/crds`
- [ ] Copy `/content/master` directory to `/content/<new latest>`
- [ ] Update `version` in the `_index.md` file of `/content/<new latest>` from `master` to the correct version.
- [ ] Create a [new release/tag](https://github.com/crossplane/docs/releases/new) named `v<EOL version>-archive` to snapshot EOL'd docs.
- [ ] Remove EOL'd docs version from "/content" directory and run `hugo` locally to check for broken links.
- [ ] Update [Algolia Crawler configuration](https://crawler.algolia.com/) to add new version to `startUrls` (e.g., add `"https://docs.crossplane.io/v<new version>/"`) and remove EOL'd version if applicable.
- [ ] Trigger [Algolia Crawler](https://crawler.algolia.com/) after publishing to reindex results with the new version.
