#!/usr/bin/env python

import argparse
import asyncio
import logging

from tools.base import CoboBot
from tools.processors import MessageDispatcher, CommandsDispatcherProcessor, ConnectionDispatcher

# setting up argument parser
parser = argparse.ArgumentParser(description='Le lou bot')
parser.add_argument('--cookie', type=str, help='usercookie to use')
parser.add_argument('--channel', type=str, help='channel to watch', default="")
parser.add_argument('--domain', type=str, help='domain to connect to', default="loult.family")
parser.add_argument('--port', type=int, help='port on which to connect the socket', default=80)
parser.add_argument('--method', type=str, help='http or https', default="https")


# setting up the various dispatchers
coco_commands = CommandsDispatcherProcessor([], "coco", default_response="de?")

root_messages_dispatcher = MessageDispatcher([coco_commands])

connections_dispatcher = ConnectionDispatcher([])

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    args = parser.parse_args()

    cocobot = CoboBot(args.cookie, args.channel, args.domain, args.port, args.method,
                      root_messages_dispatcher, connections_dispatcher)
    asyncio.get_event_loop().run_until_complete(pikabot.listen())



