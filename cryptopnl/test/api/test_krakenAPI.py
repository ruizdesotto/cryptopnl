from datetime import datetime as dt
import pytest

from cryptopnl.api.exchangeAPI import APIException
from cryptopnl.api.krakenAPI import krakenAPI

# TODO test _publicAPI

MAX_WAIT_IN_SEC_ALLOWED = 3

def test_api_domain():
    """Verify correct end point."""
    assert krakenAPI.API_DOMAIN == "https://api.kraken.com" 

def test_mock__publicAPI(mocker):
    """
    Assert correct address is reach and json has correct keys
    """
    expected_result = {krakenAPI.RESULT:"some reults", "error": "an error"}
    api_mock = mocker.patch("urllib.request.urlopen.read", return_value=True)
    api_mock_b = mocker.patch("urllib.request.urlopen.decode", return_value=True)
    # TODO define magick mock !
    assert False


def test_mock_getServerTime(mocker):
    """
    Assert the correct time is obtained
    """
    expected_result = {krakenAPI.UNIXTIME:1642967384}
    public_mock = mocker.patch("cryptopnl.api.krakenAPI.krakenAPI._publicAPI", return_value=expected_result) 
    krakenTime = krakenAPI.getServerTime()

    public_mock.assert_called_once_with("Time")
    assert isinstance(krakenTime, dt)  
    assert krakenTime.timestamp() == expected_result[krakenAPI.UNIXTIME] 

@pytest.mark.parametrize("output", 
            ["Im drunk", {}, {krakenAPI.UNIXTIME:-1}])
def test_mock_getServerTime_ImproperFormat(output, mocker):
    """
    Assert APIException if the time is not found 
    """
    mocker.patch("cryptopnl.api.krakenAPI.krakenAPI._publicAPI", return_value=output) 
    with pytest.raises(APIException):
        _ = krakenAPI.getServerTime()

def test_mock_getHistoryTrades(mocker):
    """
    Assert the retrieved json object has the correct keys and prices can be cast to numbers
    """
    pair = "XXBTZEUR"
    expected_result = {pair:[["30668.70000","0.00455250",1642967070.7617,"b","l",""]],"last":"1642969452668122012"}
    public_mock = mocker.patch("cryptopnl.api.krakenAPI.krakenAPI._publicAPI", return_value=expected_result)
    data, timestamp = krakenAPI.getHistoryTrades(pair)
    items = data[0]

    public_mock.assert_called_once_with("Trades", {"pair": pair})
    assert isinstance(data, list) 
    assert isinstance(items, list)
    assert len(items) == 3
    assert float(items[0]) == float("30668.70000")
    assert float(items[1]) == float("0.00455250")
    assert isinstance(dt.fromtimestamp(items[2]), dt)
    assert dt.fromtimestamp(items[2]) == dt.fromtimestamp(1642967070.7617)
    assert isinstance(timestamp, float)

def test_mock_getHistoryTrades_sinceParam(mocker):
    """
    Assert the retrieved data is after a specific defined time 
    """
    pair = "XXBTZEUR"
    since_time = 1643135792
    expected_result = {pair:[["30668.70000","0.00455250",1643135792.000001,"b","l",""]],"last":"1643135792000001000"}
    public_mock = mocker.patch("cryptopnl.api.krakenAPI.krakenAPI._publicAPI", return_value=expected_result)
    data, timestamp = krakenAPI.getHistoryTrades(pair, since=since_time)
    
    public_mock.assert_called_once_with("Trades", {"pair": pair, "since": str(since_time)})
    assert dt.fromtimestamp(data[0][2]) > dt.fromtimestamp(since_time)
    assert dt.fromtimestamp(timestamp) > dt.fromtimestamp(since_time)

@pytest.mark.parametrize("output", 
            ["Im drunk", 
             {"XXBTZEUR":[]}, 
             {"XXBTZEUR":[["",]]},
             {"XXBTZEUR":[["","",""]]},
             {"XXBTZEUR":[["","",""]],"last":""}
             ])
def test_mock_getHistoryTrades_ImproperFormat(output, mocker):
    """
    Assert improper formats are dealt with 
    """
    pair = "XXBTZEUR"
    mocker.patch("cryptopnl.api.krakenAPI.krakenAPI._publicAPI", return_value=output)

    with pytest.raises(APIException):
        _, _ = krakenAPI.getHistoryTrades(pair)

def test_mock_getTickerAPI():
    """NOT IMPLEMENTED"""
    with pytest.raises(NotImplementedError):
        krakenAPI.getTickerAPI()
