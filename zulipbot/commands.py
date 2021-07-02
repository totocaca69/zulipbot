#!/usr/bin/env python3

import re
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


class ZulipBotCmdGnagnagna(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("gnagnagna", "[@**Name** | off] reply 'gnagnagna' everytime @**Name** talks")
        self.full_name = "off"

    def is_to_be_processed(self, msg:ZulipMsg):
        return msg.is_to_be_processed()

    def process(self, msg:ZulipMsg):
        if msg.cmd_is_to_be_processed(self.cmd_name):
            m = re.match(r".* @\*\*(.*)\*\*", msg.msg['content'])
            if m:
                self.full_name = m.group(1)
            else:
                self.full_name = 'off'
        elif msg.msg['sender_full_name'] == self.full_name:
            msg.reply("gnagnagna, j'm'appelle {}, a gnagnagna".format(self.full_name))
