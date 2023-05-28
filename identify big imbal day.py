# -*- coding: utf-8 -*-
#Quantil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import os
'''
df1 = pd.read_csv('C:/Users/anche/NZ/broker data/20181005.csv')
df2 = pd.read_csv('C:/Users/anche/NZ/broker data/20190131.csv')
df = pd.concat([df1,df2],axis = 0)

df = df[df['Board']=='S']

df['date'] = pd.to_datetime(df['Date'],dayfirst=True).dt.date
df= df[(df['date']>=date(2018,9,1))&(df['date']<date(2018,11,1))]
df['spread'] = np.log(df['Current Offer']/df['Current Bid'])*1000
df = df[df['spread']>0]

df['value'] = df['Volume']*df['Price']

df['event'] = np.where(df['date']>=date(2018,10,1),1,0)

df['agg'] = np.where(df['Price']==df['Current Bid'],'S','nan')
df['agg'] = np.where(df['Price']==df['Current Offer'],'B',df['agg'])

df['old fee'] = df['value'].apply(lambda x: min(1+0.00002*x, 75)) 
df['relative old fee'] = (df['old fee']/df['value'])*10000
df['new fee'] = df['value'].apply(lambda x: min(0.000065*x, 75))
df['relative new fee'] = (df['new fee']/df['value'])*10000

buyer_aggressive_stock_day_value = df[(df['On Off Market']=='N')&(df['Crossing']=='N')].groupby(['date','BUYERCODE','Code']).apply(lambda x:x[x['agg']=='B']['value'].sum()).rename('agg_buy_value').reset_index()
buyer_pas_stock_day_value = df[(df['On Off Market']=='N')&(df['Crossing']=='N')].groupby(['date','BUYERCODE','Code']).apply(lambda x:x[x['agg']=='S']['value'].sum()).rename('mm_buy_value').reset_index()
buyer_stock_day_value = df[(df['On Off Market']=='N')&(df['Crossing']=='N')].groupby(['date','BUYERCODE','Code']).apply(lambda x:x['value'].sum()).rename('buy_value').reset_index()


seller_aggressive_stock_day_value = df[(df['On Off Market']=='N')&(df['Crossing']=='N')].groupby(['date','SELLERCODE','Code']).apply(lambda x:x[x['agg']=='S']['value'].sum()).rename('agg_sell_value').reset_index()
seller_pas_stock_day_value = df[(df['On Off Market']=='N')&(df['Crossing']=='N')].groupby(['date','SELLERCODE','Code']).apply(lambda x:x[x['agg']=='B']['value'].sum()).rename('mm_sell_value').reset_index()
seller_stock_day_value = df[(df['On Off Market']=='N')&(df['Crossing']=='N')].groupby(['date','SELLERCODE','Code']).apply(lambda x:x['value'].sum()).rename('sell_value').reset_index()

all_buy = buyer_aggressive_stock_day_value.merge(buyer_stock_day_value,left_on = ['date','BUYERCODE','Code'],right_on = ['date','BUYERCODE','Code'],how = 'outer').merge(buyer_pas_stock_day_value, on = ['date','BUYERCODE','Code'],how = 'outer')
all_sell = seller_aggressive_stock_day_value.merge(seller_stock_day_value,left_on = ['date','SELLERCODE','Code'],right_on = ['date','SELLERCODE','Code'],how = 'outer').merge(seller_pas_stock_day_value, on = ['date','SELLERCODE','Code'],how = 'outer')


all_value = all_buy.merge(all_sell,left_on = ['date','BUYERCODE','Code'],right_on = ['date','SELLERCODE','Code'],how = 'outer',suffixes = ['_buy','_sell'])

buy_broker_day_stock_num_trades = df.groupby(['date','Code','BUYERCODE'])['value'].count().rename('buy_trade_count').reset_index()
sell_broker_day_stock_num_trades = df.groupby(['date','Code','SELLERCODE'])['value'].count().rename('sell_trade_count').reset_index()

buy_broker_day_stock_trade_size = df.groupby(['date','Code','BUYERCODE'])['value'].mean().rename('buy_trade_size').reset_index()
sell_broker_day_stock_trade_size = df.groupby(['date','Code','SELLERCODE'])['value'].mean().rename('sell_trade_size').reset_index()

buy_broker_day_stock_trade_value = df.groupby(['date','Code','BUYERCODE'])['value'].sum().rename('buy_trade_value').reset_index()
sell_broker_day_stock_trade_value = df.groupby(['date','Code','SELLERCODE'])['value'].sum().rename('sell_trade_value').reset_index()

buy_broker_day_stock_total_old_fee = df.groupby(['date','Code','BUYERCODE'])['old fee'].sum().rename('buy_old_fee').reset_index()
sell_broker_day_stock_total_old_fee = df.groupby(['date','Code','SELLERCODE'])['old fee'].sum().rename('sell_old_fee').reset_index()

buy_broker_day_stock_total_new_fee = df.groupby(['date','Code','BUYERCODE'])['new fee'].sum().rename('buy_new_fee').reset_index()
sell_broker_day_stock_total_new_fee = df.groupby(['date','Code','SELLERCODE'])['new fee'].sum().rename('sell_new_fee').reset_index()

buy_broker_day_stock_num_trades['date'] = pd.to_datetime(buy_broker_day_stock_num_trades['date']).dt.date
buy_broker_day_stock_trade_size['date'] = pd.to_datetime(buy_broker_day_stock_trade_size['date']).dt.date
buy_broker_day_stock_trade_value['date'] = pd.to_datetime(buy_broker_day_stock_trade_value['date']).dt.date
buy_broker_day_stock_total_old_fee['date'] = pd.to_datetime(buy_broker_day_stock_total_old_fee['date']).dt.date
buy_broker_day_stock_total_new_fee['date'] = pd.to_datetime(buy_broker_day_stock_total_new_fee['date']).dt.date
all_buy['date'] = pd.to_datetime(all_buy['date']).dt.date

sell_broker_day_stock_num_trades['date'] = pd.to_datetime(sell_broker_day_stock_num_trades['date']).dt.date
sell_broker_day_stock_trade_size['date'] = pd.to_datetime(sell_broker_day_stock_trade_size['date']).dt.date
sell_broker_day_stock_trade_value['date'] = pd.to_datetime(sell_broker_day_stock_trade_value['date']).dt.date
sell_broker_day_stock_total_old_fee['date'] = pd.to_datetime(sell_broker_day_stock_total_old_fee['date']).dt.date
sell_broker_day_stock_total_new_fee['date'] = pd.to_datetime(sell_broker_day_stock_total_new_fee['date']).dt.date
all_sell['date'] = pd.to_datetime(all_sell['date']).dt.date

all_broker_stock_day_buy = all_buy.merge(buy_broker_day_stock_num_trades, on = ['date','Code','BUYERCODE'], how = 'outer')
all_broker_stock_day_buy = all_broker_stock_day_buy.merge(buy_broker_day_stock_trade_size, on = ['date','Code','BUYERCODE'], how = 'outer')
all_broker_stock_day_buy = all_broker_stock_day_buy.merge(buy_broker_day_stock_trade_value, on =['date','Code','BUYERCODE'], how = 'outer')
all_broker_stock_day_buy = all_broker_stock_day_buy.merge(buy_broker_day_stock_total_old_fee,on =['date','Code','BUYERCODE'], how = 'outer')
all_broker_stock_day_buy = all_broker_stock_day_buy.merge(buy_broker_day_stock_total_new_fee, on = ['date','Code','BUYERCODE'], how = 'outer')

all_broker_stock_day_sell = all_sell.merge(sell_broker_day_stock_num_trades, on = ['date','Code','SELLERCODE'], how = 'outer')
all_broker_stock_day_sell = all_broker_stock_day_sell.merge(sell_broker_day_stock_trade_size, on = ['date','Code','SELLERCODE'], how = 'outer')
all_broker_stock_day_sell = all_broker_stock_day_sell.merge(sell_broker_day_stock_trade_value, on =['date','Code','SELLERCODE'], how = 'outer')
all_broker_stock_day_sell = all_broker_stock_day_sell.merge(sell_broker_day_stock_total_old_fee,on =['date','Code','SELLERCODE'], how = 'outer')
all_broker_stock_day_sell = all_broker_stock_day_sell.merge(sell_broker_day_stock_total_new_fee, on = ['date','Code','SELLERCODE'], how = 'outer')


all_broker_stock_day = all_broker_stock_day_buy.merge(all_broker_stock_day_sell, left_on = ['date','Code','BUYERCODE'],right_on = ['date','Code','SELLERCODE'], how = 'outer')
all_broker_stock_day = all_broker_stock_day.fillna(0)

all_broker_stock_day['imbal'] = (all_broker_stock_day['buy_value']-all_broker_stock_day['sell_value'])/(all_broker_stock_day['buy_value']+all_broker_stock_day['sell_value'])
all_broker_stock_day['imbal_dollar'] =  all_broker_stock_day['buy_value']-all_broker_stock_day['sell_value']

all_broker_stock_day['imbal_mm'] = (all_broker_stock_day['mm_buy_value']-all_broker_stock_day['mm_sell_value'])/(all_broker_stock_day['mm_buy_value']+all_broker_stock_day['mm_sell_value'])
all_broker_stock_day['imbal_dollar_mm'] =  all_broker_stock_day['mm_buy_value']-all_broker_stock_day['mm_sell_value']

mm_stock_day_broker = all_broker_stock_day[abs(all_broker_stock_day['imbal_mm'])<0.1]
facil_stock_day_broker = all_broker_stock_day[abs(all_broker_stock_day['imbal'])>0.9]

facil_stock_day_broker.to_csv('C://Users//anche//NZ//tables update//facil_stock_day_broker.csv')

df_list = []
os.chdir('C://Users//anche//NZ//tables v2//NZ new//merged')
for file in os.listdir('C://Users//anche//NZ//tables v2//NZ new//merged'):
    df = pd.read_csv(file)
    df_list.append(df)
all_df = pd.concat(df_list,axis = 0)
all_df.to_csv('C://Users//anche//NZ//tables v2//NZ new//merged//all_merged.csv')
    
'''

