"""Compact per-day digest of the email context for a store (authoring aid). Prints events only when they change."""
import json, sys
st = sys.argv[1]
d = json.load(open(f"generated/ground_truth/writer_inputs/email_context/{st}.json"))
prev = set()
for x in d["days"]:
    ev = set(e.split(":")[0] for e in x.get("active_events", []))
    evs = ""
    if ev != prev:
        evs = f" EV+{sorted(ev-prev)} -{sorted(prev-ev)}"
        prev = ev
    if not x["open"]:
        print(x["date"], x["weekday"][:3], "CLOSED", evs); continue
    mix = ",".join(f"{k}{int(v*100)}" for k, v in x["customer_mix"].items())
    dl = ";".join(f"{s['units']}u d{s['delay_days']}{' WRONG' if s['wrong_items'] else ''}{(' '+str(s.get('wrong_detail'))) if s.get('wrong_detail') else ''}" for s in x["deliveries_received"])
    print(f"{x['date'][5:]} {x['weekday'][:3]} o={x['open']} {x['net_sales_lc']/1000:.1f}k b={x['budget_lc']/1000:.1f}k {x['vs_budget_pct']:+.0f}% u={x['units']} r={x['receipts']} v={x['visitors']} | {mix}{evs}")
    print("  T:", "; ".join(t.replace(' x', '*') for t in x["top_sellers"][:4]))
    if x["unmet_requests"]: print("  U:", "; ".join(u.replace(' size ', ' ') for u in x["unmet_requests"]))
    if x["zero_stock_key_sizes"]: print("  Z:", "; ".join(x["zero_stock_key_sizes"][:7]))
    if x["returns"]: print("  R:", "; ".join(r.replace(' reason=', ':') for r in x["returns"]))
    if dl: print("  D:", dl)
