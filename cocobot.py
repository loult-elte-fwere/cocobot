#!/usr/bin/env python

import argparse
import asyncio
import logging

from tools.base import CoboBot
from tools.processors import MessageDispatcher, CommandsDispatcherProcessor, ConnectionDispatcher
from tools.processors.messages import *

# setting up argument parser
parser = argparse.ArgumentParser(description='Le lou bot')
parser.add_argument('--cookie', type=str, help='usercookie to use')
parser.add_argument('--channel', type=str, help='channel to watch', default="")
parser.add_argument('--domain', type=str, help='domain to connect to', default="loult.family")
parser.add_argument('--port', type=int, help='port on which to connect the socket', default=80)
parser.add_argument('--method', type=str, help='http or https', default="https")
parser.add_argument('--verbose', help='print debug information', action='store_true')

# setting up coco client
cococlient = CocoClient()

# setting up the various dispatchers
cmds = [cmd_class(cococlient) for cmd_class in (CocoConnectCommand, CocoMsgCommand, CocoListCommand,
                                                CocoSwitchCommand, CocoQuitCommand, CocoBroadcastCommand)]
help_cmd = BotHelp(cmds)

coco_commands = CommandsDispatcherProcessor(cmds,
                                            "coco", default_response="de?")

root_messages_dispatcher = MessageDispatcher([coco_commands])

connections_dispatcher = ConnectionDispatcher([])

if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("websockets").setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.INFO)

    cocobot = CoboBot(args.cookie, args.channel, args.domain, args.port, args.method,
                      root_messages_dispatcher, connections_dispatcher, cococlient)
    asyncio.get_event_loop().run_until_complete(cocobot.listen())



