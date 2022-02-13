import os
import pytest
from cryptopnl.main.profits_calculator import profitsCalculator
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

@pytest.fixture
def trades_fixture(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)

    if os.path.isdir(os.path.join(test_dir, "test_files")):
        trades_file = os.path.join(test_dir, "test_files", "test_trades.csv")
        if os.path.exists(trades_file):
            return Trades(trades_file)
    
    raise FileNotFoundError("Test files not found")
    

def test_profitsCalculator_init(tmpdir, mocker):
    """
    Assert constructor buils a Trades instance from files
    """

    trades = tmpdir.join("trades.csv")
    ledger = tmpdir.join("ledger.csv")
    with pytest.raises(FileNotFoundError):
        profitsCalculator(trades_file= trades)
    trades.write("")
    with pytest.raises(FileNotFoundError):
        profitsCalculator(trades_file= trades, ledger_file=ledger)
    ledger.write("")

    mocker.patch("cryptopnl.main.trades.Trades", return_value=True)
    profits = profitsCalculator(trades_file = trades, ledger_file = ledger)
    assert type(profits._trades) == Trades
    assert type(profits._wallet) == wallet
    profits_without_ledger = profitsCalculator(trades_file = trades)
    assert type(profits_without_ledger._trades) == Trades
    return

#def test_process_all_trades():
#    assert False


def test_fiat2crypto(trades_fixture):
    """
    Asserts crypto has been bought and stored
    """

    
    assert False








