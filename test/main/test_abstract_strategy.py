from datetime import datetime as dt
import os
import pytest
import re
from collections import defaultdict
from cryptopnl.main.abstract_strategy import abstract_strategy
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

@pytest.fixture
def profitsCalculator_fixture(request):
    filename = request.module.__file__
    file_dir, _ = os.path.split(filename)
    test_dir, _ = os.path.split(file_dir)

    if os.path.isdir(os.path.join(test_dir, "_test_files")):
        trades_file = os.path.join(test_dir, "_test_files", "test_trades.csv")
        ledger_file = os.path.join(test_dir, "_test_files", "test_ledger.csv")
        if os.path.exists(trades_file) and os.path.exists(trades_file):
            return abstract_strategy(trades_file=trades_file, ledger_file=ledger_file) 
    
    raise FileNotFoundError("Test files not found")
    

def test_profitsCalculator_init(tmpdir, mocker):
    """
    Assert constructor buils a Trades instance from files
    """

    trades = tmpdir.join("trades.csv")
    ledger = tmpdir.join("ledger.csv")
    with pytest.raises(FileNotFoundError):
        abstract_strategy(trades_file = trades)
    trades.write("")
    with pytest.raises(FileNotFoundError):
        abstract_strategy(trades_file = trades, ledger_file=ledger)
    ledger.write("")

    mocker.patch("cryptopnl.main.trades.Trades", return_value=True)
    profits = abstract_strategy(trades_file = trades, ledger_file = ledger)
    assert type(profits._trades) == Trades
    assert type(profits._wallet) == wallet
    assert type(profits.fifo_gains) == defaultdict 
    assert type(profits.fifo_gains.default_factory()) == list

    profits_without_ledger = profitsCalculator(trades_file = trades)
    assert type(profits_without_ledger._trades) == Trades
    return

def test_profitsCalculator_process_all_trades(profitsCalculator_fixture, mocker):
    """
    Asserts all trades are processed  
    """

    mock_process = mocker.patch("cryptopnl.main.fifo_with_trades.profitsCalculator.process_trade", return_value=True)

    profitsCalculator_fixture.process_all_trades()
    t0 = profitsCalculator_fixture._trades._trades.iloc[0]
    t1 = profitsCalculator_fixture._trades._trades.iloc[1]
    t2 = profitsCalculator_fixture._trades._trades.iloc[2]
    t3 = profitsCalculator_fixture._trades._trades.iloc[3]

    assert mock_process.call_count == 4
    assert str(mocker.call(t0)) == str(mock_process.call_args_list[0])
    assert str(mocker.call(t1)) == str(mock_process.call_args_list[1])
    assert str(mocker.call(t2)) == str(mock_process.call_args_list[2])
    assert str(mocker.call(t3)) == str(mock_process.call_args_list[3])


def test_profitsCalculator_pnl_summary(profitsCalculator_fixture, capsys):
    """ Assert it returns summay info and prints it"""

    timestamp = dt.timestamp(dt.now())
    all_gains = {
        "2020": [(timestamp, 1.0), (timestamp, 2.0)], 
        "2021": [(timestamp, 10.0), (timestamp, 20.0)],
    }
    profitsCalculator_fixture.fifo_gains = all_gains

    pnl = profitsCalculator_fixture.pnl_summary()

    capture = capsys.readouterr()
    assert pnl == {"2020": 3.0, "2021": 30.0}
    assert re.match('2020(.*)3.0(\n)*(.*)2021(.*)30.0', capture.out)

def test_profitsCalculator_go(profitsCalculator_fixture, mocker):
    """
    Assert the functions are called
    """

    mock_process = mocker.patch("cryptopnl.main.fifo_with_trades.profitsCalculator.process_all_trades", return_value=True)
    mock_summary = mocker.patch("cryptopnl.main.fifo_with_trades.profitsCalculator.pnl_summary", return_value=True)

    profitsCalculator_fixture.go()
    mock_process.assert_called_once_with()
    mock_summary.assert_called_once_with()
