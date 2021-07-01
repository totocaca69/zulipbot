#!/usr/bin/env python3

from zulip import Client

from zulipbot.bot import ZulipBot
from zulipbot.commands import *

client = Client(config_file="./zuliprc")

bot = ZulipBot(client)
bot.add_cmd(ZulipBotCmdCoucou())
bot.run()
