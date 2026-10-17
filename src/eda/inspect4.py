import pandas as pd, numpy as np
D='/home/claude/hack/data/raw/public/'
r=lambda f: pd.read_parquet(D+f+'.parquet')
p=r('policies_motor'); p['ps']=pd.to_datetime(p.period_start); p['pe']=pd.to_datetime(p.period_end)
p['days']=(p.pe-p.ps).dt.days+1
b=p[p.exposure>1.0001]; print(b[['exposure','days']].value_counts().head(10))
print('expo vs days/365 typical', (p.exposure/(p.days/365)).describe().round(4).to_dict(), (p.exposure/(p.days/365.25)).quantile([.01,.5,.99]).to_dict())
for L in ['buildings','contents']:
    q=r('policies_'+L); big=q.sum_insured>2e6
    print(L,'SI/1000 big', (q.sum_insured[big]/1000).describe().round(0).to_dict())
    print(' premium big vs normal', q.written_premium[big].mean(), q.written_premium[~big].mean())
    print(' SI distinct min of big', q.sum_insured[big].min(), 'max normal', q.sum_insured[~big].max())
    t=r('test_'+L); print(' test big', (t.sum_insured>2e6).sum())
# customers / address quality
c=r('customers'); print('cust dup',c.customer_id.duplicated().sum()); 
for col in ['occupation','marital_status','credit_band','previous_insurer','email_domain','marketing_segment','document_preference']:
    vc=c[col].value_counts(dropna=False); print(col,len(vc), vc.head(12).to_dict())
print(c.describe().T.round(2).to_string())
c['dob']=pd.to_datetime(c.date_of_birth,errors='coerce'); print('dob range',c.dob.min(),c.dob.max(),'bad',c.dob.isna().sum())
a=r('addresses'); print('addr dup',a.address_id.duplicated().sum())
for col in ['region','urban_density','soil_type','property_type','roof_type','energy_rating','flood_zone']:
    print(col, a[col].value_counts(dropna=False).to_dict())
print(a.describe().T.round(2).to_string())
w=r('weather'); print(w.groupby('year').mean(numeric_only=True).round(3).to_string())
