from decimal import Decimal as D
from collections import defaultdict
from cryptopnl.utils.utils import dec 

def rndFloor(num, p = 5):
    """
    TODO : define purpose
    """
    return dec(int(num*dec(10**p))/dec(10**p))

# TODO define some variables like VOL or PRICE
class wallet:
    """
    A class to represent a cryptowallet.

    Attributes
    ----------
    cryptos : str[]
        array of cryptocurrency names to be included

    Methods
    -------
    add(crypto, chunk)
        Adds a crypto amount to the wallet (quantity and price)
    take(crypto, vol, boughtInFiat)
        Takes a ammount of crypto using FIFO and computes surplus 
    updateCost(cost)
        Updates the wallet's average cost
    setCost(cost)
        Sets average cost value
    getCurrentValue(prices, time)
        Gets the wallet's current value
    getCost()
        Gets the wallet's current average cost value
    """

    def __init__(self):
        """
        Constructs the wallet and sets the inital cost value to zero 
        """

        # Dict containing all the chunks 
        self.wallet = defaultdict(list) 

        # Dict containing the total amounts of each crypto
        self.amounts = defaultdict(lambda: D("0")) 
            
        # Current wallet value set to zero
        self.walletValue = D("0")
        return

    def add(self, crypto, amount, price, fee = 0):
        """
        Adds an amount of crypto

        Parameters
        ----------
        crypto (str) : crypto-currency name
        amount (float)
        price (float): price of crypto with respect to fiat (eur)
        fee (float): fee of transaction (in crypto)
        """
        amount = D(str(amount))
        price = D(str(price))
        fee = D(str(fee))
        self.wallet[crypto].append({"vol": amount-fee, "price": price})
        self.amounts[crypto] += amount - fee 
        return
          
    def take(self, crypto, vol):
        """
        Takes an amount of crypto following the FIFO method 

        Parameters
        ----------
        crypto : str
            Crypto-currency name
        vol : dec
            Amount to be deducted

        Returns
        -------
        Decimal 
            Initial FIAT (eur) value of withdrawn amount 

        Raises
        ------
        NotImplementedError
            If the crypto is not included in the wallet
        
        TODO remove empty chunks...
        TODO abstract amounts into single method 
        """
        if crypto not in self.wallet:
            raise ValueError("ERROR - CRYPTO NOT FOUND IN WALLET")

        chunks = self.wallet[crypto]
        initialFiat = 0
        self.amounts[crypto] -= vol
        for chunk in chunks:
            # Take all the chunk
            if chunk["vol"] <= vol:
                initialFiat += chunk["vol"]*chunk["price"]
                vol -= chunk["vol"]
                chunk["vol"] = D("0") 
            # Reduce current chunk and break the loop
            else :
                initialFiat += vol*chunk["price"]
                chunk["vol"] -= vol
                vol = 0
                break
        
        if vol > 0: 
            raise ValueError("Insufficient amount in the wallet")
        return initialFiat

    def updateCost(self, cost):
        """
        Update current wallet's cost with a new transaction

        Parameters
        ----------
        cost : dec 
            Transaction cost
        """
        self.walletValue += D(str(cost))

    def setCost(self, cost):
        """
        Set current wallet's cost

        Parameters
        ----------
        cost : dec 
            New wallet's cost
        """
        self.walletValue = D(str(cost))

    def getCurrentValue(self, prices, time):
        """
        Get wallet's current value

        Parameters
        ----------
        prices : class 
            Class containing info about the classes
        time : long
            Time at which the current value is asked

        Returns
        -------
        dec 
            Wallet's current value
        """
        # Todo - needs some tweaking
        currentVal = dec(0)
        for crypto in self.amounts:
            price = dec(prices.getPrice(crypto, time))
            # With/Without Rounding
            currentVal += rndFloor(self.amounts[crypto])*price
            #currentVal += (self.amounts[crypto])*price
        return currentVal 

    def getCost(self):
        """
        Get wallet's cost 

        Returns
        -------
        dec 
            Wallet's cost 

        # TODO remove method...
        """
        return self.walletValue
