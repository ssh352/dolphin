#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dolphin.OnesideDolphin import OnesideDolphin
from dolphin.Util import get_minutes_to_closemarket
#$from dolphin.Util import log
import os.path
import time


#########################################################################################

class Oneside_offline_experiment(OnesideDolphin):
    yesterday_position_path = '/tmp/OnesideDolphin/YesterdayPosition_TEST/'
    os.system("mkdir -p " + yesterday_position_path)

    def __init__(self, pairid, data_feeder, account, today_date, strategy_name, log_name):
        OnesideDolphin.__init__(self, pairid, data_feeder, account, log_name)
        self.max_stock_delta = [0.0] * 3
        self.today_date = today_date
        self.yesterday_position_file = "/tmp/OnesideDolphin/YesterdayPosition_TEST/" + strategy_name + "_" + self.pairid
        self.log("debug", "init!!!\n"+self.yesterday_position_file)
        if not os.path.isfile(self.yesterday_position_file):
            self.init_status()
        self.new_day()
        self.load_status()

    @staticmethod
    def before(pairid):
        yesterday_position_file = Oneside_offline_experiment.yesterday_position_path + pairid
        #open(yesterday_position_file, 'w').write(str((0, 0, 0, 0, 0, 0)))
    
    @staticmethod
    def after(pairid):
        pass

    def get_stock_data(self):
        tmp_stockdata_1 = self.stockdata_1
        tmp_stockdata_2 = self.stockdata_2
        self.stockdata_1 = self.data_feeder.get_data(self.stockid_1)
        self.stockdata_2 = self.data_feeder.get_data(self.stockid_2)

        if None in (self.stockdata_1, self.stockdata_2):
            self.stockdata_1 = tmp_stockdata_1
            self.stockdata_2 = tmp_stockdata_2
            return False
       
        # 计算得到当前时间，距离当天收市的时间，分钟表示
        self.minutes_to_closemarket = get_minutes_to_closemarket(self.stockdata_1['time'])
        if self.minutes_to_closemarket == -1:
            return -1
        elif self.minutes_to_closemarket == 1 and not self.today_close_tag:
            self.today_close_tag = True
            self.close_today()
 
        return True

#########################################################################################
''' 当天结束的收盘价涨跌幅如果相差超过阈值，则在第二天不进行买入操作 '''
class Buy_dependon_yest(Oneside_offline_experiment):
    def check_stop_buy(self):
        if self.minutes_to_closemarket <= 2 and abs(self.current_stock_delta[1] - self.current_stock_delta[2]) > 0.05:
            self.stop_buy_cnt += 1
            if self.stop_buy_cnt >= 3:
                self.log('debug', 'self.stop_buy!!! %s %s' % (str(self.current_stock_delta[1]), str(self.current_stock_delta[2])))
                self.stop_buy = 1
            else:
                self.stop_buy = 0
 
    def close_today(self):
        # save today's trade record
        today_trades = self.account.get_today_trades()
        if len(today_trades) == 0:
            today_trades = self.account.get_today_trades()

        for trade in today_trades:
            if trade[2] in (self.stockid_1, self.stockid_2):
                self.log('realdeal_info', '\t'.join([str(item) for item in trade]))

        # update position information
        self.update_volatility()
        self.dump_status(False)

#########################################################################################
''' 买高还是买低的策略比较 '''
class Buy_low(Oneside_offline_experiment):
    def __init__(self, pairid, data_feeder, account, today_date):
        Oneside_offline_experiment.__init__(self, pairid, data_feeder, account, today_date)
        self.buy_strategy = self.buy_strategy_category['Buy_low']


class Buy_high(Oneside_offline_experiment):
    def __init__(self, pairid, data_feeder, account, today_date):
        Oneside_offline_experiment.__init__(self, pairid, data_feeder, account, today_date)
        self.buy_strategy = self.buy_strategy_category['Buy_high']


