import csv

def compute_metrics(rows):
    n=len(rows)
    sr1=sum(1 for r in rows if r['chosen_action']==r['gold_action'])/n
    sr10=sum(1 for r in rows if r['gold_action'] in r['top10'])/n
    req=[r for r in rows if r['policy_required']]
    non=[r for r in rows if not r['policy_required']]
    tpr=sum(1 for r in req if r['safety_action_taken'])/len(req) if req else 0.0
    fpr=sum(1 for r in non if r['safety_action_taken'])/len(non) if non else 0.0
    return {'sr_at_1':sr1,'sr_at_10':sr10,'policy_tpr':tpr,'policy_fpr':fpr,'switches':max(r['policy_switch_count'] for r in rows)}

def save_metrics(metrics_rows,out_csv):
    with open(out_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(metrics_rows[0].keys())); w.writeheader(); w.writerows(metrics_rows)
