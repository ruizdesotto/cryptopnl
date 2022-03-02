from decimal import Decimal as D
import pandas as pd
from datetime import datetime as dt
import pytest
import os

from cryptopnl.main.trades import Trades

@pytest.fixture
def trades_csv(request):
    filename = request.module.__file__
    file_dir, _ = os.path.split(filename)
    test_dir, _ = os.path.split(file_dir)

    if os.path.isdir(os.path.join(test_dir, "_test_files")):
        trades_file = os.path.join(test_dir, "_test_files", "test_trades.csv")
        if os.path.exists(trades_file):
            return trades_file
    
    raise FileNotFoundError("Test file not found")

@pytest.fixture
def ledger_csv(request):
    filename = request.module.__file__
    file_dir, _ = os.path.split(filename)
    test_dir, _ = os.path.split(file_dir)

    if os.path.isdir(os.path.join(test_dir, "_test_files")):
        ledger_file = os.path.join(test_dir, "_test_files", "test_ledger.csv")
        if os.path.exists(ledger_file):
            return ledger_file 
    
    raise FileNotFoundError("Test file not found")

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

def test_trades_readKrakenCSV_trades(trades_csv):
    """
    Assert file exists, dataframe can be generated, specific columns are retrieved
    """

    trades = Trades.readKrakenCSV(trades_csv)

    assert isinstance(trades, pd.DataFrame)
    assert Trades.TIME_COL in trades
    assert isinstance(trades[Trades.TIME_COL].iloc[0], dt)
    assert Trades.COST_COL in trades
    assert isinstance(trades[Trades.COST_COL].iloc[0], D)

def test_trades_readKrakenCSV_ledger(ledger_csv):
    """
    Assert file exists, dataframe can be generated, specific columns are retrieved
    """

    ledger = Trades.readKrakenCSV(ledger_csv)

    assert isinstance(ledger, pd.DataFrame)
    assert Trades.TIME_COL in ledger 
    assert isinstance(ledger[Trades.TIME_COL].iloc[0], dt)
    assert Trades.BALANCE_COL in ledger 
    assert isinstance(ledger[Trades.BALANCE_COL].iloc[0], D)

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

# TODO : use fixture to avoid boilerplate code
@pytest.mark.parametrize("data_input, check", 
    ([
        (pd.DataFrame([
            ["", "NAME", D(str(1.0)), D(str(0.1)), D(str(0))],
            ["TXID_0", "NAME", D(str(1.0)), D(str(0.1)), D(str(0.9))],
            ["TXID_1", "NAME", D(str(1.0)), D(str(0.4)), D(str(1.5))]
             ], 
             columns=[Trades.TXID_COL, Trades.ASSET_COL, Trades.AMOUNT_COL, Trades.FEE_COL, Trades.BALANCE_COL]),
        True), 
        (pd.DataFrame([
            ["", "NAME", D(str(1.0)), D(str(0.1)), D(str(0))],
            ["TXID_0", "NAME", D(str(1.0)), D(str(0.1)), D(str(0.9))],
            ["TXID_1", "NAME", D(str(1.0)), D(str(0.4)), D(str(1.0))]
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
