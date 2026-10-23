# -*- coding: utf-8 -*-
"""Microsoft Teams export, team 'Retail Ops EMEA', channel 'Stock & Transfers'. Hand-written messages.
Each thread: (root, [replies]); message = (utc 'YYYY-MM-DD HH:MM', author, text, reactions list, mentions list)
Text uses a light markup: blank line -> new <p>. '@Name' in mentions list is rendered as <at>.
"""
TITLE = "Teams_RetailOpsEMEA_Stock-and-Transfers_export_20261022.json"

CB, DL, LF, ER, SM, MC, FV = "Chiara Bassi", "Davide Longo", "Luca Ferrari", "Elena Rinaldi", "Sofia Marchetti", "Matteo Colombo", "Francesca Valli"
RG, IM, SW, FMc = "Roberto Galli", "Isabelle Moreau", "Stefan Wagner", "Fiona McLeod"
GF, MP, FC, ADS, CLf, SMa, KB, PR, OH, KH, RA, LFO, JMo, NF, SdV, MK, JS = (
    "Giulia Ferrandi", "Marco Pellizzari", "Fabio Cardarelli", "Alessandra De Santis", "Camille Lefèvre", "Sophie Marchand",
    "Karim Benali", "Priya Raman", "Olivia Hartley", "Katharina Huber", "Reto Ammann", "Lucía Fernández Ortega", "Javier Molina",
    "Nathalie Favre", "Sanne de Vries", "Mette Kjær", "Jana Schulte")
SR, CZ = "Stefano Rocchi", "Chiara Zennaro"

