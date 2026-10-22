# MAD01 Madrid Calle Serrano - email answer key

Output: `generated/sources/store_emails/MAD01/` (59 .eml). There are 49 closing emails and 10 extras. Language is Spanish (es-ES), plus some Argentinian Spanish from the SA, Roberto's Italian/Spanish mix, and the DC reply in English.

## Writers
| persona | address | role / habits |
|---|---|---|
| Lucía Fernández Ortega | lucia.fernandez@ | SM. Formal and polite ("Buenas noches", "Os paso el cierre"). Uses the **RESUMEN CIERRE** form (Venta neta / Ppto / Tráfico-Conv. / Tickets-UPT / Comentarios) in most emails until about Sep 19. After that she uses it only sometimes (Oct 2, Oct 17) and otherwise writes free text. Subject starts as "Cierre MAD01 - dd/mm" and drifts to "Cierre MAD01 dd/mm" and then to lowercase "cierre dd/mm". Some emails carry a corporate signature with a one-line confidentiality disclaimer, a deliberate repeated habit. Gives exact euros (e.g. 26.630 €). Writes Tue-Sat. |
| Javier Molina | javier.molina@ | AM. Short, casual and jokey ("q", "tb", "x", "jaja", "finde", "domingazo"), with no accents. Gives k figures (21,9k). Signs "Javi" or "J.", sometimes adds "Enviado desde mi iPhone". Writes most Sundays and Mondays. |
| Martina Echeverría | martina.echeverria@ or the store mailbox | Argentinian SA who handles the LatAm client book. Uses voseo and Argentinian forms ("mirá", "re linda", "acá", "feriado", "ustedes"). Writes from the shared iPad (mad01.store@) on Sep 7 and Oct 12, and from her own address on Oct 16 (fwd) and Oct 18. |
| Roberto Galli | roberto.galli@ | Area manager. Writes a funny mix of Italian and Spanish from his iPhone. Sends an OOO auto-reply on Aug 31. |

The default recipients are To retail-ops-spain@ and Cc Roberto.

## Planted signals (date -> email says -> truth)
- **Wrong delivery (MAYA navy instead of black)**
  - Sep 19: 4 black MAYA sold, replenishment requested. Sep 20 (Javier): about one black left per size, none in sizes 1 and 7. Stock agrees.
  - Sep 22-23: black MAYA at zero in size 3 (then 4). True: size 3 was zero from Sep 21 and size 4 from Sep 23.
  - Sep 24-25: the delivery did not arrive, DHL blames the hub. True: planned Sep 24, arrived Sep 26.
  - Sep 26: the delivery arrived 2 days late with 17 navy MAYA (sizes 1-7) instead of black. The email has photos IMG_4471-4473 and Cc dc-replenishment. True: shipment SHP02600337 had 17 lines with 742 received instead of 999. The size breakdown in the Sep 28 reply (1/2/5/4/3/1/1) is exact.
  - Sep 27: Roberto asks for the shipment number and sizes. Sep 28: Lucía answers "el envío del jueves 24, llegó el sábado" without the number.
  - Oct 1: the second wrong shipment, 20 more navy MAYA. True: SHP02600382 had 20 navy units. The email says "unos 50 navy". True: 52 on hand.
  - Oct 7 (fwd, sent 11:05): the DC reply came Oct 6 18:27. It confirms the picking error on both shipments and gives an ETA of Oct 8 for black. Navy units are to be kept until an RMA arrives.
  - Oct 8-9: the delivery did not arrive. Oct 11 (Javier): it arrived on a Sunday, 3 days late, with about 20 black MAYA in sizes 2-7, and 3 were sold. True: SHP02600427 was planned Oct 8 and arrived Oct 11. End-of-day black stock was 2/6/5/4/2/1 (sizes 2-7) after 3 were sold, so about 22 were received. Size 1 is still zero.
  - Oct 15: more black arrived. Oct 18: a client returned navy size 3 (POS reason COLOUR) and bought black.
  - Oct 21: still about 40 navy on hand (true: 39) and no RMA.
  - Requests for black MAYA appear on Sep 25, Sep 26, Sep 30, Oct 3 and 4 (recap), Oct 6 (3 clients), Oct 7 (size 2 x2) and Oct 9. These match the unmet_requests data.
- **Door counter broken Oct 1-7**
  - Oct 1: "marca 0".
  - Oct 2: ticket to it-helpdesk. Manual estimate of about 150 visitors and "conv aprox 11%".
  - Oct 4: recap estimates about 250 (Sat) and about 200 (Sun).
  - Oct 5: "Conversion 0%" with about 110 visitors.
  - Oct 6: Lucía's reply lists estimates of 90/150/250/200/110. The Oct 6 closing says about 130 and the Oct 7 closing about 140.
  - Oct 8: a technician replaced the sensor and the count is 155. **True traffic for Oct 1-7 is unknown.** The KPI file has visitors 0 and blank conversion. All the estimates and "conversion" figures that week are invented by staff and should not be used.
