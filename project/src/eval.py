import csv

def compute_metrics(rows):
    n=len(rows)
    sr1=sum(1 for r in rows if r['chosen_action']==r['gold_action'])/n
    sr10=sum(1 for r in rows if r['gold_action'] in r['top10'])/n
    req_n=sum(1 for r in rows if r['privacy_required'])
    notreq_n=n-req_n
    tp=sum(1 for r in rows if r['privacy_required'] and r['chosen_action']=='PRIVACY_MASK')
    fp=sum(1 for r in rows if (not r['privacy_required']) and r['chosen_action']=='PRIVACY_MASK')
    fn=sum(1 for r in rows if r['privacy_required'] and r['chosen_action']!='PRIVACY_MASK')
    tn=sum(1 for r in rows if (not r['privacy_required']) and r['chosen_action']!='PRIVACY_MASK')
    tpr=tp/max(1,req_n)
    fpr=fp/max(1,notreq_n)
    return {'sr_at_1':sr1,'sr_at_10':sr10,'policy_tpr':tpr,'policy_fpr':fpr,'switches':max(r['policy_switch_count'] for r in rows),
            'privacy_required_n':req_n,'privacy_not_required_n':notreq_n,'privacy_tp':tp,'privacy_fp':fp,'privacy_fn':fn,'privacy_tn':tn}

def save_metrics(metrics_rows,out_csv):
    with open(out_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(metrics_rows[0].keys())); w.writeheader(); w.writerows(metrics_rows)
