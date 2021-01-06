# Crossplane Site

This is the the source for http://crossplane.io. It is rendered using [Jekyll](https://jekyllrb.com/) by [GitHub Pages](https://pages.github.com/). Docs from the main crossplane repo are published here automatically during the main repo CI publish.

## To preview and share changes from your fork

It is possible to live preview changes from your fork of this repo, for instance to share your
changes for review by others.

After pushing your changes to your fork, make sure that a publishing source is set within the
settings of your fork:

* Navigate to `Settings` tab, then the `Options` tab
* Scroll down to `GitHub Pages` section
* Select a `Branch` (e.g. the branch of your fork you just pushed to) for the `Source` section
* Click `Save`

Within a small amount of time, after your site has been built and published, you'll be able to see
and share a live preview with others.  The URL will be similar to the following, but with your
GitHub user name:

* https://jbw976.github.io/crossplane.github.io/

Full instructions can be found in the [GitHub Pages
docs](https://docs.github.com/en/free-pro-team@latest/github/working-with-github-pages/creating-a-github-pages-site#creating-your-site).

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

## License

The source code in this repository is licensed under the [Apache 2.0](LICENSE) license.

The documentation is distributed under [CC-BY-4.0](LICENSE-DOCS).
