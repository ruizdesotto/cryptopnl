import pandas as pd
import json
from cryptopnl.price_api.queryAPI import queryAPI

def getCloserTime(data, time):
    minLapse = 1e20
    minTime = -1
    minPrice = -1
    for chunk in data:
        tt = int(chunk[2]*1e9)
        diff = time - tt
        if diff < 0:
            break 
        if diff < minLapse:
            minTime = tt
            minPrice = chunk[0]

    if minTime == -1:
        print("ERROR FINDING POINT")
    return (minTime, minPrice)

class prices:
    def __init__(self, file, cryptos, restore = False):
        self.file = file
        self.cryptos = cryptos
        self.loadPrices(restore)
        self.savePrices()

    def savePrices(self):
        with open(self.file, 'w') as fp:
            json.dump(self.prices, fp)

    def loadPrices(self, restore = False):
        try:
            with open(self.file, 'r') as fp:
                self.prices = json.load(fp)
            if restore:
                raise Exception()
        except: 
            self.prices = {}
            for c in self.cryptos:
                self.prices[c] = {}

    def addPrice(self, crypto, time, price):
        self.prices[crypto][str(time.value)] = price
        self.savePrices()

    def getPrice(self, crypto, time):
        if str(time.value) in self.prices[crypto]:
            return self.prices[crypto][str(time.value)]
        return self.getPriceAPI(crypto, time)
    
    def getPriceAPI(self, crypto, time):
        data = queryAPI(crypto, time.value)

        (prevTime, prevPrice) = getCloserTime(data, time.value)
        print(f"Price {prevPrice} of {crypto} at {pd.to_datetime(prevTime)} (closest point of {time})")
        if (prevTime > 0):
            self.addPrice(crypto, time, prevPrice)
            return prevPrice
        return -1

if __name__ == "__main__":
    # pr = prices("myHistory/prices.json", ["jaja", "XBT", "ETH", "LTC"])
    # print(pr.prices)

    # pr = prices("myHistory/prices.json", ["XBT", "ETH", "LTC"], True)
    # print(pr.prices)

    pr = prices("myHistory/prices.json", ["XBT", "ETH", "LTC"])
    print(pr.prices)

    time = pd.to_datetime('2017-09-03 14:24:39.514800')
    price = pr.getPrice("ETH", time)
    print(price)
