from decimal import Decimal as D
import os
import pytest
from collections import defaultdict
from cryptopnl.main.profits_calculator import profitsCalculator
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

@pytest.fixture
def profitsCalculator_fixture(request):
    filename = request.module.__file__
    test_dir, _ = os.path.split(filename)

    if os.path.isdir(os.path.join(test_dir, "test_files")):
        trades_file = os.path.join(test_dir, "test_files", "test_trades.csv")
        if os.path.exists(trades_file):
            return profitsCalculator(trades_file=trades_file) 
    
    raise FileNotFoundError("Test files not found")
    

def test_profitsCalculator_init(tmpdir, mocker):
    """
    Assert constructor buils a Trades instance from files
    """

    trades = tmpdir.join("trades.csv")
    ledger = tmpdir.join("ledger.csv")
    with pytest.raises(FileNotFoundError):
        profitsCalculator(trades_file = trades)
    trades.write("")
    with pytest.raises(FileNotFoundError):
        profitsCalculator(trades_file = trades, ledger_file=ledger)
    ledger.write("")

    mocker.patch("cryptopnl.main.trades.Trades", return_value=True)
    profits = profitsCalculator(trades_file = trades, ledger_file = ledger)
    assert type(profits._trades) == Trades
    assert type(profits._wallet) == wallet
    assert type(profits.fifo_gains) == defaultdict 
    assert type(profits.fifo_gains.default_factory()) == list

    profits_without_ledger = profitsCalculator(trades_file = trades)
    assert type(profits_without_ledger._trades) == Trades
    return

#def test_process_all_trades():
#    assert False


def test_fiat2crypto(profitsCalculator_fixture):
    """
    Asserts crypto has been bought, stored and cost is updated 
    """

    trade = profitsCalculator_fixture._trades._trades.iloc[0]
    wallet = profitsCalculator_fixture._wallet
    initial_cost = 10

    wallet.setWalletCost(initial_cost)
    profitsCalculator_fixture.fiat2crypto(trade)

    assert wallet._walletCost == D(str(initial_cost)) + D(str(trade.cost)) + D(str(trade.fee))
    assert wallet.wallet[trade.pair[:-4]][0][wallet.VOL] == D(str(trade.vol))
    assert wallet.wallet[trade.pair[:-4]][0][wallet.PRICE] == D(str(trade.price))

@pytest.mark.parametrize("initial_price, expected_is_profit", [(10.0, True), (60000, False)])
def test_crypto2fiat(initial_price, expected_is_profit, profitsCalculator_fixture):
    """
    Asserts correct profit is calculated. Need to prefill the wallet
    """

    trade = profitsCalculator_fixture._trades._trades.iloc[2]
    wallet = profitsCalculator_fixture._wallet

    initial_amount = 2*trade.vol 
    wallet.add(trade.pair[:-4], initial_amount, initial_price)
    wallet.setWalletCost(initial_price)

    is_profit = profitsCalculator_fixture.crypto2fiat(trade)
    
    cash_in = D(str(trade.price)) * D(str(trade.vol)) - D(str(trade.fee))
    initial_cost = D(str(initial_price)) * D(str(trade.vol))
    profit = cash_in - initial_cost

    assert is_profit == expected_is_profit 
    assert profitsCalculator_fixture.fifo_gains[trade.time.year][0][1] == profit
    assert wallet.wallet[trade.pair[:-4]][0][wallet.VOL] == D(str(initial_amount)) - D(str(trade.vol))
    assert wallet.wallet[trade.pair[:-4]][0][wallet.PRICE] == D(str(initial_price)) 








