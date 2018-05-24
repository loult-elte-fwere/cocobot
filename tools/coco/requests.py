from urllib.request import Request, urlopen
from random import randint, choice, random
from string import ascii_uppercase

from .tools import get_city_id, coco_cipher, encode_msg

class BaseCocoRequest:
    host = 'http://cloud.coco.fr/'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0',
               'Cookie': '_ga=GA1.2.795717920.1518381607',
               'Host': 'cloud.coco.fr',
               'Referer': 'http://www.coco.fr/chat/index.html'}

    def _get_url(self):
        pass

    def _parse_response(self, response):
        pass

    def retrieve(self):
        req = Request(self._get_url(), headers=self.headers)
        response = urlopen(req).read()
        cleaned = response.decode("utf-8")[len("process1('#"):-len("');")]
        return self._parse_response(cleaned)


class LoginRequest(BaseCocoRequest):

    def __init__(self, nick: str, age: int, is_female: bool, zip_code: str):
        self.nick = nick
        self.age = str(age)
        self.sex = str('2' if is_female else '1')
        self.city = get_city_id(zip_code)

    def _get_url(self):
        identifier = str(randint(100000000, 990000000)) + '0' + ''.join(choice(ascii_uppercase) for i in range(20))
        return self.host + '40' + self.nick + '*' + self.age + self.sex + self.city + identifier

    def _parse_response(self, response):
        credentials = response[2:14]
        return credentials[:6], credentials[6:] # user_id and password


class LoggedInRequest(BaseCocoRequest):

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password

    @property
    def token(self):
        return self.user_id + self.password


class PostLoginRequest(LoggedInRequest):

    client_id_str = "3551366741*0*1aopiig*-940693579*192.168.0.14*0"

    def _get_url(self):
        return self.host + '52' + self.token + coco_cipher(self.client_id_str, self.password)

    def _parse_response(self, response):
        """Checks if the post-login was successful"""
        # TODO
        pass


class PulseRequest(LoggedInRequest):
    # typical response :
    # process1('#669276787#30130916276787003HotelDiscret#salut_toi#47130922100412004Rastapopoulos#Mes_hommages,_Mademoiselle...#47130922100412004Rastapopoulos#Jamais_un_mari_ne_sera_si_bien_veng*r_que_par_l*8amant_de_sa_femme.#40636427396758003leo913#cam.!7w2738702leo913#396758#');
    # process1('#669276787#30130916276787003HotelDiscret#chaude=#292223#32130926292223003HDirect#Salut,_te_faire_payer_pour_un_plan_sexe_ca_te_plairais_=#');
    # process1('#66945630927183748003WolfiSoDentelle#en_manque_de_sommeil_peut_etre_=_#');
    # ^ le type a 45 balais donc il doit falloir couper après 669
    # process1('#66929630926396791003Clouds#bonsoir,_comment_vas-tu_=_que_cherches_tu_=#');
    # idem avec lui, il a 29 ans
    def _get_url(self):
        return self.host + "95" + self.token + "?" + str(random())

    def _parse_response(self, response):
        """Can either be a single message or several messages"""
        # TODO
        pass


class SendMsgRequest(LoggedInRequest):

    def __init__(self, user_id, password, conv_id: str, msg: str):
        super().__init__(user_id, password)
        self.conv_id = conv_id
        self.msg = msg

    def _get_url(self):
        return self.host + "99" + self.token + self.conv_id + encode_msg(self.msg)

    def _parse_response(self, response):
        """Response to a send message request can either just be #97x or an
        actual message (like in pulse request)"""
        # TODO
        pass