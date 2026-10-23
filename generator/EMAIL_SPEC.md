# Store closing emails — spec for email-writing agents

Every evening each store sends a closing email ("mail di chiusura") with free comments, in the store's own language.
Window: **2026-08-31 → 2026-10-21** (dates in `generated/ground_truth/writer_inputs/email_context/<STORE>.json`, `open` > 0 means open).

## Output
- `generated/sources/store_emails/<STORE_ID>/<YYYYMMDD>_<HHMM>_<STORE_ID>.eml` (one RFC-822 .eml per email; Python `email` lib
  is fine). Duplicated sends, replies and forwards get their own file (add a suffix like `_re1`, `_fwd`, `_dup`).
- Put your generator script(s) and the authored bodies in `generator/emails_<group>/`.
- Append notes on what you planted (which emails carry which signals, which ones are wrong/misleading, missing days,
  duplicates, wrong dates) to `generated/ground_truth/answer_keys/emails/emails_<group>_notes.md`.

## Headers
- From: a real-looking person at the store (store manager / assistant manager / senior SA — names in stores.csv,
  invent the SAs), e.g. `Giulia Ferrandi <giulia.ferrandi@valentino-retail.example>`; sometimes the generic store mailbox
  (`mil01.store@valentino-retail.example`).
- To: the regional retail ops distribution list (e.g. `retail-ops-italy@valentino-retail.example`), Cc the area manager
  and sometimes `merch-planning@...` / `vm-team@...`. Area managers:
  Italy+Spain: Roberto Galli; France+Geneva: Isabelle Moreau; DACH: Stefan Wagner; UK/Benelux/Nordics: Fiona McLeod;
  Middle East: Omar Haddad; USA/Canada: Lauren Mitchell; Japan: 鈴木 拓也 (Takuya Suzuki); Korea: 윤성호 (Yoon Sung-ho);
  Mainland China: 赵磊 (Zhao Lei); HK/TW: Vivian Lau; SEA/Oceania: Daniel Lim.
- Date with the correct local timezone offset, usually 15–90 min after closing; sometimes next morning ("sorry, ieri
  sera è saltata la connessione"); sometimes weekend recap combining Sat+Sun. Message-ID, some In-Reply-To/References.
- Subjects vary per store and drift over time: "Chiusura 12/10", "MIL01 closing 12.10.26", "Re: chiusura",
  "chiusura sabato + domenica", "[ROM01] Report serale", "閉店報告 10/12 銀座", "마감보고 10.12 청담"...
- Mostly text/plain; some stores send HTML (copied from Outlook with a table), a few have attachments (a tiny CSV/XLSX
  closing form, or a reference to photos "IMG_4471.jpg" — a small placeholder JPEG attachment is fine), signatures with
  "Sent from my iPhone"/"Inviato da iPhone"/"iPhone から送信", legal disclaimer footers, quoted previous emails.

## Content — this is the important part
- Use the facts in `email_context/<STORE>.json` (KPI, top sellers, customer mix, unmet_requests, zero_stock_key_sizes,
  returns, deliveries, active_events) **as what the staff experienced**, not as text to paraphrase. Staff:
  - report only some things, with lag ("da giovedì", "since last week"), approximations ("una decina di clienti",
    "lots of Koreans"), nicknames ("la Nova nera", "il corto rosa", "Aurea laqué", "ピンクのショート"),
    sometimes the wrong size/colour/name, sometimes contradicting the numbers;
  - mention requests for products they don't have (unmet_requests are gold: those are the real lost sales — mention
    them often but in a human way: "3 clienti hanno chiesto la Aurea nera in 1 e 2, niente da fare"),
  - talk about traffic, weather, tourists by nationality, events in the city, construction, strikes, staff issues,
    deliveries (late, missing pieces, wrong colour), returns/defects, VM, IT problems, competitors, client feedback
    on fit/price/quality, visits of VICs, requests for transfers from other stores, waitlists.
- Not every email has signal: many are short/routine ("Tutto ok, fatturato 42k vs 51 budget, poco passaggio. Buona serata"),
  some are long venting emails, some are a structured form filled in (each store has its own habit), some include KPI
  numbers (rounded, sometimes slightly wrong vs the KPI file, sometimes gross instead of net, sometimes in k€).
- Each store has a stable "voice": 1–3 writers with different styles (formal, telegraphic, emoji, ALL CAPS shouting,
  bullet points, typos, missing accents, non-native language, mixing English retail jargon like "sell-out", "stock",
  "traffic", "conversion", "VIC", "UPT"). Writers change on days off/holidays. Styles drift a bit over weeks.
- Realistic noise: occasional missing days (~5%), double send, an email sent with the wrong date in the subject,
  an email meant for another list, an email that only says "vedi allegato", a correction email ("scusate, il fatturato
  era 38k non 83k"), out-of-office auto-replies, a reply from the area manager asking for details and the store
  answering, a forwarded customer message.
- Language: the store's language (see per-agent assignment); natural, idiomatic, how real retail staff write on
  a phone at 21:00 after a long day. NOT polished corporate prose. Do NOT write like an AI. No "I hope this email finds
  you well". No repetitive templates: if you generate with code, the bodies must be individually authored by you
  (write them as data, e.g. one Python dict per email); code only wraps them into .eml. Check that no two bodies
  share long identical sentences except deliberate store habits (e.g. a fixed form header).
- Do not mention the internal event codes, don't mention data being synthetic.
- Expected volume: one email per open store-day (≈45–50 per store) + extras (replies, duplicates, corrections).
