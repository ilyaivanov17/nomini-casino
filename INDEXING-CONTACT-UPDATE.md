# Indexing and contact update

- `params.indexingEnabled` is enabled in `hugo.toml`.
- The shared head template emits `index,follow` directives for public pages. The `/go/` route and its descendants are excluded from indexing.
- Hugo robots.txt output and sitemap generation remain enabled.
- The contact details in the localized settings and legal pages must be checked against the operating entity's official records before launch.
- The production configuration flag is enabled, but this is a technical configuration value, not independent verification of the operator, licence, payment details, bonus terms, or legal claims.

## Indexing limitations

The configuration permits crawling and indexing; it cannot guarantee that Google or another search engine will include every URL. The deployed pages must be reachable, return the expected HTTP status, and remain accessible to crawlers. Submit the production sitemap in Search Console after deployment.
