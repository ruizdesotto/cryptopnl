from decimal import Decimal as D
from collections import defaultdict
from unicodedata import decimal

class wallet:
    """
    A class to represent a cryptowallet.

    Methods
    -------
    add(crypto, chunk)
        Adds a crypto amount to the wallet (quantity and price)
    take(crypto, vol, boughtInFiat)
        Takes a ammount of crypto using FIFO and computes surplus 
    updateCost(cost)
        Updates the wallet's average cost
    setWalletCost(cost)
        Sets average cost value
    getCurrentWalletValue(prices, time)
        Gets the wallet's current value
    getWalletCost()
        Gets the wallet's current average cost value
    """

    VOL = "vol"
    PRICE = "price"

    def __init__(self):
        """
        Constructs the wallet and sets the inital cost value to zero 
        """

        # Dict containing all the chunks 
        self.wallet = defaultdict(list) 

        # Dict containing the total amounts of each crypto
        self.amounts = defaultdict(lambda: D("0")) 
            
        # Current wallet value set to zero
        self._walletCost = D("0")
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
        self.wallet[crypto].append({wallet.VOL: amount-fee, wallet.PRICE: price})
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
            Initial FIAT cost (eur) value of withdrawn amount 

        Raises
        ------
        NotImplementedError
            If the crypto is not included in the wallet
        
        TODO remove empty chunks...
        TODO abstract amounts into single method 
        """
        if crypto not in self.wallet:
            raise ValueError("ERROR - CRYPTO NOT FOUND IN WALLET")
        if type(vol) != decimal: vol = D(str(vol))

        chunks = self.wallet[crypto]
        initialCost = 0
        self.amounts[crypto] -= vol
        for chunk in chunks:
            # Take all the chunk
            if chunk[wallet.VOL] <= vol:
                initialCost += chunk[wallet.VOL]*chunk[wallet.PRICE]
                vol -= chunk[wallet.VOL]
                chunk[wallet.VOL] = D("0") 
            # Reduce current chunk and break the loop
            else :
                initialCost += vol*chunk[wallet.PRICE]
                chunk[wallet.VOL] -= vol
                vol = 0
                break
        
        if vol > 0: 
            raise ValueError("Insufficient amount in the wallet")
        return initialCost

    def getWalletCost(self):
        """
        Get wallet's cost 

        Returns
        -------
        dec Wallet's cost 
        """
        return self._walletCost

    def setWalletCost(self, cost):
        """
        Set current wallet's cost

        Parameters
        ----------
        cost : dec New wallet's cost
        """
        self._walletCost = D(str(cost))

    def updateCost(self, cost, fee = D("0")):
        """
        Update current wallet's cost with a new transaction

        Parameters
        ----------
        cost : (float) transaction cost
        fee : (float) transaction fee
        """
        self._walletCost += D(str(cost)) + D(str(fee))
        
    def getCurrentWalletValue(self, time, prices):
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
        # TODO - needs some tweaking
        currentVal = dec(0)
        for crypto in self.amounts:
            price = dec(prices.getPrice(crypto, time))
            # With/Without Rounding
            p = 5
            rnd = dec(int(self.amounts[crypto]*dec(10**p))/dec(10**p))
            currentVal += rnd*price
            #currentVal += (self.amounts[crypto])*price
        return currentVal 

