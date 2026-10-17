import pandas as pd, numpy as np
D='/home/claude/hack/data/raw/public/'
pd.set_option('display.width',250)
r=lambda f: pd.read_parquet(D+f+'.parquet')
c=r('claims'); c['ld']=pd.to_datetime(c.loss_date,errors='coerce'); c['rd']=pd.to_datetime(c.report_date,errors='coerce')
print('bad dates', c.ld.isna().sum(), c.rd.isna().sum(), 'rd<ld',(c.rd<c.ld).sum(), 'ld range',c.ld.min(),c.ld.max(),'rd max',c.rd.max())
print('dup claim_id',c.claim_id.duplicated().sum(), 'full dup', c.drop(columns=['claim_id']).duplicated().sum())
print(c.status.value_counts().to_dict()); print(c.line.value_counts().to_dict())
print('line vs prefix', pd.crosstab(c.line, c.policy_id.str[0]))
print(c.groupby(['line','peril']).size())
print('rep: paid,inc,rec', c[c.status=='repudiated'][['paid_to_date','incurred_to_date','recoveries']].describe().round(1).to_string())
print('neg', (c.paid_to_date<0).sum(), (c.incurred_to_date<0).sum(), (c.recoveries<0).sum(), 'paid>inc', (c.paid_to_date>c.incurred_to_date+0.01).sum())
cl=c[c.status=='closed']; print('closed paid!=inc', (abs(cl.paid_to_date-cl.incurred_to_date)>0.01).sum(), 'zero inc closed', (cl.incurred_to_date==0).sum())
print('rec>inc', (c.recoveries>c.incurred_to_date+0.01).sum())
c['net']=c.incurred_to_date-c.recoveries
c['ly']=c.ld.dt.year
nr=c[c.status!='repudiated']
print(nr.groupby(['line','ly']).agg(n=('net','size'),mean=('net','mean'),open=('status',lambda s:(s=='open').mean())).round(3).to_string())
print(nr.groupby(['line','peril']).net.describe(percentiles=[.5,.9,.99,.999]).round(0).to_string())
c['delay']=(c.rd-c.ld).dt.days
print(c.groupby('line').delay.describe(percentiles=[.5,.9,.95,.99]).round(0).to_string())
print(c.groupby(['line','peril']).delay.quantile(.95).round(0).to_string())
# open by age
c['age']=(pd.Timestamp('2024-12-31')-c.ld).dt.days//90
print(nr.assign(age=c.age).groupby(['line',c.age.clip(upper=12)]).status.apply(lambda s:(s=='open').mean()).unstack(0).round(3).to_string())
