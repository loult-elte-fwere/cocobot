from typing import List
from .requests import LoginRequest, PostLoginRequest

import logging


class Interlocutor:

    def __init__(self, nick: str, age:int, city: str, is_male: bool, conv_id: str):
        self.nick = nick
        self.age = age
        self.is_male = is_male
        self.city = city
        self.id = conv_id

    @classmethod
    def from_string(cls, str):
        # 47130922100412004Rastapopoulos
        # 47 (age) 1 (sexe) 30922 (city id) 100412(conv id)
        age = str[:2]
        is_male = int(str[2:3]) in (1, 6)
        city_id = str[3:8]
        conv_id = str[8:14]
        nick = str[17:]
        return cls(nick, age, city_id, is_male, conv_id)

    def __eq__(self, other):
        return other.nick == self.nick


class CocoClient:

    def __init__(self):
        self.interlocutors = []  # type: List[Interlocutor]
        self.current_interlocutor = None # type: Interlocutor

        self.user_id = None  # type:str
        self.user_pass = None  # type:str

    def connect(self, nick: str, age: int, is_female: bool, zip_code: str):
        login_req = LoginRequest(nick, age, is_female, zip_code)
        self.user_id, self.user_pass = login_req.retrieve()
        logging.info("Logged in to coco as %s" % self.nick)
        post_login_req = PostLoginRequest(self.user_id, self.user_pass)
        post_login_req.retrieve()
        logging.info("Post login successful")

    def pulse(self):
        pass

    def send_msg(self):
        pass

    def switch_conv(self, nick: str=None):
        pass