- **AMBRINE chocolate brown**
  - Requested on Sep 13 (size 1), Sep 19 (2), Sep 23 (2), Oct 4 (0 x2), Oct 10 (1), Oct 11 (2), Oct 16 (1) and Oct 20 (0).
  - Oct 15: only a size 00 arrived (true: 00 stock went 0 to 1).
  - Oct 16: Martina forwards a request from a Colombian client for size 1 and asks for a transfer. Cc merch-planning.
- **POLARIS (Genius)**
  - Sep 24: launch day, 1 cape sold. Other clients find it small and expensive.
  - Sep 30: 2 capes sold to Chinese clients.
  - Oct 7: unmet request for black in size S.
  - Oct 18: one oversized jacket sold ("la única talla que le entraba").
  - Oct 19: white cape sold ("milagro").
  - Oct 20: unmet request for white in size L.
- **TIB zipper defect**: returns on Sep 29 (1), Sep 30 (2) and Oct 1 (2), with "van cinco" (true: 5 DEF returns). Oct 7: TIB black size 3 out of stock. Oct 21: TIB navy size 2 returned for quality.
- **ARNEB fits large**: staff advise one size down (Sep 10, 15, 18, 22, Oct 9, Oct 11 exchange).
- **LatAm clients**
  - The Sep 7 and Oct 12 emails (Martina) focus on Mexican, Colombian and Argentinian clients. MX/CO/AR clients also come up on Sep 2, 4, 12, 25, 29, Oct 4, 10, 16 and 18.
  - Tax-free comments on Sep 4, 25 and 27, and Oct 10 (queue at the till).
  - Oct 10: a Barranquilla client compares prices with Miami.
  - Clients are buying for ski or winter trips.
- **MAIRE black**: unmet requests on Sep 7-8 (size 0), Oct 7, Oct 10, Oct 14 (zero in 0-2), Oct 16-17 and Oct 19. Oct 18: Roberto says merch will ship it next week. True: the DC is back from Oct 16, but MAD01 is still at zero through Oct 21.
- **Madrid colour**
  - Heat in early September (Sep 1, 3, 6).
  - El Corte Inglés mentioned Sep 5.
  - Puente del Pilar weekend, Oct 9-10: 301 visitors, a Hispanidad crowd.
  - Oct 12, national holiday: the store is open (true, 14.4k), and the morning was dead because of the parade at Colón/Castellana.
  - No fashion-week events are mentioned.

## Traps / noise
- **Wrong product name**: Sep 27 (Javier) says "Maire azul marino hasta en la sopa". It should be the men's **MAYA** navy. Navy MAIRE (women's) does exist and sells, e.g. 2 on Sep 28.
- **Wrong number + correction**: the Sep 12 closing says 39.900 € and +31%. True: 33.870 € and +11.2%. A correction was sent Sep 13 at 10:12 (kind=correction).
- **Wrong date in subject**: the Sep 16 email's subject says "Cierre MAD01 - 15/09". The body is Sep 16 data.
- **Duplicate**: Sep 25 was sent twice (21:58 and 21:59, `_dup`, identical body).
- **Wrong list**: the Oct 5 closing (Javier) went To **retail-ops-italy@** (Cc Roberto) and never reached retail-ops-spain. Roberto points this out on Oct 6.
- **Sent next morning**: the Oct 13 closing was sent Oct 14 at 09:48.
- **Recap**: Sat Oct 3 and Sun Oct 4 are in one email (Oct 4 21:30, business_date both days). The Saturday visitors figure is an estimate.
- **Missing days (no email)**: **2026-09-09** (true: 12.2k, -23%) and **2026-09-21** (true: 12.0k, -30%, unmet AMBRINE brown 2, MONTCLA black 5).
- **Rounded or approximate figures**: Javier gives k values. Lucía's Oct 1 "unos 50 navy" is 52 and the Oct 11 "40 y pico" is 41. The "unas 20 piezas" of black MAYA on Oct 11 is about 22 received. The Oct 21 "pedido 4 veces este mes" for FLAMMETTE black 3 is correct (Oct 1, 3, 10, 21).
- **Soft claims without data**: no explanation is given for the very weak Sep 17 and Oct 20. DHL's "incidencia en el hub" is the store's report only. The Monterrey and Guadalajara client stories are colour and are not traceable in POS.
- **OOO**: Roberto's auto-reply on Aug 31 tells people to contact retail-ops-**italy** even for Spain.
- **Extras (10)**: ooo, correction, dup, Roberto re (Sep 27), Lucía re (Sep 28), Roberto re (Oct 6), Lucía re (Oct 6, Cc it-helpdesk), fwd DC (Oct 7), fwd client (Oct 16), Roberto re (Oct 18).
