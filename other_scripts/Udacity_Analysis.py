import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
import numpy as np
import time
import scipy.optimize as spo
#from  util import get_data,plot_data

def test_run_averages(df,scrip):
    """Function called by Test Run."""
    #max_close=get_max_close(df,scrip)
    #print("Max Close for the stock {} is {}".format(scrip,max_close))
    #mean_volume=get_mean_volume(df,scrip)
    #print("Mean Volume for the stock {} is {}".format(scrip,mean_volume))
    #plot_data(df,scrip)
    
def test_run_stats(start_date,end_date):
    """Function called by Test Run."""

    normalized_final_df=normalize_data(final_df)
    final_df.to_csv('stocks.csv')
    ax=normalized_final_df['HDFCBANK'].plot(title='Nifty rolling mean',label='HDFCBANK')
    rolling_mean_df=get_rolling_mean(final_df['HDFCBANK'],20)
       
    rolling_mean_df.plot(label='Rolling mean',ax=ax)
    lower_band_df,upper_band_df=get_bollinger_bands(final_df['HDFCBANK'],20)
    lower_band_df.plot(label='lower band',ax=ax)
    upper_band_df.plot(label='upper band',ax=ax)
    return final_df

def data_pre_processing(df):
    df=fill_missing_values(df)
    return df

def get_data(scrips,start_date,end_date):
    df = pd.read_csv("D:/Personal/Stocks/Data/Stocks_30_Historical_Data.csv",index_col="Date",
                         parse_dates=True,usecols=['Date','Close','Scrip']) 
    df=data_pre_processing(df)    
    dates=pd.date_range(start_date,end_date)
    df_date_indexed=pd.DataFrame(index=dates)
    
    #Load Nifty
    #df_nifty=pd.read_csv("D:/Personal/Stocks/Data/NIFTY_Historical.csv",index_col="Date",
     #                    parse_dates=True,na_values=['null'],usecols=['Date','Close'])
    #df_nifty=df_nifty.rename(columns={'Close':'NIFTY'})
    #df_nifty=fill_missing_values(df_nifty)
    #df_date_indexed=df_date_indexed.join(df_nifty)
    #scrips=['HDFCBANK']
    for scrip in scrips:
        scrip_df=df[df.Scrip.eq(scrip)].sort_values(by=['Date'])
        scrip_df=scrip_df['Close']
        scrip_df=pd.DataFrame(scrip_df)
        scrip_df=scrip_df.rename(columns={'Close':scrip})
        
        #scrip_df=scrip_df/scrip_df.iloc[min_date]
        final_df=df_date_indexed.join(scrip_df)
        final_df=data_pre_processing(final_df)
        df_date_indexed=final_df
    return df_date_indexed

def get_rolling_mean(df,period):
    return df.rolling(period).mean()

def get_rolling_std(df,period):
    return df.rolling(period).std()

def get_bollinger_bands(df,period):
    mean=get_rolling_mean(df,period)
    std=get_rolling_std(df,period)
    return mean-2*std,mean+2*std

def fill_missing_values(df):
    df.fillna(method="ffill",inplace=True)
    df.fillna(method="bfill",inplace=True)
    return df


def normalize_data(df):
    return df/df.iloc[0]  
  
def get_max_close(df,scrip):
    """
    Return maximum closing price of a scrip
    """
    scrip_df=df[df.Scrip.eq(scrip)]
    return scrip_df['Close'].max()

def get_mean_volume(df,scrip):
    """
    Return mean volume of a scrip
    """
    scrip_df=df[df.Scrip.eq(scrip)]
    return scrip_df['Close'].mean()

def plot_data(final_plot,df,label,title="Stock normalized prices"):
    """
    This is for plotting data
    """
    final_plot=df.plot(label=label,title=title,fontsize=12)
    final_plot.set_xlabel("Date")
    final_plot.set_ylabel("Price")
    #scrip_df=df[df.Scrip.eq(scrip)]
    plt.show()
    final_plot=final_plot.plot('Final',final_plot=final_plot)
    return final_plot
    
def compute_daily_returns(df):
    """
    Compute daily returns
    """    
    daily_returns = df.copy()
    daily_returns[1:] = (df[1:]/df[:-1].values)-1
    daily_returns.iloc[0,:]=0
    return daily_returns

