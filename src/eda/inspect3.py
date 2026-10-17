import pandas as pd, numpy as np
from pathlib import Path; D=str(Path(__file__).resolve().parents[2]/'data/raw/public')+'/'
pd.set_option('display.width',250); pd.set_option('display.max_columns',60)
r=lambda f: pd.read_parquet(D+f+'.parquet')
for L in ['motor','buildings','contents']:
    p=r('policies_'+L); p['ps']=pd.to_datetime(p.period_start); p['pe']=pd.to_datetime(p.period_end); p['yr']=p.ps.dt.year
    calc=((p.pe-p.ps).dt.days+1)
    bad=p.exposure>1.0001
    print(L,'expo>1:',bad.sum(),'by yr',p[bad].yr.value_counts().to_dict(), 'ratio to days', (p.exposure[bad]/calc[bad]).describe().round(3).to_dict())
    print('  period_start month dist 2021', p[p.yr==2021].ps.dt.month.value_counts().sort_index().to_dict())
    print('  period_start month dist 2022', p[p.yr==2022].ps.dt.month.value_counts().sort_index().to_dict())
    print('  csc by yr', p.groupby('yr').customer_service_contacts.mean().round(3).to_dict(), 'renewal_count', p.groupby('yr').renewal_count.mean().round(2).to_dict())
    if L=='motor': print('  vehicle_age by yr', p.groupby('yr').vehicle_age.mean().round(2).to_dict())
    if L!='motor':
        s=p.sum_insured; print('  SI q', s.quantile([.9,.99,.995,.999]).to_dict(), '>2M', (s>2e6).sum(), 'ratio examples', (s[s>2e6]/1).head(5).tolist())
    if L=='buildings':
        print(pd.crosstab(p.construction_type,p.yr))
