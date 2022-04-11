from decimal import Decimal as D
from datetime import datetime as dt
import os
import pytest
import re
from collections import defaultdict
from cryptopnl.main.fifo_with_trades import fifo_with_trades 
from cryptopnl.main.trades import Trades
from cryptopnl.wallet.wallet import wallet

@pytest.fixture
def fifo_with_trades_fixture(request):
    filename = request.module.__file__
    file_dir, _ = os.path.split(filename)
    test_dir, _ = os.path.split(file_dir)

    if os.path.isdir(os.path.join(test_dir, "_test_files")):
        trades_file = os.path.join(test_dir, "_test_files", "test_trades.csv")
        if os.path.exists(trades_file):
            return fifo_with_trades(trades_file=trades_file) 
    
    raise FileNotFoundError("Test files not found")
    

def test_fifo_with_trades_init(tmpdir, mocker):
    """
    Assert constructor buils a Trades instance from files
    """

    trades = tmpdir.join("trades.csv")
    with pytest.raises(FileNotFoundError):
        fifo_with_trades(trades_file = trades)
    trades.write("")

    mocker.patch("cryptopnl.main.trades.Trades", return_value=True)
    profits = fifo_with_trades(trades_file = trades)
    assert type(profits._trades) == Trades
    assert type(profits._wallet) == wallet
    assert type(profits.fifo_gains) == defaultdict 
    assert type(profits.fifo_gains.default_factory()) == list

    return

def test_fiat2crypto(fifo_with_trades_fixture):
    """
    Asserts crypto has been bought, stored and cost is updated 
    """
    
    trade = fifo_with_trades_fixture._trades._trades.iloc[0]
    wallet = fifo_with_trades_fixture._wallet
    initial_cost = 10

    wallet.setWalletCost(initial_cost)
    fifo_with_trades_fixture.fiat2crypto(trade)

    assert wallet._walletCost == initial_cost + trade.cost + trade.fee
    assert wallet.wallet[trade.pair[:-4]][0][wallet.VOL] == trade.vol
    assert wallet.wallet[trade.pair[:-4]][0][wallet.PRICE] == trade.price

@pytest.mark.parametrize("initial_price, expected_is_profit", [(D(10), True), (D(60000), False)])
def test_crypto2fiat(initial_price, expected_is_profit, fifo_with_trades_fixture):
    """
    Asserts correct profit is calculated. Need to prefill the wallet
    """

    trade = fifo_with_trades_fixture._trades._trades.iloc[2]
    wallet = fifo_with_trades_fixture._wallet

    initial_amount = 2*trade.vol 
    wallet.add(trade.pair[:-4], initial_amount, initial_price)

    is_profit = fifo_with_trades_fixture.crypto2fiat(trade)
    
    cash_in = trade.price * trade.vol - trade.fee
    initial_cost = initial_price * trade.vol
    profit = cash_in - initial_cost

    assert is_profit == expected_is_profit 
    assert fifo_with_trades_fixture.fifo_gains[trade.time.year][0][1] == profit
    assert wallet.wallet[trade.pair[:-4]][0][wallet.VOL] == initial_amount - trade.vol
    assert wallet.wallet[trade.pair[:-4]][0][wallet.PRICE] == initial_price 

def test_crypto2crypto_buy(fifo_with_trades_fixture):
    """
    Assert crypto has been correctly moved from one place to the other
    For the time being, no profit is calculated. Crypto is bought as original price of the selling crypto
    """

    trade = fifo_with_trades_fixture._trades._trades.iloc[1]
    wallet = fifo_with_trades_fixture._wallet

    bought_crypto = trade.pair[:4] if trade.type == "buy" else trade.pair[4:]
    sold_crypto = trade.pair[4:] if trade.type == "buy" else trade.pair[:4]

    # Wallet before the transaction
    initial_amount = 2*trade.vol*trade.price  
    initial_price = D(10) 
    wallet.add(sold_crypto, initial_amount, initial_price)

    fifo_with_trades_fixture.crypto2crypto(trade)
    
    assert wallet.wallet[sold_crypto][0][wallet.VOL] == initial_amount - trade.vol*trade.price - trade.fee
    assert wallet.wallet[sold_crypto][0][wallet.PRICE] == initial_price 
    assert wallet.wallet[bought_crypto][0][wallet.VOL] == trade.vol 
    assert wallet.wallet[bought_crypto][0][wallet.PRICE] == initial_price * trade.price + trade.fee / trade.vol * initial_price

def test_crypto2crypto_sell(fifo_with_trades_fixture):
    """
    Asserts crypto has been correctly moved from one place to the other
    For the time being, no profit is calculated. Crypto is bought as original price of the selling crypto
    """

    trade = fifo_with_trades_fixture._trades._trades.iloc[3]
    wallet = fifo_with_trades_fixture._wallet

    bought_crypto = trade.pair[:4] if trade.type == "buy" else trade.pair[4:]
    sold_crypto = trade.pair[4:] if trade.type == "buy" else trade.pair[:4]

    # Wallet before the transaction
    initial_amount = 2*trade.vol  
    initial_price = D(10) 
    wallet.add(sold_crypto, initial_amount, initial_price)
    wallet.setWalletCost(initial_price * initial_amount)

    fifo_with_trades_fixture.crypto2crypto(trade)
    
    assert wallet.wallet[sold_crypto][0][wallet.VOL] == initial_amount - trade.vol
    assert wallet.wallet[sold_crypto][0][wallet.PRICE] == initial_price 
    assert wallet.wallet[bought_crypto][0][wallet.VOL] == trade.vol * trade.price - trade.fee
    assert wallet.wallet[bought_crypto][0][wallet.PRICE] == initial_price * trade.vol / (trade.cost - trade.fee) 

def test_fifo_with_trades_process_trade(fifo_with_trades_fixture, mocker):
    """
    Asserts process_trade function calls appropriate function with appropriate trade
    """

    mock_f2c = mocker.patch("cryptopnl.main.fifo_with_trades.fifo_with_trades.fiat2crypto", return_value=True)
    mock_c2f = mocker.patch("cryptopnl.main.fifo_with_trades.fifo_with_trades.crypto2fiat", return_value=True)
    mock_c2c = mocker.patch("cryptopnl.main.fifo_with_trades.fifo_with_trades.crypto2crypto", return_value=True)
    fifo_with_trades_fixture.use_ledger_4_calc = False

    t0 = fifo_with_trades_fixture._trades._trades.iloc[0]
    fifo_with_trades_fixture.process_trade(t0)
    mock_f2c.assert_called_once_with(t0)

    t1 = fifo_with_trades_fixture._trades._trades.iloc[1]
    fifo_with_trades_fixture.process_trade(t1)
    mock_c2c.assert_called_once_with(t1)

    t2 = fifo_with_trades_fixture._trades._trades.iloc[2]
    fifo_with_trades_fixture.process_trade(t2)
    mock_c2f.assert_called_once_with(t2)
