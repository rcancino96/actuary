import pandas as pd, numpy as np
D='/home/claude/hack/data/raw/public/'
pd.set_option('display.width',250)
r=lambda f: pd.read_parquet(D+f+'.parquet')
c=r('claims'); c=c[~c.drop(columns=['claim_id']).duplicated()]
c['ld']=pd.to_datetime(c.loss_date); c['rd']=pd.to_datetime(c.report_date); c['ly']=c.ld.dt.year
c=c[(c.status!='repudiated')&(c.ly>=2021)]
c['net']=c.incurred_to_date-c.recoveries
expo={}
for L in ['motor','buildings','contents']:
    p=r('policies_'+L); p['ps']=pd.to_datetime(p.period_start); p['pe']=pd.to_datetime(p.period_end)
    p['e']=((p.pe-p.ps).dt.days+1)/365.25
    expo[L]=p.groupby(p.ps.dt.year).e.sum()
rows=[]
for (L,per,y),g in c.groupby(['line','peril','ly']):
    rows.append(dict(line=L,peril=per,ly=y,freq=len(g)/expo[L][y]*1000,sev=g.net.mean(),med=g.net.median(),open=(g.status=='open').mean(),rec=g.recoveries.sum()/g.incurred_to_date.sum()))
t=pd.DataFrame(rows)
for k in ['freq','sev','med','open']:
    print('\n',k); print(t.pivot_table(index=['line','peril'],columns='ly',values=k).round(3 if k=='open' else 1).to_string())
print('\nrecovery ratio');print(t.pivot_table(index=['line','peril'],columns='ly',values='rec').round(3).to_string())
# burning cost per line per year
bc=c.groupby(['line','ly']).net.sum().unstack()
print('\nburning cost per expo'); print((bc.T/pd.DataFrame(expo)).T.round(1).to_string())
# quarterly freq in 2024 (IBNR signal)
c['lq']=c.ld.dt.to_period('Q')
print(c[c.ly>=2023].groupby(['line','lq']).size().unstack(0).to_string())
