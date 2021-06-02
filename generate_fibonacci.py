import pandas as pd
import numpy as np

#data=pd.read_csv("data/RELIANCE.csv")

indicators_csv=pd.DataFrame(columns=['scrip','all_time_high','all_time_low','Fib 23.6','Fib 38.2'
                                     ,'Fib 61.8','Fib 78.6'])
token_dict={'HDFCBANK':341249,'RELIANCE':738561,'TCS':2953217}

i=0
for scrip in token_dict.keys():
    
    data=pd.read_csv(f"data/{scrip}.csv")
    scrip_max=data['high'].max()
    scrip_min=data['high'].min()
    diff=scrip_max-scrip_min
    fb_23_6=scrip_max-(diff*0.236)
    fb_38_2=scrip_max-(diff*0.382)
    fb_61_8=scrip_max-(diff*0.618)
    fb_78_6=scrip_max-(diff*0.786)
    indicators_csv.loc[i]=scrip,scrip_max,scrip_min,fb_23_6,fb_38_2,fb_61_8,fb_78_6
    i=i+1

indicators_csv.to_csv("indicators.csv",index=False)