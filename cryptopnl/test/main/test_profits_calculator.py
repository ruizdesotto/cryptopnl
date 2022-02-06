import pytest
from cryptopnl.main.profits_calculator import profitsCalculator
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

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

def test_fiat2crypto():
    """
    Asserts crypto has been bought and stored
    """

    assert False