#########################################################################################
''' 测试各种入场逻辑 '''
class Test_enter_buystock_rise(Oneside_offline_experiment):
    def if_enter_market(self, want_buy_stock_index):
        return self.current_stock_delta[3-want_buy_stock_index] >= 0.025 \
                and self.max_delta_of_today[3-want_buy_stock_index]-self.current_stock_delta[3-want_buy_stock_index] < 0.01 \
                and (self.current_stock_delta[want_buy_stock_index] - self.min_delta_of_today[want_buy_stock_index] >= 0.01 or self.current_stock_delta[want_buy_stock_index] >= 0) \
                and self.current_stock_delta[want_buy_stock_index] < 0.025 \
                and self.current_delta_relative_prices[want_buy_stock_index] >= self.get_delta_threshold_of_entering_market()
'''从高处掉下不入'''
class Test_enter_20141219(Oneside_offline_experiment):
    def if_enter_market(self, want_buy_stock_index):
        if self.current_stock_delta[3-want_buy_stock_index] >= 0.025 \
            and self.max_delta_of_today[3-want_buy_stock_index]-self.current_stock_delta[3-want_buy_stock_index] < 0.01 \
            and (self.current_stock_delta[want_buy_stock_index] - self.min_delta_of_today[want_buy_stock_index] >= 0.01 or self.current_stock_delta[want_buy_stock_index] >= 0) \
            and self.current_stock_delta[want_buy_stock_index] < 0.025 \
            and self.current_delta_relative_prices[want_buy_stock_index] >= self.get_delta_threshold_of_entering_market() \
            and self.max_delta_of_today[want_buy_stock_index] - self.current_stock_delta[want_buy_stock_index] < 0.01:
            debug_data = []
            debug_data.append(str(self.current_stock_delta[3-want_buy_stock_index]))
            debug_data.append(str(self.max_delta_of_today[3-want_buy_stock_index]-self.current_stock_delta[3-want_buy_stock_index]))
            debug_data.append(str(self.current_stock_delta[want_buy_stock_index] - self.min_delta_of_today[want_buy_stock_index]))
            debug_data.append(str(self.current_stock_delta[want_buy_stock_index]))
            debug_data.append(str(self.current_stock_delta[want_buy_stock_index]))
            debug_data.append(str(self.current_delta_relative_prices[want_buy_stock_index]) + " " + str(self.get_delta_threshold_of_entering_market()))
            self.log("info_buy", "买入\n" + "\n".join(debug_data))
            return True
        else:
            return False

#########################################################################################
''' 清仓时机的策略比较 '''

class Test_leave_20150129(Oneside_offline_experiment):
    def if_leave_time_right(self):
#        if self.minutes_to_closemarket > 235:
#            return False
        #self.log("debug", "if_leave_time_right: %s, %s, %s"%(str(self.minutes_to_closemarket), str(self.if_enter_triggered), str(self.want_sell_index)))
        if self.minutes_to_closemarket <= 7:
            return True
        if not self.if_enter_triggered:
            if self.current_stock_delta[self.want_sell_index] >= 0.025 \
                or self.current_delta_relative_prices[3-self.want_sell_index] >= 0.01 \
                or self.minutes_to_closemarket < 118:

                debug_data = []
                debug_data.append(str(self.current_stock_delta[self.want_sell_index]))
                debug_data.append(str(self.current_delta_relative_prices[3-self.want_sell_index]))
                debug_data.append(str(self.minutes_to_closemarket))
                self.log("info_sell", "卖出trigger\n" + "\n".join(debug_data))
                self.if_enter_triggered = 1
            return False
        else:
            stock_data = (None, self.stockdata_1, self.stockdata_2)[self.want_sell_index]
            if stock_data['sell_1_price'] == 0:
                return False
            if (stock_data['sell_1_price'] - stock_data['buy_1_price']) / stock_data['sell_1_price'] <= 0.0025 \
                and self.current_stock_delta[self.want_sell_index] < self.last_stock_delta[self.want_sell_index] \
                and self.max_delta_of_today[self.want_sell_index] - self.current_stock_delta[self.want_sell_index] >= 0.005:
                debug_data = []
                debug_data.append(str((stock_data['sell_1_price'] - stock_data['buy_1_price']) / stock_data['sell_1_price']))
                debug_data.append(str(self.current_stock_delta[self.want_sell_index]) + " " + str(self.last_stock_delta[self.want_sell_index]))
                debug_data.append(str(self.max_delta_of_today[self.want_sell_index] - self.current_stock_delta[self.want_sell_index]))
                self.log("info_sell", "卖出\n" + "\n".join(debug_data))
                return True
            else:
                return False


