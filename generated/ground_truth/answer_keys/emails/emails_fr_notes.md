# emails_fr — French store closing emails (PAR01, PAR02, CAN01, GVA01)

Generator: `generator/emails_fr/` (`par01.py`, `par02.py`, `can01.py`, `gva01.py` = hand-authored bodies, one dict per
email; `build.py` = .eml wrapper; `digest.py` = helper that prints the per-day facts used while authoring).
Output: `generated/sources/store_emails/<STORE>/*.eml`. Index of every file (kind, business date covered):
`generated/ground_truth/emails_fr_index.csv`.

| Store | Files | Daily closings | Extras | Missing business days |
|---|---|---|---|---|
| PAR01 | 50 | 44 (45 open days) | 2 area-manager replies, 1 store reply, 1 correction, 1 duplicate, 1 customer forward | 16/09 (covered late in 17/09 mail) |
| PAR02 | 52 | 49 (52 open days, open Sundays) | 1 out-of-office, 1 merch reply, 1 forward (Galeries Lafayette strike note) | 18/09 (none), 10/10 (in Sat+Sun recap of 11/10), 16/10 (numbers given in the 17/10 mail) |
| CAN01 | 45 | 42 (45 open days) | 1 area-manager question, 1 store answer, 1 customer forward | 16/09, 07/10 (none), 12/10 (in Mon+Tue recap of 13/10) |
| GVA01 | 47 | 44 (45 open days) | 1 correction, 1 area-manager reply, 1 forward of a mail sent to the wrong list | 17/09 (none, apology in 18/09) |

All dates are CEST (+0200). Paris/Cannes/Genève shops are closed on Sunday except PAR02.

## Writers / voices

- **PAR01 Saint-Honoré** — *Camille Lefèvre* (SM): structured block "CA net / Entrées / transfo / Top", proper accents,
  Outlook + long legal footer, subject `PAR01 - Closing dd/mm` (drifts to `... – FW + Golden Week`, `... + points en suspens`).
  *Thomas Nguyen* (ASM): iPhone, no accents, lowercase, "bcp / pdt / pr / qq / lol", CAPS once; writes Mondays and covers
  Camille's leave 12–17/10 (incl. the strike day). *Inès Haddad* (senior SA): one formal, slightly stiff mail on 22/09.
- **PAR02 Galeries Lafayette** — *Sophie Marchand* (SM): chatty, "Bonsoir à tous", ":)", exclamation marks, talks about
  "le grand magasin", détaxe queues, Personal Shopping GL; reports **HT** (net). *Karim Benali* (ASM): very short, iPhone,
  CAPS when angry (AUREA NOIRE, VEL). *Store mailbox* `par02.store@`: fixed "FICHE DE CLOTURE" form filled mostly by *Lucie
  Park* (Korean-speaking SA) on Sundays — **amounts in the form are TTC (incl. 20% VAT)**, see traps.
- **CAN01 Cannes** — *Laetitia Rossi* (SM): longer, warm, vents about the off-season, the heat and the budget, mentions local
  clientele (Mougins, Super-Cannes villa, Monaco), yachts leaving, MIPCOM. *Julien Pastor* (ASM): telegraphic "RAS",
  Samsung phone; covers Laetitia's leave 5–10/10 and 12–13/10.
- **GVA01 Genève** — *Nathalie Favre* (SM): polite Swiss French, "Meilleures salutations", CHF written `CHF 24'620.–`,
  "septante-cinq / septante-neuf pour cent", Jeûne genevois, Thursday late opening (mails ~21:40), Saturday closes 18:00,
  two HTML mails with an Outlook table (08/10, 13/10), bilingual Swiss disclaimer. *Bruno Monnier* (ASM): short, iPhone,
  "la bise", "il caille", "natel", amounts without the "CHF" sometimes. *Elodie Rochat* (SA): one mail on 21/10 ("nonante entrées").

## Signals planted (what a good system should extract)

