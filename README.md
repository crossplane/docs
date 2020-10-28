# Crossplane Site

This is the the source for http://crossplane.io. It is rendered using [Jekyll](https://jekyllrb.com/) by [GitHub Pages](https://pages.github.com/). Docs from the main crossplane repo are published here automatically during the main repo CI publish.

## To develop locally

This runs locally watching for changes and live reloading.

```
brew install npm

make run
```

Open http://localhost:4000 in your browser.

## To run locally with local crossplane docs
Ensure `$(GOPATH)/src/github.com/crossplane/crossplane/docs` is present.

```
brew install npm

make run_docs_local
```

To run with --incremental for faster editing:
```
make run_docs_local_incremental
```
Note: `--incremental` is experimental, and sometimes gets stuck:
https://jekyllrb.com/docs/configuration/incremental-regeneration/

Open http://localhost:4000 in your browser.
