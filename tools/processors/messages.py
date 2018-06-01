from tools.coco.client import CocoClient
from tools.commons import Message, BotMessage
from tools.constants import AUTHORIZED_USERIDS
from .commons import *


class DispatcherBotProcessor(MessageProcessor):
    """A processor that matches a context, then forwards the message to a list of sub-processors.
    This enables the botprocessor-matching mechanism to behave kinda like a decision tree"""

    def __init__(self, processors_list: List[MessageProcessor]):
        self.dispatcher = MessageDispatcher(processors_list)

    def process(self, text: str, sender_id: str, users_list: UserList):
        return self.dispatcher.dispatch(text, sender_id, users_list)


class CommandsDispatcherProcessor(DispatcherBotProcessor):
    """Reacts to commands of the form '/botname command' or 'botname, command' """

    def __init__(self, processors_list: List[MessageProcessor],  trigger_word: str = None, default_response: str = None):
        super().__init__(processors_list)
        self.trigger = trigger_word
        self.default_response = default_response if default_response is not None else "Commande non reconnue, pd"

    def match(self, text: str, sender_id: str, users_list: UserList):
        trigger = self.trigger.upper() if self.trigger is not None else users_list.my_name.upper()
        return text.upper().startswith(trigger + ",") \
               or text.upper().startswith("/" + trigger)

    def process(self, text: str, sender_id : str, users_list: UserList):
        without_cmd = text[len(self.trigger)+1:]
        response = super().process(without_cmd, sender_id, users_list)
        return Message(self.default_response) if response is None else response


class BaseCocobotCommand(MessageProcessor):

    HELP_STR = None
    _cmd_suffix = ""

    def __init__(self, cococlient: CocoClient):
        self.cococlient = cococlient

    def match(self, text : str, sender_id : str, users_list : UserList):
        return text.lower().startswith(self._cmd_suffix)


class CocoConnectCommand(BaseCocobotCommand):
    HELP_STR = "/coconnect pseudo age code_postal"
    _cmd_suffix = "nnect"

    def process(self, text : str, sender_id : str, users_list : UserList):
        text = text[len(self._cmd_suffix):].strip()
        try:
            nick, age, zip_code = text.split()
        except ValueError:
            return Message("Pas le bon nombre d'arguments, pd")

        if not nick.isalnum():
            return Message("Le pseudo doit être alphanumérique, pd")

        if len(age) != 2 or not age.isnumeric():
            return Message("L'âge c'est avec DEUX chiffres (déso bulbi)")

        if int(age) < 15:
            return Message("L'âge minimum c'est 15 ans (déso bubbi)")

        if len(zip_code) != 5 or not zip_code.isnumeric():
            return Message("Le code postal c'est 5 chiffres, pd")

        try:
            self.cococlient.connect(nick, int(age), True, zip_code)
        except ValueError:
            return Message("Le code postal a pas l'air d'être bon")

        if self.cococlient.is_connected:
            return BotMessage("Connecté en tant que %s, de %s ans" % (nick, age))
        else:
            return BotMessage("La connection a chié, déswe")


class CocoMsgCommand(BaseCocobotCommand):
    HELP_STR = "/cocospeak message"
    _cmd_suffix = "speak"

    def process(self, text : str, sender_id : str, users_list : UserList):
        text = text[len(self._cmd_suffix):].strip()
        return self.cococlient.send_msg(text)


class CocoBroadcastCommand(BaseCocobotCommand):
    HELP_STR = "/cocoall message"
    _cmd_suffix = "all"

    def process(self, text : str, sender_id : str, users_list : UserList):
        text = text[len(self._cmd_suffix):].strip()
        return self.cococlient.broadcast_msg(text)


class CocoSwitchCommand(BaseCocobotCommand):
    HELP_STR = "/cocoswitch [pseudo de l'interlocuteur]"
    _cmd_suffix = "switch"

    def process(self, text : str, sender_id : str, users_list : UserList):
        text = text[len(self._cmd_suffix):].strip()
        if text:
            return self.cococlient.switch_conv(text)
        else:
            return self.cococlient.switch_conv()


class CocoListCommand(BaseCocobotCommand):
    HELP_STR = "/cocolist"
    _cmd_suffix = "list"

    def process(self, text : str, sender_id : str, users_list : UserList):
        return self.cococlient.list_convs()


class CocoQuitCommand(BaseCocobotCommand):
    HELP_STR = "/cocoquit"
    _cmd_suffix = "quit"

    def match(self, text : str, sender_id : str, users_list : UserList):
        return super().match(text, sender_id, users_list) and sender_id in AUTHORIZED_USERIDS

    def process(self, text : str, sender_id : str, users_list : UserList):
        self.cococlient.disconnect()
        return BotMessage("Déconnecté!")


class BotHelp(MessageProcessor):
    """Displays the help string for all processors in the list that have a helpt string"""

    def __init__(self, processors_list: List[BaseCocobotCommand]):
        all_help_strs = [proc.HELP_STR
                        for proc in processors_list if proc.HELP_STR is not None]
        self.help_str = ", ".join(all_help_strs)

    def match(self, text : str, sender_id : str, users_list : UserList):
        return text.lower().startswith("help")

    def process(self, text : str, sender_id : str, users_list : UserList):
        return BotMessage(self.help_str)


