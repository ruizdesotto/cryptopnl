import os
from collections import defaultdict
from cryptopnl.main.trades import Trades
from cryptopnl.main.abstract_strategy import abstract_strategy
from cryptopnl.wallet.wallet import wallet
import pandas as pd
from typing import Tuple

class fifo_with_ledger(abstract_strategy):
    """
    Profits N Losses Calculator.
    
    Loads a Trades object and a Wallet object to track the operations.
    The Trades object includes a ledger and it is used for the calculations.
    
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

    def __init__(self, trades_file:str, ledger_file:str) -> None:  
        """ 
        Initialize an instance with a Trades object and a Wallet

        Parameters
        ----------
        trades_file (str) : location of a file with the trades
        ledger_file (str) . (optional) location of a file with the ledger 
        """
        if not os.path.exists(trades_file): raise FileNotFoundError
        if not os.path.exists(ledger_file): raise FileNotFoundError

        self._trades = Trades(trades_file=trades_file, ledger_file=ledger_file)
        self._wallet = wallet()
        self.fifo_gains = defaultdict(list)
        return 

    def get_ledgers_from_trade(self, trade: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """ 
        Returns ledger's ids from a trade.
        
        Parameters
        ----------
        trade (pd.Series) : trade instance 
        
        Returns
        -------
        ledger (str, str) : tupple with the ining and outing amount
        """
        indices = trade[Trades.LEDGER_COL].split(",")
        l = self._trades._ledger
        l_id_1 = l[l[Trades.TXID_COL] == indices[0]].iloc[0]
        l_id_2 = l[l[Trades.TXID_COL] == indices[1]].iloc[0]

        if l_id_1[Trades.AMOUNT_COL] > 0: return (l_id_1, l_id_2)
        else: return (l_id_2, l_id_1)

    def process_trade(self, trade: pd.Series) -> None:
        """
        Check type of trade and uses ledger for processing it.
        # TODO to test
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """

        id_ining, id_outing = self.get_ledgers_from_trade(trade)  
        if trade.pair.endswith("EUR") and trade.type == "buy":
            # TODO encapsulate in function
            assert trade.vol == id_ining.amount
            assert trade.price == - id_outing.amount / id_ining.amount
            self.fiat2crypto(crypto = id_ining, fiat = id_outing)
        elif trade.pair.endswith("EUR") and trade.type == "sell":
            # TODO encapsulate in function
            assert trade.vol == - id_outing.amount
            assert trade.price == - id_ining.amount / id_outing.amount
            self.crypto2fiat(crypto = id_outing, fiat = id_ining)
        else:
            self.crypto2crypto(trade)
        return 

    def fiat2crypto(self, crypto: pd.Series, fiat: pd.Series) -> None:
        """
        Digest a fiat -> crypto transaction using the ledger
        
        It adds the crypto amount to the wallet and updated the cost
        
        Parameters
        ----------
        crypto: (pandas.dataFrame.row) 
        fiat: (pandas.dataFrame.row) 
        """
        price = - fiat.amount / crypto.amount
        self._wallet.add(crypto.asset, amount = crypto.amount, price = price, fee = fiat.fee)
        self._wallet.updateCost(cost = - fiat.amount, fee = fiat.fee) 
        return 

    def crypto2fiat(self, crypto: pd.Series, fiat: pd.Series) -> None:
        """
        Digest a crypto -> fiat transaction using ledger info
        
        It takes crypto from the wallet and updates the current cost and profit
        FIFO and later on, average cost method
        
        Parameters
        ----------
        crypto: (pandas.dataFrame.row) 
        fiat: (pandas.dataFrame.row) 

        Returns
        -------
        profit: (boolean) True / False for profit / loss
        # TODO : if ledger fees can be in both sides (in EUR and in crypto)
        """
        crypto_name = crypto.asset 
        initial_cost = self._wallet.take(crypto = crypto_name, vol = - crypto.amount)
        cash_in = fiat.amount - fiat.fee 
        profit = cash_in - initial_cost
        self.fifo_gains[crypto.time.year].append((crypto.time, profit))
        return profit > 0

    def crypto2crypto(self, crypto_in: pd.Series, crypto_out: pd.Series) -> None:
        """
        Digest a crypto -> crypto transaction
        
        It takes crypto from the wallet and translates it into the other crypto 
        TODO : fees and profits 
        
        Parameters
        ----------
        trade: (pandas.dataFrame.row) 
        """
        crypto_bought = crypto_in.asset 
        crypto_sold = crypto_out.asset 
        bought_amount = crypto_in.amount - crypto_in.fee
        sold_amount = -crypto_out.amount + crypto_out.fee 

        initial_cost_in_fiat = self._wallet.take(crypto = crypto_sold, vol = sold_amount)
        equivalent_price = initial_cost_in_fiat / bought_amount
        self._wallet.add(crypto = crypto_bought, amount = bought_amount, price = equivalent_price)#TODO define this , fee = fee_in_fiat)