### Black AUREA (Korean tourists) — PAR01, PAR02 (strong); GVA01, CAN01 (weak background)
- PAR01: first mention 19/09 (Korean clients showing a photo of an actress in a series); 21/09, 23/09 (asks merch for date,
  Cc merch), 24/09 (navy/white substitution works with some Chinese clients, **not with Koreans**), 26/09 (7 requests),
  28/09 (8), 29/09 (8), 1/10 (8), 2/10 (7), 3/10 (14, waitlist capped at 30), 5/10 (Thomas: "j'ai arrêté de compter après 10"
  in T1 = 11 in ground truth), 8/10, 9/10 (11, >40 names), 10/10, 12/10, 13/10, 16/10 (merch says DC restocked from 16/10,
  delivery "next week"), 19/10 and 21/10 (**still no delivery** — consistent with stock files: PAR01/PAR02 black AUREA 0–2 at
  zero through 21/10). Isabelle asks for a count on 25/09 (`_re1`), Camille answers "une quinzaine depuis le 19, 2/3 coréennes"
  on 26/09 (`_re2`; true count 19–25/09 = 13).
- PAR02: 15/09 first T1 missing; Lucie 20/09 explains the tvN drama; 22/09 transfer request (Cc merch); **merch reply 25/09**
  (`_re1`, Marco Bellini): DC out because of supplier delay on laqué nylon, restock wk42 ~16/10, no transfer possible
  (PAR01/MIL01/LON02 also at zero) — this is a cross-store confirmation of the DC constraint. 26/09 "12 demandes, 7 en T1",
  30/09 "15 dont 10 en T1", 3/10 "plus de 40" (true 48), waitlists 13 → 31 → 34 names, 19/10 asks delivery date.
- Ground-truth unmet black AUREA requests (email_context) for reference: PAR01 152, PAR02 227 units of demand. Emails
  under-report (counts given only some days, approximate).
- GVA01 mentions black AUREA sporadically (19/09, 29/09, 3/10, 7/10, 12/10, 13/10, 17/10, 19/10, 21/10) without a tourist
  story: it is ordinary stock-out, not the Korean effect. CAN01: only 31/08, 09/09, 09/10, 20/10.

### IRIDIA powder pink / Yoon Ha-eun — PAR01, PAR02
- PAR01 2/10: Asian clients show phone photos of Yoon Ha-eun (LUMIERE) in IRIDIA pink, store out of pink since end of
  September (true: zero from ~26/09 to 11/10); requests also 29–30/09 (before the photo, low level), 5/10, 6/10, 8/10, 9/10.
- PAR01 12/10: **12 pink units received** (DHL delivery on Sunday 11/10, store closed — logistics file shows actual arrival
  on a Sunday) — sell 1 every few days. 17/10 "une douzaine en stock", 19/10 Camille proposes **transferring them to Asia**
  (where the pink is sold out); Isabelle (`_re1`) will check with merch + Vivian (HK/TW). This is the key actionable signal:
  Paris pink demand was FW/tourist-driven and is now low; the stock should move to Asian stores.
- PAR02 2/10: never carried the pink (assortment has only IRIDIA off-white 20D) → staff push off-white (off-white sells
  4–5/day at PAR02, consistent with spill-over). PAR02 emails therefore do not show "pink requests" as unmet.

### Golden Week (Chinese) + Paris Fashion Week
- PAR01 29/09 FW start (stylists, buyers, VIC between shows); 30/09 GW start, ~half of tickets Chinese, détaxe paperwork
  slows staff, need extra person; 2/10 135.6 k€; 3/10 175.7 k€ "meilleur samedi"; 7/10 end of FW; 8/10 last GW day;
  9/10 "la vague chinoise retombe"; 12/10 −53% + 13 returns ("post golden week").
- PAR02 29/09 "FW not felt at the Galeries"; 30/09 49% Chinese, détaxe queue 45 min; 1/10 détaxe >1 h, asks GL for a
  dedicated counter; 2/10 16 navy AUREA sold to Chinese clients; 8/10 last day; 9/10 back to calm.
- Astra sells in Paris almost only to Chinese clients during GW (PAR01 3/10, 8/10) — consistent with Couture strong in China.

