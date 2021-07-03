#!/usr/bin/env python3

import random
import re
import typing

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

    def get_random_submission(self, subreddit_name: str,
                              limit: int = 100,
                              query: str = "",
                              sort: str = "hot") -> typing.Optional[models.Submission]:
        """Warning: this method has a timeout in-between calls. Don't use it in loops."""
        subreddit = self.reddit.subreddit(subreddit_name)
        query = "nsfw:no subreddit:{} {}".format(subreddit_name, query)
        idx = random.randint(1, limit)
        submission = None
        for submission in subreddit.search(query, sort=sort, limit=idx):
            pass
        return submission

    def reply_with_random_media(self, msg: ZulipMsg, subreddit_name: str, query: str = "url:jpg"):
        s = self.get_random_submission(subreddit_name, query=query)
        if s:
            msg.reply("[]({})".format(s.url), fenced_code_block=False)
        else:
            msg.reply("cannot find an media in subreddit={}'".format(subreddit_name),
                      is_error=True)

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
        super().__init__(reddit, "joke", "joke from reddit r/dadjokes")

    def process(self, msg: ZulipMsg):
        post = self.get_random_submission("dadjokes")
        if post:
            msg.reply("{}\n{}".format(post.title, post.selftext))


class ZulipBotCmdAww(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "aww", "picture from reddit r/aww")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_media(msg, "aww", query="url:jpg")


class ZulipBotCmdEarth(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "earth", "picture from reddit r/EarthPorn")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_media(msg, "EarthPorn", query="url:jpg")


class ZulipBotCmdGif(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "gif", "gif from reddit r/gif")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_media(msg, "aww", query="url:gif")
