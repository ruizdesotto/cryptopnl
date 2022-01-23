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
        except APIException as e:
            print(f"API call failed {e}")
            raise 

    def getServerTime():
        """
        Get server time.

        :returns: datetime object of current server time
        """
        method = "Time"
        response = krakenAPI._publicAPI(method)
        unix_time = response[krakenAPI.UNIXTIME]
        return dt.fromtimestamp(unix_time) 

    def getHistoryTrades(pair):
        """
        Get history trades for a particular cryptocurrency.

        :returns: ([[price, vol, time, ...],], last)
        """
        #TODO set interval of time
        method = "Trades"
        response = krakenAPI._publicAPI(method, params = {"pair": pair})
        try:
            for v in response.values():
                if isinstance(v, list): 
                    # do the 3 thing
                    clean_data = [i[:3] for i in v]
                    return (clean_data, response["last"])
            raise KeyError("Pair not found")
        except Exception as e:
            print(f"Trades not retrieved: {e}")
            return None

        pass

    def getTickerAPI():
        """Get updated ticker information."""
        raise NotImplementedError 