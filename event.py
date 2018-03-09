class Event(object):
    pass

class MarketEvent(Event):

    def __init__(self):
        self.type = 'MARKET'
            
class SignalEvent(Event):
    def __init__(self,symbol,datetime,signal_type):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
            
class OrderEvent(Event):

    def __init__(self,symbol,order_type,quantity,direction):
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def __repr__(self):
        return "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % (self.symbol, self.order_type, self.quantity, self.direction)

class FillEvent(Event):
    def __init__(self,timeindex,symbol,exchange,
                quantity,direction,fill_cost,comission=None):
                self.type = 'FILL'
                self.timeindex = timeindex
                self.symbol = symbol
                self.exchange = exchange
                self.quantity = quantity
                self.direction = direction
                self.fill_cost = fill_cost

                if comission is None:
                    self.commission = self.calculate_ib_commission()
                else:
                    self.comission = comission

    def calculate_ib_commission(self):
            return 1.3
