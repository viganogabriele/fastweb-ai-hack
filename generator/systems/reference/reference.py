"""MDM store-code crosswalk (partial, with gaps) + SKU code formats cheat-sheet."""
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

OUT = C.OUT / "reference"
OUT.mkdir(parents=True, exist_ok=True)
st = C.stores()


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return "store_" + re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


rows = []
for r in st.itertuples():
    rows.append(dict(store_id=r.store_id, store_name=r.store_name, sap_plant_werks=C.SAP_WERKS[r.store_id],
                     tms_shipto_kunnr=C.TMS_SHIPTO[r.store_id], crm_store_code=C.CRM_CODE[r.store_id],
                     zendesk_store_tag=slug(r.store_name), supplying_dc=C.REGION_DC[r.region],
                     aliases="; ".join(C.STORE_ALIASES[r.store_id]), last_update="2026-06-30"))
df = pd.DataFrame(rows)
# MDM gaps / stale values (documented in the answer key)
df.loc[df.store_id.isin(["CRT01", "SYD01"]), "crm_store_code"] = ""
df.loc[df.store_id == "MAD01", ["tms_shipto_kunnr", "last_update"]] = ["0000071599", "2024-02-12"]
df.loc[df.store_id == "BUS01", "zendesk_store_tag"] = "store_busan_centum"
df.to_csv(OUT / "store_code_crosswalk_MDM.csv", index=False)
(OUT / "id_formats_cheatsheet.md").write_text("""# ID formats across systems (IT architecture wiki, last edited 2025-11)

| Object | Internal / BI | SAP ERP/EWM (IT10, US20) | 3PL TKO (HK30) | TMS / carriers | Salesforce CRM | E-commerce | Zendesk |
|---|---|---|---|---|---|---|---|
| Store | MIL01 | plant WERKS 1001 | consignee name | ship-to KUNNR 0000071001 | Store__c IT01 | n/a | dropdown store_milano_montenapoleone |
| DC | DC-IT-CSG | plant IT10 | TKO-3 (client MONC01) | origin plant | n/a | inventory location WEB-EU (IT10/W100) | n/a |
| SKU (style-colour) | J20931A00012-999 | MATNR J20931A00012999 | n/a | n/a | free text | product_id J20931A00012-999 | free text |
| SKU-size | J20931A00012-999-1 | MATNR + J_3ASIZE 1 | Item Code MC31A0001299903 (size index 1-based) + EAN | n/a | free text | variant_sku J20931A00012-999-1 (TU items often without suffix; WeChat channel = EAN) | SKU field, any format |
| Shipment | SHP02600440 | delivery VBELN 0080412440 (XABLN = SHP id) | SO-TKO-xxxxx (client ref = SHP id) | AWB (carrier specific), shipper ref = VBELN or SHP or 'RIF.MITT.' | n/a | n/a | order number MC-EU-26-0xxxxxx |
| Time | local business date | local plant time, dates DD.MM.YYYY (IT) / MM/DD/YYYY (US) | HKT | UTC (BRT feed: local time mislabelled Z) | UTC (+0000) | UTC (search/notify), day in Europe/Rome (sales report) | UTC |

Notes: CRM store codes follow CRM go-live order per country (e.g. KR01 = Seoul Hyundai Apgujeong, KR02 = Seoul Cheongdam).
""", encoding="utf-8")
print("reference done")
