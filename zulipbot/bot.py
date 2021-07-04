import zulip

from zulipbot.commands import *
from zulipbot.msg import *


class ZulipBotCmdRepeat(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("repeat", "repeat last command")


class ZulipBot(object):
    """get messages, process, reply"""

    def __init__(self, client: zulip.Client, msg_filter: dict):
        self.client = client
        self.msg_filter = msg_filter
        self.cmds: list[ZulipBotCmdBase] = []
        self.add_cmd(ZulipBotCmdHelp(self.cmds))
        self.add_cmd(ZulipBotCmdRepeat())
        self.prev_cmd = None
        self.prev_msg = None

    def add_cmd(self, cmd: ZulipBotCmdBase):
        self.cmds.append(cmd)

    def run_callback(self, m):
        msg = ZulipMsg(self.client, self.msg_filter, m)
        for cmd in self.cmds:
            if cmd.is_to_be_processed(msg):
                try:
                    if cmd.cmd_name == "repeat":
                        if self.prev_cmd and self.prev_msg:
                            self.prev_cmd.process(self.prev_msg)
                        else:
                            msg.reply("no previous command", is_error=True)
                    else:
                        cmd.process(msg)
                        if msg.is_valid_cmd(cmd.cmd_name):
                            self.prev_cmd = cmd
                            self.prev_msg = msg
                except:
                    msg.reply(
                        f"{msg.cmd_prefix}{cmd.cmd_name} failed", is_error=True)

    def run(self):
        self.client.call_on_each_message(self.run_callback)
