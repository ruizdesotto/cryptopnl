import pandas as pd
import numpy as np
from decimal import Decimal as D
from cryptopnl.wallet.wallet import wallet 
from cryptopnl.price_api.prices import prices
from cryptopnl.utils.Logger import Logger
from cryptopnl.calc.balanceCheck import checkBalanceWithFees


EUR = "ZEUR"
BTC = "XXBT"
ETH = "XETH"
LTC = "XLTC"
CRYPTO = [BTC, LTC, ETH]

def dec(num):
    return D(str(num))

"Weighted average cost method (CUMP in french)"    
class cumpCalculator:
    
    def __init__(self, ledgerName, tradeName, priceName):
        self.trades = self.readCSV(tradeName)
        self.ledger = self.readCSV(ledgerName)
        self.tradeIndex = 0
        self.log = Logger()

        self.prices = prices(priceName, CRYPTO)
        self.wallet = wallet(CRYPTO)

        self.totalGains = {}
        for year in range(2017, 2022):
            self.totalGains[str(year)] = []        

    def readCSV(self, file):
        csvFile = pd.read_csv(file, thousands =',')
        csvFile['time'] = pd.to_datetime(csvFile['time'])
        return csvFile

    def processNextTrade(self):
        nextTrade = self.trades.loc[self.tradeIndex]
        pair = nextTrade.pair 
        order_type = nextTrade.type
        
        # Get corresponding ledgers
        (l0, l1) = nextTrade.ledgers.split(',')        
        l0 = self.ledger.loc[self.ledger['txid'] == l0].iloc[0]
        l1 = self.ledger.loc[self.ledger['txid'] == l1].iloc[0]
        ining = l0 if l0.amount > 0 else l1
        outing = l1 if l0.amount > 0 else l0

        # Fiat to Cryto buy 
        if pair.endswith(EUR) and order_type == "buy":
            self.fiat2crypto(nextTrade, ining, outing)
        # Fiat to Crypto sell
        elif pair.endswith(EUR) and order_type == "sell":
            self.crypto2fiat(nextTrade, outing, ining)
        # Crypto to crypto 
        else:
            self.crypto2crypto(nextTrade, ining, outing)

        walletValue = dec(self.wallet.getCurrentValue(self.prices, nextTrade.time))
        self.log.logTrade(outing, ining)
        self.log.logWallet(walletValue, self.wallet)

    def fiat2crypto(self, trade, crypto, fiat):
        assert(crypto.amount == trade.vol) 

        self.wallet.add(crypto.asset, 
                        self.chunk(dec(crypto.amount),dec(trade.price),
                                   dec(crypto.fee)))
        self.wallet.updateCost(dec(abs(fiat.amount)) + dec(fiat.fee))

    def crypto2fiat(self, trade, crypto, fiat):
        assert(abs(crypto.amount) == trade.vol)

        outAmount = - dec(crypto.amount) # + dec(crypto.fee) 
        inCash = dec(fiat.amount) - dec(fiat.fee)
        CashWFee = dec(fiat.amount) # IMPORTANT to calculate proportion chi

        self.prices.addPrice(crypto.asset, trade.time, str(trade.price))
        walletValue = self.wallet.getCurrentValue(self.prices, trade.time)
        walletCost = self.wallet.getCost()

        self.wallet.take(crypto.asset, outAmount, inCash) 
        chi = round(CashWFee / walletValue, 5)
        self.totalGains[str(trade.time.year)].append(inCash - chi*walletCost)

        self.wallet.setCost((D("1") - chi)*walletCost)

    def crypto2crypto(self, trade, ining, outing):        

        cryptoBought = ining.asset
        cryptoSold = outing.asset
        
        bought = dec(ining.amount) - dec(ining.fee)
        sold = -dec(outing.amount) + dec(outing.fee)

        # Approx price of bought crypto (it really doesnt matter)
        pr = dec(self.prices.getPrice(cryptoBought, trade.time))
        boughtInFiat = bought*pr

        self.wallet.take(cryptoSold, sold, boughtInFiat)
        self.wallet.add(cryptoBought, self.chunk(bought, pr))

    def chunk(self, vol, price, fee = dec(0)):
        return {"vol": vol-fee, "price": price}

    def next(self):
        self.tradeIndex +=1

    def processAll(self, nTrades = -1):
        if nTrades < 0:
            nTrades = self.trades.shape[0]
        for _ in range(nTrades):
            self.processNextTrade()
            self.next()
    
    def totalSurplus(self):
        totsies = dec(0) 
        for year in self.totalGains:
            totsies += dec(np.sum(self.totalGains[year]))

        return totsies
        

def doCumpCalculation(ledgers, trades, prices):
    plc = cumpCalculator(ledgers, trades,prices)

    # Processing all trades 
    plc.processAll() 
    plc.log.save()
    # print(plc.log.getTrades())
    gains = plc.totalSurplus()
    cost = plc.wallet.getCost()
    print(f"Total gains are : {gains}")
    print(f"Remaining cost is : {cost}")
    print(f"Final Gains : {gains-cost}")
    print(plc.totalGains)
    # print(plc.log.getTrades())
    # Verifying balance

    (bal, ledgerBal) = checkBalanceWithFees(plc.ledger)
    # print(f"Calculated balance is {bal}")
    # print(f"Ledger balance is {ledgerBal}")
    assert(bal==ledgerBal)

""" Todo

    Both methods : average value and fifo
    Average value : consider as well cost value per coin
"""