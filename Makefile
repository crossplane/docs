# Run jekyll in development mode

LOCAL_DOCS_DIR := docs/local

run: _data/versions.json
	docker run --rm -it \
		-p 4000:4000 -p 4001:4001 \
		-v="$(PWD)/vendor/bundle:/usr/local/bundle" \
		-v "$(PWD):/srv/jekyll" \
		jekyll/jekyll -- \
		jekyll serve --livereload --livereload-port 4001

run_docs_local: local_docs_dir _data/versions.json
	docker run --rm -it \
		-p 4000:4000 -p 4001:4001 \
		-v="$(PWD)/vendor/bundle:/usr/local/bundle" \
		-v "$(PWD):/srv/jekyll" \
		-v "$(GOPATH)/src/github.com/crossplane/crossplane/docs:/srv/jekyll/$(LOCAL_DOCS_DIR)" \
		jekyll/jekyll -- \
		jekyll serve --livereload --livereload-port 4001
	rm -d $(LOCAL_DOCS_DIR)

# Build (output is in _site)
build: _data/versions.json
	docker run --rm -it \
		-v="$(PWD)/vendor/bundle:/usr/local/bundle" \
		-v "$(PWD):/srv/jekyll" \
		jekyll/jekyll -- \
		jekyll build

# Push new changes to the live site
publish: _data/versions.json
	$(eval ROOT_DIR = $(shell pwd -P))
	git -C "$(ROOT_DIR)" add -A
	@if git -C "$(ROOT_DIR)" diff-index --cached --quiet HEAD --; then\
		echo "no changes detected";\
	else \
		echo "committing changes...";\
		git -C "$(ROOT_DIR)" -c user.email="info@crossplane.io" -c user.name="Crossplane" commit --message="docs snapshot for crossplane version \`$(DOCS_VERSION)\`"; \
		echo "pushing changes..."; \
		git -C "$(ROOT_DIR)" push; \
		echo "crossplane.github.io changes published"; \
	fi

# Generate versions.json
_data/versions.json: node_modules docs
	node preprocess.js
	@touch _data/versions.json

# Install node_modules
node_modules: package.json package-lock.json
	npm install
	@touch node_modules

# Create the local docs dir needed before _data/versions.json in some cases
local_docs_dir: 
	mkdir -p $(LOCAL_DOCS_DIR)

