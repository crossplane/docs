---
name: New Release
title: "Release Crossplane version... "
about: Cut a Crossplane release
labels: release
---

- [ ] Update the `/latest` redirect in [netlify.toml](https://github.com/crossplane/docs/blob/master/netlify.toml#L9)
- [ ] Update `params.latest` in [config.yaml](https://github.com/crossplane/docs/blob/master/config.yaml#L48)
- [ ] Create a [new release/tag](https://github.com/crossplane/docs/releases/new) named "v<EOL version>-archive" to snapshot EOL'd docs.
- [ ] Remove EOL'd docs version from "/content" directory and run `hugo` locally to check for broken links.