import os
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

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
        return 

    def process_all_trades(self):
        pass

    def process_trade(self):
        pass

    def fiat2crypto(self):
        pass

    def crypto2fiat(self):
        pass

    def crypto2crypto(self):
        pass

    def pnl_summary(self):
        pass
        