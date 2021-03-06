import sys
import os
import datetime

class PairMining(object):
    def __init__(self, data_dir):
        self.data_director = data_dir
        self.stock_info = dict()

    def loadStockInfo(self, start_date):
        cmd = 'ls %s' % self.data_director
        fileList = os.popen(cmd).readlines()
        for file in fileList:
            file = file.rstrip('\n')
            self.loadOneStockInfo(file, start_date)
        return True

    def loadOneStockInfo(self, fileName, start_date):
        start_date = int(start_date)
        fin = open(self.data_director + fileName, 'r')
        stockId = fileName
        self.stock_info[stockId] = dict()
        for line in fin:
            line = line.rstrip('\n')
            items = line.split('\t')
            date = items[0]
            date = date.replace('/', '')
            increase_price = float(items[1])
            if int(date) < start_date:
                continue
            else:
                self.stock_info[stockId][date] = increase_price
        fin.close()
        return True

    def pairMining(self, simFunction):
        #get stockId list
        stockId_list = list()
        cmd = 'ls %s' % self.data_director
        fileList = os.popen(cmd).readlines()
        for file in fileList:
            stockId = file.strip()
            stockId_list.append(stockId)

        stockId_list.sort()
        #calculate similarity distance between any two stocks
        for i in range(0, len(stockId_list) - 1):
            for j in range(i + 1, len(stockId_list)):
                stock_id_1 = stockId_list[i]
                stock_id_2 = stockId_list[j]
                similarity = self.calculateSimilarity(stock_id_1, stock_id_2, simFunction)
                print stock_id_1 + 'VS' + stock_id_2 + '\t' + str(similarity)

        return True

    def calculateSimilarity(self, stock_id_1, stock_id_2, simFunction):
        #stock_1_info is a dict, key:date, value:increase_price
        stock_1_info = self.stock_info[stock_id_1]
        stock_2_info = self.stock_info[stock_id_2]
        date_stock_1_set = set(stock_1_info.keys())
        date_stock_2_set = set(stock_2_info.keys())
        price_list_1 = list()
        price_list_2 = list()
        for date in sorted(date_stock_1_set & date_stock_2_set):
            price_list_1.append(stock_1_info[date])
            price_list_2.append(stock_2_info[date])
        if len(price_list_1) <= 50:
            return 0
        if simFunction == 'cos':
            similarity = self.cosineBasedDistance(price_list_1, price_list_2)
        elif simFunction == 'euc':
            similarity = self.euclideanBasedDistance(price_list_1, price_list_2)
        elif simFunction == 'pea':
            similarity = self.pearsonBasedDistance(price_list_1, price_list_2)
        return similarity

    def cosineBasedDistance(self, price_list_1, price_list_2):
        if len(price_list_1) != len(price_list_2):
            return False

        f_sum_xx = 0
        f_sum_yy = 0
        f_sum_xy = 0
        for i in range(0, len(price_list_1)):
            f_sum_xx += pow(price_list_1[i], 2)
            f_sum_yy += pow(price_list_2[i], 2)
            f_sum_xy += price_list_1[i] * price_list_2[i]
        simi = f_sum_xy / (pow(f_sum_xx, 0.5) * pow(f_sum_yy, 0.5))
        return simi

    def pearsonBasedDistance(self, price_list_1, price_list_2):
        if len(price_list_1) != len(price_list_2):
            return False

        sum1 = sum(price_list_1)
        sum2 = sum(price_list_2)
        length = len(price_list_1)
        sum1Sq = sum([pow(price_list_1[i], 2) for i in range(0, length)])
        sum2Sq = sum([pow(price_list_2[i], 2) for i in range(0, length)])
        pSum = sum([price_list_1[i] * price_list_2[i] for i in range(0, length)])
        fenzi = pSum - (sum1 * sum2 / length)
        fenmu = pow((sum1Sq -  pow(sum1, 2) / length) * (sum2Sq - pow(sum2, 2) / length), 0.5)
        if fenmu == 0:
            return 0
        simi = fenzi / fenmu
        return simi

    def euclideanBasedDistance(self, price_list_1, price_list_2):
        if len(price_list_1) != len(price_list_2):
            return False

        f_sum_dist = 0
        for i in range(0, len(price_list_1)):
            f_sum_dist += pow((price_list_1[i] - price_list_2[i]), 2)
        simi = 1 / (1 + pow(f_sum_dist / len(price_list_1), 0.5))
        return simi

    def run(self, start_date, simFunction):
        self.loadStockInfo(start_date)
        self.pairMining(simFunction)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:', sys.argv[0], '<data_dir> <start_date> <similarity_type: cos for cosine and euc for euclidean and pea for pearson>'
        sys.exit(0)
    if not sys.argv[3] in ['cos', 'euc', 'pea']:
        print 'similarity type is illegal. cos for cosine and euc for euclidean and pea for pearson'
        sys.exit(0)
    pairMiningObj = PairMining(sys.argv[1])
    pairMiningObj.run(sys.argv[2], sys.argv[3])
    

