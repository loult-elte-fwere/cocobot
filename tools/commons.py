

class UserList:
    """Wrapper around the 'currently connected users' dictionary"""

    def __init__(self, userlist_data):
        self.users = {user_data["userid"]: user_data for user_data in userlist_data}
        for id, user in self.users.items():
            if "you" in user["params"] and user["params"]["you"]:
                self.my_id = id

    def del_user(self, user_id):
        del self.users[user_id]

    def add_user(self, user_id, params):
        self.users[user_id] = {"params": params}

    def __getitem__(self, item : str):
        return self.users[item]["params"]

    def name(self, user_id):
        return self.users[user_id]["params"]["name"]

    def get_all_names(self):
        return [user["params"]["name"] for user in self.users.values()]

    def itsme(self, user_id):
        return self.my_id == user_id

    @property
    def my_name(self):
        return self.name(self.my_id)

    def __str__(self):
        return "Connected users :\n" \
               "%s" % "\n".join(["\t - %s" % self.name(user_id) for user_id in self.users])


class AbstractResponse:
    pass


class Message(AbstractResponse):

    def __init__(self, msg: str):
        self.msg = msg

    def to_dict(self):
        return {"lang": "fr", "msg": self.msg, "type": "msg"}


class BotMessage(AbstractResponse):

    def __init__(self, msg: str):
        self.msg = msg

    def to_dict(self):
        return {"type": "bot", "msg": self.msg}


class Sound(AbstractResponse):

    def __init__(self, sound_filepath: str):
        self.filepath = sound_filepath

    def get_bytes(self):
        with open(self.filepath, "rb") as soundfile:
            return soundfile.read()


class AttackCommand(AbstractResponse):

    def __init__(self, target_name: str, offset=1):
        self.target = target_name
        self.offset = offset

    def to_dict(self):
        return {"target": self.target, "order": self.offset, "type": "attack"}


class Sleep(AbstractResponse):

    def __init__(self, duration : int):
        self.duration = duration