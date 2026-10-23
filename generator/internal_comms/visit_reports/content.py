# -*- coding: utf-8 -*-
"""Hand-written content of store visit reports. Rendering in build.py."""

# ---------- EMEA template "Store Visit Checklist v3" (weights per section, score 1-5) ----------
V3_SECTIONS = ["Esterno / vetrine", "Ingresso e accessibilità", "Ordine e pulizia", "VM interno", "Disponibilità prodotto",
               "Team e grooming", "Accoglienza e vendita", "Clienteling", "Back office / stock room", "Sicurezza"]
V3_WEIGHTS = [10, 10, 5, 10, 20, 10, 15, 10, 5, 5]

REPORTS = []

REPORTS.append(dict(
    file="2026-09-24_ROM01_visita_RGalli.docx", template="v3", lang="it",
    title="STORE VISIT CHECKLIST v3", store="ROM01 – Roma Via Condotti", date="24/09/2026", visitor="Roberto Galli (Area Manager)",
    attendees="Alessandra De Santis (SM), Fabio Cardarelli (ASM), 3 SA in turno",
    kpi="MTD vendite vs budget: -22% circa | settimana scorsa -45% | traffico: contapersone da verificare (store dice metà del normale)",
    scores=[1, 2, 4, 4, 3, 5, 4, 3, 4, 2],
    notes=[
        "Esterno / vetrine: dal 14/09 cantiere del Comune sul marciapiede + ponteggio sulla facciata del palazzo. La recinzione copre "
        "praticamente le due vetrine laterali, quella centrale si vede solo da vicino. Da via Condotti chi arriva da piazza di Spagna non vede il negozio.",
        "Ingresso: passaggio pedonale di circa 1 m tra le transenne, con i passeggini non si passa. Insegna coperta dai teli.",
        "Cartello del cantiere: 'fine lavori prevista 06/11/2026'. Il capocantiere a voce dice che forse finiscono prima.",
        "Traffico: a mio avviso calo intorno al -30% (oggi pomeriggio ho contato io 40 ingressi in un'ora). Il team parla di -50%, da confrontare con il contapersone.",
        "Interno ok, ordinato, VM della parete uomo da sistemare (Nova verde oliva in prima posizione, non ha senso).",
        "Stock: Aurea nera ancora presente in tutte le taglie (13-14 pz), Vlogo Cardigan ok. Il team chiede meno arrivi finché c'è il cantiere, il magazzino è pieno.",
        "Team motivato ma demoralizzato, molte ore 'vuote'. Proposto di usarle per clienteling telefonico.",
    ],
    actions=[
        ("Richiesta a facility di cavalletto/totem con logo all'angolo con via Bocca di Leone + permesso Comune", "R. Galli", "30/09"),
        ("Vetrofanie / stampa sulla recinzione del cantiere (verificare con VM e con il condominio)", "S. Marchetti (VM)", "09/10"),
        ("Campagna chiamate clienti top 150 con invito in boutique", "A. De Santis", "02/10"),
        ("Valutare riduzione allocazione ROM01 fino a fine lavori", "L. Ferrari", "n/a"),
        ("Verificare dato contapersone settembre", "F. Cardarelli", "25/09"),
    ],
    total_label="Punteggio pesato"))

