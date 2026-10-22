"""Tiny mock server for the warehouse / logistics / marketing / planning agents (stdlib http.server only + pandas).

Run from the repo root:
    .venv/bin/python generator/systems/mock_agents/server.py --port 8088
Then e.g.
    curl 'http://localhost:8088/warehouse/.well-known/agent-card.json'
    curl 'http://localhost:8088/warehouse/v1/atp?plant=HK30&material=J20931A00618510'
    curl -X POST localhost:8088/logistics/v1/transfer-requests -d '{"source":"ROM01","dest":"MIL01","sku":"J20931A00012-999","size":"1","qty":2,"requestedAtLocal":"2026-09-22T12:51:00"}'
    curl -X POST localhost:8088/planning/a2a -d '{"jsonrpc":"2.0","id":1,"method":"message/send","params":{"message":{"role":"user","messageId":"m1",
         "parts":[{"kind":"data","data":{"store":"SEL01","sku":"J20931A00618-510","demandMultiplier":6}}],"metadata":{"skill":"propose_replenishment"}}}}'
All answers are computed from the files in generated/sources/ ("today" = 2026-10-22; pass asOf to replay the past).
Set DATA_ROOT to point elsewhere. --strict-auth makes the server require the auth header declared in each agent card.
"""
import argparse
import json
import sys
import traceback
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import handlers as H  # noqa: E402

CARDS = {p.stem.split("-")[0]: p for p in (H.SYS / "agents" / "agent_cards").glob("*.json")}
STRICT = False


def _p(qs, k, default=None):
    v = qs.get(k)
    return v[0] if v else default


def customs_holds(country=None):
    c = pd.read_csv(H.SYS / "logistics" / "customs_declarations.csv", dtype=str)
    c = c[c.status != "CLEARED"]
    if country:
        c = c[c.dest_country == country]
    return {"holds": c.fillna("").to_dict("records")}


def social_alerts(date_from=None, topic=None):
    s = pd.read_csv(H.SYS / "marketing" / "social_listening_alerts_export.csv", dtype=str)
    if date_from:
        s = s[s.triggered_at_utc >= date_from]
    if topic:
        s = s[s.topic_query.str.contains(topic, case=False, na=False)]
    return {"alerts": s.fillna("").to_dict("records")}


def quality_stock(prefix):
    f = H.SYS / "warehouse" / "api_samples" / "wmsgw_GET_quality_stock_TIB_20261022.json"
    d = json.loads(f.read_text(encoding="utf-8"))
    d.pop("_request", None)
    if prefix and not "J10911A00305".startswith(prefix[:12]):
        return {"positions": [], "note": "no quality stock"}
    return d


def otb(region, category=None):
    df = pd.read_excel(H.SYS / "planning" / "FW26_merch_plan_OTB_v5.xlsx", sheet_name=region, header=3)
    df.columns = ["Categoria", "Misura"] + list(df.columns[2:])
    df["Categoria"] = df["Categoria"].ffill()
    if category:
        df = df[df.Categoria.astype(str).str.contains(category, case=False)]
    return {"region": region, "unit": "EUR k", "rows": df.fillna("").to_dict("records")}


def stock(plant, material, date=None):
    mat = H.norm_material(material)
    date = str(H._d(date) if date else (H.TODAY - pd.Timedelta(days=1)))[:10]
    if plant == "HK30":
        f = H.SYS / "warehouse" / "pcl_tko_inventory" / f"TKO_INV_SNAPSHOT_{date.replace('-', '')}.csv"
        if not f.exists():
            return {"error": "NO_FILE", "message": f"3PL snapshot for {date} not available"}
        df = pd.read_csv(f, dtype=str, encoding="utf-8-sig")
        df = df[df["Item Code"].str.startswith("MC" + mat[4:12] + mat[12:])]
        return {"plant": plant, "material": mat, "date": date, "source": "PCL 3PL feed", "positions": df.fillna("").to_dict("records")}
    ym = date[:7].replace("-", "")
    f = H.SYS / "warehouse" / f"sap_stock_{plant}" / f"MARD_AFS_{plant}_{ym}.csv"
    if plant == "IT10":
        df = pd.read_csv(f, sep=";", dtype=str)
        key = f"{date[8:10]}.{date[5:7]}.{date[:4]}"
    else:
        df = pd.read_csv(f, dtype=str, encoding="cp1252")
        key = f"{date[5:7]}/{date[8:10]}/{date[:4]}"
    df = df[(df.STICHTAG == key) & (df.MATNR == mat)]
    if df.empty:
        return {"plant": plant, "material": mat, "date": date, "positions": [], "note": "no rows (no extraction on Sundays at IT10)"}
    return {"plant": plant, "material": mat, "date": date, "positions": df.fillna("").to_dict("records")}


