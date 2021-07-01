#!/usr/bin/env python3


class ZulipMsg(object):
    """message functions"""

    robot_prefix = ":robot:"
    cmd_prefix = "!"

    def __init__(self, client, msg):
        self.client = client
        self.msg = msg

    def is_to_be_processed(self):
        return self.msg['content'].split()[0] != self.robot_prefix and \
            self.msg['type'] == 'private' and \
            self.msg['display_recipient'][0]['short_name'] == 'antoine.madec'

    def cmd_is_to_be_processed(self, cmd_name):
        first_word = self.msg['content'].split()[0]
        return self.is_to_be_processed() and \
            first_word[0] == self.cmd_prefix and first_word[1:] == cmd_name

    def reply(self, txt, fenced_code_block=True):
        if self.msg["type"] == "private":
            rep = {"type": "private",
                   "to": [x["id"] for x in self.msg["display_recipient"]]
                   }
        elif self.msg["type"] == "stream":
            rep = {"type": "stream",
                   "to": self.msg["display_recipient"],
                   "topic": self.msg["subject"]
                   }
        else:
            return
        if fenced_code_block:
            txt = "```\n{}\n```".format(txt)
        rep["content"] = "{}\n{}".format(self.robot_prefix, txt)
        self.client.send_message(rep)
