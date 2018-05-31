import logging
import random
from typing import List, Dict, Tuple, Union, Set
from collections import defaultdict

from .requests import LoginRequest, PostLoginRequest, PulseRequest, SendMsgRequest
from ..commons import BotMessage, Message, AbstractResponse


class Interlocutor:

    def __init__(self, nick: str, age: int, city: str, is_male: bool, conv_id: str):
        self.nick = nick
        self.age = age
        self.is_male = is_male
        self.city = city
        self.id = conv_id

    @classmethod
    def from_string(cls, str):
        # 47130922100412004Rastapopoulos
        # 47 (age) 1 (sexe) 30922 (city id) 100412(conv id)
        age = int(str[:2])
        is_male = int(str[2:3]) in (1, 6)
        city_id = str[3:8]
        conv_id = str[8:14]
        nick = str[17:]
        return cls(nick, age, city_id, is_male, conv_id)

    def to_botmessage(self):
        sex_indic = "un homme" if self.is_male else "une femme"
        return BotMessage("Conversation avec %s, %s de %i ans" %(self.nick, sex_indic, self.age))

    def __eq__(self, other):
        return other.nick == self.nick

    def __hash__(self):
        return hash(self.nick)


class CocoClient:

    def __init__(self):
        self.interlocutors = set()  # type: Set[Interlocutor]
        self.current_interlocutor = None # type: Interlocutor
        self.histories = defaultdict(list)  # type:defaultdict[Interlocutor,List[Tuple]]

        self.user_id = None  # type:str
        self.user_pass = None  # type:str
        self.nick = None  # type:str
        self.is_connected = False

    def _format_history(self, interlocutor: Interlocutor):
        if interlocutor in self.histories:
            return [BotMessage("💬 %s: %s" % (nick, msg))
                    for nick, msg in self.histories[interlocutor][-5:]]
        else:
            return []

    def __process_and_format_received_msg(self, received_msgs):
        out = []
        for user_code, msg in received_msgs:
            user = Interlocutor.from_string(user_code)
            self.interlocutors.add(user)
            self.histories[user].append((user.nick, msg))
            logging.info("Msg from %s : %s" % (user.nick, msg))

            if self.current_interlocutor is not None and user == self.current_interlocutor:
                out.append(Message("💬 %s: %s" % (user.nick, msg)))
            else:
                out.append(BotMessage("💬 %s: %s" % (user.nick, msg)))
        return out

    def disconnect(self):
        self.interlocutors = set()
        self.histories = defaultdict(list)
        self.current_interlocutor = None
        self.is_connected = False
        self.nick = None

    def connect(self, nick: str, age: int, is_female: bool, zip_code: str):
        self.disconnect()

        self.nick = nick
        login_req = LoginRequest(nick, age, is_female, zip_code)
        self.user_id, self.user_pass = login_req.retrieve()
        logging.info("Logged in to coco as %s" % self.nick)
        post_login_req = PostLoginRequest(self.user_id, self.user_pass)
        if post_login_req.retrieve():
            logging.info("Post login successful")
            self.is_connected = True

        else:
            logging.info("Post login failed")

    def pulse(self) -> List[AbstractResponse]:
        pulse_req = PulseRequest(self.user_id, self.user_pass)
        received_msg = pulse_req.retrieve()
        return self.__process_and_format_received_msg(received_msg)

    def send_msg(self, msg: str) -> List[AbstractResponse]:
        if self.current_interlocutor is not None:
            sendmsg_req = SendMsgRequest(self.user_id, self.user_pass, self.current_interlocutor.id, msg)
            output = sendmsg_req.retrieve()
            self.histories[self.current_interlocutor].append((self.nick, msg))
            out_msg = Message("💬 %s: %s" % (self.nick, msg))

            if output:
                return [out_msg] + self.__process_and_format_received_msg(output)
            else:
                return [out_msg]
        else:
            return [BotMessage("Il faut sélectionner une conversation d'abord pd")]

    def switch_conv(self, nick: str=None) -> Union[List[BotMessage], BotMessage]:
        if not self.interlocutors:
            return BotMessage("Pas de conversations en cours")

        new_interlocutor = None
        if nick is not None:
            for usr in self.interlocutors:
                if usr.nick.upper() == nick.upper():
                    new_interlocutor = usr
                    break
        else:
            new_interlocutor = random.choice(list(self.interlocutors))

        if new_interlocutor is None:
            return BotMessage("Impossible de trouver l'utilisateur")
        else:
            self.current_interlocutor = new_interlocutor
            return [new_interlocutor.to_botmessage()] + \
                   self._format_history(self.current_interlocutor)

    def list_convs(self):
        return BotMessage("Conversations : " + ", ".join(["%s(%i)" % (usr.nick, usr.age)
                                                          for usr in self.interlocutors]))