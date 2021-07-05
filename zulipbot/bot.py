import zulip

from zulipbot.commands import *
from zulipbot.msg import *


class ZulipBot(object):
    """get messages, process, reply"""

    def __init__(self, client: zulip.Client, msg_filter: dict):
        self.client = client
        self.msg_filter = msg_filter
        self.cmds: list[ZulipBotCmdBase] = []
        self.add_cmd(ZulipBotCmdHelp(self.cmds))
        self.add_cmd(ZulipBotCmdRepeat(self.cmds))

    def add_cmd(self, cmd: ZulipBotCmdBase):
        self.cmds.append(cmd)

    def run_callback(self, m):
        msg = ZulipMsg(self.client, self.msg_filter, m)
        for cmd in self.cmds:
            if cmd.is_to_be_processed(msg):
                try:
                    cmd.process(msg)
                except:
                    msg.reply(
                        f"{msg.cmd_prefix}{cmd.cmd_name} failed", is_error=True)

    def run(self):
        self.client.call_on_each_message(self.run_callback)