#mm_stock_day_broker = pd.read_csv('C://Users//anche//NZ//tables v2//NZ new//mm_stock_day_broker.csv')
#mm_stock_day_broker['date'] = pd.to_datetime(mm_stock_day_broker['date']).dt.date
#facil_stock_day_broker = pd.read_csv('C://Users//anche//NZ//tables v2//NZ new//facil_stock_day_broker.csv')
#facil_stock_day_broker['date'] = pd.to_datetime(facil_stock_day_broker['date']).dt.date
'''
all_stock_day_broker= pd.read_csv('C://Users//anche//NZ//tables v2//NZ new//all_stock_day_broker.csv')
all_stock_day_broker['date'] = pd.to_datetime(all_broker_stock_day['date']).dt.date
'''
all_df = pd.read_csv('C://Users//anche//NZ//tables v2//NZ new//merged//all_merged.csv')
all_df['date'] = pd.to_datetime(all_df['date_x']).dt.date
all_df['quote_alive'] = all_df.groupby(['stock','date'])['adj mtime'].shift(-1) - all_df['adj mtime'] 
all_df['Price Impact'] = all_df['Effective Spread'] - all_df['Realized Spread']
all_df['liq_maker'] = np.where(all_df['direction']=='S',all_df['BUYERCODE'],np.nan)
all_df['liq_maker'] = np.where(all_df['direction']=='B',all_df['SELLERCODE'],all_df['liq_maker'])

