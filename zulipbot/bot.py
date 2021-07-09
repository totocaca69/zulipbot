from multiprocessing import Process, Queue

import zulip

from zulipbot.commands import *
from zulipbot.msg import *


class ZulipBot(object):
    """get messages, process, reply"""

    def __init__(self, client: zulip.Client, msg_filter: dict):
        self.client = client
        self.msg_filter = msg_filter
        self.cmds: list[ZulipBotCmdBase] = []
        self.msg_queues: dict[str,Queue] = {}
        self.add_cmd(ZulipBotCmdHelp(self.cmds))
        self.add_cmd(ZulipBotCmdRepeat(self.cmds))

    def add_cmd(self, cmd: ZulipBotCmdBase):
        self.cmds.append(cmd)
        self.msg_queues[cmd.cmd_name] = Queue()

    def run_cmd(self, cmd: ZulipBotCmdBase, msg: ZulipMsg):
        try:
            cmd.process(msg)
        except:
            msg.reply(
                f"{msg.cmd_prefix}{cmd.cmd_name} failed", is_error=True)

    def process_queue(self, cmd: ZulipBotCmdBase):
        while True:
            msg = self.msg_queues[cmd.cmd_name].get()
            self.run_cmd(cmd, msg)

    def run_callback(self, m):
        msg = ZulipMsg(self.client, self.msg_filter, m)
        for cmd in self.cmds:
            if cmd.is_to_be_processed(msg):
                self.msg_queues[cmd.cmd_name].put(msg)

    def run(self):
        for cmd in self.cmds:
            p = Process(target=self.process_queue, args=(cmd,))
            p.start()
        self.client.call_on_each_message(self.run_callback)