### Transport strike Tue 13/10 — PAR01, PAR02
- PAR01 13/10 (Thomas): lines 1/8/9 down, 2 SAs arrived at noon, 266 entries, 32.9 k€ vs 64.5.
- PAR02 12/10 forward of the Galeries Lafayette management note (strike announced) + 13/10: 99 entries, corner opened at
  10:45, high conversion 19%.

### Cold snap
- GVA01 (real cold snap 12–19/10): 10/10 forecast of cold, 12/10 "la bise", 6 °C; 13/10 snow to 1000 m, Salève white;
  14/10 "il caille"; 15/10 +79%, 16/10 CHF 49'840 (+95%, "record"); 17/10 lost sales because black down jackets broken
  in all sizes (urgent restock request, Cc merch); 19/10 "dernier jour de froid"; 20/10 "redoux, 14 degrés".
- PAR01/PAR02 milder echo: 13/10 "il commence à faire frais", 14/10 Aurea navy + beanies, 17/10 "le froid = bonnets"
  (white beanie x12 at PAR01, Aria at PAR02).
- CAN01: **no** cold snap (17/10 "encore 23°") — correct reading: Cannes is not affected.

### AMALIA chocolate brown — PAR01 (strong), PAR02/CAN01 (weak)
- PAR01: 11/09 first "vue sur Instagram", only 6 pieces; 17/09 (for 16/09), 23/09, 29/09, 2/10, 3/10 (x2), 6/10 (4 requests,
  "le noir ne remplace pas"), 10/10 (4 requests in T1, asks other stores), 12/10, 16/10 (4 requests 0–3), 19/10. Ground truth: 20.
- PAR02: 11/09 brown requested even in knitwear (CASHMERE TURTLENECK chocolate M), 26/09, 2/10, 8/10, 19/10.
- CAN01 1/10 one request in size 4.

### VEL zipper defect
- PAR01 28/09 first 2 returns ("le curseur se bloque puis se casse", bought end of August), 1/10 "8 depuis lundi", items
  from mid-August, 2/10 five returns, 9/10 **forwarded customer complaint** (`_fwd`), 19/10 "près de 30" (true 28); Isabelle
  19/10: quality note coming, exchange/refund, code DEF.
