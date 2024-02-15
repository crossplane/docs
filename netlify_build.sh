#!/usr/bin/env bash

LATEST_VER="1.15"

cp -R content/v$LATEST_VER content/latest

sed -i "s/^\s*version: \"$LATEST_VER\"//g" content/latest/_index.md

sed -i 's/# writeStats: true/writeStats: true/g' config.yaml
cat config.yaml

if [ "$CONTEXT" = "production" ]; then
hugo --minify --baseURL https://docs.crossplane.io/
elif [ "$CONTEXT" = "branch-deploy" ]; then
echo "Building branch deploy with URL $DEPLOY_PRIME_URL"
hugo --minify --baseURL $DEPLOY_PRIME_URL
else
echo "Building other deploy $CONTEXT with URL https://deploy-preview-$REVIEW_ID--crossplane.netlify.app/"
hugo --minify --baseURL https://deploy-preview-$REVIEW_ID--crossplane.netlify.app/
fi