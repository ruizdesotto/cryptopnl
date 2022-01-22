

class exchangeAPI():

    def publicAPI(method, params = {}, log = True):
        """
        Public API format
        :param method 
        :param params
        """
        api_data = "?"
        for k, v in params.items():
            api_data += f"{k}={v}&"
        
        query = API_DOMAIN + API_PBLC + method + api_data
        if log: print(f"{dt.now().strftime('%d/%m/%Y %H:%M:%S')} - Quering:\n\t{query}\n")
        try: return get(query).json()
        except Exception as error: print("API call failed (%s)" % error)
        return None 

    def getServerTime():
        method = "Time" 
        data = publicAPI(method)
        unix = data["result"]["unixtime"]
        return dt.fromtimestamp(unix)

    def getPriceAPI(pair, offset = 0, t = None):
        """
            getPriceAPI: API to retrieve data from kraken exchange
                the max number of instances returned is 1000

            :param pair
            :param offset : in ns, offset from now to retrieve the data 
            :param t : in ns, starting timestamp for the query 
            :return : (non-parsed info from the exchange, timestamp)
        """
        if t is None and offset: t = time.time_ns() 

        method = "Trades"
        params = {"pair": pair}
        if offset or t is not None: params["since"] =  t - offset 

        data = publicAPI(method, params)
        try:
            data = data["result"]
            for key in data: 
                if isinstance(data[key], list): return (data[key], data["last"])
            raise Exception("Improper format") 
        except Exception as error:
            print("API call failed (%s)" % error)
            return None
            
    def getTickerAPI(pair):
        """
            getTickerAPI: API to retrieve data from kraken exchange
                Current price information
            :param pair
            :return : ticker info dictionary 
        """
        method = "Ticker"
        params = {"pair": pair}

        data = publicAPI(method, params)
        try:
            data = data["result"]
            for key in data: return data[key]
            raise Exception("Improper format") 
        except Exception as error:
            print("API call failed (%s)" % error)
            return None

    if __name__ == "__main__":

        print(getServerTime())
        print(getTickerAPI("adaeur"))
