# ====================================================================================
# Colors

BLACK        := $(shell printf "\033[30m")
BLACK_BOLD   := $(shell printf "\033[30;1m")
RED          := $(shell printf "\033[31m")
RED_BOLD     := $(shell printf "\033[31;1m")
GREEN        := $(shell printf "\033[32m")
GREEN_BOLD   := $(shell printf "\033[32;1m")
YELLOW       := $(shell printf "\033[33m")
YELLOW_BOLD  := $(shell printf "\033[33;1m")
BLUE         := $(shell printf "\033[34m")
BLUE_BOLD    := $(shell printf "\033[34;1m")
MAGENTA      := $(shell printf "\033[35m")
MAGENTA_BOLD := $(shell printf "\033[35;1m")
CYAN         := $(shell printf "\033[36m")
CYAN_BOLD    := $(shell printf "\033[36;1m")
WHITE        := $(shell printf "\033[37m")
WHITE_BOLD   := $(shell printf "\033[37;1m")
CNone        := $(shell printf "\033[0m")

# ====================================================================================
# Logger

TIME_LONG	= `date +%Y-%m-%d' '%H:%M:%S`
TIME_SHORT	= `date +%H:%M:%S`
TIME		= $(TIME_SHORT)

INFO	= echo ${TIME} ${BLUE}[ .. ]${CNone}
WARN	= echo ${TIME} ${YELLOW}[WARN]${CNone}
ERR		= echo ${TIME} ${RED}[FAIL]${CNone}
OK		= echo ${TIME} ${GREEN}[ OK ]${CNone}
FAIL	= (echo ${TIME} ${RED}[FAIL]${CNone} && false)

# ====================================================================================
# System Info

# Set the host's OS. Only linux and darwin supported for now.
HOSTOS ?= $(shell uname -s | tr '[:upper:]' '[:lower:]')
ifeq ($(filter darwin linux,$(HOSTOS)),)
$(error build only supported on linux and darwin host currently)
endif

# Set the host's arch.
HOSTARCH ?= $(shell uname -m)

# Automatically translate x86_64 to amd64.
ifeq ($(HOSTARCH),x86_64)
HOSTARCH := amd64
endif

# Automatically translate aarch64 to arm64.
ifeq ($(HOSTARCH),aarch64)
HOSTARCH := arm64
endif

# If OS is darwin then hugo uses universal prefix.
ifeq ($(HOSTOS),darwin)
HOSTARCH := universal
endif

# ====================================================================================
# Tools

HUGO_VERSION ?= 0.107.0
HUGO := ./hugo-$(HUGO_VERSION)

$(HUGO):
	@$(INFO) installing hugo $(HUGO_VERSION)
	@curl -fsSLo $(HUGO).tar.gz https://github.com/gohugoio/hugo/releases/download/v$(HUGO_VERSION)/hugo_extended_$(HUGO_VERSION)_$(HOSTOS)-$(HOSTARCH).tar.gz || $(FAIL)
	@tar -zxf $(HUGO).tar.gz hugo || $(FAIL)
	@mv hugo $(HUGO) && chmod +x $(HUGO)
	@$(OK) finished installing hugo $(HUGO_VERSION)

# ====================================================================================
# Targets

# Run local development server.
run: $(HUGO)
	@$(INFO) starting hugo development server
	@$(HUGO) server

# Build hugo site.
build: $(HUGO)
	@$(INFO) building hugo site
	@$(HUGO) --minify --baseURL https://crossplane.io || $(FAIL)
	@$(OK) successfully built hugo site

# Validate that hugo builds successfully.
# NOTE(hasheddan): this target exists so that validation can expand to inlude
# other actions rather than just building.
validate: build

# Push new changes to the live site.
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
