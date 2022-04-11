import abc
import os
from collections import defaultdict
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet
import pandas as pd
from typing import Tuple

class abstract_strategy(metaclass = abc.ABCMeta):
    """
    Profits N Losses Calculator (not literally abstract).
    
    Loads a Trades object and a Wallet object to track the operations.
    
    Attributes:
    ----------
    :param _trades: Trade instance with all trades information (optional ledger)
    :param _wallet: wallet instance to track all cryptocurrency
    TODO :param gains: pandas dataframe tracking current profits or losses

    Methods:
    --------
    process_all_trades()
        Loop over all the trades to calculate all the profits / losses
    process_trade()
        Process one trade identifying the type : crypto/fiat or vice versa
    fiat2crypto() : abstract
        Trade involving buying cryptocurrency
    crypto2fiat() : abstract
        Trade involving selling cryptocurrency
    crypto2crypto() : abstract
        Trade involving the exchange of two cryptocurrencies
    pnl_summary()
        Detailed information over the profits and losses
    go()
        Process and generates a summary of earning
    """

    def __init__(self, trades_file:str, ledger_file:str = None) -> None:  
        """ 
        Initialize an instance with a Trades object and a Wallet

        Parameters
        ----------
        trades_file (str) : location of a file with the trades
        ledger_file (str) . (optional) location of a file with the ledger 
        """
        if not os.path.exists(trades_file): raise FileNotFoundError
        if ledger_file and not os.path.exists(ledger_file): raise FileNotFoundError

        self.use_ledger_4_calc = True
        self._trades = Trades(trades_file=trades_file, ledger_file=ledger_file)
        self._wallet = wallet()
        self.fifo_gains = defaultdict(list)
        return 

    def process_all_trades(self) -> None:
        """ Iterate over all trades. """
        for _, trade in self._trades:
            self.process_trade(trade)
        return 

    @abc.abstractmethod
    def process_trade(self, trade: pd.Series) -> None:
        """
        Check type of trade 
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """

        pass

    @abc.abstractmethod
    def fiat2crypto(self, trade: pd.Series) -> None:
        """
        Digest a fiat -> crypto transaction
        
        It adds the crypto amount to the wallet and updated the cost
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """
        pass

    @abc.abstractmethod
    def crypto2fiat(self, trade: pd.Series) -> None:
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
        # TODO : if ledger fees can be in both sides (in EUR and in crypto)
        """
        pass

    @abc.abstractmethod
    def crypto2crypto(self, trade: pd.Series) -> None:
        """
        Digest a crypto -> crypto transaction
        
        It takes crypto from the wallet and translates it into the other crypto 
        TODO : fees and profits 
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """

        pass
    
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