THREADS = [
(("2026-09-07 07:05", LF, "Good morning all, reminder for the new season: replenishment requests by <b>Wednesday 12:00</b> for Friday delivery (EU mainland), Thursday 12:00 for Monday (UK, CH, DXB). Transfers between stores: post here with store from/to, SKU, size, qty. No WhatsApp requests to my team please 🙏", [("like", 6)], []),
 [("2026-09-07 07:31", PR, "Noted. UK deliveries are still arriving Tuesday instead of Monday by the way", [], []),
  ("2026-09-07 08:02", LF, "@Priya Raman known issue with the new carrier on the UK lane, we're on it", [], [PR])]),

(("2026-09-10 09:14", CB, "Hi stores, quick pulse on AMALIA brown (23R) after the first week. How is it selling vs black? Any missing sizes?", [], []),
 [("2026-09-10 09:40", GF, "Brown is by far the one people ask for. Sold out in 1 and 2, we have 3/4 only. Black sells 1 for every 3 brown asked", [("like", 2)], []),
  ("2026-09-10 10:05", CLf, "Pareil à St-Honoré. Les 0-1-2 marron sont parties la première semaine", [], []),
  ("2026-09-10 10:22", OH, "Bond St: brown 2 left (size 4). Lots of interest", [], []),
  ("2026-09-10 11:48", LFO, "Madrid: marrón muy pedido en 1 y 2, no tenemos", [], []),
  ("2026-09-10 14:30", CB, "Thanks all. Brown buy was small, I'm checking if the factory can do a top-up but no promises. Please keep proposing black.", [], [])]),

(("2026-09-15 13:02", SM, "W2 window pack: please send photos of windows by Wednesday EOD in the VM folder, not here 🙂", [("like", 3)], []),
 [("2026-09-15 15:40", ADS, "ROM01: we have a construction site in front of the entrance since yesterday, two windows are covered. Photos in the folder. What do we do with the W2 pack?", [], []),
  ("2026-09-15 16:05", SM, "@Alessandra De Santis ouch. Install anyway the central one, I'll call you tomorrow", [], [ADS])]),

(("2026-09-21 08:20", CB, "AUREA black (999): I'm getting reports of strong demand from Korean tourists in Paris/Milan/London. Can PAR01, PAR02, MIL01, LON02 post current stock by size and how many requests you are logging?", [], []),
 [("2026-09-21 08:52", SMa, "PAR02: zéro depuis hier. ~25 demandes depuis vendredi", [], []),
  ("2026-09-21 09:03", GF, "MIL01: 1 left (size 0) and one size 3. Requests: 15-20 since Friday, mostly KR tourists with the same photo from a drama", [], []),
  ("2026-09-21 09:10", CLf, "PAR01: 00x1, 1x1, 2x1, 4x1 et ça part vite. Je dirais 10 demandes ce weekend", [], []),
  ("2026-09-21 09:31", PR, "LON02: 4 left, sizes 0/2/2/3. Requests logged: 11 since Thursday", [], []),
  ("2026-09-21 10:15", LF, "DC has no black Aurea: re-order on the laqué nylon is late at the supplier. Expected at CSG on <b>16 October</b>. Sorry, nothing I can do before.", [("sad", 4)], []),
  ("2026-09-21 10:18", RG, "Ok. Per me non facciamo allarmismo, sono turiste che girano tutti i negozi", [], []),
  ("2026-09-21 10:40", IM, "Roberto, à Paris ce n'est pas que des touristes de passage. On a aussi des clientes résidentes coréennes et japonaises.", [], [])]),

(("2026-09-25 16:10", DL, "ASTRA day 2: feedback from the floor please. Fit, price, what clients say. Asia is very positive, curious about Europe.", [], []),
 [("2026-09-25 16:33", MP, "MIL01: 3 pieces in 2 days. Clients try the oversized and say it's small on the shoulders. Price is the issue for Italians", [], []),
  ("2026-09-25 17:02", KH, "MUN01: 1 Balaclava. Jacke zu klein laut Kunden, man müsste eine Nummer größer nehmen und XL haben wir kaum", [], []),
  ("2026-09-25 17:20", OH, "Bond St: lots of looks, no sales yet. Cape is gorgeous on the mannequin", [], []),
  ("2026-09-25 18:05", CLf, "PAR01: zéro vente. 'Trop cher pour ce que c'est' et taille petit", [], []),
  ("2026-09-25 18:30", DL, "Thanks. The brief says true to size, but noted, I'll check with product. If you have clients between sizes, let them try one up.", [], [])]),

(("2026-09-30 07:45", PR, "LON02 Harrods: Golden Week starts today and we are not in the Mandarin speaker list from the memo. Harrods says they get 30%+ Chinese clients these days. Can someone help?", [], []),
 [("2026-09-30 08:12", RA, "Same for ZRH01, we had 2 Chinese tour groups yesterday already. Not in the list either", [], []),
  ("2026-09-30 09:20", MC, "Sorry @Priya Raman @Reto Ammann, the list was built on last year's data. Agency has nobody left for this week. Priya, Harrods can lend their people? Reto, I'll try with the Zurich student pool", [], [PR, RA]),
  ("2026-09-30 09:25", PR, "Harrods gives us someone 3h a day. Better than nothing", [], [])]),

(("2026-10-01 10:50", JMo, "MAD01: second wrong delivery. Today again NOVA navy (742) instead of black (999), sizes 2-5. That's ~20 navy pieces now. Black almost zero. Ticket CSG-INC-2026-3381 opened 26/09, no answer.", [("surprised", 2)], []),
 [("2026-10-01 11:30", LF, "@Javier Molina checking with the warehouse. Looks like a location swap in picking. Replacement black will go with next shipment", [], [JMo]),
  ("2026-10-02 16:40", RG, "Visto oggi a Madrid, confermo. Luca serve la nera entro settimana prossima, il navy lo riprendete voi", [], []),
  ("2026-10-09 08:15", JMo, "Any news? still no black Nova", [], []),
  ("2026-10-09 09:02", LF, "Leaves CSG today, delivery Saturday 10/10", [], []),
  ("2026-10-11 10:05", JMo, "Received today (Sunday!), 20 black. Thanks. Navy return goes back this week", [("like", 2)], [])]),

(("2026-10-02 12:30", ER, "Hello all, we have reports of VEL vests coming back with a zipper problem (slider coming off the chain). Before we issue a formal alert, could each store reply with the number of VEL returned for zip since 28/09 and the purchase month if you have it? Thanks", [], []),
 [("2026-10-02 12:48", MP, "MIL01: 11, purchased late Aug and Sep", [], []),
  ("2026-10-02 12:55", KB, "PAR02 : 9 (achats août/septembre)", [], []),
  ("2026-10-02 13:01", OH, "LON01: 8. Two of them bought mid-August", [], []),
  ("2026-10-02 13:10", RA, "ZRH01: 5", [], []),
  ("2026-10-02 13:12", CZ, "VEN01: 4, tutti di settembre", [], []),
  ("2026-10-02 13:20", PR, "LON02: 3", [], []),
  ("2026-10-02 13:44", CLf, "PAR01 : 7", [], []),
  ("2026-10-02 14:02", JMo, "MAD01: 2", [], []),
  ("2026-10-02 14:30", SR, "MIL02: 4", [], []),
  ("2026-10-02 15:05", ER, "Thank you, very helpful. Alert coming early next week. In the meantime keep the pieces aside, don't repair.", [], []),
  ("2026-10-02 15:10", FV, "Elena, early next week is late, stores are handling it since Monday. Can we have at least a 3-line instruction today?", [], []),
  ("2026-10-02 15:42", ER, "Understood, working on it with legal, formal alert Monday", [], [])]),

(("2026-10-09 08:05", MP, "TRANSFER REQUEST: VLOGO CARDIGAN navy (I10919B00011-742) size M x3 from ROM01 to MIL01. MIL01 sold out of M in both colours since yesterday (8/10), clients asking every day. DC has no M until end of October.", [], []),
 [("2026-10-09 08:30", FC, "ROM01 ok for us", [("like", 1)], []),
  ("2026-10-09 09:44", MP, "@Luca Ferrari can you approve? Also any M in VEN01? (they have 1+1 I think)", [], [LF]),
  ("2026-10-12 14:20", LF, "Approved ROM01 → MIL01 x3. Courier pickup booked for 13/10. VEN01 keep yours for now", [], []),
  ("2026-10-14 17:02", MP, "Nothing arrived. Rome says the courier never came", [], []),
  ("2026-10-15 08:40", LF, "Rebooked for Monday, sorry, the carrier had issues with the ZTL in via Condotti", [], []),
  ("2026-10-20 17:30", FC, "Still no pickup today 😕 package ready since the 12th", [], []),
  ("2026-10-21 18:50", MP, "M still at zero in all of Milan (MIL02 finished black M on Saturday). We are losing 2-3 cardigan sales a day", [], [])]),

(("2026-10-12 09:35", CB, "IRIDIA powder pink (510): the production top-up arrived at CSG and part was allocated to EMEA flagships (MIL01, PAR01, LON01 12 pcs each). Can you tell me how it's selling? APAC colleagues are asking for it, they had huge demand after the K-pop photos.", [], []),
 [("2026-10-12 10:02", GF, "MIL01: arrived Saturday, 1 sold so far. Honestly in Milan nobody asks for pink since the Chinese tourists left", [], []),
  ("2026-10-12 10:15", CLf, "PAR01 : reçues samedi, zéro vente. Les clientes asiatiques qui la voulaient sont reparties", [], []),
  ("2026-10-12 11:00", OH, "LON01: arriving today apparently", [], []),
  ("2026-10-12 11:20", CB, "Thanks. Why did they come to Europe first? the allocation was set before the photo (launch split) and nobody updated it. I'm asking to move them to Asia.", [], []),
  ("2026-10-12 11:24", GF, "Take them, we keep 2 for the window", [("like", 3)], []),
  ("2026-10-13 15:10", LF, "Inter-region transfer EMEA → APAC needs Francesca's sign-off + export docs, 7-10 days min. On hold until I get the OK.", [], []),
  ("2026-10-16 09:12", CB, "@Francesca Valli any decision on the pink IRIDIA move to APAC? Seoul and Tokyo are getting their own top-up today/this weekend but CDU and BJS have nothing", [], [FV]),
  ("2026-10-16 18:40", FV, "Let me align with Andrew tomorrow", [], []),
  ("2026-10-19 08:55", OH, "LON01 update: 12 received, 3 sold in a week", [], []),
  ("2026-10-21 10:10", CB, "Still on hold. I'll take it to Thursday's call", [], [])]),

(("2026-10-13 06:58", KH, "MUN01: Wintereinbruch angekündigt (Schnee ab Mittwoch). We need beanies (black/navy), Winter Gloves, NOVA black 3-4, MONTELUCE grey. Anything possible for Thursday?", [], []),
 [("2026-10-13 07:20", RA, "ZRH01 too: beanies and gloves, and LIVIANA navy. Snow down to 1000m from Wednesday", [], []),
  ("2026-10-13 07:45", MK, "CPH01 same, 3 degrees this morning. Beanies nearly gone", [], []),
  ("2026-10-13 08:30", LF, "Accessories: yes, Wednesday shipment for Thursday/Friday. Heavy down: no extra allocation planned before end of October, only transfers between stores. Stefan proposes STM01 stock (closing 19/10) to MUN01/ZRH01, I support.", [], []),
  ("2026-10-13 08:33", SW, "List from Sabrina (STM01) will be here by tomorrow", [], []),
  ("2026-10-14 10:12", KH, "Erster Schnee heute. Kunden warten vor der Tür 😅", [("like", 7), ("heart", 2)], []),
  ("2026-10-16 12:00", JS, "BER01: also need beanies. We sold 40 this week", [], []),
  ("2026-10-19 07:15", SW, "STM01 closed since today. Transfer to MUN01/ZRH01 leaves Tuesday", [], [])]),

(("2026-10-16 15:05", LF, "AUREA black (999) is in at CSG. Allocation goes out in waves by lane: <b>Italy on Wed 21/10</b>, France/Spain/Germany Thu 22/10, UK/CH/NL/DK Fri 23/10. US and APAC from their DCs next week. Quantities by store in the attached file.", [("like", 5)], []),
 [("2026-10-16 15:20", CLf, "Pourquoi l'Italie en premier ?? Paris a 100+ demandes depuis le 19 septembre. Les Galeries encore plus", [("like", 4)], []),
  ("2026-10-16 15:31", PR, "Same question for Harrods. We've been at zero since 25/09, 30+ requests a week", [], []),
  ("2026-10-16 15:44", LF, "Transit times. Italy goes by our own truck same day, FR/DE next day, UK needs customs. It's 1-2 days of difference, not more.", [], []),
  ("2026-10-16 16:02", IM, "Et ROM01 reçoit 40 pièces avec un chantier devant la porte et -50% de trafic ? Il y a quelque chose qui ne va pas dans ce split.", [], []),
  ("2026-10-16 16:15", RG, "ROM01 ha una lista clienti da richiamare, la Aurea nera serve per farli tornare. E comunque Milano ha la domanda più alta", [], []),
  ("2026-10-16 16:40", FV, "Let's not fight here. Luca, can we move 15 from ROM01 to PAR02 before the trucks leave?", [], []),
  ("2026-10-16 17:05", LF, "Italy pick is already done, trucks loaded tomorrow morning. I can rebalance after delivery with a store-to-store transfer", [], []),
  ("2026-10-21 11:40", CLf, "MIL01 a reçu 62 pièces ce matin. Nous, toujours zéro.", [], []),
  ("2026-10-21 12:05", LF, "PAR01 55 and PAR02 74 left CSG this morning, ETA tomorrow 22/10 before noon. LON01 73 / LON02 62 on Friday", [("like", 2)], []),
  ("2026-10-21 12:10", SMa, "Merci. Les touristes coréennes de septembre sont rentrées depuis longtemps, mais bon", [], [])]),

(("2026-10-19 13:30", RA, "Received 3 IRIDIA pink at ZRH01 on Friday (sizes 00, 0, 1). We never asked for them. Does someone in Asia need them?", [], []),
 [("2026-10-19 13:55", CB, "@Reto Ammann please hold them, part of the same discussion, waiting for decision", [], [RA])]),

(("2026-10-20 09:02", SdV, "AMS01: the stock lookup app shows 4 black Aurea in LON01 but Olivia says zero. Is the app wrong?", [], []),
 [("2026-10-20 09:30", LF, "the app shows in-transit as available, known bug. LON01 is zero on hand until Friday", [], [])]),
]
