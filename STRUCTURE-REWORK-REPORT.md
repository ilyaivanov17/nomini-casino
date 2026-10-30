# Instant Casino — compact structure report

## New URL structure

The project now has 10 rendered content pages per language (60 total across de, en, es, pt, ja and pl): homepage; three grouped slot guides; bonus terms; payments; account/login/registration/FAQ; safer gambling; editorial team and methodology; legal/privacy hub.

## Consolidation

- Slot catalogue entries are grouped into three localized expert guides. Repeated boilerplate is trimmed while game-specific profiles and useful mechanics sections are retained.
- Bonus and payment entries are combined into focused comparison guides.
- Registration, login, FAQ and FAQ catalogue entries are combined into one account-help guide.
- Contact, editorial-policy and author profile content is consolidated into the About/editorial page.
- Privacy, cookies and imprint content is combined into a legal hub. Check local legal requirements before publishing; separate documents may be required in some jurisdictions.
- Old source Markdown is preserved under `content-archive-original/`, which Hugo does not render because it is outside `content/`.
- Old URLs are mapped through Hugo `aliases` on the destination guides. Verify generated redirects on the actual Hugo version and host before deployment.

## Publication notes

All new pages retain `editorial-review-pending`. Verify RTP, payment availability, bonus conditions, legal claims, and author approvals before publication. The production domain remains the existing configured domain and should be replaced with the actual domain before launch.
