import bs4
from bs4 import BeautifulSoup
import investpy
import iexfinance
import time

url="https://finance.yahoo.com/quote/F*SI.CMX?p=F*SI.CMX&.tsrc=fin-srch"




#comm=investpy.commodities.get_commodities_overview('metals', as_json=False, n_results=100)
while True:
 comm=investpy.commodities.get_commodities_overview('metals', as_json=False, n_results=100)   
 print(comm[comm['name']=='Silver']['last'].values[0])
 #time.sleep(5)

investpy.indices.get_indices_list(country=None) 
investpy.indices.get_index_information(index='NIFTY', country='india', as_json=False)

investpy.indices.get_indices_overview('india', as_json=False, n_results=2)
investpy.indices.get_indices_overview('united states'   , as_json=False, n_results=5)