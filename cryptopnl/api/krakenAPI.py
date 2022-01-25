from datetime import datetime as dt
import json
from urllib import request
from cryptopnl.api.exchangeAPI import exchangeAPI, APIException

class krakenAPI(exchangeAPI):

    API_DOMAIN  = "https://api.kraken.com"
    PUBLIC = "/0/public/"
    RESULT = "result"
    UNIXTIME = "unixtime"

    def _publicAPI(method, params = None, since = None):
        """
        Generic public API request.

        :param method: API method to retrieve data from
        :returns: JSON response
        :raises APIException: if there was a connexion error
        """
        # TODO:LOGGING add logging here

        if params is None: api_data = "" 
        else:
            api_data = "&".join([k + "=" + v for k,v in params.items()])
        query = "".join([krakenAPI.API_DOMAIN, krakenAPI.PUBLIC, method, "?", api_data])
        api_request = request.Request(query)
        api_request.add_header("User-Agent", "Kraken REST API")
        
        try:
            api_reply = request.urlopen(api_request).read()
            api_reply = api_reply.decode()
            api_reply = json.loads(api_reply)
            return api_reply[krakenAPI.RESULT]
        except KeyError:
            print("No results retrieved")
            print(api_reply)
            raise
        except APIException as e: # Maybe not here or like here
            print(f"API call failed {e}")
            raise 

    def getServerTime():
        """
        Get server time.

        :returns: datetime object of current server time
        """
        method = "Time"
        response = krakenAPI._publicAPI(method)
        try:
            unix_time = response[krakenAPI.UNIXTIME]
            return dt.fromtimestamp(unix_time) 
        except KeyError as e:
            raise APIException(e)
        except OSError as e:
            raise APIException(e)
        

    def getHistoryTrades(pair, since = None):
        """
        Get history trades for a particular cryptocurrency.
        If since is not given, the last 1000 values will be given, 
        else the 1000 following the timestamp are.

        :param pair: cryptocurrency pair
        :param since: (optional) timestamp in ns to which start the query 
        :returns: ([[price, vol, time (s), ...],], last (s))
        """
        method = "Trades"
        params = {"pair": pair}
        if since is not None: params["since"] = str(since)
        response = krakenAPI._publicAPI(method, params)
        try:
            for v in response.values():
                if isinstance(v, list): 
                    clean_data = [i[:3] for i in v]
                    return (clean_data, float(response["last"])/1e9)
        except KeyError as e:
            raise APIException()
        

    def getTickerAPI():
        """Get updated ticker information."""
        raise NotImplementedError 