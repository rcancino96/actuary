import pandas as pd, numpy as np
from pathlib import Path; D=str(Path(__file__).resolve().parents[2]/'data/raw/public')+'/'
r=lambda f: pd.read_parquet(D+f+'.parquet')
c=r('claims'); c['ld']=pd.to_datetime(c.loss_date)
dups=c.drop(columns=['claim_id']).duplicated(keep=False)
print('dup sample'); print(c[dups].sort_values(['policy_id','loss_date']).head(6).to_string())
c=c[~c.drop(columns=['claim_id']).duplicated()]
for L,pre in [('motor','M'),('buildings','B'),('contents','C')]:
    p=r('policies_'+L)[['row_id','policy_id','period_start','period_end']]
    p['ps']=pd.to_datetime(p.period_start); p['pe']=pd.to_datetime(p.period_end)
    # overlaps
    s=p.sort_values(['policy_id','ps']); prev=s.groupby('policy_id').pe.shift()
    print(L,'overlapping rows',(s.ps<=prev).sum(), 'gaps', ((s.ps-prev).dt.days>1).sum())
    cc=c[c.line==L]
    m=cc.merge(p,on='policy_id',how='left')
    m['in']=(m.ld>=m.ps)&(m.ld<=m.pe)
    hits=m[m['in']].groupby('claim_id').size()
    nomatch=cc[~cc.claim_id.isin(hits.index)]
    print(' claims',len(cc),'matched once',(hits==1).sum(),'multi',(hits>1).sum(),'unmatched',len(nomatch),
          'unmatched policy unknown', (~nomatch.policy_id.isin(p.policy_id)).sum(),
          'unmatched by ly', nomatch.ld.dt.year.value_counts().to_dict(), 'status', nomatch.status.value_counts().to_dict())
    # unmatched known policy: how far outside
    um=m[m.claim_id.isin(nomatch.claim_id)]
    if len(um):
        um['dist']=np.minimum((um.ld-um.pe).dt.days.abs(),(um.ps-um.ld).dt.days.abs())
        print('  min dist days', um.groupby('claim_id').dist.min().describe().round(0).to_dict())
