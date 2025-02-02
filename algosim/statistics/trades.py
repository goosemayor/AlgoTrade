import numpy as np
import pandas as pd
import os
import yaml
from tqdm import tqdm
from copy import deepcopy
#from numba import jit
import pdb

class Trades(object):
    """
    统计每个标的物平均每天买入和卖出的数量, 以及平均交易金额，还手率
    """
    def __init__(self, account_path):
        self.account_path = account_path
        print('[Statistics][Trades] init ...')
        self.stats = {}

    def run(self):
        self.load_fill()
        self.cal_trades()
        self.cal_bps()
        self.store()


    def load_fill(self):
        print('[Statistics][Trades] load_fill ...')
        self.history_fill_df = pd.read_csv(os.path.join(self.account_path, 'exec', 'history_fill.csv'), dtype={'证券代码':np.str}, index_col=0)
        self.history_fill_df.index = self.history_fill_df['成交日期'].values.astype('str')
        
        self.BuyPrice_df = pd.read_csv(os.path.join(self.account_path, 'price', 'BuyPrice01.csv'), index_col=0)
        self.SellPrice_df = pd.read_csv(os.path.join(self.account_path, 'price', 'SellPrice01.csv'), index_col=0)
        self.BuyPrice_df[self.BuyPrice_df==0] = np.nan
        self.BuyPrice_df = self.BuyPrice_df.fillna(method='ffill')
        self.SellPrice_df[self.SellPrice_df==0] = np.nan
        self.SellPrice_df = self.SellPrice_df.fillna(method='ffill')

        
    def cal_trades(self):
        self.stats['daily_buy_trades_amount'] = int(self.history_fill_df.loc[self.history_fill_df['买卖方向']=='买']['成交额'].sum())

        self.stats['daily_sell_trades_amount'] = int(self.history_fill_df.loc[self.history_fill_df['买卖方向']=='卖']['成交额'].sum())
        self.stats['daily_trades_amount'] = self.stats['daily_buy_trades_amount'] + self.stats['daily_sell_trades_amount']
        self.stats['total_trades_nums'] = self.history_fill_df.shape[0]
        

                

    def cal_bps(self):
        """
        将买卖每笔对应起来，统计每笔交易的bps
        """
        print('[Statistics][Trades] cal_bps ...')
        self.bps_df = pd.DataFrame()
        for code in tqdm(self.history_fill_df['证券代码'].unique()):
            df = self.history_fill_df.loc[self.history_fill_df['证券代码'] == code]
            df_5 = df.loc[df['买卖方向'] == '买'][['成交日期','成交价格', '成交数量', '成交额']]
            df_6 = df.loc[df['买卖方向'] == '卖'][['成交日期','成交价格', '成交数量', '成交额']]
            if df_5['成交数量'].sum() > df_6['成交数量'].sum():
                df_6 = df_6.append(pd.DataFrame({code:{'成交价格':self.BuyPrice_df.iloc[-1][code],\
                                                       '成交日期':str(self.BuyPrice_df.index.values[-1]),\
                                                        '成交数量':df_5['成交数量'].sum() - df_6['成交数量'].sum(),\
                                                      '成交额':self.BuyPrice_df.iloc[-1][code] *(df_5['成交数量'].sum()-df_6['成交数量'].sum())}}).T, sort=False)
            elif df_5['成交数量'].sum() < df_6['成交数量'].sum():
                # 卖比买多
                df_5 = df_5.append(pd.DataFrame({code:{'成交价格':self.SellPrice_df.iloc[-1][code],\
                                                       '成交日期':str(self.SellPrice_df.index.values[-1]),\
                                                      '成交数量':df_6['成交数量'].sum()-df_5['成交数量'].sum(),\
                                                      '成交额':self.SellPrice_df.iloc[-1][code] *(df_6['成交数量'].sum()-df_5['成交数量'].sum())}}).T, sort=False)

            bps = {code: {'bps':(df_6['成交额'].sum()/df_5['成交额'].sum() - 1)*10000,
                   '买成交数量':df_5['成交数量'].sum(),
                   '卖成交数量':df_6['成交数量'].sum(),
                    '买成交额':df_5['成交额'].sum(),
                    '卖成交额':df_6['成交额'].sum()}}
            self.bps_df = self.bps_df.append(pd.DataFrame(bps).T)
        return
    
    def store(self):
        self.store_path = os.path.join(self.account_path, 'statistics')
        if not os.path.exists(self.store_path):
            os.mkdir(self.store_path)
            
        with open(os.path.join(self.store_path, 'trades.yaml').replace(':', '-'), 'w') as f:
            yaml.dump(self.stats, f, encoding='unicode', sort_keys=False)
        self.bps_df.to_csv(os.path.join(self.store_path, 'bps.csv'))
        return

