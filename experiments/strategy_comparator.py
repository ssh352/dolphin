#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import mktime, localtime, strftime, strptime
from collections import defaultdict

from dolphin import Account, StockDataFeeder, Util
from dolphin.Account import VirtualAccount
from dolphin.StockDataFeeder import StockHistoryMySQLDataFeeder

import OnesideStrategy as ST
from OnesideStrategy import Oneside_offline_experiment as EX

from conf.dbconf import dbconf

class NoneStrategy:
    pass


def compare_strategy(pairid, start_date, end_date, S1, S2):
    r1 = run_strategy( pairid, start_date, end_date, S1)
    r2 = run_strategy( pairid, start_date, end_date, S2)
    show_result( pairid, r1, r2, S1, S2 )


def show_result( pairid, r1, r2, S1, S2 ):
    print '**********************************************************'
    print '**************** pairid: ' + pairid + ' ***************'
    print '{0:15s} {1:15s} {2:15s}'.format('', S1.__name__, S2.__name__)
    for today_date in sorted(r1.keys()):
        print '{0:15s} {1:15.2f}  {2:15.2f}'.format(today_date, r1[today_date], r2[today_date])


def run_strategy( pairid, start_date, end_date, Strategy ):
    if Strategy is NoneStrategy:
        return defaultdict(int)

    EX.before(pairid)

    result = {}
    today_date = start_date
    while today_date <= end_date:
        if not Util.if_close_market_today(today_date):
            data_feeder = StockHistoryMySQLDataFeeder(pairid, today_date)
            account = VirtualAccount()
            s = Strategy(pairid, data_feeder, account, today_date)
            s.run()
            result[today_date] = s.get_virtual_profit()
        today_date = strftime('%Y-%m-%d', localtime(mktime(strptime(today_date+' 00:00:00', '%Y-%m-%d %H:%M:%S')) + 24*3600 ))
    
    EX.after(pairid)

    profits = [v for k, v in result.iteritems()]
    total_profit = sum( profits )
    total_days = len( profits )
    deal_days = len( [v for v in profits if v != 0] )
    success_days = len( [v for v in profits if v > 0] )
    result['deal_days'] = deal_days
    result['success_days'] = success_days
    result['total_days'] = total_days
    result['total_profit'] = total_profit
    return result


candidate_stock_pairs = Util.candidate_stock_pairs

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) != 4:
        print "usage: python strategy_comparator.py pairid start_date end_date"
        sys.exit(-1)

    pairid = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    Util.reconnect_database(dbconf)
    Util.disable_store2database()
    os.system( 'rm -f ./dolphin/log/Experiment_'+pairid )
    Util.init_logging('Experiment_'+pairid)

    S1 = ST.Test_leave_chaseup_sellbuygap
    S2 = NoneStrategy

    if pairid.lower() == 'all':
        for pairid in candidate_stock_pairs:
            compare_strategy( pairid, start_date, end_date, S1, S2 )
    else:
        compare_strategy( pairid, start_date, end_date, S1, S2 )
