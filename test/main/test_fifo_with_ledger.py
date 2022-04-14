from decimal import Decimal as D
from datetime import datetime as dt
import os
import pytest
import re
from collections import defaultdict
from cryptopnl.main.fifo_with_ledger import fifo_with_ledger
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

@pytest.fixture
def fifo_with_ledger_fixture(request):
    filename = request.module.__file__
    file_dir, _ = os.path.split(filename)
    test_dir, _ = os.path.split(file_dir)

    if os.path.isdir(os.path.join(test_dir, "_test_files")):
        trades_file = os.path.join(test_dir, "_test_files", "test_trades.csv")
        ledger_file = os.path.join(test_dir, "_test_files", "test_ledger.csv")
        if os.path.exists(trades_file) and os.path.exists(trades_file):
            return fifo_with_ledger(trades_file=trades_file, ledger_file=ledger_file) 
    
    raise FileNotFoundError("Test files not found")
    

def test_fifo_with_ledger_init(tmpdir, mocker):
    """
    Assert constructor buils a Trades instance from files
    """

    trades = tmpdir.join("trades.csv")
    ledger = tmpdir.join("ledger.csv")
    with pytest.raises(TypeError):
        fifo_with_ledger(trades_file = trades)
    with pytest.raises(FileNotFoundError):
        fifo_with_ledger(trades_file = trades, ledger_file=ledger)
    trades.write("")
    with pytest.raises(FileNotFoundError):
        fifo_with_ledger(trades_file = trades, ledger_file=ledger)
    ledger.write("")

    mocker.patch("cryptopnl.main.trades.Trades", return_value=True)
    profits = fifo_with_ledger(trades_file = trades, ledger_file = ledger)
    assert type(profits._trades) == Trades
    assert type(profits._wallet) == wallet
    assert type(profits.fifo_gains) == defaultdict 
    assert type(profits.fifo_gains.default_factory()) == list
    return

def test_get_ledgers_from_trade(fifo_with_ledger_fixture):
    "Asert the correct lines of the ledger are found"

    # First trade
    trade = fifo_with_ledger_fixture._trades._trades.iloc[0]
    l_ining_expected = fifo_with_ledger_fixture._trades._ledger.iloc[2]
    l_outing_expected = fifo_with_ledger_fixture._trades._ledger.iloc[3]

    l_ining, l_outing = fifo_with_ledger_fixture.get_ledgers_from_trade(trade)
    assert str(l_ining) == str(l_ining_expected)
    assert str(l_outing) == str(l_outing_expected)

    # Second trade
    trade = fifo_with_ledger_fixture._trades._trades.iloc[2]
    l_ining_expected = fifo_with_ledger_fixture._trades._ledger.iloc[7]
    l_outing_expected = fifo_with_ledger_fixture._trades._ledger.iloc[6]

    l_ining, l_outing = fifo_with_ledger_fixture.get_ledgers_from_trade(trade)
    assert str(l_ining) == str(l_ining_expected)
    assert str(l_outing) == str(l_outing_expected)

def test_fiat2crypto(fifo_with_ledger_fixture):
    """
    Asserts crypto has been bought, stored and cost is updated 
    """

    crypto = fifo_with_ledger_fixture._trades._ledger.iloc[2]
    fiat = fifo_with_ledger_fixture._trades._ledger.iloc[3]
    wallet = fifo_with_ledger_fixture._wallet
    initial_cost = 10
    crypto_name = crypto.asset

    wallet.setWalletCost(initial_cost)
    fifo_with_ledger_fixture.fiat2crypto(crypto = crypto, fiat = fiat)

    assert wallet._walletCost == initial_cost - fiat.amount + fiat.fee
    assert wallet.wallet[crypto_name][0][wallet.VOL] == crypto.amount 
    assert wallet.wallet[crypto_name][0][wallet.PRICE] == - fiat.amount / crypto.amount 
     
