from decimal import Decimal 
from collections import defaultdict

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

    COST = "cost"
    VOL = "vol"
    PRICE = "price"

    def __init__(self):
        """
        Constructs the wallet and sets the inital cost value to zero 
        """

        # Dict containing all the chunks 
        self.wallet = defaultdict(list) 

        # Dict containing the total amounts of each crypto
        self.amounts = defaultdict(Decimal) 
            
        # Current wallet value set to zero
        self._walletCost = Decimal()
        return

    def add(self, crypto:str, amount:Decimal, price:Decimal, fee:Decimal = Decimal()) -> None:
        """
        Adds an amount of crypto

        Parameters
        ----------
        crypto (str) : crypto-currency name
        amount (float)
        price (float): price of crypto with respect to fiat (eur)
        fee (float): fee of transaction (in fiat)
        """

        chunk = {
            wallet.COST: price*amount + fee,
            wallet.VOL: amount, 
            wallet.PRICE: price, 
            }
        self.wallet[crypto].append(chunk)
        self.amounts[crypto] += amount   # TODO do it elsewhere
        return
          
    def take(self, crypto:str, vol:Decimal):
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

        chunks = self.wallet[crypto]
        initialCost = 0
        self.amounts[crypto] -= vol
        for chunk in chunks:
            # Take all the chunk
            if chunk[wallet.VOL] <= vol:
                initialCost += chunk[wallet.COST]
                vol -= chunk[wallet.VOL]
                chunk[wallet.VOL] = Decimal() 
                chunk[wallet.COST] = Decimal() 
            # Reduce current chunk and break the loop
            else :
                vol_fraction = vol  / chunk[wallet.VOL]
                extra_cost = chunk[wallet.COST] * vol_fraction 
                chunk[wallet.VOL] -= vol
                chunk[wallet.COST] -= extra_cost 
                initialCost += extra_cost
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

    def setWalletCost(self, cost:Decimal):
        """
        Set current wallet's cost

        Parameters
        ----------
        cost : dec New wallet's cost
        """
        self._walletCost = cost 

    def updateCost(self, cost:Decimal, fee:Decimal = Decimal()):
        """
        Update current wallet's cost with a new transaction

        Parameters
        ----------
        cost : (float) transaction cost
        fee : (float) transaction fee
        """
        self._walletCost += cost + fee 
        
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
        currentVal = Decimal 
        for crypto in self.amounts:
            price = Decimal(prices.getPrice(crypto, time))
            # With/Without Rounding
            p = 5
            rnd = Decimal(int(self.amounts[crypto]*Decimal(10**p))/Decimal(10**p))
            currentVal += rnd*price
            #currentVal += (self.amounts[crypto])*price
        return currentVal 

