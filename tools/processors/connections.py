import logging
from typing import List

from tools.commons import UserList


class ConnectProcessor:
    def match(self, sender_id: str, users_list: UserList) -> bool:
        """Returns true if this is the kind of user connection a processor should respond to"""
        pass

    def process(self, sender_id: str, users_list: UserList) -> str:
        """Processes a message and returns an answer"""
        pass


class ConnectionDispatcher:

    def __init__(self, processor_list: List[ConnectProcessor]):
        self.processor_list = processor_list

    def dispatch(self, sender_id: str, users_list: UserList) -> str:
        """Tells its first botprocessor to match the message to process this message and returns its answer"""
        for processor in self.processor_list:
            if processor.match(sender_id, users_list):
                logging.info("Matched %s" % processor.__class__.__name__)
                return processor.process(sender_id, users_list)

        return None
