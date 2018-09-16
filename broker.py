import datetime
import queue

from abc import ABCMeta, abstractmethod
from event import FillEvent, OrderEvent

class Broker(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError('Implement execute_order before proceeding')
    

class BasicBroker(Broker):

    def __init__(self, events):
        self.events = events
        
    def execute_order(self, event):
        if event.type == 'ORDER':
            fill_event = FillEvent(event.stamp,
                            event.symbol, 'BROKER', event.quantity,
                            event.order_type)
            self.events.put(fill_event)