# ------------------------------------------------------------------ skill dispatch (A2A)
def dispatch(agent, skill, d):
    if agent == "warehouse":
        if skill == "get_atp":
            return H.wh_atp(d.get("plant", "ALL"), d["material"], d.get("asOf"), d.get("size"))
        if skill == "get_stock":
            return stock(d["plant"], d["material"], d.get("date"))
        if skill == "get_inbound_po":
            return H.wh_po(d["purchaseOrder"], d.get("asOf"))
        if skill == "get_quality_stock":
            return quality_stock(d.get("materialPrefix", ""))
        if skill == "create_reservation":
            return H.wh_reservation(d["plant"], d["material"], d["size"], int(d["qty"]), d.get("purpose", "PR_SAMPLE"), d.get("asOf"))
    if agent == "logistics":
        if skill == "track_shipment":
            return H.lg_tracking(d["ref"], d.get("asOfUtc"))
        if skill == "get_lane":
            return H.lg_lane(d["origin"], d["dest"])
        if skill == "request_transfer":
            return H.lg_transfer_request(d["source"], d["dest"], d["sku"], d["size"], int(d["qty"]), d["requestedAtLocal"], d.get("requiredBy"))
        if skill == "customs_status":
            return customs_holds(d.get("country"))
    if agent == "marketing":
        if skill == "get_campaign_calendar":
            return H.mk_calendar(d.get("market"), d.get("from"), d.get("to"))
        if skill == "get_waitlist":
            return H.mk_waitlist(d.get("store"), d.get("item"), d.get("status"))
        if skill == "draft_clienteling_message":
            return H.mk_message_draft(d["clientName"], d["storeName"], d["language"], d["item"], d["size"], bool(d["available"]), d.get("eta"))
        if skill == "get_social_alerts":
            return social_alerts(d.get("from"), d.get("topic"))
    if agent == "planning":
        if skill == "get_replenishment_parameters":
            return H.pl_params(d["store"])
        if skill == "propose_replenishment":
            return H.pl_replenishment_proposal(d["store"], d["sku"], d.get("asOf"), float(d.get("demandMultiplier", 1.0)), d.get("sizes"))
        if skill == "get_allocation_plan":
            return H.pl_allocation(d["sku"])
        if skill == "get_otb":
            return otb(d["region"], d.get("category"))
    raise ValueError(f"unknown skill {agent}/{skill}")


REST = {  # (agent, method, path-prefix) -> (skill, path-param name)
    ("warehouse", "GET", "/v1/atp"): ("get_atp", None), ("warehouse", "GET", "/v1/stock"): ("get_stock", None),
    ("warehouse", "GET", "/v1/inbound/purchase-orders/"): ("get_inbound_po", "purchaseOrder"),
    ("warehouse", "GET", "/v1/quality-stock"): ("get_quality_stock", None), ("warehouse", "POST", "/v1/reservations"): ("create_reservation", None),
    ("logistics", "GET", "/v1/shipments/"): ("track_shipment", "ref"), ("logistics", "GET", "/v1/lanes"): ("get_lane", None),
    ("logistics", "POST", "/v1/transfer-requests"): ("request_transfer", None), ("logistics", "GET", "/v1/customs/holds"): ("customs_status", None),
    ("marketing", "GET", "/v1/campaign-calendar"): ("get_campaign_calendar", None), ("marketing", "GET", "/v1/waitlists"): ("get_waitlist", None),
    ("marketing", "POST", "/v1/clienteling-message-draft"): ("draft_clienteling_message", None),
    ("marketing", "GET", "/v1/social-alerts"): ("get_social_alerts", None),
    ("planning", "GET", "/v1/replenishment-parameters/"): ("get_replenishment_parameters", "store"),
    ("planning", "POST", "/v1/replenishment-proposal"): ("propose_replenishment", None),
    ("planning", "GET", "/v1/allocation-plan"): ("get_allocation_plan", None), ("planning", "GET", "/v1/otb"): ("get_otb", None),
}
AUTH = {"warehouse": "Authorization", "logistics": "X-Api-Key", "marketing": "Authorization", "planning": "Authorization"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _route(self, method):
        u = urlparse(self.path)
        parts = u.path.strip("/").split("/", 1)
        agent, rest = parts[0], "/" + (parts[1] if len(parts) > 1 else "")
        if agent not in CARDS:
            return self._send(404, {"error": "UNKNOWN_AGENT", "agents": sorted(CARDS)})
        if rest == "/.well-known/agent-card.json" and method == "GET":
            return self._send(200, json.loads(CARDS[agent].read_text(encoding="utf-8")))
        if STRICT and not self.headers.get(AUTH[agent]):
            return self._send(401, {"error": "UNAUTHORIZED", "message": f"missing {AUTH[agent]} header"})
        body = {}
        if method == "POST":
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
        try:
            if rest == "/a2a" and method == "POST":
                msg = body.get("params", {}).get("message", {})
                skill = (msg.get("metadata") or {}).get("skill")
                data = next((p["data"] for p in msg.get("parts", []) if p.get("kind") == "data"), {})
                res = dispatch(agent, skill, data)
                ctx = msg.get("contextId") or str(uuid.uuid4())
                return self._send(200, {"jsonrpc": "2.0", "id": body.get("id"), "result": {
                    "kind": "task", "id": str(uuid.uuid4()), "contextId": ctx, "status": {"state": "completed"},
                    "artifacts": [{"artifactId": str(uuid.uuid4()), "name": f"{skill}_result", "parts": [{"kind": "data", "data": res}]}]}})
            for (ag, m, prefix), (skill, pname) in REST.items():
                if ag == agent and m == method and rest.startswith(prefix):
                    qs = {k: v[0] for k, v in parse_qs(u.query).items()}
                    data = {**qs, **body}
                    if pname:
                        data[pname] = rest[len(prefix):].split("/")[0]
                    return self._send(200, dispatch(agent, skill, data))
            return self._send(404, {"error": "NOT_FOUND", "path": u.path})
        except (KeyError, ValueError, TypeError) as e:
            return self._send(400, {"error": "BAD_REQUEST", "message": str(e)})
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._send(500, {"error": "INTERNAL", "message": str(e)})

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8088)
    ap.add_argument("--strict-auth", action="store_true")
    a = ap.parse_args()
    STRICT = a.strict_auth
    print(f"mock agents on http://localhost:{a.port}/{{warehouse,logistics,marketing,planning}}  data={H.ROOT}")
    ThreadingHTTPServer(("0.0.0.0", a.port), Handler).serve_forever()
