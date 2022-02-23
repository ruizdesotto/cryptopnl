from operator import eq
import os
from collections import defaultdict
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet
from decimal import Decimal as D

class profitsCalculator:
    """
    Profits N Losses Calculator.
    
    It loads a Trades object and a Wallet object to track the operations.
    
    Attributes:
    ----------
    :param _trades: Trade instance with all trades information (optional ledger)
    :param _wallet: wallet instance to track all cryptocurrency
    :param gains: pandas dataframe tracking current profits or losses

    Methods:
    --------
    process_all_trades()
        Loop over all the trades to calculate all the profits / losses
    process_trade()
        Process one trade identifying the type : crypto/fiat or vice versa
    fiat2crypto()
        Trade involving buying cryptocurrency
    crypto2fiat()
        Trade involving selling cryptocurrency
    crypto2crypto()
        Trade involving the exchange of two cryptocurrencies
    pnl_summary()
        Detailed information over the profits and losses
    """

    def __init__(self, trades_file, ledger_file = None):  
        """ 
        Initializes an instance with a Trades object and a Wallet

        Parameters
        ----------
        trades_file (str) : location of a file with the trades
        ledger_file (str) . (optional) location of a file with the ledger 
        """
        if not os.path.exists(trades_file): raise FileNotFoundError
        if ledger_file and not os.path.exists(ledger_file): raise FileNotFoundError
        self._trades = Trades(trades_file=trades_file, ledger_file=ledger_file)
        self._wallet = wallet()
        self.fifo_gains = defaultdict(list)
        return 

    def process_all_trades(self):
        """
        Iterates over all trades

        _trades is iterable
        """
        for _, trade in self._trades:
            self.process_trade(trade)
        return 

    def process_trade(self, trade):
        """
        Checks what type of trades it to use appropriate function 
        
        TODO : add ledger as an option
        TODO : Warning does not check a trade falls within one of the three categories
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """

        if trade.pair.endswith("EUR") and trade.type == "buy":
            self.fiat2crypto(trade)
        elif trade.pair.endswith("EUR") and trade.type == "sell":
            self.crypto2fiat(trade)
        else:
            self.crypto2crypto(trade)
        return 

    def fiat2crypto(self, trade):
        """
        Digest a fiat -> crypto transaction
        
        It adds the crypto amount to the wallet and updated the cost
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """
        crypto = trade.pair[:-4] # Likely to bug
        self._wallet.add(crypto, trade.vol, trade.price)
        self._wallet.updateCost(trade.cost, trade.fee)
        return 

    def crypto2fiat(self, trade):
        """
        Digest a crypto -> fiat transaction
        
        It takes crypto from the wallet and updates the current cost and profit
        FIFO and later on, average cost method
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 

        Returns
        -------
        profit: (boolean) True / False for profit / loss
        """

        crypto = trade.pair[:-4]
        initial_cost = self._wallet.take(crypto = crypto, vol = trade.vol)
        cash_in = D(str(trade.price)) * D(str(trade.vol)) - D(str(trade.fee))
        profit = cash_in - initial_cost
        self.fifo_gains[trade.time.year].append((trade.time, profit))
        return profit > 0

    def crypto2crypto(self, trade):
        """
        Digest a crypto -> crypto transaction
        
        It takes crypto from the wallet and translates it into the other crypto 
        TODO : fees and profits 
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """
        print("This is an annoying print to remind you to include fees and profits")

        if trade.type == "buy":
            crypto_bought = trade.pair[:4]
            crypto_sold = trade.pair[4:]
            sold_amount = trade.cost
            bought_amount = trade.vol
        else:
            crypto_bought = trade.pair[4:]
            crypto_sold = trade.pair[:4]
            sold_amount = trade.vol
            bought_amount = trade.cost

        initial_cost_in_fiat = self._wallet.take(crypto_sold, sold_amount)
        equivalent_price = D(str(initial_cost_in_fiat)) / D(str(bought_amount))
        self._wallet.add(crypto_bought, bought_amount, equivalent_price)

    def pnl_summary(self):
        """
        Calculate a summary of all the profits and print it

        Return a simplified dictionary 
        """
        summary = {year: sum(p for (_, p) in profits) 
                            for (year, profits) in self.fifo_gains.items()} 
        print("\n".join(f"{year}: {profit}" for year, profit in summary.items()))
        return summary
        
    def go(self):
        self.process_all_trades()
        self.pnl_summary()
        return 0