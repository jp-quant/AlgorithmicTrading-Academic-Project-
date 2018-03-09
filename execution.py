import datetime
import Queue

from abc import ABCMeta, abstractmethod
from event import FillEvent, OrderEvent

class Execution(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError('Implement execute_order before proceeding')
    

class BasicExecution(Execution):

    def __init__(self, events):
        self.events = events
        
    def execute_order(self, event):
        if event.type == 'ORDER':
            fill_event = FillEvent(datetime.datetime.utcnow(),
                            event.symbol, 'BROKER', event.quantity,
                            event.direction, None)
            self.events.put(fill_event)
