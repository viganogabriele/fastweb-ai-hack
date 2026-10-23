# External data – answer key (`generated/sources/external/`)

Scripts: `generator/external/` (`run_all.py` regenerates weather, fx, calendars, events_feed, tourism, trends, macro;
`news/build.py`, `events/build.py`, `social/make_social.py` regenerate news, city documents and social posts). All seeded / deterministic.
Helper truth tables (for testers only): `ground_truth/external_weather_truth.csv` (canonical metric daily weather per city, before
provider formatting), `ground_truth/external_fx_truth_per_EUR.csv` (daily mid rates incl. weekends, TWD/AED).

General rule: every sub-source imitates a different provider, with its own units, date formats, encodings, lags and holes.
Nothing is "wrong" on purpose unless listed under *traps*; everything else is a format/coverage quirk teams must normalise.

---------------------------------------------------------------------------------------------------------------------------
## weather/

Coverage: all 33 distinct store cities, daily 2024-09-01 → 2026-10-21. `coverage_by_city.csv` maps city → provider folder.

| folder | cities | format / units | quirks |
|---|---|---|---|
| `eu_meteoarchive/` | 16 EU/CH/UK cities | Open-Meteo-like JSON, one file per city per API version | **schema change 2026-03-01**: v1 (`weathercode`, `windspeed_10m_max` km/h) → v2 (`weather_code`, `wind_speed_10m_max` **m/s**, gusts m/s, `sunshine_duration` in **seconds**, new `temperature_2m_mean`). Values are model grid cells: **St. Moritz grid elevation 2163 m → temps ≈2 °C colder than the village**. `snowfall_sum` ≈ 0.7× real snow (model under-estimates; Munich Oct 14 shows 4.9 cm vs ~7 cm real). London v2 uses `timezone: GMT` (daily aggregation in UTC during BST). Copenhagen v2: all values null 2026-07-14..18. Milano v1: day 2025-06-03 missing from the time axis. Paris v2 ends 2026-10-20 (latency, Oct 21 missing). |
| `us_ncei_ghcnd/` | New York, Miami, Beverly Hills, Aspen | GHCN-Daily CSV, **°F, inches, mph** | Beverly Hills = LOS ANGELES DOWNTOWN USC station (13 km away, ~+1 °F urban bias). **2026-09-10 row missing** (hottest day of the heat wave, 41 °C ≈ 106 °F). Aspen gap 2025-02-09..15. TAVG blank ~8%. WT flags = condition (1/blank). Snow only NYC/Aspen. Aspen no RHAV. |
| `ca_eccc_climate/` | Toronto | ECCC daily CSV per year, UTF-8 BOM, °C | flag columns (`M` missing ~1%, `T` trace, gust `<31`); no humidity. |
| `jp_jma/` | Tokyo, Osaka | JMA download CSV, **Shift_JIS (cp932)**, 5 header rows, value + 品質情報 + 均質番号 triplets | two files per city (split at 2025-09-01). Quality flag 8 = final, **5 = provisional from 2026-10-01**. Wind m/s, condition as Japanese text (天気概況). Snowfall `--` = none. |
| `kr_kma_asos/` | Seoul (108), Busan (159) | KMA ASOS CSV, **cp949**, both stations in one file | **blank precipitation = no rain (not missing)**; 일기현상 only filled for rain/snow/fog/haze. |
| `cn_tianqi_portal/` | Shanghai, Beijing, Chengdu | scraped portal CSV, UTF-8 BOM | integer temps with `℃` suffix, condition text with `A转B`, wind as Beaufort level text (`3级`, `<3级`, `微风`), AQI. **No precipitation and no humidity**. Chengdu gap 2024-12-09..14. |
| `hk_hko/` | Hong Kong | HKO daily extract, bilingual headers | `微量/Trace`, `***` missing (2025-08-22). Typhoon days below. |
| `tw_cwa_466920/` | Taipei | monthly CSV (26 files), 2 header rows (Chinese + codes) | `T` trace, `X` instrument fault, `/` not observed; station pressure. |
| `sg_mss/` | Singapore (Changi) | MSS-style CSV, cp1252 | mean temp missing shown as em dash (cp1252 byte 0x97); no humidity. |
| `au_bom_066214/` | Sydney | 3 separate files (max, min, rain) | **rainfall = 24 h to 9 am, attributed to the measurement day** (≈ previous day's rain); Quality `N` (not QC'd) from 2026-08-15. Southern hemisphere: October is spring (≈21 °C). |
| `global_weatherhub_api/` | Dubai (full period) + overlap Aug–Oct 2026 for Toronto, Sydney, Singapore, Taipei, Shanghai, Beijing, Chengdu | commercial API JSON, °C and °F both | model values: small biases and precipitation ×0.6–1.3 vs the official stations → the two sources disagree on the overlapping days (official station wins). `date_epoch` = local midnight in UTC → for Asian/Australian cities it falls on the previous UTC date. |
| `forecast/` | all 33 | 10-day forecast issued 2026-10-22 03:41Z (run 00Z), local dates | see *forecast signals*. |
| `venezia_maree/` | Venezia | tide gauge, cm on ZMPS | see below. |

