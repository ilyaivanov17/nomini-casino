# Visual and Language Audit — Instant Casino

## Scope
Reviewed the homepage template, author-card rendering, and the About, Account Help, and Payments pages across the configured site languages (German, English, Spanish, Portuguese, Polish, and Japanese).

## Findings and changes
- The About, Account Help, and Payments pages referenced generic SVG guide illustrations despite suitable photographic assets already being available. Updated their screenshot/illustration references to `casino-editorial.webp`, `casino-account.webp`, and `casino-payments.webp`, respectively, in every configured language.
- The homepage already includes a contributor section that renders author portraits from each author profile's `photo` field. All seven English author profiles have a photo path configured, so no fabricated identity portraits were added.
- Corrected the homepage Book of Dead artwork reference from a non-existent `.webp` file to the available `.jpg` asset.
- The configured site languages do not include Russian. Keep visible page copy and any text embedded in future artwork localized to the page language; use text-free imagery wherever practical.

## QA still recommended before deployment
1. Build with the project's pinned Hugo version and run the existing sitemap/content validation workflow.
2. Check the homepage and `/about/`, `/account-help/`, and `/payments/` at desktop and mobile widths.
3. Inspect all author portraits and confirm that each image depicts the named contributor before publication.
4. Run a rendered-page language scan. Source files contain multilingual translations by design, so a raw repository-wide Cyrillic scan is not a reliable check for Russian user-facing text.
5. Confirm the contact details and factual claims before production; this visual pass does not verify business identity or legal/compliance claims.
