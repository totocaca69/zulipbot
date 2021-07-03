#!/usr/bin/env python3

import re

from praw import Reddit, models

from .msg import *


# --------------------------------------------------------------
# base clases
# --------------------------------------------------------------
class ZulipBotCmdBase(object):
    def __init__(self, cmd_name: str, help: str):
        self.cmd_name = cmd_name
        self.help = help

    def is_to_be_processed(self, msg: ZulipMsg) -> bool:
        return msg.is_valid_cmd(self.cmd_name)

    def process(self, msg: ZulipMsg):
        print(msg)
        return


class ZulipBotCmdRedditBase(ZulipBotCmdBase):
    def __init__(self, reddit: Reddit, cmd_name: str, help: str):
        super().__init__(cmd_name, help)
        self.reddit = reddit
        self.reddit.read_only = True

    def get_random_rising_submission(self, subreddit_name: str) -> models.Submission:
        subreddit = self.reddit.subreddit(subreddit_name)
        for submission in subreddit.random_rising(limit=1):
            return submission
        return models.Submission(reddit=self.reddit)

    def process(self, msg: ZulipMsg):
        print(msg)
        return


# --------------------------------------------------------------
# command classes
# --------------------------------------------------------------
class ZulipBotCmdHelp(ZulipBotCmdBase):
    def __init__(self, cmds: list[ZulipBotCmdBase]):
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


class ZulipBotCmdJoke(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "joke", "get joke from reddit's r/dadjokes")

    def process(self, msg: ZulipMsg):
        post = self.get_random_rising_submission("dadjokes")
        msg.reply("{}\n{}".format(post.title, post.selftext))