Planted scenario signals (truth table values):
- **Cold snap Oct 12–19 2026** in München, Berlin, Zürich, St. Moritz, København, Amsterdam, Genève: cold front with rain Oct 11, tmax ≈7–8 °C Oct 12 then **2–6 °C Oct 13–19** (St. Moritz −3..+1 °C), tmin below 0 °C Oct 15–18. **Munich first snow of the season Oct 14** (≈7 cm, + 2.4 cm Oct 15; no snow in Munich before that date in autumn 2026). St. Moritz 18 + 23 + 6 cm Oct 13–15; Zürich rain/sleet (snow only above ~1000 m); Courmayeur/Cortina 12 + 5 cm Oct 14–15; Genève bise Oct 15–17 (gusts 62–78 km/h); Amsterdam stormy Oct 13 (gust 78 km/h); Berlin flurries Oct 15. Recovery Oct 20–21 (8–11 °C).
- **Milder echo Oct 13–19**: Paris/London ≈10.5–13 °C, Milano ≈11–13 °C (normal 16–19), mostly dry; Venezia/Roma −2/−3 °C.
- **Japan warm Sep 28–Oct 11**: Tokyo 27–29 °C, Osaka 27.5–29.6 °C, mostly sunny; drops to 24 → 20 °C from Oct 12, ~17–18 °C by Oct 20–21.
- **Hong Kong typhoon (Yamaneko) Sep 16–18**: HKO HQ daily rain 22.4 / **361.0** / 16.2 mm, min pressure 978.6 hPa on Sep 17; matches `events/hongkong/` hourly obs (sum 361 mm on Sep 17) and signal log (T8 16/09 23:40 → T3 18/09 13:40).
- **LA heat wave Sep 8–12**: 38–41 °C (truth), i.e. 100–106 °F at the USC station, RH 14–24% (Sep 10 row missing in GHCN file).
- **Venezia Oct 19–20**: scirocco + rain (17.8 mm Oct 20, gusts 63 km/h).

Venice tide gauge (`venezia_maree/`): hourly 2024-09-01..2026-10-21 for Punta della Salute (inside lagoon) and Piattaforma CNR (open sea);
**times in "ora solare" (UTC+1) all year**; `-999` = missing CNR value. MOSE closures visible as sea >108 cm while lagoon stays ~60 cm
(2024-11-22, 2025-11-14, 2025-12-03). **2026-10-20: MOSE raised too late → lagoon hourly 105 (08:00), 116 (09:00), 117 (10:00); 10-minute file
peak 118 cm at 09:40.** CNR max ≈108 at ~09:00 (agrees with the tide-centre bulletin). Hourly values Oct 19–21 match the tide centre's own CSV
in `events/venice/`, except Oct 20 07:00 which is missing there (telemetry) and filled (88) in the validated archive. Oct 7 2026 false
alarm: forecast 110, observed max 91 (hourly) / 92 (bulletin, 08:50).

Forecast signals (issued Oct 22, a forecast, not truth): second cold spell for CEU/Alps from Oct 27 (München 7.9 → 3.4 °C Oct 27–30, Berlin
down to ~2 °C Oct 30 with flurries, Zürich ~5–8 °C; rain probability 70% Oct 27–28; **St. Moritz 10–13 cm snow/day Oct 27–30**);
Seoul drops from 19 °C to 12–15 °C Oct 23–25; Tokyo cools to 15–18 °C from Oct 25 (13.7 °C Oct 31); Beijing ~10 °C Oct 26; Sydney 21–27 °C. Days 6–10 low confidence.

---------------------------------------------------------------------------------------------------------------------------
## fx/

- `ecb_reference/eurofxref-hist.csv` + `.xml`: units per 1 EUR, TARGET business days only (no weekends, 1 Jan, Good Friday, Easter Monday,
  1 May, 25–26 Dec), newest first, trailing comma, `CYP` column always `N/A`. **2025-08-14 missing** (publication glitch).
  **BGN → N/A from 2026** (Bulgaria joined the euro). **TWD and AED are not in the ECB set.**
- `twd_fixing/USDTWD_close_113-115.csv`: USD/TWD (not EUR!) with **ROC calendar dates** (`115/10/21` = 2026-10-21), Taiwan holidays missing.
- `fxfeed_usd_base/daily_snapshots.jsonl`: commercial feed, **base USD**, includes weekends, 23:59:59Z snapshots, last record is intraday
  2026-10-22; AED fixed 3.6725 (peg). Tiny noise vs ECB (different source/time).
