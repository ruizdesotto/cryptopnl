import abc

class exchangeAPI(metaclass = abc.ABCMeta):

    @property
    @abc.abstractmethod
    def API_DOMAIN():
        pass

    @abc.abstractstaticmethod
    def _publicAPI():
        """Generic public API request."""
        pass

    @abc.abstractstaticmethod
    def getServerTime():
        """Get server time."""
        pass

    @abc.abstractstaticmethod
    def getHistoryTrades():
        """Get history trades for a particular cryptocurrency."""
        pass

    @abc.abstractstaticmethod
    def getTickerAPI():
        """Get updated ticker information."""
        pass


class APIException(Exception):
    pass