# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 16:37:20 2021

@author: sravula
"""

import pandas as pd

nse_sheet=pd.read_csv("ind_nifty50list.csv")
eq_instruments=pd.read_csv("eq_instruments.csv")

dim_script=nse_sheet

df_merge_col=pd.merge(nse_sheet,eq_instruments,left_on='Symbol',right_on='tradingsymbol',how='inner')

df_merge_col.to_csv('dim_scrips.csv')