@pytest.mark.parametrize("initial_price, expected_is_profit", [(D(10), True), (D(60000), False)])
def test_crypto2fiat(initial_price, expected_is_profit, fifo_with_ledger_fixture):
    """
    Asserts correct profit is calculated. Need to prefill the wallet
    """

    crypto = fifo_with_ledger_fixture._trades._ledger.iloc[6]
    fiat = fifo_with_ledger_fixture._trades._ledger.iloc[7]
    wallet = fifo_with_ledger_fixture._wallet

    initial_amount = 2*(- crypto.amount)
    wallet.add(crypto.asset, initial_amount, initial_price)

    is_profit = fifo_with_ledger_fixture.crypto2fiat(crypto = crypto, fiat = fiat)
    
    cash_in = fiat.amount - fiat.fee
    initial_cost = initial_price * (- crypto.amount)
    profit = cash_in - initial_cost

    assert is_profit == expected_is_profit 
    assert fifo_with_ledger_fixture.fifo_gains[crypto.time.year][0][1] == profit
    assert wallet.wallet[crypto.asset][0][wallet.VOL] == initial_amount - (- crypto.amount)
    assert wallet.wallet[crypto.asset][0][wallet.PRICE] == initial_price 

@pytest.mark.parametrize("index_in, index_out", [(4, 5), (9, 8)])
def test_crypto2crypto(index_in, index_out, fifo_with_ledger_fixture):
    """
    Assert crypto has been correctly moved from one place to the other
    For the time being, no profit is calculated. Crypto is bought as original price of the selling crypto
    """

    crypto_in = fifo_with_ledger_fixture._trades._ledger.iloc[index_in]
    crypto_out = fifo_with_ledger_fixture._trades._ledger.iloc[index_out]
    wallet = fifo_with_ledger_fixture._wallet

    bought_crypto = crypto_in.asset
    sold_crypto = crypto_out.asset

    # Wallet before the transaction
    initial_amount = -2*crypto_out.amount  
    initial_price = D(10) 
    wallet.add(sold_crypto, initial_amount, initial_price)

    fifo_with_ledger_fixture.crypto2crypto(crypto_in, crypto_out)
    
    assert wallet.wallet[sold_crypto][0][wallet.VOL] == initial_amount - abs(crypto_out.amount) - crypto_out.fee
    assert wallet.wallet[sold_crypto][0][wallet.PRICE] == initial_price 
    assert wallet.wallet[bought_crypto][0][wallet.VOL] == crypto_in.amount - crypto_in.fee
    assert wallet.wallet[bought_crypto][0][wallet.PRICE] == ( abs(crypto_out.amount) + crypto_out.fee ) / (crypto_in.amount - crypto_in.fee) * initial_price

def test_fifo_with_ledger_process_trade(fifo_with_ledger_fixture, mocker):
    """
    Asserts process_trade function calls appropriate function with appropriate trade
    """

    mock_f2c = mocker.patch("cryptopnl.main.fifo_with_ledger.fifo_with_ledger.fiat2crypto", return_value=True)
    mock_c2f = mocker.patch("cryptopnl.main.fifo_with_ledger.fifo_with_ledger.crypto2fiat", return_value=True)
    mock_c2c = mocker.patch("cryptopnl.main.fifo_with_ledger.fifo_with_ledger.crypto2crypto", return_value=True)

    t0 = fifo_with_ledger_fixture._trades._trades.iloc[0]
    fiat = fifo_with_ledger_fixture._trades._ledger.iloc[3]
    crypto = fifo_with_ledger_fixture._trades._ledger.iloc[2]
    fifo_with_ledger_fixture.process_trade(t0)
    mock_f2c.assert_called_once_with(fiat, crypto)

    t1 = fifo_with_ledger_fixture._trades._trades.iloc[1]
    crypto_in = fifo_with_ledger_fixture._trades._ledger.iloc[4]
    crypto_out = fifo_with_ledger_fixture._trades._ledger.iloc[5]
    fifo_with_ledger_fixture.process_trade(t1)
    mock_c2c.assert_called_once_with(crypto_in, crypto_out)

    t2 = fifo_with_ledger_fixture._trades._trades.iloc[2]
    fiat = fifo_with_ledger_fixture._trades._ledger.iloc[7]
    crypto = fifo_with_ledger_fixture._trades._ledger.iloc[6]
    fifo_with_ledger_fixture.process_trade(t2)
    mock_c2f.assert_called_once_with(crypto, fiat)

    t3 = fifo_with_ledger_fixture._trades._trades.iloc[4]
    crypto_in = fifo_with_ledger_fixture._trades._ledger.iloc[9]
    crypto_out = fifo_with_ledger_fixture._trades._ledger.iloc[8]
    fifo_with_ledger_fixture.process_trade(t3)
    mock_c2c.assert_called_once_with(crypto_in, crypto_out)