from datetime import datetime as dt
import os
import pytest
import re
from collections import defaultdict
from cryptopnl.main.abstract_strategy import abstract_strategy
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

class not_so_abstract_strategy(abstract_strategy):
    def process_trade(self, trade) -> None:
        pass
    def fiat2crypto(self) -> None:
        pass 
    def crypto2fiat(self) -> None:
        pass
    def crypto2crypto(self) -> None:
        pass

@pytest.fixture
def abstract_strategy_fixture(request):
    filename = request.module.__file__
    file_dir, _ = os.path.split(filename)
    test_dir, _ = os.path.split(file_dir)

    if os.path.isdir(os.path.join(test_dir, "_test_files")):
        trades_file = os.path.join(test_dir, "_test_files", "test_trades.csv")
        if os.path.exists(trades_file) and os.path.exists(trades_file):
            return not_so_abstract_strategy(trades_file=trades_file) 
    
    raise FileNotFoundError("Test files not found")
    

def test_abstract_strategy_init(tmpdir, mocker):
    """
    Assert constructor buils a Trades instance from files
    """

    trades = tmpdir.join("trades.csv")
    with pytest.raises(FileNotFoundError):
        not_so_abstract_strategy(trades_file = trades)
    trades.write("")

    mocker.patch("cryptopnl.main.trades.Trades", return_value=True)
    profits = not_so_abstract_strategy(trades_file = trades)
    assert type(profits._trades) == Trades
    assert type(profits._wallet) == wallet
    assert type(profits.fifo_gains) == defaultdict 
    assert type(profits.fifo_gains.default_factory()) == list
    return

def test_abstract_strategy_process_all_trades(abstract_strategy_fixture, mocker):
    """
    Asserts all trades are processed  
    """
    mock_process = mocker.patch(f"{__name__}.not_so_abstract_strategy.process_trade", return_value=True)

    abstract_strategy_fixture.process_all_trades()
    t0 = abstract_strategy_fixture._trades._trades.iloc[0]
    t1 = abstract_strategy_fixture._trades._trades.iloc[1]
    t2 = abstract_strategy_fixture._trades._trades.iloc[2]
    t3 = abstract_strategy_fixture._trades._trades.iloc[3]

    assert mock_process.call_count == 4
    assert str(mocker.call(t0)) == str(mock_process.call_args_list[0])
    assert str(mocker.call(t1)) == str(mock_process.call_args_list[1])
    assert str(mocker.call(t2)) == str(mock_process.call_args_list[2])
    assert str(mocker.call(t3)) == str(mock_process.call_args_list[3])


def test_abstract_strategy_pnl_summary(abstract_strategy_fixture, capsys):
    """ Assert it returns summay info and prints it"""

    timestamp = dt.timestamp(dt.now())
    all_gains = {
        "2020": [(timestamp, 1.0), (timestamp, 2.0)], 
        "2021": [(timestamp, 10.0), (timestamp, 20.0)],
    }
    abstract_strategy_fixture.fifo_gains = all_gains

    pnl = abstract_strategy_fixture.pnl_summary()

    capture = capsys.readouterr()
    assert pnl == {"2020": 3.0, "2021": 30.0}
    assert re.match('2020(.*)3.0(\n)*(.*)2021(.*)30.0', capture.out)

def test_abstract_strategy_go(abstract_strategy_fixture, mocker):
    """
    Assert the functions are called
    """

    mock_process = mocker.patch("cryptopnl.main.fifo_with_trades.abstract_strategy.process_all_trades", return_value=True)
    mock_summary = mocker.patch("cryptopnl.main.fifo_with_trades.abstract_strategy.pnl_summary", return_value=True)

    abstract_strategy_fixture.go()
    mock_process.assert_called_once_with()
    mock_summary.assert_called_once_with()
