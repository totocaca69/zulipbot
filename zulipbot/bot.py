#!/usr/bin/env python3

from zulipbot.msg import *
from zulipbot.commands import *


class ZulipBot(object):
    """get messages, process, reply"""

    def __init__(self, client, msg_filter):
        self.client = client
        self.msg_filter = msg_filter
        self.cmds = []
        self.add_cmd(ZulipBotCmdHelp(self.cmds))

    def add_cmd(self, cmd):
        self.cmds.append(cmd)

    def run_callback(self, m):
        msg = ZulipMsg(self.client, self.msg_filter, m)
        for cmd in self.cmds:
            if cmd.is_to_be_processed(msg):
                cmd.process(msg)

    def run(self):
        self.client.call_on_each_message(self.run_callback)