class Test_leave_fix_time(Oneside_offline_experiment):
    def if_leave_time_right(self):
        return self.minutes_to_closemarket <= 5

class Test_leave_tomorrow_close(Oneside_offline_experiment):
    def if_leave_time_right(self):
        stock_data = (None, self.stockdata_1, self.stockdata_2)[self.want_sell_index]
        if stock_data['today_open_price'] > self.want_sell_stock_enter_price:
            return self.minutes_to_closemarket <= 5
        else:
            return self.minutes_to_closemarket <= 230


class Test_leave_chaseup_sellbuygap(Oneside_offline_experiment):
    def if_leave_time_right(self):
        if self.minutes_to_closemarket <= 5:
            return True
        stock_data = (None, self.stockdata_1, self.stockdata_2)[self.want_sell_index]
        if stock_data['current_price'] / self.want_sell_stock_enter_price < 1 and self.minutes_to_closemarket <= 235:
            return True
        if not self.if_enter_triggered:
            if self.current_stock_delta[self.want_sell_index] >= 0.025 or self.current_delta_relative_prices[3-self.want_sell_index] >= 0.01:
                self.if_enter_triggered = 1
            return False
        else:
            if stock_data['sell_1_price'] == 0:
                return False
            return (stock_data['sell_1_price'] - stock_data['buy_1_price']) / stock_data['sell_1_price'] <= 0.0025 \
                and self.current_stock_delta[self.want_sell_index] < self.last_stock_delta[self.want_sell_index] \
                and self.max_delta_of_today[self.want_sell_index] - self.current_stock_delta[self.want_sell_index] >= 0.005



class Test_leave_use_delta(Oneside_offline_experiment):
    def if_leave_time_right(self):
        if self.minutes_to_closemarket >= 230:
            return False
        if self.minutes_to_closemarket <= 5:
            return True

        average_volatility = sum(self.volatility)/len(self.volatility)
        leave_rise_threshold = 0.0225
        if average_volatility <= 0.04:
            leave_rise_threshold = 0.015
        elif average_volatility >= 0.06:
            leave_rise_threshold = 0.03
        else:
            leave_rise_threshold = 0.015 + (average_volatility-0.04)*3/4

        if not self.if_enter_triggered:
            if self.current_stock_delta[self.want_sell_index] >= leave_rise_threshold or self.current_delta_relative_prices[3-self.want_sell_index] >= 0.01:
                self.if_enter_triggered = 1
            return False
        else:
            stock_data = (None, self.stockdata_1, self.stockdata_2)[self.want_sell_index]
            if stock_data['sell_1_price'] == 0:
                return False
            return (stock_data['sell_1_price'] - stock_data['buy_1_price']) / stock_data['sell_1_price'] <= 0.0025 \
                and self.current_stock_delta[self.want_sell_index] < self.last_stock_delta[self.want_sell_index] \
                and self.max_delta_of_today[self.want_sell_index] - self.current_stock_delta[self.want_sell_index] >= 0.005


#########################################################################################
''' 考虑要不要加入news notification '''
class Test_not_check_news(Oneside_offline_experiment):
    ''' 检查这个pair是否有重大新闻，如有则不进行交易 '''
    def check_big_news(self):
        return

