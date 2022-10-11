
# Push new changes to the live site
publish:
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
