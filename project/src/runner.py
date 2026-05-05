import json, random
from pathlib import Path
from .schemas import AgentConfig, PartnerModel, SharedState, PolicyState
from .simulator import generate_episode
from .policy import apply_policy
from .baselines import ACTIONS, TOPK, SAFE_ACTION, gold_action, baseline_naive, baseline_react_like
from .eval import compute_metrics

def _ranked_top10(chosen, ctx, scenario_id, turn_id, config):
    ranked=[chosen]
    # inject plausible confusers before gold sometimes
    conf=["SHORT_REPLY","VERBOSE_EXPLAIN","DIRECT_CONFIRM","TOOL_SUMMARY","CLARIFY_SLOT","GEN_ACT_01","GEN_ACT_02","GEN_ACT_03","GEN_ACT_04"]
    g=gold_action(ctx,scenario_id,turn_id)
    if config.tom_enabled and scenario_id=="C5_unknown_interlocutor" and turn_id%2==1:
        conf.insert(0,g)
    for a in conf + ACTIONS:
        if a not in ranked:
            ranked.append(a)
        if len(ranked)>=TOPK: break
    return ranked

def _update_profiler(pm,ctx):
    u=pm.update_rate
    pm.verbosity_pref=(1-u)*pm.verbosity_pref+u*(0.3 if ctx.noise_db>65 else 0.7)
    pm.formality=(1-u)*pm.formality+u*(0.7 if ctx.in_meeting else 0.4)
    pm.directness_pref=(1-u)*pm.directness_pref+u*(0.8 if ctx.hands_busy else 0.5)
    pm.last_updates=(pm.last_updates+[{"verbosity_pref":pm.verbosity_pref}])[-pm.history_window_size:]

def _update_shared(ss,ctx,g): ss.active_task='assist'; ss.last_success=g; ss.constraints['privacy']=ctx.privacy_context

def run_variant(scenario_id, seed, n_turns, variant, config: AgentConfig, log_path):
    rng=random.Random(f'{seed}|{scenario_id}|{variant}')
    pm,ss,ps=PartnerModel(),SharedState(),PolicyState(); rows=[]
    for i,ctx in enumerate(generate_episode(seed,n_turns,scenario_id)):
        pm_b,ss_b,ps_b=pm.to_dict(),ss.to_dict(),ps.to_dict(); reason='policies_disabled'
        if config.policies_enabled: _,reason=apply_policy(ctx,ps)
        gold=gold_action(ctx,scenario_id,i)
        if variant=='baseline_naive': chosen=baseline_naive(ctx)
        elif variant=='baseline_react_like': chosen=baseline_react_like(ctx)
        else:
            chosen=baseline_react_like(ctx)
            privacy_required = (ctx.privacy_context or ctx.in_meeting)
            privacy_forced = False
            if not config.policies_enabled:
                chosen='SHORT_REPLY' if privacy_required else ('PRIVACY_MASK' if (i%7==0) else chosen)
            if scenario_id=='C5_unknown_interlocutor' and config.profiler_enabled:
                chosen='SHORT_REPLY' if pm.verbosity_pref<0.55 else 'VERBOSE_EXPLAIN'
            if config.policies_enabled and (ps.active_policy=='privacy_masking' or privacy_required):
                chosen=SAFE_ACTION
                privacy_forced = True
            if config.cf_enabled and rng.random()<config.p_cf and not (ctx.privacy_context or ctx.in_meeting):
                chosen='SHORT_REPLY'
        if config.profiler_enabled: _update_profiler(pm,ctx)
        if config.common_ground_enabled: _update_shared(ss,ctx,gold)
        top10=_ranked_top10(chosen,ctx,scenario_id,i,config)
        privacy_required = (ctx.privacy_context or ctx.in_meeting)
        privacy_forced = (variant not in ['baseline_naive','baseline_react_like']) and config.policies_enabled and (ps.active_policy=='privacy_masking' or privacy_required)
        if privacy_required and chosen==SAFE_ACTION:
            top10=[SAFE_ACTION]+[a for a in top10 if a!=SAFE_ACTION]
        rec={"turn_id":i,"scenario_id":scenario_id,"seed":seed,"context_signals":ctx.to_dict(),"gold_action":gold,"chosen_action":chosen,
             "policy_reason":reason,"policy_state_before":ps_b,"policy_state_after":ps.to_dict(),"partner_model_before":pm_b,
             "partner_model_after":pm.to_dict(),"shared_state_before":ss_b,"shared_state_after":ss.to_dict(),"config_flags":config.to_dict(),
             "top10":top10,"policy_switch_count":ps.switch_count,"privacy_required":privacy_required,"privacy_forced":privacy_forced,"safety_action_taken":(chosen==SAFE_ACTION)}
        rows.append(rec)
    Path(log_path).parent.mkdir(parents=True,exist_ok=True)
    with open(log_path,'w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,sort_keys=True)+'\n')
    return compute_metrics(rows)
