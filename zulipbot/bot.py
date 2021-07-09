import getpass
from multiprocessing import Manager, Process, Queue
import socket

import zulip

from zulipbot.commands import *
from zulipbot.msg import *


class ZulipBot(object):
    """get messages, process, reply"""

    def __init__(self, client: zulip.Client, msg_filter: dict):
        self.client = client
        self.msg_filter = msg_filter
        self.cmds: list[ZulipBotCmdBase] = []
        self.msg_queues: dict[str, Queue] = {}
        # variables shared with all the threads
        self.manager = Manager()
        self.create_shared_dict()
        # bot-dependant commands
        self.add_cmd(ZulipBotCmdHelp(self.cmds))
        self.add_cmd(ZulipBotCmdRepeat(self.cmds))
        self.add_cmd(ZulipBotCmdBot(self.shared_dict))

    def create_shared_dict(self):
        self.shared_dict: dict = self.manager.dict()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        self.shared_dict['running'] = True
        self.shared_dict['usename'] = getpass.getuser()
        self.shared_dict['hostname'] = socket.gethostname()
        self.shared_dict['ip'] = ip

    def add_cmd(self, cmd: ZulipBotCmdBase):
        self.cmds.append(cmd)
        self.msg_queues[cmd.cmd_name] = Queue()

    def cmd_is_to_be_processed(self, cmd: ZulipBotCmdBase, msg: ZulipMsg) -> bool:
        return (self.shared_dict['running'] or cmd.cmd_name == "bot") \
            and cmd.is_to_be_processed(msg)

    def run_cmd(self, cmd: ZulipBotCmdBase, msg: ZulipMsg):
        try:
            cmd.process(msg)
        except:
            msg.reply(
                f"{msg.cmd_prefix}{cmd.cmd_name} failed", is_error=True)

    def process_queue(self, cmd: ZulipBotCmdBase):
        while True:
            msg = self.msg_queues[cmd.cmd_name].get()
            if self.cmd_is_to_be_processed(cmd, msg):
                self.run_cmd(cmd, msg)

    def fill_queues(self, m):
        msg = ZulipMsg(self.client, self.msg_filter, m)
        for cmd in self.cmds:
            if self.cmd_is_to_be_processed(cmd, msg):
                self.msg_queues[cmd.cmd_name].put(msg)

    def run(self):
        for cmd in self.cmds:
            p = Process(target=self.process_queue, args=(cmd,))
            p.start()
        self.client.call_on_each_message(self.fill_queues)
