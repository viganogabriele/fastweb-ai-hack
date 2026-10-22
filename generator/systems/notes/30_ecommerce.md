## E-commerce (`ecommerce/`)

Model: online demand per storefront country = event-free store baseline of that country × online share, with online-specific event
multipliers; fulfilled from three web reserves (`W100` at IT10 = EU/AE, US20 = US/CA, HK30 = APAC incl. AU). Web reserves are topped up
on Mondays (14-day cover, event-blind) unless the DC is blocked; extra top-ups on key receipts (Oct 9 ILVARO pink share, Oct 17 MAIRE black,
Oct 20 ILVARO black). Unserved demand becomes notify-me requests. ~14k units online in 82 days.

### Files
- `shopify_sales_by_variant_daily.csv` – day (storefront local day), `sales_channel` (`Online Store`; CN = `WeChat Mini Program`),
  billing country, product/variant title, `variant_sku`, ordered / returned / net quantity, gross, discounts, returns, net, **currency of the
  storefront** (EUR, GBP, CHF, DKK, AED, USD, CAD, JPY, KRW, CNY, HKD, TWD, SGD, AUD – do not sum without FX).
  Quirks: **2026-09-30 rows are duplicated** (BI job appended twice, 200 exact duplicates); `variant_sku` for one-size (TU) items mostly
  **without the `-TU` suffix**; WeChat rows carry the **EAN** as variant_sku; returns are booked on the return date (net quantity can be negative).
  TIB defect returns (reason DEFECTIVE in the model) appear from ~Sep 28, ARNEB returns (size too large) and POLARIS EU returns (too small).
- `back_in_stock_requests.csv` – one row per request (UTC). Status SENT/CONVERTED once the variant was restocked on that web node,
  PENDING otherwise. ~6% duplicate subscriptions by the same person. 1,858 requests, **1,666 for ILVARO 510**
  (KR 738, CN 446, JP 250, HK 80, TW 75, SG 34; EU/US only ~35). MAIRE black 148 (KR 77, GB 17, CN 10, JP 9, FR 8, IT 6...) Sep 13 → Oct 16.
  The planning call notes of Oct 2 quote "~700 notify-me this morning" – the export has ~190 pink requests before 09:15 CET Oct 2 (~270 for the day):
  the e-com figure was inflated (page views / provisional).
- `inventory_availability_log.csv` – OUT_OF_STOCK / BACK_IN_STOCK transitions per web node × variant (UTC).
  **ILVARO 510 APAC: all sizes OOS between 2026-10-01 22:22 and 23:38 UTC = Oct 2 07:22–08:38 KST** (KR/CN/JP storefronts share the APAC node).
  EU sizes 00/0 OOS Oct 2, all EU/US sizes by Oct 5. Top-up back in stock Oct 8 21:30 UTC (APAC) / Oct 9 04:30 UTC (EU) and APAC sold out again
  by ~Oct 9 12:00 UTC. MAIRE black sizes go OOS Sep 14–26 (APAC/EMEA), back Oct 17. AMBRINE brown 0/1/2 OOS from Sep 26–Oct 10.
- `site_search_queries_daily.csv` – per day × site × raw search term, searches, results, clicks, exits, zero-result flag. Event queries:
  `ilvaro pink`, `일바로 핑크` (0 results – Korean name not indexed), `윤하은 몽클레르`, `尹夏恩同款`, `イルヴァロ ピンク` (0 results),
  `yoon ha eun`, `ilvaro rosa`/`ilvaro rose` (0 results – site uses "rosa cipria"/"rose poudré"), typos `ilvaro pnk`, `maire blak`;
  `maire black` / `마이레 블랙` / `maire noir` / `maire nero` from Sep 17–19; `ambrine marrone/marron/brown`; `tib zip`, `cerniera gilet`
  from Sep 29; `価格改定` from Oct 9; `双11 价格` from Oct 18; `daunenjacke damen lang` during the cold snap; AU searches for `polo`,
  `t-shirt`, `light jacket`. Raw terms are not normalised (~7% upper-case or padded/title-case variants).

### Correct readings
- Online confirms the K-pop spike is Asia-wide and immediate (Oct 2 morning KST), while EU/US online pink demand is modest:
  stock should flow to APAC, not EU.
- Zero-result searches in Korean/Japanese/Italian/French for ILVARO pink are a merchandising fix (synonyms) and a demand signal.
