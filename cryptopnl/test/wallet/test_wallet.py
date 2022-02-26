from collections import defaultdict
from distutils.ccompiler import new_compiler
import pytest

from decimal import Decimal as D 
from cryptopnl.wallet.wallet import wallet

@pytest.fixture
def test_wallet():
    return wallet()

def test_wallet_init():
    """
    Test a wallet instance is initialized
    inner variables wallet and amounts are default dicts (list and D("0"))
    inner variable _walletCost is a decimal 0
    """

    test_wallet = wallet()

    assert type(test_wallet.wallet) is defaultdict
    assert test_wallet.wallet.default_factory is list
    assert type(test_wallet.amounts) is defaultdict
    assert test_wallet.amounts.default_factory() == D("0")
    assert test_wallet._walletCost == D("0") 
    
def test_wallet_add(test_wallet):
    """
    Test that some ammount of crypto has been added (first with fee included)
    """
    crypto = "BTC"
    amount, price, fee = 10, 5000, 1

    test_wallet.add(crypto, amount, price, fee)

    assert crypto in test_wallet.wallet
    assert crypto in test_wallet.amounts
    assert test_wallet.wallet[crypto][0][wallet.COST] == D(str(amount))*D(str(price)) + D(str(fee))
    assert test_wallet.wallet[crypto][0][wallet.VOL] == D(str(amount)) 
    assert test_wallet.wallet[crypto][0][wallet.PRICE] == price 
    assert test_wallet.amounts[crypto] == D(str(amount)) 

    test_wallet.add(crypto, amount, price)
    assert len(test_wallet.wallet[crypto]) == 2
    assert test_wallet.wallet[crypto][1][wallet.COST] == D(str(amount))*D(str(price)) 
    assert test_wallet.wallet[crypto][1][wallet.VOL] == D(str(amount)) 
    assert test_wallet.wallet[crypto][1][wallet.PRICE] == price 
    assert test_wallet.amounts[crypto] == 2*D(str(amount)) 

def test_wallet_take_from_one_chunk(test_wallet):
    """
    Take some amount of crypto (from same trade) from wallet (FIFO strategy)
    """
    
    crypto = "BTC"
    amount, price, fee = D(10), D(5000), D(1)
    test_wallet.add(crypto, amount, price, fee)
    test_wallet.add(crypto, amount, 2*price, fee) # Second transcation was more expensive

    out = D(7)
    initial_fiat_val = test_wallet.take(crypto, out)
    assert initial_fiat_val == out*price + out/amount*fee
    assert test_wallet.wallet[crypto][0][wallet.COST] == (D(1) - out/amount)*(amount*price + fee)
    assert test_wallet.wallet[crypto][0][wallet.VOL] == amount - out 
    assert test_wallet.amounts[crypto] == 2*amount - out

def test_wallet_take_from_two_chunks(test_wallet):
    """
    Take some amount of crypto (from different trades) from wallet (FIFO strategy)
    """
    
    crypto = "BTC"
    amount, price, fee = D(10), D(5000), D(1)
    test_wallet.add(crypto, amount, price, fee)
    test_wallet.add(crypto, amount, 2*price, fee) # Second transcation was more expensive

    out = D(14)
    initial_fiat_val = test_wallet.take(crypto, out)
    assert initial_fiat_val == (amount*price + fee + 
                                (out - amount)*2*price + (out - amount)/amount*fee)
    assert test_wallet.wallet[crypto][0][wallet.COST] == D() 
    assert test_wallet.wallet[crypto][0][wallet.VOL] == D() 
    assert test_wallet.wallet[crypto][1][wallet.COST] == (D(1) - (out - amount)/amount)*(amount*2*price + fee)
    assert test_wallet.wallet[crypto][1][wallet.VOL] == 2*amount - out
    assert test_wallet.amounts[crypto] == 2*amount - out

def test_wallet_take_nocrypto():
    """
    Attempt to take crypto non existing in the wallet
    Raises a ValueError
    """
    test_wallet = wallet()
    crypto = "BTC"
    amount = D(10)
    with pytest.raises(ValueError):
        test_wallet.take(crypto, amount)

def test_wallet_take_more_than_available():
    """
    Attemp to take more crypto thant there is in the wallet
    Raises a ValueError
    """
    test_wallet = wallet() 
    crypto = "BTC"
    amount, price, fee = D(10), D(5000), D(1)
    test_wallet.add(crypto, amount+fee, price, fee)
    test_wallet.add(crypto, amount+fee, 2*price, fee) # 2nd is more expensive

    out = 3*amount 
    with pytest.raises(ValueError):
        test_wallet.take(crypto, out)

def test_wallet_update_cost():
    """
    Updates wallets value (or initial cost)
    """
    test_wallet = wallet()
    add_cost = D(5)
    test_wallet.updateCost(add_cost)
    test_wallet.updateCost(add_cost)
    assert test_wallet._walletCost == 2*add_cost

def test_wallet_set_cost():
    """
    Updates wallets value (or initial cost)
    """
    test_wallet = wallet()
    new_cost = D(5)
    test_wallet.setWalletCost(2*new_cost)
    test_wallet.setWalletCost(new_cost)
    assert test_wallet._walletCost == new_cost

# TODO test wallet.getCurrentWalletValue -> triggers an API