- Levels (per EUR): USD 1.02–1.19, JPY 156–177 (weak yen in 2025–26, supports Japan tax-free boom), KRW 1460–1660 (spike Dec 2024 / Apr 2025),
  CNY 7.6–8.3, GBP 0.82–0.89, CHF 0.92–0.95, DKK 7.46 peg. Store currencies all derivable (TWD via USD, AED via peg).

---------------------------------------------------------------------------------------------------------------------------
## calendars/

- `public_holidays/<CC>_public_holidays_2024-2027.ics` for 16 countries + `CN_...ics` + `syukujitsu_JP.csv` (Shift_JIS, government layout).
  Regional holidays flagged with `X-SUBDIVISION` (IT-MI Sant'Ambrogio, IT-RM 29 Jun, DE-BY/DE-BE, CH-ZH/CH-GE/CH-GR, ES-MD, CA-ON, AU-NSW...).
  Quirks: **US file contains non-holidays** tagged `[observance]` / `CATEGORIES:Observance` (Halloween, Black Friday, Valentine's, Mother's Day);
  IT "Madonna della Salute" is a city feast, not a day off; **CN file has multi-day VEVENTs (DTEND exclusive) and `调休上班` make-up working
  days (`CATEGORIES:班` = weekend days that are WORKING days, e.g. 2026-09-20, 2026-10-10)**; 2027 CN schedule is extrapolated; AE 2027 lunar
  dates tentative. TW file uses LF instead of CRLF. Notable 2026 items: KR substitute holidays Oct 5 (개천절) and Chuseok Sep 24–26,
  KR local election Jun 3; JP Silver Week Sep 19–23 (Sep 22 bridge 休日); CA Thanksgiving Oct 12; CN National Day Oct 1–7 + Mid-Autumn Sep 25–27;
  TW National Day observed Oct 9, Retrocession Day Oct 25/26 (new since 2025); HK Chung Yeung observed Oct 19; IT San Francesco Oct 4 (new
  national holiday from 2026, fell on a Sunday).
- `school_holidays/school_holidays_aggregated.csv` (inclusive dates) + `fr-calendrier-scolaire.csv` (French open-data layout: **"Date de début"
  = evening of last school day, "Date de fin" = day classes resume**, timestamps with +01/+02 offsets; Paris Zone C, Cannes Zone B).
  Relevant: Zürich Herbstferien Oct 5–16 2026; DK uge 42 Oct 10–18; NL Midden Oct 10–18 / Noord+Zuid Oct 17–25; Berlin Oct 19–31; Genève
  Oct 19–23; FR Toussaint Oct 17–Nov 2; UK half term Oct 26–30; Bavaria Nov 2–6; Dubai mid-term Oct 12–18 (provisional); NSW spring break
  Sep 28–Oct 9; SG Sep holidays Sep 5–13.
- `retail_cultural/retail_cultural_calendar_2024_2027.csv`: Golden Week (CN, JP), Chuseok, CNY, Diwali, Ramadan/Eid, Singles' Day (presales
  from Oct 20 2026), Double 12, 618, 520, Black Friday/Cyber Monday, Boxing Day, Pepero/White Day, Oktoberfest, sales seasons IT/FR,
  Dubai Shopping Festival, Singapore GP, JP price-revision date Nov 1, KR long weekends.
