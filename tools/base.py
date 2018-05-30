import html
import json
import logging

from asyncio import sleep, gather

import websockets

from tools.coco.client import CocoClient
from tools.commons import AbstractResponse, Message, BotMessage, AttackCommand, Sound, UserList
from tools.processors import MessageDispatcher, ConnectionDispatcher


class CoboBot:
    COCO_PULSE_TICK = 1 # number of seconds between each check

    def __init__(self, cookie: str, channel: str, domain: str, port: int, method: str,
                 messages_dispatcher: MessageDispatcher,
                 connect_dispatcher: ConnectionDispatcher,
                 cococlient: CocoClient):

        # setting up variables required by the server. The default is a Kabutops on the main lou server, I think
        self.cookie = cookie
        self.channel = "" if channel == "root" else channel
        self.domain = domain
        self.port = port
        self.method = method
        self.msg_dispatch = messages_dispatcher
        self.cnt_dispatch = connect_dispatcher
        self.user_list = None # type: UserList
        self.cococlient = cococlient

    async def _send_message(self, message):
        if isinstance(message, dict):
            await self.socket.send(json.dumps(message))
        elif isinstance(message, bytes):
            await self.socket.send(message)

    async def _dispatch_response(self, response_obj : AbstractResponse):
        if isinstance(response_obj, (Message, BotMessage, AttackCommand)):
            await self._send_message(response_obj.to_dict())
        elif isinstance(response_obj, Sound):
            await self._send_message(response_obj.get_bytes())

    async def _on_connect(self, msg_data):
        # registering the user to the user list
        self.user_list.add_user(msg_data["userid"], msg_data["params"])
        logging.info("%s connected" % self.user_list.name(msg_data["userid"]))
        message = self.cnt_dispatch.dispatch(msg_data["userid"], self.user_list)
        await self._send_message(message)

    async def _on_disconnect(self, msg_data):
        # removing the user from the userlist
        logging.info("%s disconnected" % self.user_list.name(msg_data["userid"]))
        self.user_list.del_user(msg_data["userid"])

    async def _on_message(self, msg_data):
        msg_data["msg"] = html.unescape(msg_data["msg"])  # removing HTML shitty encoding
        # logging the message to the DB
        logging.info("%s says : \"%s\"" % (self.user_list.name(msg_data["userid"]), msg_data["msg"]))

        response = None
        # dispatching the message to the processors. If there's a response, send it to the chat
        if not self.user_list.itsme(msg_data["userid"]):
            response = self.msg_dispatch.dispatch(msg_data["msg"], msg_data["userid"], self.user_list)

        if isinstance(response, list):
            for response_obj in response:
                await self._dispatch_response(response_obj)
        elif isinstance(response, AbstractResponse):
            await self._dispatch_response(response)

    async def socket_listener(self):
        while True:
            msg = await self.socket.recv()
            if type(msg) != bytes:
                msg_data = json.loads(msg, encoding="utf-8")
                msg_type = msg_data.get("type", "")
                if msg_type == "userlist":
                    self.user_list = UserList(msg_data["users"])
                    logging.info(str(self.user_list))

                elif msg_type == "msg":
                    await self._on_message(msg_data)

                elif msg_type == "connect":
                    await self._on_connect(msg_data)

                elif msg_type == "disconnect":
                    await self._on_disconnect(msg_data)

            else:
                logging.debug("Received sound file")

    async def coco_pulse(self):
        while True:
            logging.debug("Checking coco for new messages")
            await sleep(self.COCO_PULSE_TICK)
            if self.cococlient.is_connected:
                new_messages = self.cococlient.pulse()
                if isinstance(new_messages, list):
                    for response_obj in new_messages:
                        await self._dispatch_response(response_obj)
                elif isinstance(new_messages, AbstractResponse):
                    await self._dispatch_response(new_messages)

    async def listen(self):
        if self.method == "https":
            socket_address = 'wss://%s/socket/%s' % (self.domain, self.channel)
        else:
            socket_address = 'ws://%s:%i/socket/%s' % (self.domain, self.port, self.channel)
        logging.info("Listening to socket on %s" % socket_address)
        async with websockets.connect(socket_address,
                                      extra_headers={"cookie": "id=%s" % self.cookie}) as websocket:
            self.socket = websocket
            await gather(self.socket_listener(), self.coco_pulse())


