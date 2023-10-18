#!/usr/bin/env bash

LATEST_VER="1.14"

cp -R content/v$LATEST_VER content/latest

sed -i "s/^\s*version: \"$LATEST_VER\"//g" content/latest/_index.md

sed -i 's/# writeStats: true/writeStats: true/g' config.yaml
cat config.yaml

if [ "$CONTEXT" = "production" ]; then
hugo --minify --baseURL https://docs.crossplane.io/
else
hugo --minify --baseURL https://deploy-preview-$REVIEW_ID--crossplane.netlify.app/
fi