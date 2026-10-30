# Production and indexing changes

- `params.productionReady` is set to `true`.
- `params.indexingEnabled` remains `true`.
- The global robots meta policy now allows indexing for every public content page regardless of legacy page-level `noindex` front matter.
- The only path excluded by the template policy is `/go` and descendants under `/go/`.
- `robots.txt` disallows crawling `/go/`; redirect endpoints should also send `X-Robots-Tag: noindex` at the hosting/CDN layer where supported.
- Hugo sitemap generation contains content pages, not redirect endpoints, because `/go/` is not a content page in this repository.

## Important verification status

Enabling the build flag does not make unverified facts true. The source registry and editorial settings still show pending verification for operator identity, offer terms, payment methods, and responsible-gaming details. Verify these against official primary sources before presenting them as confirmed or treating the website as fully launch-approved.
