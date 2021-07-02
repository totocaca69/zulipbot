#!/usr/bin/env python3

from zulip import Client
import praw

from zulipbot.bot import ZulipBot
from zulipbot.commands import *

client = Client(config_file="./zuliprc")    # requires ./zuliprc
reddit = praw.Reddit("bot1")                # requires ./praw.ini

msg_filter = {
    "type": "stream",
    "display_recipient": "Bosch",
}
# msg_filter = {
#     "type": "private"
# }

bot = ZulipBot(client, msg_filter)

bot.add_cmd(ZulipBotCmdCoucou())
bot.add_cmd(ZulipBotCmdGnagnagna())
bot.add_cmd(ZulipBotCmdJoke(reddit))

bot.run()
