#!/usr/bin/env python3

from .msg import *


class ZulipBotCmdBase(object):
    def __init__(self, cmd_name, help):
        self.cmd_name = cmd_name
        self.help = help

    def is_to_be_processed(self, msg:ZulipMsg):
        return msg.cmd_is_to_be_processed(self.cmd_name)

    def process(self, msg:ZulipMsg):
        print(msg)
        return


class ZulipBotCmdHelp(ZulipBotCmdBase):
    def __init__(self, cmds):
        super().__init__("help", "display this help")
        self.cmds = cmds

    def process(self, msg:ZulipMsg):
        help_list = []
        for cmd in self.cmds:
            help_list.append("!{:10s} : {}".format(cmd.cmd_name, cmd.help))
        msg.reply("\n".join(sorted(help_list)))


class ZulipBotCmdCoucou(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("coucou", "reply 'coucou'")

    def process(self, msg:ZulipMsg):
        msg.reply("coucou")
