SHELL := /usr/bin/env bash
.PHONY: help dev check build mobile-check smoke draft promote clean

help:
	@printf '%s\n' 'Instant Casino commands:' '  make dev    Start the local Hugo preview' '  make check  Run content, language, SEO and production-output checks' '  make build  Build and validate the production output' '  make mobile-check Run mobile browser smoke tests (Playwright)' '  make smoke URL=https://example.com Check the deployed site over HTTP' '  make draft SLUG=my-new-page TYPE=article Create linked language drafts' '  make promote SLUG=my-new-page REVIEWER=editor Promote reviewed drafts to content/' '  make clean  Remove generated output and Hugo cache'

dev:
	@./scripts/dev-preview.sh

check:
	@./scripts/check-all.sh

draft:
	@test -n "$(SLUG)" || (echo "Usage: make draft SLUG=my-new-page [TYPE=page|article|bonus|payment|slot|faq]" >&2; exit 2)
	@python3 scripts/new-content.py "$(SLUG)" --type "$(if $(TYPE),$(TYPE),page)"

promote:
	@test -n "$(SLUG)" || (echo "Usage: make promote SLUG=my-new-page REVIEWER=editor" >&2; exit 2)
	@test -n "$(REVIEWER)" || (echo "ERROR: REVIEWER is required for human approval" >&2; exit 2)
	@python3 scripts/promote-draft.py "$(SLUG)" --reviewed-by "$(REVIEWER)"

mobile-check:
	@./scripts/test-mobile.sh

smoke:
	@test -n "$(URL)" || (echo "Usage: make smoke URL=https://example.com" >&2; exit 2)
	@python3 scripts/smoke-production.py "$(URL)"

build:
	@./scripts/build-production.sh

clean:
	rm -rf public resources/_gen .hugo_build.lock
