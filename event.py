class Event(object):
    pass


# ALL EVENTS CONTAIN TIMESTAMP


# MARKET EVENT = NEW DATAPOINT IS RELEASED/NEW TICK APPEARED ON SCREEN
class MarketEvent(Event):

    def __init__(self, stamp):
        self.type = 'MARKET'
        self.stamp = stamp

# SIGNAL EVENT: NEW SIGNAL AVAILABLE FROM STRATEGY, TELLING PORTFOLIO TO BUY OR SELL, with stamp of when signal released       
class SignalEvent(Event):

    def __init__(self,symbol,stamp,order_type,action,shares,limit_price=None,stop_price=None):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.shares= shares
        self.action = action # BUY, SELL
        self.order_type = order_type
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.stamp = stamp

# ORDER EVENT: NEW ORDER PLACED BY PORTFOLIO
class OrderEvent(Event):

    def __init__(self,symbol,stamp,order_type,action,shares,limit_price=None,stop_price=None):
        self.type = 'ORDER'
        self.symbol = symbol
        self.shares = shares # int64
        self.action = action # 'BUY','SELL'
        self.order_type = order_type # 'MARKET','STOP','LIMIT','STOP-LIMIT'
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.stamp = stamp

    def __repr__(self):
        return '''ORDER[-type=%s]: %s],
            Action = %s, Shares=%s
            TimeStamp= %s ''' % (self.order_type,self.symbol, self.action, self.shares, self.stamp)

# FILL EVENT: AN ORDER WAS PLACED
class FillEvent(Event):
    def __init__(self,stamp,symbol,exchange,
                shares,action,order_type,commission=None):
                self.type = 'FILL'
                self.stamp = stamp
                self.symbol = symbol
                self.exchange = exchange
                self.shares = shares
                self.action = action
                self.order_type = order_type

                if commission is None:
                    self.commission = self.calculate_ib_commission()
                else:
                    self.commission = commission

    def calculate_ib_commission(self):
            return 0.0
