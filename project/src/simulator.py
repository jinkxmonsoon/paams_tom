import random
from .schemas import ContextSignals

def _clamp(x, lo=0.0, hi=1.0): return max(lo, min(hi, x))
def _budgets(net): return (1200,1200) if net=='good' else (500,700) if net=='poor' else (120,300)

def generate_episode(seed:int,n_turns:int,scenario_id:str):
    r=random.Random(f'{seed}|{scenario_id}|{n_turns}')
    out=[]
    for t in range(n_turns):
        if scenario_id=='C1_silent_desk': noise,net,privacy,meeting,hands=28+r.uniform(-4,4),'good',False,False,False
        elif scenario_id=='C2_walk_outdoor':
            noise=50+(24 if t%5 in (2,3) else 0)+r.uniform(-8,8); net=['good','poor','off'][r.randint(0,2)]; privacy=False; meeting=False; hands=(t%3==0)
        elif scenario_id=='C3_meeting_privacy':
            noise=46+r.uniform(-6,6); net='poor' if (t+seed)%4==0 else 'good'; privacy=True; meeting=True; hands=False
        elif scenario_id=='C5_unknown_interlocutor':
            noise=40+r.uniform(-5,5); net='good'; privacy=False; meeting=False; hands=False
        else: raise ValueError(scenario_id)
        asr=_clamp(1-noise/100+r.uniform(-0.03,0.03)); tok,lat=_budgets(net)
        out.append(ContextSignals(round(noise,2),round(asr,3),net,privacy,hands,meeting,tok,lat))
    return out
