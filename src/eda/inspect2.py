import pandas as pd, numpy as np
D='/home/claude/hack/data/raw/public/'
pd.set_option('display.width',250); pd.set_option('display.max_columns',60)
r=lambda f: pd.read_parquet(D+f+'.parquet')
w=r('weather'); print('weather years', w.year.value_counts().sort_index().to_dict())
print('weather dup', w.duplicated(['address_id','year']).sum())
for L in ['motor','buildings','contents']:
    p=r('policies_'+L); t=r('test_'+L)
    print('\n#####',L, 'train',len(p),'test',len(t))
    for c in p.columns:
        if p[c].dtype==object or str(p[c].dtype) in ('str','string','bool'):
            if c in('row_id','policy_id','customer_id','address_id','period_start','period_end'):continue
            vc=p[c].astype(str).value_counts()
            if len(vc)<40: print(' ',c, vc.to_dict(), '| test:', t[c].astype(str).value_counts().to_dict() if c in t else '-')
            else: print(' ',c,'nuniq',len(vc), 'test unseen', (~t[c].isin(p[c])).mean() if c in t else '-')
    num=p.select_dtypes('number')
    print(num.describe(percentiles=[.01,.5,.99]).T.round(2).to_string())
    print('test num'); print(t.select_dtypes('number').describe(percentiles=[.01,.5,.99]).T.round(2).to_string())
    p['ps']=pd.to_datetime(p.period_start); p['pe']=pd.to_datetime(p.period_end)
    p['yr']=p.ps.dt.year
    print('rows/yr',p.yr.value_counts().sort_index().to_dict(),'expo/yr',p.groupby('yr').exposure.sum().round(0).to_dict())
    calc=((p.pe-p.ps).dt.days+1)/365.25
    print('exposure diff vs dates: max abs',(calc-p.exposure).abs().max(), 'q99', (calc-p.exposure).abs().quantile(.99))
    print('cross-year rows', (p.pe.dt.year!=p.ps.dt.year).sum(), 'neg/zero expo', (p.exposure<=0).sum())
    print('dup row_id',p.row_id.duplicated().sum())
    print('test period', t.period_start.min(), t.period_end.max(), 'test expo', t.exposure.describe().round(3).to_dict())
    print('test policies seen in train', t.policy_id.isin(p.policy_id).mean())
