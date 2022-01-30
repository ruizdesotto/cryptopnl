
class pnl_calculator:
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


    def __init__(self):
        pass

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
        