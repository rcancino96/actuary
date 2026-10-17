import pandas as pd, numpy as np
D='/home/claude/hack/data/raw/public/'
pd.set_option('display.width',250)
r=lambda f: pd.read_parquet(D+f+'.parquet')
c=r('claims'); c=c[~c.drop(columns=['claim_id']).duplicated()]; c=c[c.status!='repudiated']; c['ld']=pd.to_datetime(c.loss_date)
p=r('policies_motor'); p['ps']=pd.to_datetime(p.period_start); p['pe']=pd.to_datetime(p.period_end)
m=c[c.line=='motor'].merge(p[['row_id','policy_id','ps','pe']],on='policy_id'); m=m[(m.ld>=m.ps)&(m.ld<=m.pe)]
n=m.groupby('row_id').size(); p['nclm']=p.row_id.map(n).fillna(0)
print('claims/row by csc'); print(p.groupby(p.customer_service_contacts.clip(upper=8)).agg(rows=('nclm','size'),clm=('nclm','mean')).round(3).T.to_string())
print('csc dist by n claims'); print(p.groupby(p.nclm.clip(upper=3)).customer_service_contacts.describe().round(2).to_string())
print('test csc dist', r('test_motor').customer_service_contacts.value_counts().sort_index().to_dict())
print('train 2024 csc dist', p[p.ps.dt.year==2024].customer_service_contacts.value_counts().sort_index().head(10).to_dict())
print('renewal_decision vs claims'); print(p.groupby('renewal_decision').nclm.mean().round(3).to_dict())
print('missed_payments vs claims'); print(p.groupby('missed_payments_12m').nclm.mean().round(3).to_dict())
for L in ['motor','buildings','contents']:
    t=r('test_'+L); t['ps']=pd.to_datetime(t.period_start); t['pe']=pd.to_datetime(t.period_end)
    d=((t.pe-t.ps).dt.days+1)/365
    print(L,'test expo vs days ratio', (t.exposure/d).describe().round(4).to_dict(), 'rows not starting jan1', (t.ps.dt.dayofyear>1).mean().round(3), 'end<dec31',(t.pe.dt.dayofyear<365).mean().round(3))
    print('  test rows per policy', t.policy_id.value_counts().value_counts().to_dict())
