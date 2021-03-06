import os
from collections import defaultdict
from cryptopnl.main.abstract_strategy import abstract_strategy
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet
import pandas as pd
from typing import Tuple

class fifo_with_trades(abstract_strategy):
    """
    Profits N Losses Calculator.
    
    Loads a Trades object and a Wallet object to track the operations.
    
    Attributes:
    ----------
    :param _trades: Trade instance with all trades information (optional ledger)
    :param _wallet: wallet instance to track all cryptocurrency
    TODO :param gains: pandas dataframe tracking current profits or losses

    Methods:
    --------
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
    go()
        Process and generates a summary of earning
    """
    def __init__(self, trades_file:str) -> None:  
        """ 
        Initialize an instance with a Trades object and a Wallet

        Parameters
        ----------
        trades_file (str) : location of a file with the trades
        """
        if not os.path.exists(trades_file): raise FileNotFoundError

        self._trades = Trades(trades_file=trades_file)
        self._wallet = wallet()
        self.fifo_gains = defaultdict(list)
        return 

    def process_trade(self, trade: pd.Series) -> None:
        """
        Check type of trade 
        
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

    def fiat2crypto(self, trade: pd.Series) -> None:
        """
        Digest a fiat -> crypto transaction
        
        It adds the crypto amount to the wallet and updated the cost
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """
        crypto_name = trade.pair[:-4] # Likely to bug
        self._wallet.add(crypto_name, amount = trade.vol, price = trade.price, fee = trade.fee)
        self._wallet.updateCost(cost = trade.cost, fee = trade.fee) # TODO redondant
        return 

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
        crypto = trade.pair[:-4]
        initial_cost = self._wallet.take(crypto = crypto, vol = trade.vol)
        #cash_in = trade.price * trade.vol - trade.fee # TODO redondant cost
        cash_in = trade.cost - trade.fee
        profit = cash_in - initial_cost
        self.fifo_gains[trade.time.year].append((trade.time, profit))
        return profit > 0

    def crypto2crypto(self, trade: pd.Series) -> None:
        """
        Digest a crypto -> crypto transaction
        
        It takes crypto from the wallet and translates it into the other crypto 
        TODO : fees and profits 
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """

        if trade.type == "buy":
            crypto_bought = trade.pair[:4]
            crypto_sold = trade.pair[4:]
            bought_amount = trade.vol
            sold_amount = trade.cost + trade.fee
            fee = trade.fee / trade.price
        else:
            crypto_bought = trade.pair[4:]
            crypto_sold = trade.pair[:4]
            bought_amount = trade.cost - trade.fee
            sold_amount = trade.vol
            fee = trade.fee

        initial_cost_in_fiat = self._wallet.take(crypto = crypto_sold, vol = sold_amount)
        equivalent_price = initial_cost_in_fiat / bought_amount
        fee_in_fiat = equivalent_price * fee 
        self._wallet.add(crypto = crypto_bought, amount = bought_amount, price = equivalent_price, fee = fee_in_fiat)