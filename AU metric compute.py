import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import datetime as dt
from datetime import timedelta

#cross_listed = ['A2M','AFP','AIA','AIZ','BGP','CBL','CNU','CEN','EBO','EVO','FBU','FPH','FSF','GNE','GTK','IFT','IKE','KMD','MEZ','MEQ','MPP','MCY','NTL','NZK','NZM','OCA','OHE','PPH','RBD','SKC','SMP','SM1','SNZ','SKO','SKT','SPK','TGH','TME','TLT','TRA','TWR','VGL','ZEL']
o_time = 10*3600*1000000
c_time = 16*3600*1000000


def metric(filename):
    df = pd.read_csv(filename)
    df['venue'] = df['#RIC'].str.split('.', expand=True)[1]
    df['stock'] = df['#RIC'].str.split('.', expand=True)[0]
    # df['timestamp'] = (df['Date[L]'] + df['Time[L]'])

    # correct daylight saving
    df['timestamp'] = pd.to_datetime(df['Date-Time'], utc=False)
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert('Australia/Sydney')
    df['date'] = df['timestamp'].dt.date

    df['Price'] = df.groupby(['stock', 'date'])['Price'].shift(-2)
    df['Volume'] = df.groupby(['stock', 'date'])['Volume'].shift(-2)
    df['Buyer ID'] = df.groupby(['stock', 'date'])['Buyer ID'].shift(-2)
    df['Seller ID'] = df.groupby(['stock', 'date'])['Seller ID'].shift(-2)
    df['Qualifiers'] = df.groupby(['stock', 'date'])['Qualifiers'].shift(-2)
    df['Tick Dir.'] = df.groupby(['stock', 'date'])['Tick Dir.'].shift(-2)
    df = df[(df['Price'].notnull()) | (df['Bid Price'].notnull())]

    # continue other metric

    df['value'] = df['Price'] * df['Volume']
    #
    df['fee'] = df['value'].apply(lambda x: min(0.0015 * x, 75))

    df['trades'] = np.where(df['Price'].notnull(), 1, 0)

    df['time'] = df['timestamp'].dt.time
    # time in microsecond
    df['mtime'] = df['time'].apply(
        lambda x: x.hour * 3600 * 1000000 + x.minute * 60 * 1000000 + x.second * 1000000 + x.microsecond)
    df['adj mtime'] = np.where(
        ((df['date'] > date(2017, 10, 1)) & (df['date'] <= date(2018, 3, 31))) | (df['date'] > date(2018, 10, 17)),
        df['mtime'] + 3600 * 1000000, df['mtime'])
    df['mtime_1m'] = df['adj mtime'] + 60 * 1000000

    df['Ask Size abs'] = df['Ask Size']
    df['Bid Size abs'] = df['Bid Size']
    # fil in quoting status of the previous quote
    quotes_cols = ['Bid Price', 'Bid Size', 'Ask Price', 'Ask Size', 'Ask Size abs', 'Bid Size abs']
    # df = df.sort_values(['venue', 'extra_timestamp'])
    df[quotes_cols] = df.groupby(['venue'])[quotes_cols].fillna(method='ffill')

    df['MidQuote'] = np.where((df['Bid Price'] != 0) & (df['Ask Price'] != 0),
                              (df['Bid Price'] + df['Ask Price']) / 2.0, np.nan)

    # assign trade direction

    df['direction'] = np.where(df['Price'] > df['MidQuote'], 'B', np.nan)
    df['direction'] = np.where(df['Price'] < df['MidQuote'], 'S', df['direction'])
    df['direction'] = np.where(df['Price'] == df['MidQuote'], 'C', df['direction'])

    # o_time = dt.time(10, 0, 0)
    # c_time = dt.time(17, 0, 0)

    df = df[(df['adj mtime'] > o_time) & (df['adj mtime'] < c_time)]

    daily_value = df.groupby(['date', 'stock'])['value'].sum().reset_index()
    daily_value = daily_value.rename(columns={'value': 'daily_value'})
    df = df.merge(daily_value, on=['date', 'stock'], how='left')
    df['value'] = df['Price'] * df['Volume']
    df['issue'] = np.where(((df['direction'] == 'S') & (df['Price'] < df['Bid Price'])) | (
            (df['direction'] == 'B') & (df['Price'] > df['Ask Price'])), 1, 0)

    df['vol_issue'] = np.where(((df['direction'] == 'S') & (df['Volume'] > df['Bid Size abs'])) | (
            (df['direction'] == 'B') & (df['Volume'] > df['Ask Size abs'])), 1, 0)

    df['quote_alive'] = df.groupby(['stock', 'date'])['adj mtime'].shift(-1) - df['adj mtime']
    df['quote_alive'] = df['quote_alive'].replace(0, np.nan)
    df['quote_alive'] = df['quote_alive'].fillna(method='ffill')

    df['value win'] = np.where(df['value'] > df['value'].quantile(0.95), df['value'].quantile(0.95), df['value'])
    #     df_cross = df[df['stock'].isin(cross_listed)]
    #     df_cross['value win'] = np.where(df_cross['value']>df_cross['value'].quantile(0.95),df_cross['value'].quantile(0.95),df_cross['value'])

    df['Quoted Spread'] = np.where(
        (df['Ask Price'] != 0) & (df['Bid Price'] != 0) & (df['Ask Price'] > df['Bid Price']),
        df['Ask Price'] - df['Bid Price'], np.nan)
    df['Quoted Spread_TW'] = df['Quoted Spread'] * df['quote_alive']
    df[f'at tick'] = np.where(
        ((df['Quoted Spread'] < 0.01) & (df['MidQuote'] > 0.2)) | (
                (df['Quoted Spread'] < 0.001) & (df['MidQuote'] < 0.2)), 1, 0)
    df[f'at tick time'] = df['at tick'] * df['quote_alive']
    b_sel = df.direction == 'B'
    df.loc[b_sel, f'Effective Spread'] = 2 * (df.loc[b_sel, f'Price'] - df.loc[b_sel, 'MidQuote'])
    s_sel = df.direction == 'S'
    df.loc[s_sel, f'Effective Spread'] = 2 * (df.loc[s_sel, 'MidQuote'] - df.loc[s_sel, f'Price'])

    df[f'Effective Spread_VW'] = df[f'Effective Spread'] * df[f'value']
    df.loc[b_sel, f'Effective Spread bps'] = 2 * (df.loc[b_sel, f'Price'] - df.loc[b_sel, 'MidQuote']) / df.loc[
        b_sel, 'MidQuote']
    df.loc[s_sel, f'Effective Spread bps'] = 2 * (df.loc[s_sel, 'MidQuote'] - df.loc[s_sel, f'Price']) / df.loc[
        b_sel, 'MidQuote']

    df[f'Effective Spread bps_VW'] = df[f'Effective Spread bps'] * df[f'value']

    trade_size = df.groupby(['date', 'stock'])['value'].mean().reset_index()
    trade_size = trade_size.rename(columns={'value': 'trade size'})
    df_trades = df[df['Price'].notnull()]
    Quoted_spread_TW = (df.groupby(['stock', 'date'])['Quoted Spread_TW'].sum() / \
                        df.groupby(['stock', 'date'])['quote_alive'].sum()).reset_index()
    Quoted_spread_TW = Quoted_spread_TW.rename(columns={0: 'quoted spread'})

    df['MidQuote_TW'] = df['MidQuote'] * df['quote_alive']

    midpoint_TW = (df.groupby(['stock', 'date'])['MidQuote_TW'].sum() / \
                   df.groupby(['stock', 'date'])['quote_alive'].sum()).reset_index()
    midpoint_TW = midpoint_TW.rename(columns={0: 'midpoint'})

    min_tick_TW = (df.groupby(['stock', 'date'])['at tick time'].sum() / \
                   df.groupby(['stock', 'date'])[
                       'quote_alive'].sum()).reset_index()
    min_tick_TW = min_tick_TW.rename(columns={0: 'tick time'})

    Value_weighted_Effective_Spread = (df.groupby(['stock', 'date'])['Effective Spread_VW'].sum() / \
                                       df[df['Effective Spread_VW'].notnull()].groupby(['stock', 'date'])[
                                           'value'].sum()).reset_index()

    Value_weighted_Effective_Spread = Value_weighted_Effective_Spread.rename(
        columns={0: 'value weighted effective spread'})

    Value_weighted_Effective_Spread_bps = ((df.groupby(['stock', 'date'])['Effective Spread bps_VW'].sum() / \
                                            df[df['Effective Spread bps_VW'].notnull()].groupby(['stock', 'date'])[
                                                'value'].sum()) * 10000).reset_index()
    Value_weighted_Effective_Spread_bps = Value_weighted_Effective_Spread_bps.rename(
        columns={0: 'value weighted effective spread bps'})

    # realized spread
    df = df.sort_values('adj mtime', ascending=True)
    df_realized = pd.merge_asof(df, df[['stock', 'date', 'adj mtime', 'MidQuote']], left_on=['mtime_1m'],
                                right_on=['adj mtime'],
                                by=['stock', 'date'], suffixes=('', '_1m_matched'),
                                allow_exact_matches=False)

    b_sel = df_realized.direction == 'B'
    df_realized.loc[b_sel, f'Realized Spread'] = 2 * (
                df_realized.loc[b_sel, f'Price'] - df_realized.loc[b_sel, 'MidQuote_1m_matched'])
    s_sel = df_realized.direction == 'S'
    df_realized.loc[s_sel, f'Realized Spread'] = 2 * (
                df_realized.loc[s_sel, 'MidQuote_1m_matched'] - df_realized.loc[s_sel, f'Price'])

    df_realized[f'Realized Spread_VW'] = df_realized[f'Realized Spread'] * df_realized[f'value']
    df_realized.loc[b_sel, f'Realized Spread bps'] = 2 * (
                df_realized.loc[b_sel, f'Price'] - df_realized.loc[b_sel, 'MidQuote_1m_matched']) / df_realized.loc[
                                                         b_sel, 'MidQuote_1m_matched']
    df_realized.loc[s_sel, f'Realized Spread bps'] = 2 * (
                df_realized.loc[s_sel, 'MidQuote_1m_matched'] - df_realized.loc[s_sel, f'Price']) / df_realized.loc[
                                                         s_sel, 'MidQuote_1m_matched']

    df_realized[f'Realized Spread bps_VW'] = df_realized[f'Realized Spread bps'] * df_realized[f'value']

    Value_weighted_Realized_Spread = (df_realized.groupby(['stock', 'date'])['Realized Spread_VW'].sum() / \
                                      df_realized[df_realized['Realized Spread_VW'].notnull()].groupby(
                                          ['stock', 'date'])['value'].sum()).reset_index()

    Value_weighted_Realized_Spread = Value_weighted_Realized_Spread.rename(
        columns={0: 'value weighted realized spread'})

    Value_weighted_Realized_Spread_bps = ((df_realized.groupby(['stock', 'date'])['Realized Spread bps_VW'].sum() / \
                                           df_realized[df_realized['Realized Spread bps_VW'].notnull()].groupby(
                                               ['stock', 'date'])['value'].sum()) * 10000).reset_index()
    Value_weighted_Realized_Spread_bps = Value_weighted_Realized_Spread_bps.rename(
        columns={0: 'value weighted realized spread bps'})

    # compute market order
    market_order = df.groupby(['stock', 'date', 'adj mtime'])['value'].sum().reset_index()

    daily_market_order = market_order.groupby(['stock', 'date'])['value'].mean().reset_index()
    daily_market_order = daily_market_order.rename(columns={'value': 'market order value'})

    # compute price order

    df['bid diff'] = df.groupby(['stock', 'venue', 'date'])['Bid Price'].diff()
    df['bid order'] = np.where(df['bid diff'] == 0, df.groupby(['stock', 'venue', 'date'])['Bid Size abs'].diff(),
                               np.nan)
    df['bid order'] = np.where(df['bid diff'] > 0, df['Bid Size abs'], df['bid order'])

    df['bid order'] = np.where(df['bid order'] > 0, df['bid order'], np.nan)

    df['ask diff'] = df.groupby(['stock', 'venue', 'date'])['Ask Price'].diff()
    df['ask order'] = np.where(df['ask diff'] == 0, df.groupby(['stock', 'venue', 'date'])['Ask Size abs'].diff(),
                               np.nan)
    df['ask order'] = np.where(df['ask diff'] < 0, df['Ask Size abs'], df['ask order'])
    df['ask order'] = np.where(df['ask order'] > 0, df['ask order'], np.nan)

    daily_bid_order = df.groupby(['stock', 'date'])['bid order'].mean().reset_index()
    daily_bid_order = daily_bid_order.rename(columns={'bid order': 'bid order value'})

    daily_ask_order = df.groupby(['stock', 'date'])['ask order'].mean().reset_index()
    daily_ask_order = daily_ask_order.rename(columns={'ask order': 'ask order value'})

    daily_order = daily_bid_order.merge(daily_ask_order, on=['stock', 'date'])

    num_quote_update = df.groupby(['stock', 'date'])['Bid Price'].count().reset_index()
    num_quote_update = num_quote_update.rename(columns={'Bid Price': 'num_quote_update'})

    num_trades = df.groupby(['stock', 'date'])['Price'].count().reset_index()
    num_trades = num_trades.rename(columns={'Price': 'num_trades'})

    daily_value['date'] = pd.to_datetime(daily_value['date'])
    Quoted_spread_TW['date'] = pd.to_datetime(Quoted_spread_TW['date'])

    min_tick_TW['date'] = pd.to_datetime(min_tick_TW['date'])
    Value_weighted_Effective_Spread['date'] = pd.to_datetime(Value_weighted_Effective_Spread['date'])
    Value_weighted_Effective_Spread_bps['date'] = pd.to_datetime(Value_weighted_Effective_Spread_bps['date'])
    Value_weighted_Realized_Spread['date'] = pd.to_datetime(Value_weighted_Realized_Spread['date'])
    Value_weighted_Realized_Spread_bps['date'] = pd.to_datetime(Value_weighted_Realized_Spread_bps['date'])
    daily_market_order['date'] = pd.to_datetime(daily_market_order['date'])
    daily_order['date'] = pd.to_datetime(daily_order['date'])
    num_quote_update['date'] = pd.to_datetime(num_quote_update['date'])
    num_trades['date'] = pd.to_datetime(num_trades['date'])
    midpoint_TW['date'] = pd.to_datetime(midpoint_TW['date'])

    all_metric = daily_value.merge(Quoted_spread_TW, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(min_tick_TW, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(Value_weighted_Effective_Spread, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(Value_weighted_Effective_Spread_bps, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(Value_weighted_Realized_Spread, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(Value_weighted_Realized_Spread_bps, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(daily_market_order, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(daily_order, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(num_quote_update, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(num_trades, on=['stock', 'date'], how='outer')
    all_metric = all_metric.merge(midpoint_TW, on=['stock', 'date'], how='outer')
    return (all_metric, df_trades)

import os
os.chdir('C:/Users/anche/NZ/trth data/AORD TAQ')
metric_list = []
trades_list = []
for file in os.listdir('C:/Users/anche/NZ/trth data/AORD TAQ'):
    try:
        metric_list.append(metric(file)[0])
        trades_list.append(metric(file)[1])
    except:
        print(file)
all_metrics = pd.concat(metric_list)

all_metrics.to_csv('C:/Users/anche/NZ/tables v2/AU metric allord.csv')


all_trades = pd.concat(trades_list)
all_trades.to_csv('C:/Users/anche/NZ/tables v2/AU trades.csv')