REPORTS.append(dict(
    file="2026-10-02_MAD01_visita_RGalli.docx", template="v3", lang="it",
    title="STORE VISIT CHECKLIST v3", store="MAD01 – Madrid Serrano", date="02/10/2026", visitor="Roberto Galli",
    attendees="Lucía Fernández Ortega (SM), Javier Molina (ASM)",
    kpi="Settembre chiuso a -14% vs budget (dato store) | conversione: NON disponibile, contapersone a zero da ieri",
    scores=[4, 4, 5, 3, 2, 4, 4, 4, 3, 4],
    notes=[
        "Problema principale: Nova. Nelle due ultime consegne (26/09 e ieri 01/10) è arrivata Nova blu navy al posto della nera. "
        "In negozio adesso circa 20 Nova blu e 3 nere (taglie 1, 2, 5). Clienti spagnoli chiedono quasi solo la nera.",
        "Ticket aperto con CSG per l'errore di picking. Lucía ha mandato foto delle etichette. Promesso reso + sostituzione 'entro la settimana prossima'.",
        "Contapersone: da 01/10 segna 0. Ticket IT INC0049817. Quindi per questa settimana la conversione nel report KPI è da ignorare.",
        "Amalia cioccolato: richieste costanti, mancano la 1 e la 2. Il team propone la nera, funziona poco.",
        "VEL: 2 resi per zip nell'ultima settimana. Il team non sapeva che codice usare, hanno messo QUALITY.",
        "Vetrine ok, conformi al pack W2. Pulizia ottima.",
    ],
    actions=[
        ("Sollecito CSG per sostituzione Nova nera (taglie 1-5) e ritiro navy in eccesso", "R. Galli / L. Ferrari", "07/10"),
        ("Ticket contapersone: escalation al fornitore", "J. Molina", "05/10"),
        ("Usare codice reso corretto per difetti", "L. Fernández", "subito"),
    ],
    total_label="Punteggio pesato"))

REPORTS.append(dict(
    file="2026-10-06_PAR02_visite_IMoreau.docx", template="v3", lang="fr",
    title="VISITE BOUTIQUE – GRILLE v3", store="PAR02 – Galeries Lafayette Haussmann", date="06/10/2026", visitor="Isabelle Moreau (Area Manager France & Genève)",
    attendees="Sophie Marchand (SM), Karim Benali (ASM), Mei Lin (renfort mandarin GL)",
    kpi="Semaine dernière : +28 % vs budget (estimation store), clientèle chinoise ~30 %, coréenne en forte hausse depuis mi-septembre",
    scores=[4, 3, 4, 4, 1, 4, 4, 2, 3, 4],
    notes=[
        "Rupture totale de la Aurea noire depuis environ le 21/09. Le cahier de liste d'attente compte plus de 60 noms (j'ai compté 64), "
        "en grande majorité des clientes coréennes et chinoises de passage à Paris 2 ou 3 jours : liste peu exploitable, la plupart seront reparties à l'arrivée du stock.",
        "Les vendeuses proposent la Aurea beige et marine : quelques essais, très peu de conversion d'après Karim (je pense qu'il faut insister davantage, la beige est très jolie portée).",
        "Amalia marron : tailles 0, 1 et 2 absentes, demandée tous les jours. Reste du 3 et du 4.",
        "Flux très fort Fashion Week + vacances chinoises, file d'attente à l'entrée du corner samedi. Personnel GL partagé, pas assez de cabines.",
        "VEL : 9 retours fermeture éclair depuis le 29/09, rangés dans un carton en réserve, pas encore de procédure officielle reçue. ",
        "Astra : 1 cape vendue, retours clients 'taille petit' sur le blouson oversize.",
    ],
    actions=[
        ("Demander priorité d'allocation Aurea noire PAR01/PAR02 sur l'arrivage du 16/10", "I. Moreau", "07/10"),
        ("Former l'équipe à la vente de la Aurea beige comme alternative", "S. Marchand", "10/10"),
        ("Nettoyer la liste d'attente : garder uniquement clientes résidentes / joignables", "K. Benali", "09/10"),
        ("Retours VEL : attendre consigne qualité", "S. Marchand", "—"),
    ],
    total_label="Score pondéré"))

