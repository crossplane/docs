.PHONY: vale-check vale-add-term vale-test vale-test-changed help

# Vale maintenance and testing commands

vale-check:
	@bash utils/vale/scripts/check-vocab.sh

vale-add-term:
	@bash utils/vale/scripts/add-term.sh

vale-test:
	vale --config=utils/vale/.vale.ini content/

vale-test-changed:
	vale --config=utils/vale/.vale.ini $$(git diff --name-only master...HEAD | grep "^content/")

help:
	@echo "Available Vale commands:"
	@echo "  make vale-check         - Run vocabulary maintenance checks"
	@echo "  make vale-add-term      - Interactively add a term to vocabulary"
	@echo "  make vale-test          - Test all documentation with Vale"
	@echo "  make vale-test-changed  - Test only changed files (what CI does)"