all_df['liq_taker'] = np.where(all_df['direction']=='B',all_df['BUYERCODE'],np.nan)
all_df['liq_taker'] = np.where(all_df['direction']=='S',all_df['SELLERCODE'],all_df['liq_taker'])
all_df[f'tick'] = np.where(all_df['MidQuote adj'] <= 0.2,0.001,np.nan)
all_df[f'tick'] = np.where((all_df['MidQuote adj'] > 0.2)&(all_df['MidQuote adj'] <= 0.5),0.005,all_df[f'tick'])
all_df[f'tick'] = np.where(all_df['MidQuote adj'] > 0.5,0.01,all_df[f'tick'])

all_df['Effective Spread ticks'] = all_df['Effective Spread']/all_df[f'tick']
all_df['Realized Spread ticks'] = all_df['Realized Spread']/all_df[f'tick']
all_df['Price Impact ticks'] = all_df['Price Impact']/all_df[f'tick']


day_es_maker = all_df.groupby(['stock','date','liq_maker']).apply(lambda x: (x['Effective Spread ticks']*x['value']).sum()/x['value'].sum()).rename('day_es_maker').reset_index()
day_es_taker = all_df.groupby(['stock','date','liq_taker']).apply(lambda x: (x['Effective Spread ticks']*x['value']).sum()/x['value'].sum()).rename('day_es_taker').reset_index()

day_rs_maker = all_df.groupby(['stock','date','liq_maker']).apply(lambda x: (x['Realized Spread ticks']*x['value']).sum()/x['value'].sum()).rename('day_rs_maker').reset_index()
day_rs_taker = all_df.groupby(['stock','date','liq_taker']).apply(lambda x: (x['Realized Spread ticks']*x['value']).sum()/x['value'].sum()).rename('day_rs_taker').reset_index()

day_pi_maker = all_df.groupby(['stock','date','liq_maker']).apply(lambda x: (x['Price Impact ticks']*x['value']).sum()/x['value'].sum()).rename('day_pi_maker').reset_index()
day_pi_taker = all_df.groupby(['stock','date','liq_taker']).apply(lambda x: (x['Price Impact ticks']*x['value']).sum()/x['value'].sum()).rename('day_pi_taker').reset_index()

day_maker_metrics = day_es_maker.merge(day_rs_maker, on = ['stock','date','liq_maker'])
day_maker_metrics = day_maker_metrics.merge(day_pi_maker, on = ['stock','date','liq_maker'])

day_maker_metrics.to_csv('C://Users//anche//NZ//tables update//maker_metrics.csv')
day_taker_metrics = day_es_taker.merge(day_rs_taker, on = ['stock','date','liq_taker'])
day_taker_metrics = day_taker_metrics.merge(day_pi_taker, on = ['stock','date','liq_taker'])
day_taker_metrics.to_csv('C://Users//anche//NZ//tables update//taker_metrics.csv')
#day_buy_metrics = day_buy_metrics.merge(all_stock_day_broker, left_on = ['stock','date','BUYERCODE'],right_on =['Code','date','BUYERCODE'] , how = 'left')
#day_sell_metrics = day_sell_metrics.merge(all_stock_day_broker, left_on = ['stock','date','SELLERCODE'],right_on =['Code','date','SELLERCODE'], how = 'left')



#df = all_df.merge(all_stock_day_broker, on = ['stock','date','Code'], how = 'left')

#df = df.merge(facil_stock_day_broker, on = ['stock','date'], how = 'left')


