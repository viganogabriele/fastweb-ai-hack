"""Authoring aid: per-day KPI figures as staff would quote them (net, gross incl. VAT, ATV, UPT, CR)."""
import json, sys
VAT = {"SHA01": 1.13, "BJS01": 1.13, "CDU01": 1.13, "HKG01": 1.0, "TPE01": 1.05}
st = sys.argv[1]
d = json.load(open(f"generated/ground_truth/writer_inputs/email_context/{st}.json"))
for x in d["days"]:
    if not x["open"]:
        print(x["date"], "CLOSED"); continue
    n, b, r, u, v = x["net_sales_lc"], x["budget_lc"], x["receipts"], x["units"], x["visitors"]
    g = n * VAT[st]
    print(f"{x['date']} {x['weekday'][:3]} net={n/1e4:.2f}万 gross={g/1e4:.2f}万 bud={b/1e4:.2f}万 budG={b*VAT[st]/1e4:.2f}万 ach={n/b*100:.0f}% "
          f"vis={v} rec={r} CR={r/v*100:.1f}% ATV={n/r:,.0f} ATVg={g/r:,.0f} UPT={u/r:.2f} units={u}")