REPORTS.append(dict(
    file="2026-09-30_LON02_visit_FMcLeod.docx", template="v3", lang="en",
    title="STORE VISIT CHECKLIST v3", store="LON02 Harrods", date="30/09/2026", visitor="Fiona McLeod",
    attendees="Priya Raman, James Whitcombe",
    kpi="wk39 +6% vs bud (Priya's number)",
    scores=[5, 4, 4, 4, 2, 4, 3, None, 3, 4],
    notes=[
        "Aurea black gone since last week. Priya keeps a list, 30-ish names, mostly Korean ladies, many tourists.",
        "Golden Week starting, Chinese groups already today. We are NOT on the Mandarin support list from Matteo's memo?? Harrods lend us one of theirs some hours. Raised it.",
        "Clienteling n/a, CRM tablet broken since Friday.",
        "2 VEL returned for zip this week, odd. Keep an eye.",
        "Selling floor tidy. Harrods VM rules on height of the rails = we lose one rail. Old story.",
    ],
    actions=[("Ask Matteo for Mandarin support LON02 Oct 1-8", "FMcL", "1/10"), ("CRM tablet ticket", "JW", "asap"),
             ("Push black Aurea allocation for Harrods", "FMcL", "ongoing")],
    total_label="Weighted score"))

REPORTS.append(dict(
    file="2026-10-15_MUN01_Filialbesuch_SWagner.docx", template="v3", lang="de", to_pdf=True,
    title="FILIALBESUCH – CHECKLISTE v3", store="MUN01 München Maximilianstraße", date="15.10.2026", visitor="Stefan Wagner (Area Manager DACH)",
    attendees="Katharina Huber (Store Managerin), Florian Brandl (stv.)",
    kpi="Vorwoche -26 % vs Budget, diese Woche bis gestern deutlich drüber (Mo–Mi ca. +40 %), Frequenz hoch",
    scores=[4, 4, 4, 4, 2, 5, 5, 4, 3, 5],
    notes=[
        "Gestern (Mi 14.10.) erster Schnee in München. Seit Montag stürmen die Kunden die Winterjacken.",
        "Ausverkauft bzw. Lücken: NOVA schwarz Gr. 3 und 4, AUREA schwarz komplett (seit Wochen), Vlogo Beanie schwarz und navy, Winter Gloves nur noch 2 Stück. Monteluce grau läuft sehr gut.",
        "Katharina schlägt vor, Ware aus St. Moritz zu holen (schließt am 19.10. für die Zwischensaison) – sehr sinnvoll, Liste ist in Vorbereitung.",
        "ASTRA: steht seit drei Wochen fast unverkauft da. Kunden probieren, finden es zu klein geschnitten und für den Preis nicht überzeugend.",
        "ARTEM: zwei Umtausche wegen Größe, das Team empfiehlt inzwischen eine Nummer kleiner.",
        "Team sehr gut, trotz Ansturm ruhig. Lob an Florian für die Kassenorganisation.",
    ],
    actions=[("Umlagerung STM01 → MUN01 (Heavy Down, Mützen, Handschuhe)", "S. Wagner / L. Ferrari", "19.10."),
             ("Nachbestellung Beanies/Gloves beim Replenishment", "F. Brandl", "16.10."),
             ("ASTRA: Rücksendung an DC prüfen", "Merchandising", "offen")],
    total_label="Gewichteter Score"))

# ---------- VM checklist (English, reportlab PDF) ----------
VM_MIL01 = dict(
    file="2026-10-01_MIL01_VM_check_SMarchetti.pdf", store="MIL01 Milano Montenapoleone", date="01 Oct 2026",
    visitor="Sofia Marchetti (VM EMEA) with Giulia Ferrandi (SM)",
    rows=[
        ("Window 1 – FW26 campaign", "OK", "W1-01", "Lights: 2 spots off on the left, ticket to facility"),
        ("Window 2 – IRIDIA", "OK", "W2-01", "Off-white and black only. Pink on the mannequin was taken off the window (only 1 piece in store, sold?)"),
        ("Window 3 – ASTRA", "OK", "W3-01", ""),
        ("Women wall – icons", "KO", "WW-03", "AUREA black slot empty, filled with beige + navy. Team says black gone since ~19/09"),
        ("Women table – newness", "OK", "WT-01", "Amalia brown: only sizes 3 and 4 on the rail"),
        ("Men wall – icons", "OK", "MW-01", "Nova black depth ok"),
        ("Men knit table", "OK", "MK-02", "Vlogo Cardigan stacks full, good"),
        ("ASTRA island", "OK", "PI-01", "Great visibility, low conversion (2 pieces sold since 24/09)"),
        ("Cash desk accessories", "OK", "CD-01", ""),
        ("Fitting rooms", "KO", "FR-02", "Queue at 15:00 – Chinese tour group, 2 Mandarin temps on the floor"),
        ("Back of house", "NA", "-", "VEL returns box with 5-6 vests (zipper) sitting next to the steamer, to be labelled"),
    ],
    comment="Compliance 82% (9/11 OK). Store very busy because of Golden Week, most of the visit done standing next to the "
            "women wall. Strong request from the team for black Aurea (Korean clients ask every hour). Suggest to keep the beige "
            "on the wall but not to fill the black slot with navy, it looks like we are hiding the problem.")

