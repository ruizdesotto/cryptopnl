from decimal import Decimal as D, getcontext
from cryptopnl.utils.utils import dec 

def rndFloor(num, p = 5):
    return dec(int(num*dec(10**p))/dec(10**p))

class wallet:
    """
    A class to represent a crypto-wallet.

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

    def __init__(self, cryptos):
        """
        Constructs the wallet and sets the inital cost value to zero 

        Parameters
        ----------
        cryptos : str[]
            array of cryptocurrency names to be included
        """
        # Dict containing all the chunks 
        self.wallet = {}

        # Dict containing the total amounts of each crypto
        self.amounts = {}

        for c in cryptos:
            self.wallet[c] = []
            self.amounts[c] = D("0")
            
        # Current wallet value set to zero
        self.walletValue = D("0")

    def add(self, crypto, chunk):
        """
        Adds an amount of crypto

        Parameters
        ----------
        crypto : str
            Crypto-currency name
        chunk : dict {vol, price}
            Dict containint the amount and the price of the transaction
        """
        self.wallet[crypto].append(chunk)
        self.amounts[crypto] += chunk["vol"] 
          
    def take(self, crypto, vol, boughtInFiat):
        """
        Takes an amount of crypto following the FIFO method 

        Parameters
        ----------
        crypto : str
            Crypto-currency name
        vol : dec
            Amount to be deducted
        boughInFiat : float
            Cash-out to deduce the surplus

        Returns
        -------
        float
            Surplus value obtained with the transaction

        Raises
        ------
        NotImplementedError
            If the crypto is not included in the wallet
        """
        if crypto not in self.wallet:
            raise NotImplementedError("ERROR - CRYPTO NOT FOUND IN WALLET")

        chunks = self.wallet[crypto]
        initialFiat = 0
        self.amounts[crypto] -= vol
        for chunk in chunks:
            # Take all the chunk
            if chunk["vol"] <= vol:
                initialFiat += chunk["vol"]*chunk["price"]
                vol -= chunk["vol"]
                chunk["vol"] = 0
            # Reduce current chunk and break the loop
            else :
                initialFiat += vol*chunk["price"]
                chunk["vol"] -= vol
                break
        
        return float(boughtInFiat - initialFiat)

    def updateCost(self, cost):
        """
        Update current wallet's cost with a new transaction

        Parameters
        ----------
        cost : dec 
            Transaction cost
        """
        self.walletValue += cost

    def setCost(self, cost):
        """
        Set current wallet's cost

        Parameters
        ----------
        cost : dec 
            New wallet's cost
        """
        self.walletValue = cost

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
        """
        return dec(self.walletValue)