- `fashion_weeks/fashion_calendar_export.json`: NY/London/Milan/Paris (+ men's, Seoul, Tokyo, Shanghai, Copenhagen) 2024–2027.
  **Milan entries use dd/mm/yyyy, all others ISO.** MFW SS27 Sep 22–28 2026, PFW SS27 Sep 29–Oct 7 2026.

---------------------------------------------------------------------------------------------------------------------------
## events/city_events/ (ticketing aggregators)

- `eventhub_global_feed.json`: ~6,760 events in all 33 cities, 2024-09 → 2026-12 (≈150 curated "major" + generated regular concerts,
  sports, fairs, performing arts). `expected_attendance` free-form (int, "12,000", "~120k", "1.5M", null); multi-day attendance is cumulative.
  `start_local` is local wall-clock **except partner-synced rows ending with `Z` (UTC)** – e.g. duplicate TIFF row `EVH-P-55120`
  (UTC times, attendance "450k") duplicates the regular TIFF 2026 row.
  Scenario-relevant majors: MFW Sep 22–28, PFW Sep 29–Oct 7, Oktoberfest Sep 19–Oct 4, TIFF Sep 10–20, UNGA high-level week Sep 21–26
  (attendance null, note on frozen zones Madison/Park Ave), BIFF Oct 1–10, Singapore GP Oct 9–11 (race start 2026-10-11T12:00Z = 20:00 SGT),
  Frieze London Oct 14–18, ADE Amsterdam Oct 14–18, Amsterdam/Toronto marathons Oct 18, Munich marathon Oct 11, Berlin marathon Sep 27,
  Mondial de l'Auto Oct 13–18, GITEX Dubai Oct 12–16, Shanghai FW Oct 9–16, Festa del Cinema Roma Oct 15–25, Biennale Arte (to Nov 22),
  Art Basel Paris Oct 23–25 (future), Tokyo IFF Oct 26–Nov 4 (future), NYC Marathon Nov 1. History: Milano Cortina Olympics Feb 6–22 2026,
  Jubilee 2025 in Rome, Expo 2025 Osaka, Salone del Mobile, FIFA World Cup 2026 (NY/NJ, Miami, LA, Toronto).
  Forward-looking signal: **LUMIERE world tour – Seoul KSPO Dome Nov 14–15, Tokyo Dome Nov 28–29 (announced Oct 6)** → further IRIDIA
  pink interest likely in KR/JP in November. **"Northpeak Cheongdam Pop-up" Oct 15–Nov 15** (the competitor pop-up across from SEL01).
  Status quirks: HK lantern carnival Sep 17 `cancelled` (typhoon signal 8); Munich open-air concert Oct 14 `postponed` (snow); ~2% random
  cancellations.
- `asia_ticketing_feed_export.csv`: 29 Asian events in local language, dates in country formats (KR `yyyy.mm.dd`, JP `yyyy/m/d`, SG
  `dd/mm/yyyy`!), counts like `16만`, `7万人`, `15萬`. **Trap: BIFF listed Oct 2–11 here vs Oct 1–10 in the global feed (correct: Oct 1–10).**
  Includes Tmall Double 11 presale start Oct 20 and the Northpeak pop-up.

---------------------------------------------------------------------------------------------------------------------------
## tourism/

Underlying monthly model per destination × nationality with seasonality, trend (CN +13%/yr, KR +7%, JP outbound −3%, GCC +6%) and
event effects: Jubilee (Rome 2025 +10%), Olympics (Milan/Cortina Feb 2026 +28%), Expo Osaka 2025, FIFA WC (US/CA Jun–Jul 2026),
**CN to Milan/Paris +14% from Jul 2026 (new TFU–MXP flights / visa fast track)**, **KR to Milan/Paris/London +22% Sep–Oct 2026**,
HK Sep 2026 −5% (typhoon), Ramadan dips for GCC→Dubai.

`arrivals_official/` – **publication lags are the main trap: none of the monthly sources covers October 2026, most stop at Jul/Aug.**
| file | latest | format quirks |
|---|---|---|
| IT `movimento_clienti_...csv` | **Jul 2026** (2026 = provvisorio) | `;`, latin-1, Italian country names, **Venezia rows use `.` thousands separator** (`12.345` = 12345), Cortina small. |
| FR `frequentation_hoteliere_*.csv` | Aug 2026 | wide (months as columns), **thousands with decimal comma**, `(p)` in headers for provisional months, 3 preamble lines. |
| GB `inbound_visits_london_quarterly.csv` | **2026 Q2** | quarterly only, visits/nights in 000s, spend £m. |
| DE `45412-0035_...csv` | Aug 2026 | GENESIS layout, cp1252, preamble/footer, German month names, `.` = unknown (Berlin Aug 2026 OTH nights). |
| CH `hesta_communes_provenance.csv` | Aug 2026 | bilingual DE/FR labels, Zürich/Genève/St. Moritz. |
| ES `frontur_..._madrid.tsv` | Aug 2026 | TSV, period `2026M08`, `.` thousands separator. |
| EU `estat_tour_occ_arnat_NL_DK.tsv` | **Jul 2026** | Eurostat TSV (`geo\TIME_PERIOD`), flags ` p` provisional, `: c` confidential (DK Dec 2025 CN/IT). |
| AE `dubai_visitors_ytd_by_source.csv` | Aug 2026 | **cumulative YTD (millions)** – must difference to get monthly. |
| US `i94_arrivals_by_residence.csv` | **Jul 2026** | national + port-of-entry splits (NY, Miami, LA). |
| CA `24100053_...ontario.csv` | Aug 2026 | Ontario only, STATUS E = estimate. |
| JP `訪日外客数_...csv` | **Sep 2026** | wide, Japanese, second row = 確定値/暫定値/**推計値** (Sep = estimate). |
| KR `외래관광객_...csv` (cp949) + `국민해외관광객_월별.csv` | Sep 2026 | inbound by nationality + **Korean outbound departures** with Europe share (up in Sep 2026, Chuseok). |
| TW `來臺旅客_...csv` | Aug 2026 | ROC year months (`115年8月`). |
| SG `visitor_arrivals_...csv` | Sep 2026 | `2026 Sep` month labels. |
| AU `340101_...csv` | Aug 2026 | '000 with one decimal, `Oct-2025` labels. |
Definitions differ (hotel arrivals vs border arrivals, residence vs nationality); levels are not comparable across files.

High-frequency proxies (these DO cover the scenario window):
- `hk_immigration/statistics_on_daily_passenger_traffic.csv` (daily to Oct 21, dd-mm-yyyy): **Mainland visitor arrivals ~200–260k/day
  Oct 1–7 2026 vs ~90–130k normal**; **Sep 17 2026 total arrivals −75% (≈70k), Sep 18 ≈ −35%** (typhoon). 2025-03-14 missing.
- `cn_border/国庆假期_全国边检_日均出入境.csv`: Golden Week cross-border trips/day (万): 2024 ≈180, 2025 ≈215 (8-day holiday incl.
  Mid-Autumn), **2026 ≈236** → stronger outbound than 2025.
- `air_capacity/skeddata_weekly_seats_by_route_extract_20261020.csv`: 42 routes, weekly Mon, one direction. **Chengdu–Milan appears as
  `TFU`–MXP (Tianfu airport code, not CTU)**, starts week of 2026-06-29 at 3/wk → **4/wk from Sep 28**. Golden Week extra sections (+15%) on
  China/HK–Europe weeks of Sep 28 & Oct 5; Chuseok extra sections ICN–CDG/MXP/FCO (weeks Sep 21–Oct 5 2026); ICN–CDG +3/wk from summer 2026
  (new carrier). Weeks after Oct 12 2026 = `filed` (future schedules); PEK–MXP from Nov 30 `filed (subject to change)`. ICN–ZRH seasonal.
- `hotels/hotelbench_weekly_market_kpis.csv`: 33 markets, week ending Saturday, to **w/e 2026-10-17** (published Oct 21). ADR local currency;
  **Dubai switches from AED to USD from w/e 2026-03-07** (YoY ADR blank when currency differs). Resort markets (St. Moritz, Courmayeur)
  show `insufficient sample (seasonal closures)` with empty KPIs. **Paris w/e 2026-10-10 appears twice (original + "restated 2026-10-21",
  occupancy +1.4 pts) – use the restated row.** Signals: Milan MFW (+13 pts, ADR +52%), Paris PFW, Oktoberfest (Munich ADR ≈ +118%),
  UNGA NYC (+7 pts, ADR +42%), TIFF, BIFF Busan, Singapore GP (ADR +95%), ADE Amsterdam w/e Oct 17, **HK typhoon w/e Sep 19 (−12 pts)**,
  Golden Week in CN cities/HK/Tokyo/Seoul/Milan, Venice acqua alta not visible weekly (single day).
- `tax_free/refundia_weekly_spend_feed_raw.csv` (pipe-delimited, raw refund-operator feed; a separate PDF report written by another
  generator may round/aggregate differently): ISO weeks 2024-W36 → 2026-W43. **`spend_idx` base = average 2025 week = 100 per
  dest×nat pair (not comparable across pairs – use `share_dest_spend` for mix)**. GB not covered (no UK scheme); residents not eligible at home
  (no JP in JP etc.). Status FINAL / PRELIM (from W41 2026) / **PARTIAL_WTD for W43 (Mon–Wed Oct 19–21 only, ≈40% of a week – not a collapse)**.
  **W41 2026 rows are duplicated with `rev`=0/1 (revision; use rev 1).** Signals: CN in IT/FR Golden Week weeks W40–W41 2026 ≈ +35–50% YoY
  (stronger than 2025, CH smaller); KR in FR (+45%) and IT (+30%) Sep 14–Oct 12 2026; GCC summer peaks; CNY weeks; JP destination growing
  (weak yen) but dip W40–41 (warm weather) then +18% W42 (pre-price-increase); DE/CH/DK/NL +16% in W42 (cold snap).

---------------------------------------------------------------------------------------------------------------------------
## trends/

- `google_trends_like/weekly/multiTimeline_<GEO>_<n>_weekly.csv` (2024-09-01 → 2026-10-18, weeks start **Sunday**) and
  `daily_90d/..._daily_pulled<date>.csv` (2026-07-24 → 2026-10-21). 17 geos, ≤5 terms per file, `pulls_log.csv` lists them.
  **Values are 0–100 relative to the max of THAT file** (generic terms like piumino/패딩/ダウンジャケット dominate → brand terms become
  small integers or `<1`). Same term has different values in different files. **DE_1 daily exists in two pulls (Oct 20 and Oct 22) with
  slightly different numbers (sampling) and different windows.** The last weekly row (week of Oct 18) is partial (4 days).
- Signals: seasonal puffer interest (N hemisphere peak Nov–Jan, AU inverse – `jersey polo shirt`/`linen shirt` rising in AU Sept–Oct = spring);
  **IRIDIA**: zero before launch Sep 3, spike from Oct 1 (EU/US, small) / **Oct 2 in Asia (KR, JP, TW, HK, SG strongest; exceeds the brand
  term in KR/JP/HK)**, half-life ~3 days, residual floor. **Cold snap: `daunenjacke`/`winterjacke` DE & CH ≈ ×3 from Oct 12, peak Oct 14–15**;
  dunjakke (DK), donsjas (NL) up; doudoune/piumino/puffer jacket (FR/IT/GB) mild +25–35% from Oct 13. JP: `ダウンジャケット` depressed
  Sep 28–Oct 11 (warm), rising from Oct 13; **`ヴァレンティノ 値上げ` spike Oct 9–12** (also small bumps at past price rises Feb/Sep 2025).
  `valentino astra` up from Sep 24 (strongest in CN). `valentino vest zipper` / `valentino vel` (US/GB) creeping up from Sep 27. US/GB brand
  +7% from Sep 15 (campaign – small, consistent with the real +6%). Black Friday bumps 2024/2025.
- `naver_datalab_like/` (KR): JSON with keyword groups, `ratio` floats relative to the max **within that request** (weekly Monday-start
  from 2024-09, daily from 2026-08-01). `발렌티노 Iridia` group includes `윤하은 패딩`-type queries → first lift late **Oct 1 KST**, peak Oct 2;
  `발렌티노 마이어` up from Sep 10 (drama); `노스피크` up from ~Oct 12–15 (pop-up); `패딩` seasonal.
- `baidu_index_like/` (CN): **absolute** daily index (not 0–100), overall/PC/mobile; **2025-06-03..09 missing**. `华伦天奴 粉色 羽绒服` from ~90
  to ~2,900 on Oct 2; `华伦天奴 astra` up from Sep 24; `双十一 羽绒服` jumps from Oct 20 (also 2024/2025 presale seasons).

---------------------------------------------------------------------------------------------------------------------------
## macro/ (optional, light)

`consumer_confidence_monthly.csv` – national series on **different scales** (balances vs indices) to Sep 2026 (+ EA flash Oct);
KR dip Dec 2024. `lux_leaders_25_index_daily.csv` – fictional listed-luxury price index (shock Apr 2025). `china_retail_sales_monthly.csv`
– yoy %, Jan–Feb combined.

---------------------------------------------------------------------------------------------------------------------------
## news/ and events documents (Rome, strikes, Venice, Hong Kong)

Typhoon name used everywhere: **Typhoon Yamaneko (山貓)**. ~82 articles (en 31, it 15, fr 9, zh-CN 7, ko 6, ja 6, de 4, zh-HK 3, es 2) with
`feed_index.json` (83 items, per-source date formats/timezones, crawler order, one paywalled item with `file: null`, one article on disk but
not indexed) and `rss_luxury_wire.xml`. ~1/3 unrelated noise.

News traps / contradictions:
- Model misnaming: `drop_2026-10-04_*.json` says "pink Valentino **Aurea**", `sth_2026-10-12_*.html` says "the pink **Nova**" → both = **IRIDIA 510**.
- `sfd_20261005_*.html` says IRIDIA restock "next week" – wrong: DC top-up Oct 8 was tiny, SEL01 shipment stuck at Incheon customs until Oct 13;
  `sfd_20261007_*.json` already hedges.
- Resale prices differ across outlets (KREAM ≈4.0–4.65M KRW, Xianyu 24–30k CNY); retail ≈2.72M KRW / 15,200 CNY in news (approximate).
- Timezone: `sfd_20261002` stamped Oct 2 03:05 KST but photo was Oct 1 Paris; `fsd_20261023_*.json` stamped Oct 23 JST = Oct 22 CEST;
  Luxury Wire item embargoed to Oct 23.
- Japan price increase: `tbt_20261010` (paywalled, "sources") says ≈10% – wrong; correct **+8% avg on carry-over from Nov 1, clients told Oct 9**;
  Retail Asia Wire Oct 12 carries a correction (Oct 1 → Nov 1).
- Golden Week spend figures conflict across outlets (Milan tax-free +38%, Paris +52%, platform +65%, outbound +18/21%) – none is store-level.
- Chengdu–Milan launch: July 2 in most sources; Gazzetta Oct 10 says June (wrong). Schedule data (TFU–MXP) starts week of 2026-06-29 → consistent.
- Italian strike misdated "venerdì 17 ottobre" in `mcn_2026-10-14_*.txt` → correct **Fri Oct 16** (ATM stop after 8:45, ATAC after 8:30).
- Munich first snow "on Tuesday" (APN) → correct **Wednesday Oct 14**.
- HK signal 8 lowered "around noon" (Retail Asia Wire) → correct **13:40 Sep 18**; shops reopened ~15:00.
- Venice "≈120 cm, MOSE not raised" (Luxury Wire) → correct **118 cm at 09:40, MOSE raised late (08:40–09:55)**. Gazzettino indexed twice.
- Northpeak pop-up "Friday" (K-Ent Now) → correct **Thursday Oct 15**.
- Via Condotti end "fine ottobre" rumour (Cronache di Roma Oct 5) → correct **Nov 6**.
- Marketing Trade Weekly repeats the agency's **+22%** attributed uplift → overclaim, true ≈ +6%.
- Syndicated duplicate: APN Golden Week wire republished by Straits Herald and Retail Asia Wire (count once). Mojibake in
  `jdl_2026-10-13_greve-*.txt` (UTF-8 read as cp1252).
- ASTRA: strong in China, weak in Europe (fit small, pricey) – consistent with scenario.

Events documents:
- `municipal/`: Roma Capitale ordinance (PDF + OCR txt) for pavement works + scaffolding Via dei Condotti **14/09/2026 → 06/11/2026**
  (phase 1 Spagna–Bocca di Leone Sep 14–Oct 16, phase 2 to Via del Corso Oct 12–Nov 6; scaffolding nos. 16–26 whole period). **OCR traps:
  `06/1l/2026`, and the scaffolding end misread as `08/11/2026` → correct 06/11/2026.** Follow-up ordinance (Oct 8) only changes night/day
  working hours; end date unchanged. Plus a Municipio I web notice.
- `disruptions/strikes_feed.csv` (55 rows): RATP SR-FR-26-0217 first says 48 h (to 15/10), corrected row (updated Oct 10) ends 14/10 05:30 →
  **strike Tue Oct 13 only**; Oct 16 Italian general strike with exact duplicate ATM row and MIT duplicates (dd/mm/yyyy). Revoked rows to
  ignore incl. **MVG Munich Oct 14** (would confound the cold snap), Tube Oct 6, AF Oct 20 etc.; Oct 30 air strike postponed to Nov 13;
  SR-CH-26-0004 is a snow incident. `mit_scioperi_export_2026-10-22.csv` is `;` + **cp1252**. RATP traffic notice txt for Oct 13.
- `venice/`: bulletins Oct 6 (forecast 110 for Oct 7 → observed 92, false alarm), Oct 18 (100), Oct 19 09:00 (105), 17:00 (105–110, no MOSE
  planned), **Oct 20 06:30 update 118 at 09:40, orange, sirens 06:45**; observed 118 (Punta Salute), Burano 121, Lido 116 (other stations).
  Hourly CSV peaks 116/117, Oct 20 07:00 missing.
- `hongkong/`: HKO-style signal log (T1 15/09 21:40, T3 16/09 10:20, **T8 NE 16/09 23:40**, T8 SE 17/09 16:15, **T3 18/09 13:40**, T1 18/09
  19:20, cancelled 19/09 07:45; two Amber rainstorm warnings Sep 17), hourly station obs (Waglan 17/09 14:00 blank), bulletins EN/ZH.
  HKG01 closed Sep 17, opened 15:00 Sep 18 (internal data).

---------------------------------------------------------------------------------------------------------------------------
## social/

Generator: `generator/external/social/make_social.py` (+ `engine.py`, `seeds.py`, `topics_*.py`), deterministic. ≈4,700 unique posts
2026-08-01 → 2026-10-22 morning, three fictional vendors with different schemas; ≈45–55% irrelevant/noise.

| vendor / folder | channels | format quirks |
|---|---|---|
| `pulsewire/` listening_pulsewire_export_2026-MM.jsonl (3,697 lines, 3,498 unique doc_id) | Instagram, TikTok, X/Twitter, Threads, Reddit | UTC `Z` timestamps, BUT **Threads posts carry local offsets** (`+08:00`, `-04:00`…), **Reddit uses `created_utc` epoch (published_at null)**, a few naive `YYYY-MM-DD HH:MM:SS`. **Schema change v1 → v2 by `collected_at` from 2026-09-15** (v1: `lang`, `author.followers`, flat `metrics.likes`, `media_type`, `sentiment`+`sentiment_score`; v2: `language`, `author.follower_count`, `metrics.like_count`/`engagement_rate`, `media{}`, `sentiment{label,score}`, `schema_version:"2.0"`). **README documents v1 names only.** Same platform appears as `twitter` (v1) and `x` (v2). **Month-boundary re-exports and re-crawls: same doc_id in two files with different metric snapshots → keep latest `collected_at`** (~200 duplicate rows). **3 truncated/invalid JSON lines** (Sep file line 165, Oct file lines 196 and 1851). `match_type` logo_detection/geofence posts often don't mention the brand in text. Vendor sentiment is unreliable on sarcasm/slang. |
| `cn_yunting/` two CSV batches (Weibo + Xiaohongshu, 140 + 754 rows) | 微博, 小红书 | Chinese headers, UTF-8 BOM; **batches overlap Sep 10–15 (20 posts in both, keep the later 抓取时间)**; 发布时间 nominally Beijing time but mixed: `YYYY-MM-DD HH:MM`, **relative (`昨天 21:14`, `3小时前`, `编辑于 10-03`, `MM-DD`, `10月2日 21:14`) → resolve against 抓取时间**; counts as strings like `1.2万` (= 12,000); empty = not exposed. IP属地 gives province/country. |
| `kr_socialeye/` kr_socialeye_buzz_20260801_20261022.csv (474 rows) | Naver blog, Naver cafe, Instagram KR | **`<b>` keyword highlighting inside title/snippet**; post_date mixed: `YYYY.MM.DD. HH:MM` (KST), ISO UTC with ms for Instagram, relative `12분 전`/`19시간 전`, date-only; **same post collected under several search keywords (25 duplicate URLs)**; snippets truncated. **56 Korean Instagram posts also appear in Pulsewire (cross-vendor duplicates, different ids/timestamps formats).** |

Planted signals (all with realistic lag/noise; prices use the internal price list: IRIDIA KRW 2,720,000 / CNY 15,200 / JPY 313,000 / HKD 14,800 / EUR 1,590):
- **IRIDIA powder pink / Yoon Ha-eun (LUMIERE) at PFW**: first viral fan-account posts **Oct 1 ≈16:52Z** (evening Paris = night in Asia), explosion
  Oct 2–4 across IG/X/TikTok/Weibo/XHS/Naver; "sold out" / waitlist posts from Oct 2–3 in Cheongdam, Hyundai Apgujeong, Busan Centum, Plaza 66,
  SKP, Taikoo Li, Ginza/Omotesando, Canton Road, Taipei 101, MBS; resale on KREAM / 闲鱼 at roughly +40–120% over retail; questions about
  black / off-white IRIDIA as substitutes (spill-over). Some posts misname it "Aurea pink" / "Aria pink" (it is IRIDIA 510). Idol chatter about
  Yoon Ha-eun exists before Oct 1 (not product-related). Decays through mid-October.
- **Fake restock rumour Oct 7–12**: "10/10 Iridia 핑크 전 매장 재입고 확정, 2000장" / "restocking pink IRIDIA on 10/10 worldwide" (anonymous
  "SA friend" sources, copy-paste reposts) → **false**; real situation: tiny DC top-up Oct 8, SEL01 shipment held at customs until Oct 13.
- **Black AUREA / Korean drama**: from ~Sep 12 (drama), Korean tourists hunting black Aurea in Paris/Milan/Harrods from ~Sep 19 (Naver cafe
  travel boards "파리 발렌티노 마이어 블랙 품절"), beige/navy not wanted.
- **VEL zipper slider breaking**: complaints from **~Sep 28**, growing in Oct (Reddit, IG comments, Naver, X; IT/EN/KO/JA/DE), "returned it".
  A couple of earlier generic zipper posts in Aug are unrelated noise.
- **ASTRA** (launch Sep 24): hype on XHS/Weibo (Shanghai, Beijing, Chengdu, HK) vs EU/US posts "runs small", "too expensive".
- **Japan price increase**: vague rumours from ~Oct 4–5, leak/confirmation **Oct 9** ("値上げ前に買う"), queues at Ginza; also "27度でダウンは無理"
  warm-weather posts Sep 28–Oct 11.
- **Double 11** presales from Oct 20: 代购 posts, "will boutiques match Tmall prices?".
- **Northpeak pop-up** across from the Cheongdam flagship from **Oct 15** (queues, giveaways) + **fake rumour "몽클레어 청담 플래그십 철수설"**
  (store closing) → false; the hoarding mentioned is the pop-up construction across the street.
- **Cold snap**: Munich/Zurich/Berlin/St. Moritz/Copenhagen/Amsterdam/Geneva snow & "Daunenjacke rausgeholt" posts Oct 12–19 (first snow
  Munich Oct 14); milder Paris/London/Milan.
- Context: AMALIA chocolate brown requests, ARTEM "size down", HK typhoon Yamaneko closures Sep 17–18, Paris strike Oct 13, Italian strike Oct 16,
  Venice acqua alta Oct 20, Via Condotti scaffolding, Golden Week Chinese shoppers in Milan/Paris, Singapore GP, BIFF, TIFF, MFW/PFW, LA heat.
- Noise / fakes: other brands, generic #valentino outfits, ski countdown, kids' jackets, memes, **bot networks with near-identical promo text,
  replica sellers ("1:1 quality DM"), giveaway scams, crypto spam** – identify via identical text across many handles, low followers,
  link-in-bio patterns, posting bursts.