# ---------- Japanese 店舗巡回レポート ----------
JP_TYO01 = dict(
    file="2026-10-14_TYO01_店舗巡回レポート_鈴木.docx", to_pdf=True,
    head=[("店舗", "銀座店（TYO01）"), ("巡回日", "2026年10月14日（水）13:00〜17:30"), ("巡回者", "鈴木 拓也（エリアマネージャー）"),
          ("対応者", "佐藤 美咲 店長、田中 健一 副店長")],
    checks=[("ウィンドウ／VM", "○", "秋冬キャンペーン通り。IRIDIAのピンクのボディは現在ブラックに変更済み（在庫なしのため）"),
            ("店内清掃・整理整頓", "◎", ""),
            ("商品在庫（ダウン主力）", "△", "価格改定の案内以降、NOVA・AUREAの駆け込み購入あり。AUREAブラックは残り1着（サイズ4）で実質欠品"),
            ("新作（IRIDIA/AMALIA/ARTEM）", "×", "IRIDIAパウダーピンク 10/4より在庫ゼロ、お問い合わせ多数。ウェイティング40名以上。入荷予定は16日と本社より連絡"),
            ("接客・身だしなみ", "◎", ""),
            ("顧客管理（LINE・電話）", "○", "価格改定のご案内は10/9より開始。VIC約120名中、連絡済み約80名"),
            ("返品・修理", "△", "VELのファスナー不具合の返品が9月末から続いている。本社通達（10/5）以降は手順通り"),
            ("バックヤード", "○", "")],
    comment="10月第1週は気温が高く（28℃前後）、ダウンはほとんど動かなかったが、先週末から気温が下がり、さらに11月の価格改定の案内で"
            "NOVA・AUREAを中心に購入が増えている。中国のお客様は国慶節明けで減少。\n"
            "IRIDIAピンクについてはSNSの影響で問い合わせが非常に多いが、一時的なものと見ている。入荷分は既存のウェイティングで消化見込み。\n"
            "※AUREAブラックは銀座は実質欠品、表参道も今週末で欠品の可能性あり。MDへ追加の確認を依頼。",
    actions=[("AUREAブラック 追加配分の確認", "鈴木 → 山口（MD）", "10/16"), ("IRIDIAピンク入荷時のウェイティング順の連絡", "田中", "入荷日"),
             ("価格改定 残りVICへの連絡完了", "佐藤", "10/20")])

