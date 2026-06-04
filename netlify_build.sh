#!/usr/bin/env bash

# Which which version is the "Latest"?
LATEST_VER="2.3"

# Which CLI docs version is the "Latest"? Tracked separately from core so the
# two version lines can diverge. Keep in sync with params.cliLatest in config.yaml.
CLI_LATEST_VER="2.3"

# Make a copy of /content/$LATEST_VER to the directory /latest
# Search indexing only points to /latest, this prevents broken or out of date
# search results
cp -R content/v$LATEST_VER content/latest

# Set the `version` front matter to prevent redirect issues with the version
# drop-down menu.
sed -i "s/^\s*version: \"$LATEST_VER\"//g" content/latest/_index.md

# Make a copy of /content/cli/v$CLI_LATEST_VER to /content/cli/latest, mirroring
# the core /latest copy. Strip only the version line; the cascaded `track: "cli"`
# must survive so the copy stays on the CLI track.
cp -R content/cli/v$CLI_LATEST_VER content/cli/latest
sed -i "s/^\s*version: \"$CLI_LATEST_VER\"//g" content/cli/latest/_index.md

# Enable Hugo writeStats to enable PurgeCSS optimizations.
# docs: https://gohugo.io/getting-started/configuration/#configure-build
sed -i 's/# writeStats: true/writeStats: true/g' config.yaml
cat config.yaml

# $CONTEXT is a Netlify environmental variable.
# https://docs.netlify.com/configure-builds/environment-variables/#build-metadata

# For production set the baseURL to be the docs URL
if [ "$CONTEXT" = "production" ]; then
hugo --minify --baseURL https://docs.crossplane.io/

# For any other context use the Netlify deploy URL.
elif [ "$CONTEXT" = "branch-deploy" ]; then
echo "Building branch deploy with URL $DEPLOY_PRIME_URL"
hugo --minify --baseURL $DEPLOY_PRIME_URL
else
echo "Building other deploy $CONTEXT with URL https://deploy-preview-$REVIEW_ID--crossplane.netlify.app/"
hugo --minify --baseURL https://deploy-preview-$REVIEW_ID--crossplane.netlify.app/
fi
