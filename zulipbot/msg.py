import re
from typing import Any, Union

import zulip

from .audio import *


class ZulipMsg(object):
    """message functions"""

    robot_prefix = ":robot:"
    cmd_prefix = "!"

    def __init__(self,
                 client: zulip.Client,
                 msg_filter: dict,
                 msg: dict):
        self.client = client
        self.msg_filter = msg_filter
        self.msg = msg
        self.cmd_options: dict[str, Union[str, bool]] \
            = self.parse_cmd_options()

    def get_option(self, option_name: str, default_value: Union[str, bool]) -> Any:
        return self.cmd_options[option_name] if option_name in self.cmd_options \
            else default_value

    def parse_cmd_options(self) -> dict[str, Union[str, bool]]:
        """parse msg content, remove --option(=val) and return a dict with those options"""
        d = {}
        content = self.msg['content']
        split_content: list[str] = self.msg['content'].split()
        content = []
        for word in split_content:
            if word.startswith('--'):
                word = word.replace('--', '')
                w_split = word.split('=')
                if len(w_split) > 1:
                    d[w_split[0]] = w_split[1]
                else:
                    d[w_split[0]] = True
            else:
                content.append(word)
        self.msg['content'] = " ".join(content)
        return d

    def get_arg(self, index: int) -> str:
        """index=0: returns command name
        index=-1: retuns all args
        index=n: retuns n-th arg"""
        arg = ""
        msg_list = self.msg['content'].split()
        is_cmd = msg_list[0][0] == self.cmd_prefix
        if is_cmd and index < len(msg_list):
            if index == -1:
                arg = " ".join(msg_list[1:])
            else:
                arg = msg_list[index]
                # remove prefix to get command name
                if index == 0:
                    arg = arg[1:]
        return arg

    def get_full_name_from_handle(self, handle_string: str) -> str:
        full_name = ""
        m = re.match(r"^@\*\*(.*)\*\*", handle_string)
        if m:
            full_name = m.group(1)
        return full_name

    def is_valid(self) -> bool:
        not_a_robot = self.msg['content'].split()[0] != self.robot_prefix
        valid = True
        for key in self.msg_filter.keys():
            if key not in self.msg.keys() or self.msg[key] != self.msg_filter[key]:
                valid = False
                break
        return not_a_robot and valid

    def is_valid_cmd(self, cmd_name: Union[str, list[str]]) -> bool:
        cmd_name_list = [cmd_name] if isinstance(cmd_name, str) else cmd_name
        msg_cmd_name = self.get_arg(0)
        return self.is_valid() and msg_cmd_name in cmd_name_list

    def reply(self, txt: str,
              fenced_code_block: bool = True,
              is_error: bool = False,
              speak: bool = False,
              speak_lang: str = 'en',
              status_str: str = "",
              use_options: bool = True):
        if use_options:
            speak = self.get_option('speak', speak)
            speak_lang = self.get_option('lang', speak_lang)
        prefix = self.robot_prefix
        if is_error:
            prefix += " :danger:**ERROR**:danger:"
        if status_str:
            prefix += f" *{status_str}*"

        if speak:
            # don't create pulsectl object to avoid pickle+ctypes object issue
            AudioPlayer(use_pulsectl=False).speak(txt, language=speak_lang)
        else:
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
            rep["content"] = "{}\n{}".format(prefix, txt)
            self.client.send_message(rep)
