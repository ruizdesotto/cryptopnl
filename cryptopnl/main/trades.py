import pandas as pd
import collections
from decimal import Decimal as D

class Trades:
    """
    A class to represent all the trades and possibly the ledger status.

    Attributes
    ----------
    :param _trades: pandas dataframe with the trades information
    :para _ledgers: (optional) pandas dataframe with the ledger information

    Methods
    -------
    __iter__() 
        Loops through the trades dataframe
    balance_check()
        Checks the coherence in the ledger file
    readKrakeCSV()
        Reads file and transform it into a pandas dataframe object

    """

    TIME_COL = "time"    
    TXID_COL = "txid"
    PAIR_COL = "pair"
    TYPE_COL = "type"
    PRICE_COL = "price"
    COST_COL = "cost"
    FEE_COL = "fee"
    VOL_COL = "vol"
    ASSET_COL = "asset"
    AMOUNT_COL = "amount"
    BALANCE_COL ="balance"

    def __init__(self, trades_file, ledger_file = None):
        """
        Construction of the trades (and ledger) objects

        :param trades_file: (str) file location
        :param ledger_file: (str) file location
        """
        self._trades = Trades.readKrakenCSV(trades_file)
        self._ledger = Trades.readKrakenCSV(ledger_file) if ledger_file else None

    def __iter__(self):
        """
        Iterator that loops on the trades
        """
        return self._trades.iterrows()

    def balance_check(self):
        """ Balance check based on the ledger information
        
        :returns : True if coherent
                   False if non coherent
        :raises ValueError: if attempting to read a non existing ledger
        # TODO loop could be optimized
        """
        if self._ledger is None: raise ValueError("Theres is no ledger loaded.")

        ledger_status = collections.defaultdict(lambda: D("0"))
        ledger_calculus = collections.defaultdict(lambda: D("0"))
        for _, row in self._ledger.iterrows():
            if type(row[Trades.TXID_COL]) == str and row[Trades.TXID_COL]:
                ledger_calculus[Trades.ASSET_COL] += D(str(row[Trades.AMOUNT_COL])) - D(str(row[Trades.FEE_COL]))
                ledger_status[Trades.ASSET_COL] = D(str(row[Trades.BALANCE_COL]))

        for asset in ledger_status:
            if ledger_status[asset] != ledger_calculus[asset]: return False

        return True
          

    @staticmethod
    def readKrakenCSV(file):
        """
        Static method to read and convert trades into a pandas dataframe
        
        :param file: (str) file location
        :return : pandas.DataFrame (trades or ledger)
        """
        df = pd.read_csv(file)
        df[Trades.TIME_COL] = pd.to_datetime(df[Trades.TIME_COL])
        return df
