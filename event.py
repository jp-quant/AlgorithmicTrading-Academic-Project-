class Event(object):
    pass


# ALL EVENTS CONTAIN TIMESTAMP


# MARKET EVENT = NEW DATAPOINT IS RELEASED/NEW TICK APPEARED ON SCREEN
class MarketEvent(Event):

    def __init__(self, stamp):
        self.type = 'MARKET'
        self.stamp = stamp

# SIGNAL EVENT: NEW SIGNAL AVAILABLE FROM STRATEGY, TELLING PORTFOLIO TO BUY OR SELL AT TIMESTAMP       
class SignalEvent(Event):

    def __init__(self,symbol,stamp,action = None,quantity = None):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.stamp = stamp
        self.action = action # BUY, SELL, EXIT
        self.quantity = quantity

# ORDER EVENT: NEW ORDER PLACED BY PORTFOLIO
class OrderEvent(Event):

    def __init__(self,symbol,stamp,order_type,quantity):
        self.type = 'ORDER'
        self.symbol = symbol
        self.quantity = quantity
        self.order_type = order_type
        self.stamp = stamp

    def __repr__(self):
        return "ORDER --> Symbol=%s, Type=%s, Quantity=%s TimeStamp= %s " % (self.symbol, self.order_type, self.quantity, self.stamp)

# FILL EVENT: AN ORDER WAS PLACED
class FillEvent(Event):
    def __init__(self,stamp,symbol,exchange,
                quantity,order_type,commission=None):
                self.type = 'FILL'
                self.stamp = stamp
                self.symbol = symbol
                self.exchange = exchange
                self.quantity = quantity
                self.order_type = order_type

                if commission is None:
                    self.commission = self.calculate_ib_commission()
                else:
                    self.commission = commission

    def calculate_ib_commission(self):
            return 1.3
