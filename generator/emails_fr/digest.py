"""Print a compact per-day digest of email_context for authoring (helper only)."""
import json, sys
for st in sys.argv[1:]:
    d = json.load(open(f'generated/ground_truth/writer_inputs/email_context/{st}.json'))
    print('=====', st)
    for x in d['days']:
        if not x['open']:
            print(x['date'][5:], x['weekday'][:3], 'CLOSED'); continue
        mix = ' '.join(f"{k}{int(v*100)}" for k, v in x['customer_mix'].items())
        dl = '; '.join(f"{y['units']}u d{y['delay_days']}{' WRONG' if y['wrong_items'] else ''}" for y in x['deliveries_received'])
        print(f"{x['date'][5:]} {x['weekday'][:3]} open={x['open']} sales={x['net_sales_lc']:.0f} bud={x['budget_lc']:.0f} ({x['vs_budget_pct']}) u={x['units']} rc={x['receipts']} vis={x['visitors']} cv={x['conversion']:.3f} | {mix}")
        print('   TOP:', ', '.join(x['top_sellers']))
        if x['unmet_requests']: print('   UNMET:', ', '.join(x['unmet_requests']))
        if x['zero_stock_key_sizes']: print('   ZERO:', ', '.join(x['zero_stock_key_sizes']))
        if x['returns']: print('   RET:', ', '.join(x['returns']))
        if dl: print('   DLV:', dl)
        if x['active_events']: print('   EV:', ' '.join(e.split(':')[0] for e in x['active_events']))
