# Instant Casino modernization plan

## Goal

Reduce repetitive editorial and release work while preserving factual accuracy, language quality, user safety, and search-engine accessibility. Hugo remains the static generator; Cloudflare Pages remains the hosting/deployment platform. Content generation never publishes directly.

## Workstreams and acceptance criteria

### Phase 1 — Reliable build pipeline (implemented in this package)
- One `make check` command runs static content, bonus, SEO, locale, Cyrillic, Hugo build, sitemap and public-output checks.
- One `make build` command creates the minified production output and checks for accidental source/secret files.
- GitHub Actions runs the same core checks and a mobile browser smoke test.
- Acceptance: all static checks pass; CI is green; Hugo build succeeds using Hugo Extended; generated sitemap is valid; no forbidden Cyrillic text appears in public-facing source.

### Phase 2 — Draft-first content factory (scaffold implemented; editorial workflow remains human-led)
- `make draft SLUG=... TYPE=...` creates six language-specific draft files and refuses overwrites.
- Generated files are `draft: true` and marked `article_review_status: draft`.
- Bonus data remains centralized in `data/bonuses.yaml`; verified records require a primary source URL.
- Acceptance: a test slug creates exactly six draft files; a duplicate slug fails without changing existing files; drafts do not appear in production output; each locale is reviewed before publication.

### Phase 3 — Editorial trust and localization
- Maintain a primary-source register for operator identity, licensing claims, bonus terms and affiliate destinations.
- Store reviewer, reviewed date, source URL and recheck date for claims that can change.
- Adapt content to each locale; do not auto-publish raw machine translation.
- Acceptance: every material, time-sensitive claim has a source and review date; locale coverage is complete; no unsupported ratings, claims or invented terms.

### Phase 4 — Human-approved release
- Protect `main` in repository settings; require CI and human approval before merge.
- Use Cloudflare Pages Preview deployments for review; apply Cloudflare Access to previews if non-public.
- Production deploys only after approved changes are merged to `main`.
- Acceptance: an unapproved pull request cannot enter the production branch; reviewers can inspect preview URLs; post-deploy smoke checks pass.

### Phase 5 — Performance and search feedback loop
- Capture a baseline for Core Web Vitals, image weight, build time, Search Console impressions/clicks and indexed landing pages.
- Add performance budgets and route-level checks only after collecting a baseline.
- Prioritize pages using search demand, existing impressions, user intent and content gaps—not page count alone.
- Acceptance: each release is compared against the baseline; regressions are reported; content priorities are based on observed search data.

## Success metrics

Record these before optimizing and review monthly:
- Median time from a content brief to a review-ready draft.
- Percentage of drafts passing checks on the first run.
- Missing translation count and broken internal-link count.
- Production build duration and CI failure rate.
- Core Web Vitals by device and locale.
- Search Console impressions, clicks, CTR and indexed pages by language.
- Percentage of time-sensitive claims with a source and review date.

No ranking or traffic increase is guaranteed by tooling alone. Technical quality enables discovery; original and trustworthy content plus ongoing measurement determine whether the site improves against competitors.
