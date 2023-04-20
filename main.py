#!/usr/bin/env python3

import json
import os.path
import sys

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
assert_file_exists("./msg_filters.json")
client = Client(config_file="./zuliprc")
reddit = praw.Reddit("zulipbot")
with open('./msg_filters.json') as f:
    msg_filter = json.load(f)

bot = ZulipBot(client, msg_filter)
bot.add_cmd(ZulipBotCmdGnagnagna())
bot.add_cmd(ZulipBotCmdWeather())
bot.add_cmd(ZulipBotCmdSpeak())
bot.add_cmd(ZulipBotCmdAudio())
bot.add_cmd(ZulipBotCmdVolume())
bot.add_cmd(ZulipBotCmdPlay())
bot.add_cmd(ZulipBotCmdRecord())
bot.add_cmd(ZulipBotCmdStop())
bot.add_cmd(ZulipBotCmdJoke(reddit))
bot.add_cmd(ZulipBotCmdAww(reddit))
bot.add_cmd(ZulipBotCmdGif(reddit))
bot.add_cmd(ZulipBotCmdRedPost(reddit))
bot.add_cmd(ZulipBotCmdRedPic(reddit))
bot.add_cmd(ZulipBotCmdRedGif(reddit))
bot.add_cmd(ZulipBotCmdRedPlay(reddit))
bot.add_cmd(ZulipBotCmdLunch())
bot.add_cmd(ZulipBotCmdZenQuote())
bot.run()