def compute_portfolio_statistics():
    start_date='2010-01-01'
    end_date='2020-01-01'
    print(weights_df[weights_df.symbols.eq('HDFCBANK')]['weight'])
    df=get_data(symbols,start_date,end_date)
    df=compute_daily_returns(df)
    portfolio_daily_returns=pd.DataFrame(columns=['daily_returns'])
    dates=pd.date_range(start_date,end_date)
    adjusted_daily_returns=pd.DataFrame(index=dates,columns=['daily_returns'])
    risk_free_daily_returns=pd.DataFrame(index=dates,columns=['daily_returns'])
    
    portfolio_daily_returns['daily_returns']=0.5*df['HDFCBANK']+0.3*df['TATAELXSI']+0.2*df['BAJAJFINSV']
    print(portfolio_daily_returns)
    risk_free_daily= 0.06 ** (1/252)
    print("risk_free_daily is ",risk_free_daily)
    risk_free_daily_returns['daily_returns']=risk_free_daily
    print(risk_free_daily_returns['daily_returns'])
    adjusted_daily_returns['daily_returns']=portfolio_daily_returns['daily_returns']-risk_free_daily_returns['daily_returns']
    sharpe_ratio=adjusted_daily_returns['daily_returns'].mean()/portfolio_daily_returns['daily_returns'].std()
    print("sharpe ratio is ",sharpe_ratio)
 
def f(X):
    Y=(X-1.5)**2 + 0.5
    print("X={},Y={}".format(X,Y)) # for tracing
    return Y

def compute_error(line,data):
    """
    Compute error between given line model and data points
    """
    err = np.sum((data[:,1]-(line[0]*data[:,0]+line[1]))**2)
    return err

def fit_line():
    pass

def compute_portfolio_sharpe_ratio(params):
    a=params[0]
    b=params[1]
    c=params[2]
    
    start_date='2010-01-01'
    end_date='2020-01-01' 
    scrips=['HDFCBANK','TATAELXSI','BAJAJFINSV']  
    df=get_data(scrips,start_date,end_date)
    dates=pd.date_range(start_date,end_date)
    adjusted_daily_returns=pd.DataFrame(index=dates,columns=['daily_returns'])
    risk_free_daily_returns=pd.DataFrame(index=dates,columns=['daily_returns'])
    portfolio_daily_returns =df
    portfolio_daily_returns['daily_returns']=a*df['HDFCBANK']+b*df['TATAELXSI']+c*df['BAJAJFINSV']
    #print(portfolio_daily_returns)
    risk_free_daily= 0.06 ** (1/252)
    #print("risk_free_daily is ",risk_free_daily)
    risk_free_daily_returns['daily_returns']=risk_free_daily
    #print(risk_free_daily_returns['daily_returns'])
    adjusted_daily_returns['daily_returns']=portfolio_daily_returns['daily_returns']-risk_free_daily_returns['daily_returns']
    sharpe_ratio=adjusted_daily_returns['daily_returns'].mean()/portfolio_daily_returns['daily_returns'].std()
    print("sharpe ratio is ",sharpe_ratio,"params:",params)
    return -1*sharpe_ratio

def apply_sum_constraint(inputs):
    #only results with 0 are accepted other are rejected
       return 1-np.sum(inputs)

def maximise_sharpe_ratio():
    #XGuess=2.0
    #min_result=spo.minimize(f,XGuess, method ='SLSQP', options = {'disp': True})
    #print("Minima found at:")
    #print("X={},Y={}".format(min_result.x,min_result.fun))

    start_date='2007-01-01'
    end_date='2020-01-01'
    scrips=['HDFCBANK','TATAELXSI','BAJAJFINSV']    
    params=[0.2,0.4,0.4] 
    df=get_data(scrips,start_date,end_date)
    compute_portfolio_sharpe_ratio(params)
    
    allocation_constraints=({'type': 'eq', "fun": apply_sum_constraint })
    min_result=spo.minimize(compute_portfolio_sharpe_ratio,params, method ='SLSQP',bounds=((0.1,0.9),(0.1,0.9),(0.1,0.9)), options = {'disp': True},constraints=allocation_constraints)
    print("allocation_parameters={},Maximised_Sharpe_Ratio={}".format(min_result.x,-1*min_result.fun))
    
 
def test_run():
    maximise_sharpe_ratio()
    
if __name__ == "__main__":
    start_time=time.time()
    
    test_run()
    
    
    end_time=time.time()
    print(end_time-start_time," Seconds")

