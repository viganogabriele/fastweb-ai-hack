import json,glob,collections,datetime as dt,re
out=[]
for f in sorted(glob.glob('generated/ground_truth/writer_inputs/email_context/*.json')):
    d=json.load(open(f)); s=d['store']['store_id']
    out.append(f"=== {s} {d['store']['currency']}")
    weeks=collections.OrderedDict()
    for day in d['days']:
        date=dt.date.fromisoformat(day['date']); w=date.isocalendar()[1]
        if w<36: continue
        W=weeks.setdefault(w,dict(sales=0,bud=0,days=0,unmet=collections.Counter(),defret=0,sizeret=0,dly=[],ev=set(),mix=collections.Counter(),nd=0))
        if day['open']>0: W['days']+=1
        W['sales']+=day.get('net_sales_lc') or 0; W['bud']+=day.get('budget_lc') or 0
        for u in day.get('unmet_requests',[]):
            m=re.match(r'(.*) size (\S+) x(\d+)$',u)
            if m: W['unmet'][m.group(1)]+=int(m.group(3))
        for r in day.get('returns',[]):
            if 'DEF' in r: W['defret']+=1
            if r.startswith('ARTEM') and 'SIZE' in r: W['sizeret']+=1
        for k,v in (day.get('customer_mix') or {}).items(): W['mix'][k]+=v
        W['nd']+=1
        for dl in day.get('deliveries_received',[]):
            if dl['delay_days'] or dl['wrong_items']: W['dly'].append(f"{day['date'][5:]}:{dl['delay_days']}d{'W' if dl['wrong_items'] else ''}")
        for e in day.get('active_events',[]): W['ev'].add(e.split(':')[0])
    for w,W in weeks.items():
        vs=(W['sales']/W['bud']-1)*100 if W['bud'] else 0
        mix=",".join(f"{k}{v/W['nd']:.0%}" for k,v in W['mix'].most_common(3))
        un=", ".join(f"{k} {v}" for k,v in W['unmet'].most_common(4) if v>=2)
        out.append(f" W{w} d={W['days']} s={W['sales']/1000:.0f}k vs={vs:+.0f}% {mix} ev={','.join(sorted(W['ev']))} DEF={W['defret']} ARNsz={W['sizeret']} {'dly='+' '.join(W['dly']) if W['dly'] else ''}")
        if un: out.append("   unmet: "+un)
open('/tmp/ic/digest2.txt','w').write("\n".join(out))
