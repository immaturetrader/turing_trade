import pandas as pd
import numpy as np

#data=pd.read_csv("data/RELIANCE.csv")

indicators_csv=pd.DataFrame(columns=['exchange','scrip','scrip_name','all_time_high','all_time_low','Fib 23.6','Fib 38.2'
                                     ,'Fib 61.8','Fib 78.6'])
dim_scrips=pd.read_csv('dim_scrips.csv')
ichmoku_cloud=pd.DataFrame(columns=['exchange','scrip','scrip_name','open','high','low','close','volume','conversion_line','base_line','lead_span_A','lead_span_B','lagging_span'])
i=0
total_scrips=len(dim_scrips)
try:
 for i,row in dim_scrips.iterrows():
    scrip=row['Symbol']
    scrip_name=row['Company Name']
    #print(f"Analysing scrip {scrip}")
    data=pd.read_parquet(f"data/{scrip}.parquet")
    #data.index=pd.to_datetime(data['date'])
    date_index_without_tz=data.index.tz_convert(None)
    data.index=pd.to_datetime(date_index_without_tz)
    data['scrip']=scrip
    data['scrip_name']=scrip_name
    data['exchange']="NSE"    
    scrip_max=data['high'].max()
    scrip_min=data['high'].min()
    diff=scrip_max-scrip_min
    fb_23_6=scrip_max-(diff*0.236)
    fb_38_2=scrip_max-(diff*0.382)
    fb_61_8=scrip_max-(diff*0.618)
    fb_78_6=scrip_max-(diff*0.786)
    
    # Define length of Tenkan Sen or Conversion Line
    cl_period = 20 
    
    # Define length of Kijun Sen or Base Line
    bl_period = 60  
    
    # Define length of Senkou Sen B or Leading Span B
    lead_span_b_period = 120  
    
    # Define length of Chikou Span or Lagging Span
    lag_span_period = 30  
    
    # Calculate conversion line
    high_20 = data['high'].rolling(cl_period).max()
    low_20 = data['low'].rolling(cl_period).min()
    data['conversion_line'] = (high_20 + low_20) / 2
    
    # Calculate based line
    high_60 = data['high'].rolling(bl_period).max()
    low_60 = data['low'].rolling(bl_period).min()
    data['base_line'] = (high_60 + low_60) / 2
    
    # Calculate leading span A
    data['lead_span_A'] = ((data.conversion_line + data.base_line) / 2).shift(lag_span_period)
    
    # Calculate leading span B
    high_120 = data['high'].rolling(120).max()
    low_120 = data['high'].rolling(120).min()
    data['lead_span_B'] = ((high_120 + low_120) / 2).shift(lead_span_b_period)
    
    # Calculate lagging span
    data['lagging_span'] = data['close'].shift(-lag_span_period)

    indicators_csv.loc[i]="NSE",scrip,scrip_name,scrip_max,scrip_min,fb_23_6,fb_38_2,fb_61_8,fb_78_6
    #data.to_csv("ichmoku_cloud.csv")
    ichmoku_cloud=pd.concat([ichmoku_cloud,data])
    print(f"Analysis Completed {round((i+1)/total_scrips*100,2)} % ",end="\r")
    i=i+1
    
except Exception as e:
    print(e)

indicators_csv.to_excel("indicators.xlsx",index=False)
print("\nGenerated fibonacci")
ichmoku_cloud.to_csv("ichmoku_cloud.csv")
print("Generated ichmoku")