# ---------- Korean 매장 방문 보고서 ----------
KR_SEL01 = dict(
    file="2026-10-16_SEL01_매장방문보고서_윤성호.docx",
    head=[("매장", "청담 플래그십 (SEL01)"), ("방문일", "2026.10.16 (금) 14:00~18:00"), ("방문자", "윤성호 AM"), ("면담", "김지현 점장, 박민수 부점장")],
    score_rows=[("외관/윈도우", 18, 20), ("매장 VM", 16, 20), ("재고/상품 운영", 9, 20), ("판매/서비스", 17, 20), ("고객관리(CRM)", 15, 20)],
    body=[
        "1. 경쟁사 팝업: 10/15(목)부터 매장 맞은편에 캐나다 아우터 브랜드 팝업 오픈. 방문 시점 대기줄 약 70~80명, 사은품(토트백) 증정. "
        "저희 매장 앞 유동인구는 많아졌으나 입점객은 체감상 감소. 김지현 점장 의견으로는 20대 고객이 확실히 줄었다고 함.",
        "2. Iridia 인디핑크: 10/2 이후 완판. 진열대에는 디스플레이용 1장(오염 있어 판매 불가)만 남아 있음. 대기 고객 리스트 90명 이상. "
        "10/13 입고분(세관 지연, KC 인증서 누락 건)에는 핑크가 포함되지 않았음. 핑크 추가 입고 일정 미확정, 본사 회신 필요.",
        "3. Aurea 블랙: 10/3경 소진. 하루 평균 3~5명 문의.",
        "4. VEL 지퍼 불량 반품 9/28 이후 누적 약 15건. 매장 공지 늦게 받음(10/5).",
        "5. 매장 컨디션 양호, 직원 사기는 보통. 핑크 문의 응대로 피로도 높음.",
    ],
    actions=[("인디핑크 추가 물량 및 입고일 확인 (오지은 MD)", "윤성호", "10/19"), ("경쟁사 팝업 기간 VIC 프라이빗 초대 행사 검토", "김지현", "10/23"),
             ("디스플레이용 핑크 1장 수선/폐기 여부 결정", "박민수", "10/20")])

# ---------- Chinese 门店巡店报告 ----------
CN_SHA01 = dict(
    file="2026-10-09_SHA01_巡店报告_赵磊.docx",
    head=[("门店", "上海恒隆广场旗舰店 SHA01"), ("巡店日期", "2026年10月9日（周五）"), ("巡店人", "赵磊（区域经理）"), ("陪同", "王静（店长）、陈浩（副店长）")],
    items=[("橱窗及陈列", 9, "ASTRA橱窗效果很好，很多客人拍照"), ("商品及库存", 6, "ASTRA CAPE 白色 M/L 断码；IRIDIA粉色已售罄（仅剩1件样衣）"),
           ("销售服务", 9, ""), ("客户关系 CRM", 8, "国庆期间新增会员约160人，外地客为主"), ("后仓管理", 7, "VEL退货堆在后仓，等待质检通知"),
           ("人员排班", 8, "国庆连班，员工较累，下周安排调休")],
    summary="国庆黄金周期间（10/1-10/7）客流明显提升，外地游客多，试穿多成交率一般。ASTRA系列表现突出，CAPE白色基本卖空，"
            "客人愿意等货，建议总部考虑追加。IRIDIA粉色受明星同款影响，10月3日左右售罄，目前登记等货客人30余位。"
            "VEL拉链问题9月底开始出现退货，上周一共约15件，10月5日才收到总部通知，门店之前按“质量问题”录入，需要更正。"
            "ARTEM有客人反映偏大，建议小一码。",
    actions=[("ASTRA CAPE 追单申请", "赵磊/孙怡雯", "10/12"), ("VEL退货原因代码更正为DEF", "陈浩", "10/10"),
             ("粉色IRIDIA等货名单整理，到货优先通知VIC", "王静", "持续")])

