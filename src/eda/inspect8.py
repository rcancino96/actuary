import pandas as pd, numpy as np
D='/home/claude/hack/data/raw/public/'
pd.set_option('display.width',250)
c=pd.read_parquet(D+'claims.parquet'); c=c[~c.drop(columns=['claim_id']).duplicated()]
c['ld']=pd.to_datetime(c.loss_date); c['rd']=pd.to_datetime(c.report_date); c['ly']=c.ld.dt.year
c=c[(c.status!='repudiated')&(c.ly>=2021)]; c['net']=c.incurred_to_date-c.recoveries
c['delay']=(c.rd-c.ld).dt.days
c['dq']=pd.cut(c.delay,[0,30,90,180,365,730,2000])
for per in ['bodily_injury','subsidence','fire','flood','third_party_prop','own_damage']:
    g=c[(c.peril==per)&(c.ly<=2022)]
    print(per,'sev by delay (ly2021-22)'); print(g.groupby('dq',observed=True).net.agg(['size','mean','median']).round(0).T.to_string())
    print(' open vs closed mean by ly'); print(c[c.peril==per].groupby(['ly','status']).net.agg(['size','mean','median']).round(0).unstack().to_string())
# paid vs incurred for open
o=c[c.status=='open']; print('open paid/inc by peril', (o.groupby('peril').paid_to_date.sum()/o.groupby('peril').incurred_to_date.sum()).round(3).to_dict())
# BI large
bi=c[c.peril=='bodily_injury'].net; print('BI top', bi.nlargest(10).round(0).tolist())
for per in c.peril.unique():
    x=c[c.peril==per].net; print(per,'top5',x.nlargest(5).round(0).tolist())
