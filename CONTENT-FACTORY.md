# Content Factory and release workflow

This project is a static Hugo site. The factory is intentionally draft-first: scripts create editable scaffolds, while a human owns factual accuracy, localization, and publication approval.

## Create a linked six-language draft

```bash
make draft SLUG=bonus-terms-checklist TYPE=article
# Edit all six files under drafts/ and remove every TODO placeholder.
make promote SLUG=bonus-terms-checklist REVIEWER=editor-handle
```

Supported types: `page`, `article`, `bonus`, `payment`, `slot`, `faq`. The command creates one Markdown scaffold under `drafts/<language>/` for each configured locale and refuses to overwrite any existing file. Hugo does not build the `drafts/` directory. These files contain placeholders and are **not publishable content** until each locale is independently written and reviewed. `make promote` requires all six locale files, rejects unresolved TODOs/placeholders and existing destination files, then records the reviewer and date before copying into `content/`.

## Editorial states

1. `draft`: structure exists; no publication.
2. `editorial-review-pending`: content is written, but still requires source and language review.
3. `reviewed`: a named reviewer has checked factual claims, localization, links and disclosures.
4. Release candidate: all audits pass and a Cloudflare Preview deployment has been manually checked.
5. Production: a human merges/approves the release according to the repository and Cloudflare settings.

Do not set `article_review_status: reviewed` without a real review. For offers, use `data/bonuses.yaml` as the source of truth; only set `status: verified` after checking the operator's official terms and adding a primary-source URL and expiry/recheck date.

## Local quality gates

```bash
make check
make mobile-check
make build
make smoke URL=https://your-production-domain.example
```

`make check` runs the content, bonus, SEO, language coverage, Cyrillic guard, Hugo production build, sitemap, and public-output checks. `make mobile-check` requires Node.js, Playwright and Chromium. `make smoke` checks key public routes and the `/go/` noindex signal after deployment.

## Manual approval with Cloudflare Pages

For the requested human-in-the-loop workflow, do not make content-generation scripts deploy directly. Use a protected Git branch and pull requests:

- Protect `main`; require the `Hugo production build` status check and at least one human approval before merge.
- Connect Cloudflare Pages to the repository; production branch is `main` and build output directory is `public`.
- Keep preview deployments for review. Restrict preview deployments with Cloudflare Access if they should not be public.
- After a preview is approved, merge to `main`; Cloudflare Pages then performs the production deployment.
- After deployment, run `make smoke URL=https://your-production-domain.example` and inspect representative desktop/mobile pages.

Cloudflare account settings and GitHub branch protections must be configured in their dashboards; repository files alone cannot turn these account-level controls on.

## SEO principles

- Keep one canonical URL per language version and correct reciprocal `hreflang` links.
- Keep tracking/redirect routes such as `/go/` out of search results; do not blanket-noindex legitimate content pages.
- Do not publish doorway pages, near-duplicates, fake reviews, invented ratings, or unsubstantiated bonus terms.
- Use `lastmod` only when content actually changes; add primary sources for claims that can change.
- Review Search Console queries and landing-page performance before choosing the next content cluster.

## Definition of done for a page

- [ ] The page answers a specific user intent with original, useful information.
- [ ] Claims that can change have a primary source and a checked date.
- [ ] The language version is editorially adapted, not just mechanically translated.
- [ ] Title, description, canonical, hreflang, headings and internal links are correct.
- [ ] No Cyrillic characters appear in public-facing source files (project requirement).
- [ ] Keyboard, mobile layout and key links have been checked.
- [ ] A human reviewer has approved the preview before merge.
