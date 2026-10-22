"""Compact per-day digest of the email context for a store (authoring aid). Handles zero-sales days."""
import json, sys
st = sys.argv[1]
d = json.load(open(f"generated/ground_truth/writer_inputs/email_context/{st}.json"))
for x in d["days"]:
    if not x["open"]:
        print(x["date"], x["weekday"][:3], "CLOSED", x.get("active_events")); continue
    if "net_sales_lc" not in x:
        print(f"{x['date']} {x['weekday'][:3]} OPEN BUT ZERO SALES (no KPI row; door counter still counted a few visitors)")
    else:
        mix = ",".join(f"{k}{int(v*100)}" for k, v in x["customer_mix"].items())
        print(f"{x['date']} {x['weekday'][:3]} o={x['open']} {x['net_sales_lc']/1000:.1f}k b={x['budget_lc']/1000:.1f}k {x['vs_budget_pct']:+.0f}% u={x['units']} r={x['receipts']} v={x['visitors']} | {mix}")
    dl = ";".join(f"{s['units']}u d{s['delay_days']}{' WRONG' if s['wrong_items'] else ''}{(' '+str(s.get('wrong_detail'))) if s.get('wrong_detail') else ''}" for s in x["deliveries_received"])
    if x["top_sellers"]: print("   TOP:", "; ".join(x["top_sellers"][:4]))
    if x["unmet_requests"]: print("   UNMET:", "; ".join(x["unmet_requests"]))
    if x["zero_stock_key_sizes"]: print("   ZERO:", "; ".join(x["zero_stock_key_sizes"][:6]))
    if x["returns"]: print("   RET:", "; ".join(x["returns"]))
    if dl: print("   DELIV:", dl)
    if x["active_events"]: print("   EV:", [e.split(':')[1].strip() for e in x["active_events"]])