# ---------- Americas store walk ----------
US_NYC02 = dict(
    file="2026-10-08_NYC02_Store_Walk_LMitchell.docx", to_pdf=True,
    head=[("Store", "NYC02 – SoHo"), ("Date", "Thursday 10/8/2026"), ("Visited by", "Lauren Mitchell, Area Manager"), ("Met with", "Tyler Brooks (SM), Ana Gutierrez (ASM)")],
    grid=[("Exterior & windows", "Meets"), ("Floor standards", "Meets"), ("Product availability", "Below"), ("Clienteling", "Meets"),
          ("Operations / POS", "Below"), ("People", "Exceeds")],
    text=[
        "POS: registers went down Tuesday 10/6 from about 2:10pm to 5:40pm. Team kept selling on manual slips and keyed everything in "
        "Wednesday morning, so Tuesday shows low and Wednesday inflated in the flash report. Tyler estimates 60% of Tuesday's tickets "
        "moved to Wednesday. IT root cause: network switch, replaced.",
        "Campaign: the team says the bus shelter ads on Broadway brought some new faces, traffic feels a bit up, nothing dramatic.",
        "Product: IRIDIA black and off-white getting asked for since the weekend (the K-pop thing), we have a few. VEL zipper returns, "
        "8 last week. ASTRA: 1 cape sold since launch, clients try the oversized and say it runs small, price is the bigger issue.",
        "People: Ana did a great job handling the outage, clients were very understanding.",
    ],
    actions=[("Confirm with Finance that 10/6 sales were re-dated to 10/7 (flag for comp reporting)", "LM", "10/9"),
             ("VEL returns: follow QA-26-017", "TB", "ongoing"), ("ASTRA: ask Nicole Park about transfer out to Asia", "LM", "10/15")])

# ---------- SYD01 (short, EN) ----------
AU_SYD01 = dict(
    file="2026-09-29_SYD01_visit_DLim.docx",
    head=[("Store", "Sydney Castlereagh St (SYD01)"), ("Date", "29 Sep 2026"), ("Visitor", "Daniel Lim"), ("With", "Chloe Mitchell, Arjun Patel")],
    grid=[("Windows", "4/5"), ("Floor", "4/5"), ("Stock mix", "2/5"), ("Service", "5/5"), ("Back of house", "3/5")],
    text=[
        "Weather 22-25 deg, full spring. Store is full of heavy down from the FW buy and the replenishment keeps sending more Nova/Aurea/Liviana. "
        "Stockroom is packed, we counted 140+ down jackets.",
        "Clients walk in asking for polos, logo tees, caps, light jackets (Mario style), we are out of most tees in M and L.",
        "Chloe says the weekly forecast email from the planning tool shows down jackets as the top expected sellers again. It's spring here lah.",
        "Proposal: stop heavy replenishment to SYD until April, send some heavy stock back to TKO for North Asia, ask for SS carry-over jersey.",
        "VEL: first zip return yesterday.",
    ],
    actions=[("Raise forecast/seasonality issue with Priya Nair (merch) again", "DL", "2/10"), ("RTV heavy down list", "AP", "6/10")])

# ---------- HKG01 (reportlab PDF, EN) ----------
HK_HKG01 = dict(
    file="2026-09-22_HKG01_visit_report_VLau.pdf",
    lines=[
        ("STORE VISIT REPORT – HKG01 Canton Road", "t"),
        ("Date: 22/09/2026   Visitor: Vivian Lau   Store team: Karen Chan (SM), Ming Wong (ASM)", "s"),
        ("1. Typhoon follow-up", "h"),
        ("Store closed Thu 17/9 (T8). Re-opened Fri 18/9 at 15:00 after signal lowered. Small water ingress at the service door, "
         "2 cartons of accessories wet (beanies, caps), written off: list sent to finance. No damage on the floor.", "p"),
        ("2. Business", "h"),
        ("Last week clearly below budget because of the closure (lost ~1.5 days). Mainland visitors coming back this week, "
         "Canton Road busy again on Sunday.", "p"),
        ("3. ASTRA launch 24/9", "h"),
        ("Island set up, team briefed, 6 clients pre-booked appointments. Stock: CAPE black 6 / white 4, OVERSIZED 8, BALACLAVA 12.", "p"),
        ("4. Golden Week prep", "h"),
        ("Need extra staff 1-7 Oct: 2 part-timers confirmed. Check UnionPay terminal #2 (intermittent).", "p"),
        ("Score: 86/100   (Standards 27/30, Stock 22/30, People 20/20, CRM 17/20)", "b"),
        ("Next visit: after Golden Week.", "s"),
    ])
