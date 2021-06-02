from turing_library.kiteext import KiteExt
import json
import pandas as pd
import logging
from time import sleep
from datetime import datetime as dt
from datetime import timedelta as td
import dill
import time
import json
import pandas as pd
import logging
from time import sleep
from datetime import datetime as dt
from datetime import timedelta as td
import dill
from datetime import datetime
#user = json.loads(open('userzerodha.json', 'r').read().rstrip())
#userid=user['user_id']
#password=user['password']
#twofa=user['twofa']

from turing_library.big_query_client import big_query
from turing_library.alice_blue_execution import alice_blue_execution
from turing_library.firestore_client import fire_store
from turing_library.kiteext import KiteExt
from google.cloud import storage



fs=fire_store()
  

class zerodha_data():

    def get_historical_data(self,kite,token,from_date,to_date,intervel):
    
        df_row_merged=pd.DataFrame()
        Total_Days=(to_date-from_date).days
        print("total days:"+str(Total_Days))
        
    #Only 60 days of data can be fetched with intervel of 1 min
    # so, iterating and travesring backwards till the difference/intervel gets less than 60 days(from the feom_date). Once it is less than 60 days get last set of data and break the loop! cheers!
        if Total_Days>=60:
            while(1):
                if (to_date-from_date).days>60:
                   
                    data = kite.historical_data(token,to_date - td(days=60), to_date,intervel)
                    to_date=to_date - td(days=60)
                    
                    df_row_merged = pd.concat([df_row_merged, pd.DataFrame(data)], ignore_index=True)
                    time.sleep(0.2)
                else:
                    
                    data = kite.historical_data(token,to_date - td(days= (to_date-from_date).days), to_date,intervel)
                    
                    df_row_merged = pd.concat([df_row_merged, pd.DataFrame(data)], ignore_index=True)
                    break
                    
                
        else:
            
            data = kite.historical_data(token,to_date - td(days= (to_date-from_date).days), to_date,intervel)
            print("data1:"+str(data))
            print(pd.DataFrame(data))
            
            df_row_merged = pd.concat([df_row_merged, pd.DataFrame(data)], ignore_index=True)
        
        print(df_row_merged)
        return(df_row_merged)
        
        

def get_broker_details(broker):
    table='broker_admin'
    docs = fs.client.collection(table).where(u'broker',u'==','angel_broking').stream()
    return [doc.to_dict() for doc in docs][0]
    

            
user=get_broker_details('zerodha')
kite = KiteExt()
kite.login_with_credentials(
    userid=user['client_id'], password=user['password'], twofa=user['twofa'])
print(kite.profile())

z=zerodha_data()
from_date=datetime.strptime("2008-01-01",'%Y-%m-%d')
to_date=datetime.strptime("2021-05-01",'%Y-%m-%d')
token_dict={'HDFCBANK':341249,'RELIANCE':738561,'TCS':2953217}

data=z.get_historical_data(kite,2953217,from_date,to_date,"day")
data.to_csv("data/TCS.csv",index=False)



from smartapi import SmartConnect
obj=SmartConnect(api_key="3XkvUW0H")
username='R381604'
pwd='497666124153'
data = obj.generateSession(username,pwd)
refreshToken= data['data']['refreshToken']

#fetch the feedtoken
feedToken=obj.getfeedToken()

#fetch User Profile
userProfile= obj.getProfile(refreshToken)

historicParam={
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_DAY",
    "fromdate": "1970-02-08 00:00", 
    "todate": "1970-05-08 00:00"
    }
d=pd.DataFrame(obj.getCandleData(historicParam)['data'],columns=['date','open','high','low','close','volume'])