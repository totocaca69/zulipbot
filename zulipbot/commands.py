#!/usr/bin/env python3

import random
import re

from .msg import *


class ZulipBotCmdBase(object):
    def __init__(self, cmd_name, help):
        self.cmd_name = cmd_name
        self.help = help

    def is_to_be_processed(self, msg: ZulipMsg):
        return msg.is_valid_cmd(self.cmd_name)

    def process(self, msg: ZulipMsg):
        print(msg)
        return


class ZulipBotCmdHelp(ZulipBotCmdBase):
    def __init__(self, cmds):
        super().__init__("help", "display this help")
        self.cmds = cmds

    def process(self, msg: ZulipMsg):
        help_list = []
        for cmd in self.cmds:
            help_list.append("!{:10s} : {}".format(cmd.cmd_name, cmd.help))
        msg.reply("\n".join(sorted(help_list)))


class ZulipBotCmdCoucou(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("coucou", "reply 'coucou'")

    def process(self, msg: ZulipMsg):
        msg.reply("coucou")


class ZulipBotCmdGnagnagna(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("gnagnagna",
                         "[@**Name** | off] reply 'gnagnagna' everytime @**Name** talks")
        self.full_name = "off"

    def is_to_be_processed(self, msg: ZulipMsg):
        return msg.is_valid()

    def process(self, msg: ZulipMsg):
        if msg.is_valid_cmd(self.cmd_name):
            m = re.match(r".* @\*\*(.*)\*\*", msg.msg['content'])
            if m:
                self.full_name = m.group(1)
            else:
                self.full_name = 'off'
        elif msg.msg['sender_full_name'] == self.full_name:
            msg.reply(
                "gnagnagna, j'm'appelle {}, a gnagnagna".format(self.full_name))


class ZulipBotCmdJoke(ZulipBotCmdBase):
    def __init__(self, reddit):
        super().__init__("joke", "get joke from reddit's r/dadjokes")
        self.reddit = reddit
        self.reddit.read_only = True

    def process(self, msg: ZulipMsg):
        subreddit = self.reddit.subreddit("dadjokes")
        idx = random.randint(0, 99)
        post = None
        # ugly as fuck
        for post in subreddit.hot(limit=idx):
            pass
        if post:
            msg.reply("{}\n{}".format(post.title, post.selftext))
