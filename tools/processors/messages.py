from tools.commons import Message
from .commons import *


class DispatcherBotProcessor(MessageProcessor):
    """A processor that matches a context, then forwards the message to a list of sub-processors.
    This enables the botprocessor-matching mechanism to behave kinda like a decision tree"""

    def __init__(self, processors_list : List[MessageProcessor]):
        self.dispatcher = MessageDispatcher(processors_list)

    def process(self, text : str, sender_id : str, users_list : UserList):
        return self.dispatcher.dispatch(text, sender_id, users_list)


class CommandsDispatcherProcessor(DispatcherBotProcessor):
    """Reacts to commands of the form '/botname command' or 'botname, command' """

    def __init__(self, processors_list: List[MessageProcessor],  trigger_word: str = None, default_response :str = None):
        super().__init__(processors_list)
        self.trigger = trigger_word
        self.default_response = default_response if default_response is not None else "Commande non reconnue, pd"

    def match(self, text : str, sender_id : str, users_list : UserList):
        trigger = self.trigger.upper() if self.trigger is not None else users_list.my_name.upper()
        return text.upper().startswith(trigger + ",") \
               or text.upper().startswith("/" + trigger)

    def process(self, text : str, sender_id : str, users_list : UserList):
        without_cmd = text[len(users_list.my_name)+1:]
        response = super().process(without_cmd, sender_id, users_list)
        return Message(self.default_response) if response is None else response

