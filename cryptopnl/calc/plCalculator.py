import pandas as pd
import numpy as np
from decimal import Decimal as D
from cryptopnl.wallet.wallet import wallet
from cryptopnl.price_api.prices import prices
from cryptopnl.utils.Logger import Logger
from cryptopnl.calc.balanceCheck import checkBalanceWithFees

class plCalculator:
    
    def __init__(self, ledgerName, tradeName, priceName):
        self.ledger = self.readCSV(ledgerName)
        self.trades = self.readCSV(tradeName)
        self.log = Logger()
        self.tradeIndex = 0

        self.prices = prices(priceName, ["XBT", "ETH", "LTC"])
        self.wallet = wallet(["XBT", "ETH", "LTC"])
        self.fees = {"XXBT": [], "XETH": [], "XLTC": []}
        self.feesInEur = {"ZEUR": [], "XXBT": [], "XETH": [], "XLTC": []}

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

        # Case 1 Fiat to Cryto buy 
        if pair.endswith("EUR") and order_type == "buy":
            self.fiat2crypto(nextTrade, ining, outing)
        # Case 2 Fiat to Crypto sell
        elif pair.endswith("EUR") and order_type == "sell":
            self.crypto2fiat(nextTrade, outing, ining)
        # Case 3 Crypto to crypto ?
        else:
            self.crypto2crypto(nextTrade, ining, outing)


    def fiat2crypto(self, trade, crypto, fiat):
        base = trade.pair[1:4]
        quote = trade.pair[5:]

        assert(crypto.amount == trade.vol) 
        self.wallet.add(base, self.chunk(crypto.amount, trade.price))

        # Saving fees
        if fiat.fee > 0:  self.feesInEur[fiat.asset].append(fiat.fee) 
        if crypto.fee > 0: 
            self.fees[crypto.asset].append(crypto.fee) 
            self.feesInEur[crypto.asset].append(crypto.fee*trade.price) 
        
        self.log.logTrade(f"{self.tradeIndex}: {trade.cost} of FIAT {quote} ==> {trade.vol} Crypto {base}")

    def crypto2fiat(self, trade, crypto, fiat):
        base = trade.pair[1:4]
        quote = trade.pair[5:]

        assert(abs(crypto.amount) == trade.vol)
        boughtInFiat = trade.vol*trade.price 

        # Possible gains/losses
        gains = self.wallet.take(base, D(str(trade.vol)), D(str(boughtInFiat)))
        self.totalGains[str(trade.time.year)].append(gains)

        # Saving fees
        if fiat.fee > 0:  self.feesInEur[fiat.asset].append(fiat.fee) 
        if crypto.fee > 0: 
            self.fees[crypto.asset].append(crypto.fee) 
            self.feesInEur[crypto.asset].append(crypto.fee*trade.price) 

        self.log.logTrade(f"{self.tradeIndex}: {trade.vol} of {base} ==> {boughtInFiat} of {quote} (GAINS : {gains})")

    def crypto2crypto(self, trade, ining, outing):        

        if trade.type == "buy":
            cryptoBought = trade.pair[1:4]
            cryptoSold = trade.pair[5:]
            sold = trade.cost
            bought = trade.vol            
        else:
            cryptoSold = trade.pair[1:4]
            cryptoBought = trade.pair[5:]
            sold = trade.vol 
            bought = trade.cost
        assert(ining.amount==bought)
        assert(-outing.amount==sold)

        # Substract fees
        bought = ining.amount - ining.fee
        sold = -outing.amount + outing.fee
        # Approx price of bought crypto (it really doesnt matter, except for fees ?)
        pr = float(self.prices.getPrice(cryptoBought, trade.time))
        boughtInFiat = bought*pr

        gains = self.wallet.take(cryptoSold, D(str(sold)), D(str(boughtInFiat)))
        self.totalGains[str(trade.time.year)].append(gains)
        self.wallet.add(cryptoBought, self.chunk(bought, pr))

        self.log.logTrade(f"{self.tradeIndex}: {sold} of {cryptoSold} ==> {bought} of {cryptoBought} (GAINS : {gains})")

    def chunk(self, vol, price):
        return {"vol": D(str(vol)), "price": D(str(price))}

    def next(self):
        self.tradeIndex +=1

    def processAll(self):
        nTrades = self.trades.shape[0] # simplify
        for _ in range(nTrades):
            self.processNextTrade()
            self.next()
    
    def totalSurplus(self):
        totsies = 0
        for year in self.totalGains:
            totsies += np.sum(self.totalGains[year])

        allFees = 0 
        for cur in self.feesInEur:
            allFees += np.sum(self.feesInEur[cur])
        return (totsies, allFees) 

if __name__ == "__main__":
    plc = plCalculator("myHistory/ledgers.csv",
                        "myHistory/trades.csv",
                        "myHistory/prices.json")

    # Processing all trades 
    plc.processAll() 
    # print(plc.log.getTrades())
    (gains, fees) = plc.totalSurplus()
    print(f"Total gains are : {gains} (fees : {fees}) -> TOTAL : {gains-fees}")

    # Verifying balance
    (bal, ledgerBal) = checkBalanceWithFees(plc.ledger)
    # print(f"Calculated balance is {bal}")
    # print(f"Ledger balance is {ledgerBal}")
    assert(bal==ledgerBal)

""" Todo
fees : substract fees to processing
fees price happens with the price denoting and they are eligible for deduction (as in crypto to fiat)
    but remember to take em out of the wallet
"""