---
name: New Release
title: "Release Crossplane version... "
about: Cut a Crossplane release
labels: release
---

- [ ] Update the `$LATEST_VER` parameter in [netlify_build.sh](https://github.com/crossplane/docs/blob/master/netlify_build.sh#L3)
- [ ] Update `params.latest` in [config.yaml](https://github.com/crossplane/docs/blob/master/config.yaml#L93)
- [ ] Update `version` in the `_index.md` file of `/content/<new latest>` from `master` to the correct version.
- [ ] Copy Crossplane [cluster/crds](https://github.com/crossplane/crossplane/tree/master/cluster/crds) contents to `/content/<new latest>/api/crds`.
- [ ] Create a [new release/tag](https://github.com/crossplane/docs/releases/new) named "v<EOL version>-archive" to snapshot EOL'd docs.
- [ ] Remove EOL'd docs version from "/content" directory and run `hugo` locally to check for broken links.
- [ ] Trigger [Algolia Crawler](https://crawler.algolia.com/) after publishing to reindex results.