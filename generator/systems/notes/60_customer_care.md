## Customer care (`customer_care/`)

- `zendesk_tickets_export_2026-08-01_2026-10-22.csv` – ~1,260 tickets, Zendesk CSV style (UTC `Created at/Updated at/Solved at`
  "YYYY-MM-DD HH:MM:SS" without offset), channels email/web/chat/whatsapp/phone/kakaotalk/line/wechat/instagram_dm, groups by region,
  custom fields `Category [list]`, `Product/Style [txt]`, `SKU [txt]` (with/without size suffix, often empty), `Store [list]` (Zendesk dropdown
  slugs), `Order number [txt]` (`MC-EU|US|AP-26-0xxxxxx`), `Country [list]`, `Satisfaction`. Descriptions are the customer's first message in
  their language (it/fr/en-US/en-GB/de/es/ja/ko/zh-cn/zh-tw), composed from authored sentences + openers/closers.
- Signal volumes (approx.): IRIDIA pink availability ~200 (from Oct 2, decaying; KR/JP/CN/TW/HK first), IRIDIA black spill-over ~22,
  VEL zipper defect ~89 (from Sep 25, rising), AUREA black ~58 (Sep 16 → Oct 17), ARTEM too large ~38 (from Sep 10), delivery delays ~73
  (incl. Korean clients waiting for items reserved at Cheongdam during the customs hold), Japan price increase ~28 (from Oct 9), Double 11
  price matching ~16 (from Oct 18), ASTRA fit small EU ~15 / availability CN ~12, AMALIA brown ~16, VLOGO CARDIGAN M ~9; ~680 background tickets.
- `zendesk_ticket_comments_sample.json` – 150 threads (customer message, agent macro, optional follow-up, internal notes).
  Macros change over time: VEL "send photos, we'll assess repair" before Oct 3, then "quality issue on a limited batch – full refund or
  replacement". **Inconsistent agent information** (planted): some IRIDIA macros say restock "end of October" (ko/en) or "mid/late November"
  (ja/zh) – truth: next receipt Nov 20, nothing before except store allocations from the Oct 8 top-up. The JP price macro says items reserved in
  store keep the old price if collected by Oct 31 (policy unclear in other sources).

### Data-quality quirks
- 14 VEL defect tickets mis-categorised as `other` / `returns_refund` / empty; ~4% tickets with empty category.
- Inconsistent tags for the same issue: `zip_defect`, `zipper`, `cerniera`, `tib_zip`, `defect zipper`.
- 18 duplicated tickets (same customer re-wrote by email): status `closed`, tag `merged`, different Id.
- KakaoTalk tickets of Oct 3–4 were imported late: `Created at = 2026-10-06 01:12:44` (tag `kakao_import`) – their real date is earlier.
- Agent "Pierre D." writes store values as `boutique-paris-saint-honore` instead of the dropdown slug.
- Descriptions mention local times ("7시 반") while timestamps are UTC.