- PAR02 29/09 first, 3/10 "7 VEL RETOURNES" (true 7), several after. GVA01 2/10, 3/10, 6/10 ("troisième en une semaine,
  problème connu ?"), Isabelle reply 7/10 confirms the mid-August lot; 19/10. CAN01 3/10 and 19/10.

### ARTEM fits large
- PAR01 10/09 (first delivery: "taille grand, une taille en dessous"), 21/09 exchange 3→2, 22/09 return T3, 7/10 request 6,
  20/10 return T5. PAR02 12/09 "ATTENTION ARTEM taille grand, 2 clients sur 3 ont pris −1", 13/10, 17/10 (5→4), 18/10.
  CAN01 10/09, 26/09 (sold one size down), 16/10 (client normally 7, the 6 too tight in shoulders — counter-example).
  GVA01 9/09, 28/09, 12/10, 19/10.

### Couture ASTRA
- PAR01 24/09 launch: try-ons, "taille petit", price 2 900 € for the cape scares; 3/10 & 8/10 sold only to Chinese
  clients; 15/10 Thomas asks to stop shipments ("on n'en vend plus du tout depuis la fin de la Golden Week") — slight
  exaggeration: 3 units sold 9–10/10, then 0 from 11/10 to 18/10.
- PAR02 8/10: 14 balaclavas received, "on en vend 2-3 par semaine" — **under-estimate**: PAR02 sold ~17 balaclavas between
  25/09 and 8/10 (~8/week). Balaclava (450 €) sells; the issue in Europe is the cape/oversized.
- CAN01 and GVA01 are **not** weak on Astra: CAN01 sells capes to wealthy local/Monaco clients (24/09, 1/10, 3/10, 9/10,
  10/10, 14/10; Laetitia: "la Astra plaît à notre clientèle aisée"); GVA01 26/09 a Saudi client buys 2 white capes.
  Correct reading: underperformance is in the main EU flagship (PAR01), not uniform.

### Other real signals
- Broken sizes / replenishment requests: PAR01 hoodie S/M (1/09), XXL knit men (5/09, Cc merch), Montgenèvre noir 5,
  VLOGO CARDIGAN M navy/black at zero from 19–21/10; PAR02 VLOGO CARDIGAN black M at zero from 14/10; CAN01 Aria/Liviana noir
  (2/09 → received 17/09), jersey polo noir S/L in September heat, Vtrack W 39; GVA01 Mistral noir 4/5, cardigan marine S
  (3 requests), Rosière 3, dolcevita marine XXL (3 requests).
- Deliveries: PAR01 2/09 (+3 days), 18/09 (+1 day); CAN01 5/09 (+2 days) — all match logistics delay_days.

## Traps / noise (with correct reading)

1. **PAR02 form amounts are TTC (VAT incl.)**: 04/09 `38 016 €` (net 31 680), 13/09 `44 208` (36 840), 20/09 `58 645`
   (48 871), 04/10 CSV `97 820` (81 517), 18/10 `62 256` (51 880). Divide by 1.2 to compare with KPI net sales. Sophie's free-text
   mails say "HT" and are net; Karim's are net without saying it.
2. **PAR01 02/10 wrong revenue** "153,6 k€" corrected 26 min later (`_corr`) to 135,6 k€.
3. **PAR01 03/10 duplicate send** (`_dup`, identical body 2 min later) — do not double count.
4. **GVA01 25/09** Bruno writes CHF 32'790; correction next morning (`_corr`): CHF 23'790.
5. **GVA01 10/10** Nathalie writes budget "CHF 28'760.–" — true budget is CHF 32'760 (typo, not corrected).
6. **Wrong date in subject**: PAR01 file `20261014_2019_PAR01.eml` subject "closing 13/10" but reports 14/10 (53,6k);
   CAN01 `20260929_1935_CAN01.eml` subject "Cloture 28/09" but reports 29/09 (8,7k). Use the Date header.
7. **Late send**: PAR01 07/10 closing sent 08/10 08:42 (subject says 07/10). GVA01/PAR01/PAR02 late or merged days listed
   in the table above (`business_date` in the index CSV).
8. **Wrong distribution list**: GVA01 16/10 sent to `retail-ops-dach@` + Stefan Wagner, forwarded to the France list on
   17/10 (`_fwd`). Same numbers, count once.
9. **Out-of-office** auto-reply from Isabelle (PAR02 07/09, `_auto`) — no content.
10. **Attachment-only mails**: PAR02 04/10 (CSV, cp1252, `;`), CAN01 06/10 (XLSX, CA HT). PAR01 08/09 has 2 placeholder JPEGs.
11. **HTML-only tables**: GVA01 08/10 and 13/10 have a text/plain alternative with the same data.
12. **PAR02 15/10 +79%** is a single Personal Shopping family order (6 Aria noires + 2 Aurea blanches), not a trend; "sans ça
    on était autour de 50k".
13. **AUREA quality returns** PAR01 07/09–08/09 (couture qui file, photos) are ordinary returns (reason QUALITY in POS), not a
    defect event — don't confuse with the VEL defect.
14. **PAR01 09/09** "TPE 2 en panne 15h–16h" — an in-store anecdote with no trace in other systems (sales on that day are
    simply low, −49%). Not a POS outage event.
15. **Local events that are not drivers**: CAN01 Festival de la Plaisance (8–13/09: "personne ne remonte la Croisette"),
    MIPCOM (12–16/10: lots of badges, little shopping; 15/10 two Korean producers buy — a one-off), GVA01 Jeûne genevois
    10/09 (city closed, low sales). None should be modelled as demand uplift.
16. **CAN01 budget complaint** (14/09 `_re2`): Laetitia says Sept/Oct budget ignores the off-season. Opinion, but consistent
    with CAN01 being below budget almost every day; not an event.
17. PAR01 Oct 1 claim "8 VEL since Monday" is correct (28/09–01/10); "dépôt réapprovisionné depuis vendredi" (16/10) is
    correct per DC constraints, but no store delivery of black AUREA happens by 21/10.
18. Staff customer-mix figures are approximate and sometimes attributed to the tax-free desk ("17% d'après la détaxe").
