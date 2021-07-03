#!/usr/bin/env python3

import json
import sys
import os.path

import praw
from zulip import Client

from zulipbot.bot import ZulipBot
from zulipbot.commands import *


# --------------------------------------------------------------
# functions
# --------------------------------------------------------------
def assert_file_exists(path):
    if not os.path.isfile(path):
        print("ERROR: file '{}' wasn't found\nSee README.md".format(path),
              file=sys.stderr)
        exit(1)


# --------------------------------------------------------------
# execution
# --------------------------------------------------------------
assert_file_exists("./zuliprc")
assert_file_exists("./praw.ini")
assert_file_exists("./msg_filter.json")
client = Client(config_file="./zuliprc")
reddit = praw.Reddit("zulipbot")
with open('./msg_filter.json') as f:
    msg_filter = json.load(f)

bot = ZulipBot(client, msg_filter)
bot.add_cmd(ZulipBotCmdCoucou())
bot.add_cmd(ZulipBotCmdGnagnagna())
bot.add_cmd(ZulipBotCmdJoke(reddit))
bot.run()
