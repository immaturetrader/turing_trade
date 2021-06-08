#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
title: backtest poc
Created on Fri May 14 01:03:35 2021

@author: manojpotharlankavenkatanaga
"""


import json
import argparse
import datetime
from google.cloud import firestore
from google.cloud import bigquery

import json
import pandas as pd
import logging
from time import sleep
from datetime import datetime as dt
from datetime import timedelta as td
import dill

import matplotlib.pyplot as plt
from big_query_client import *


from backtesting import Backtest 
from backtesting.test._test import *


import inspect
import os
import sys
import time
import unittest
import warnings
from contextlib import contextmanager
from glob import glob
from runpy import run_path
from tempfile import NamedTemporaryFile, gettempdir
from unittest import TestCase
from unittest.mock import patch

import numpy as np
import pandas as pd
import talib
from matplotlib import pyplot as plt

from backtesting import Backtest, Strategy
from backtesting.lib import (
    OHLCV_AGG,
    barssince,
    cross,
    crossover,
    quantile,
    SignalStrategy,
    TrailingStrategy,
    resample_apply,
    plot_heatmaps,
    random_ohlc_data,
)
from backtesting.test import GOOG, EURUSD, SMA
from backtesting._util import _Indicator, _as_str, _Array, try_



class RSI(Strategy):
    # NOTE: These values are also used on the website!
    n=60
    

    def init(self):
        self.RSI = self.I(talib.RSI, self.data.Close,self.n)
        #print("rsi:"+str(self.RSI))
        

    def next(self):
        if self.RSI[-1]>=self.n and self.RSI[-1]<80:
            #print("self.RSI[-1]: "+str(self.RSI[-1]))
            self.position.close()
            self.buy()
        elif self.RSI[-1]<=100-self.n and self.RSI[-1]>20:
            self.position.close()
            self.sell()
            
class SmaCross(Strategy):
    # NOTE: These values are also used on the website!
    n1 = 3
    n2 = 5
    

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        #print("self.sma1 :"+str(self.sma1))
        print("len:"+str(len(self.sma1)))
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
        

class BigQueryExecution:
    def __init__(self, working_dir="/Users/manojpotharlankavenkatanaga/Desktop/AlgoTrade/Manoj Codes/", credential_file='My First Project-13a2fb826159.json'):
        self.working_dir=working_dir
        self.credential_file=credential_file
        
        
    def get_backtest_ohlc_data(self):
        
        
        bq = bigquery.Client.from_service_account_json(self.working_dir+self.credential_file)
        bq_details = json.loads(open(self.working_dir+self.credential_file, 'r').read().rstrip())
        
        
        query = f""" SELECT * 
        FROM `{bq_details['project_id']}.Historical_Data.BANK_NIFTY_DAYWISE_HISTORY`"""
        
        query_job = bq.query(query)
        ohlc_data = query_job.to_dataframe()
        ohlc_data["date"]= pd.to_datetime(ohlc_data["date"])
        ohlc_data_INDEX=ohlc_data.set_index(pd.DatetimeIndex(ohlc_data['date']), inplace=True)  
        print(type(ohlc_data.index))
        ohlc_data1=ohlc_data.drop('date',axis=1)
        ohlc_data1['volume']=1
        ohlc=ohlc_data1.rename(columns = {'open': 'Open', 'high':'High','low':'Low','close':'Close','volume':'Volume'}, inplace = False)
        return ohlc
        
        
            
                



