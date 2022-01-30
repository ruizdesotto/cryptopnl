from multiprocessing.sharedctypes import Value
import pandas as pd
from datetime import datetime as dt
import pytest

from cryptopnl.main.trades import Trades

#TODO when creating dataframe, use decimal automatically IMPORTANT

def test_trades_init(mocker):
    """
    Test a trades object can be initialized
    Assert information about trades and ledger are in the shape of a pd.dataFrame
    Assert ledger is an optional parameter
    """

    mocker.patch("cryptopnl.main.trades.Trades.readKrakenCSV", return_value=pd.DataFrame())
    trades = Trades(trades_file = "/some/trades.csv", ledger_file = "/some/ledger.csv")
    assert isinstance(trades._trades, pd.DataFrame)
    assert isinstance(trades._ledger, pd.DataFrame)

    trades_no_ledger = Trades(trades_file = "/some/trades.csv")
    assert isinstance(trades_no_ledger._trades, pd.DataFrame)
    assert trades_no_ledger._ledger is None

def test_trades_readKrakenCSV(tmpdir):
    """
    Assert file exists, dataframe can be generated, specific columns are retrieved
    """

    some_trades = tmpdir.join("trades.csv")
    data = '"txid","ordertxid","pair","time","type","ordertype","price","cost","fee","vol","margin","misc","ledgers"\n"EIXO2E","OMS7LN","XXBTZEUR","2017-09-01 19:07:54.0965","buy","limit",1.00000,9.983,0.01500,0.00245000,0.00000,"","LOZGS7,LZORUL"'
    some_trades.write(data)
    trades = Trades.readKrakenCSV(some_trades)
    assert isinstance(trades, pd.DataFrame)
    assert Trades.TIME_COL in trades
    assert isinstance(trades[Trades.TIME_COL].iloc[0], dt)

def test_trades_iter(mocker):
    """
    Assert we can iterate over the trades
    """

    some_trades = pd.DataFrame([(1,10),(2,20),(3,30)], columns=["c0", "c1"])
    mocker.patch("cryptopnl.main.trades.Trades.readKrakenCSV", return_value=some_trades)
    trades = Trades(trades_file = "/some/trades.csv", ledger_file = "/some/ledger.csv")

    for _, d in trades: 
        assert isinstance(d, pd.Series) 
        assert d["c0"] is not None
        assert d["c1"] is not None
@pytest.mark.parametrize("data_input, check", 
    ([
        (pd.DataFrame([
            ["", "NAME", 1.0, 0.1, 0],
            ["TXID_0", "NAME", 1.0, 0.1, 0.9],
            ["TXID_1", "NAME", 1.0, 0.4, 1.5]
             ], 
             columns=[Trades.TXID_COL, Trades.ASSET_COL, Trades.AMOUNT_COL, Trades.FEE_COL, Trades.BALANCE_COL]),
        True), 
        (pd.DataFrame([
            ["", "NAME", 1.0, 0.1, 0],
            ["TXID_0", "NAME", 1.0, 0.1, 0.9],
            ["TXID_1", "NAME", 1.0, 0.4, 1.0]
             ], 
             columns=[Trades.TXID_COL, Trades.ASSET_COL, Trades.AMOUNT_COL, Trades.FEE_COL, Trades.BALANCE_COL]),
        False), 
    ]))
def test_balance_check(data_input, check, mocker):
    mocker.patch("cryptopnl.main.trades.Trades.readKrakenCSV", return_value = data_input)
    trades_obj = Trades("/some/trades.csv", "/some/ledger.csv")
    balance_checking = trades_obj.balance_check()
    assert balance_checking == check

def test_balance_check_error(mocker):
    mocker.patch("cryptopnl.main.trades.Trades.readKrakenCSV", return_value = "some_val")
    trades_obj = Trades("/some/trades.csv")
    with pytest.raises(ValueError):
        trades_obj.balance_check()
