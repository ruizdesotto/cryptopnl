from datetime import datetime as dt
import pytest

from cryptopnl.api.krakenAPI import krakenAPI

# Not sure if I should use mock values to test the class
# Putting the API tag to methods that require connexion
# Equivalent mock values for off-line testing
# TODO test _publicAPI

MAX_WAIT_IN_SEC_ALLOWED = 3

def test_api_domain():
    """Verify correct end point."""
    assert krakenAPI.API_DOMAIN == "https://api.kraken.com" 

@pytest.mark.apitest
def test_getServerTime():
    """Retrieves a date close to now"""
    krakenTime = krakenAPI.getServerTime()
    deltaSeconds = (dt.now()-krakenTime).total_seconds()
    assert isinstance(krakenTime, dt)  
    assert abs(deltaSeconds) < MAX_WAIT_IN_SEC_ALLOWED    
    
@pytest.mark.apitest
def test_getHistoryTrades():
    """
    Retrieves information for a certain pair, ex. btceur
    Assert the retieved json object has the correct keys and prices can be cast to numbers
    """
    pair = "XXBTZEUR"
    data, timestamp = krakenAPI.getHistoryTrades(pair)
    assert isinstance(data, list) 
    items = data[0]
    assert isinstance(items, list)
    assert len(items) == 3
    try:
        float(items[0])
        float(items[1])
    except ValueError:
        assert "string" == "number"
    else:
        assert dt.fromtimestamp(items[2])
    assert isinstance(timestamp, str)

def test_mock_getServerTime(mocker):
    """
    Assert the correct time is obtained
    Mocking the api request (static method _publicAPI)
    """
    expected_result = {krakenAPI.UNIXTIME:1642967384}
    mocker.patch("cryptopnl.api.krakenAPI.krakenAPI._publicAPI", return_value=expected_result) 
    krakenTime = krakenAPI.getServerTime()
    assert isinstance(krakenTime, dt)  
    assert krakenTime.timestamp() == expected_result[krakenAPI.UNIXTIME] 

def test_mock_getHistoryTrades(mocker):
    """
    Assert the retrieved json object has the correct keys and prices can be cast to numbers
    Mocking the api request (static method _publicAPI)
    """
    pair = "XXBTZEUR"
    expected_result = {pair:[["30668.70000","0.00455250",1642967070.7617,"b","l",""]],"last":"1642969452668122012"}
    mocker.patch("cryptopnl.api.krakenAPI.krakenAPI._publicAPI", return_value=expected_result)
    data, timestamp = krakenAPI.getHistoryTrades(pair)
    assert isinstance(data, list) 
    items = data[0]
    assert isinstance(items, list)
    assert len(items) == 3
    assert float(items[0]) == float("30668.70000")
    assert float(items[1]) == float("0.00455250")
    assert isinstance(dt.fromtimestamp(items[2]), dt)
    assert dt.fromtimestamp(items[2]) == dt.fromtimestamp(1642967070.7617)
    assert isinstance(timestamp, str)

def test_getTickerAPI():
    """NOT IMPLEMENTED"""
    with pytest.raises(NotImplementedError):
        krakenAPI.getTickerAPI()

def test_mock_getHistoryTrades_sinceParam():
    assert False

    
