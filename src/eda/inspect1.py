import pandas as pd, sys
from pathlib import Path; D=str(Path(__file__).resolve().parents[2]/'data/raw/public')+'/'
pd.set_option('display.width',250); pd.set_option('display.max_columns',60)
for f in ['customers','addresses','weather','policies_motor','policies_buildings','policies_contents','claims','test_motor','test_buildings','test_contents','sample_submission']:
    df=pd.read_parquet(D+f+'.parquet')
    print('\n=====',f,df.shape)
    print(df.dtypes.to_string())
    na=df.isna().mean(); na=na[na>0]
    if len(na): print('NA:',na.round(3).to_dict())
    print(df.head(3).T.to_string())
