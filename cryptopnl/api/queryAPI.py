import urllib.request as urllib2
import json

OFFSET = int(6e10) # 1min in ns of previous trades

def queryAPI(crypto, time, offset=OFFSET, logging = True):
    if logging: print("Querying...")
    api_domain = "https://api.kraken.com/0/public/Trades?"
    pair = crypto.lower()+"zeur"
    api_data = f"pair={pair}&since={time-offset}"
    api_request = urllib2.Request(api_domain + api_data)
    api_request.add_header("User-Agent", "Kraken REST API")

    try:
        api_reply = urllib2.urlopen(api_request).read().decode()
        data = json.loads(api_reply)   
        data = data["result"][pair.upper()]
        return data
    except Exception as error:
        print("API call failed (%s)" % error)
        return None