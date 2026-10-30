# Image system

- The home hero uses `static/images/instant-casino-hero.webp`, a locally stored original casino-themed banner. It is constrained to a rounded, fixed-height hero panel rather than full-screen imagery.
- Topic cards use local artwork selected from `hugo.toml` under `[params.images.guides]`.
- Editorial topics (bonuses, payments, account security, responsible play, editorial method and slot mechanics) use original topic illustrations under `static/images/guides/`. These are illustrations, not screenshots or claims about a real operator interface.
- Slot profile cards use locally stored slot artwork in `static/images/slots/`; verify licensing before production.
- All imagery is displayed in small, consistent 16:9 card frames; the layout does not stretch card art to fill the viewport.
- To replace an image, overwrite the corresponding file or change its path in `hugo.toml`. Routine image swaps do not require template or CSS edits.


## Visual update (October 2026)

- `instant-casino-hero.webp` and `instant-casino-social.webp` are the new original casino still-life image (roulette, chips, warm gold light; no embedded text or external casino logo).
- `guides/casino-bonus.webp`, `guides/casino-payments.webp`, `guides/casino-account.webp`, and `guides/casino-editorial.webp` are focused crops of the same original scene for compact editorial cards.
- The homepage uses game-art files already bundled under `static/images/slots/` for its game-profile cards.
- Image paths are configured centrally in `hugo.toml`; the homepage template handles layout and responsive presentation.
