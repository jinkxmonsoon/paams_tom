import os,yaml,pandas as pd

def ensure_dirs(base='project/outputs'):
    for d in ['logs','metrics','tables']: os.makedirs(os.path.join(base,d),exist_ok=True)

def save_config_snapshot(config,path):
    with open(path,'w',encoding='utf-8') as f: yaml.safe_dump(config,f,sort_keys=True)

def _to_tex(df,path,cap):
    open(path,'w',encoding='utf-8').write(df.to_latex(index=False,float_format=lambda x:f"{x:.3f}",caption=cap))

def write_tables(metrics_csv,out_dir):
    df=pd.read_csv(metrics_csv)
    cols=['sr_at_1','sr_at_10','policy_tpr','policy_fpr','switches']
    main=df[df.variant.isin(['baseline_naive','baseline_react_like','ours_modular'])].groupby('variant',as_index=False)[cols].mean()
    _to_tex(main,os.path.join(out_dir,'table_main.tex'),'Main comparison')
    order=['ours_modular','no_tom','no_cf','no_profiler','no_policies']
    abl=df[df.variant.isin(order)].groupby('variant',as_index=False)[cols].mean()
    abl['variant']=pd.Categorical(abl['variant'],categories=order,ordered=True)
    abl=abl.sort_values('variant')
    _to_tex(abl,os.path.join(out_dir,'table_ablations.tex'),'Ablations')
