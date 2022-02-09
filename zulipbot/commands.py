import asyncio
import json
import random
from typing import Optional, Union

from praw import Reddit, models
import python_weather

from .audio import *
from .msg import *


# --------------------------------------------------------------
# base clases
# --------------------------------------------------------------
class ZulipBotCmdBase(object):
    def __init__(self, cmd_name: str, help: str, help_args: str = ""):
        self.cmd_name = cmd_name
        self.help = help
        self.help_args = help_args
        self.help_category = "misc"
        self.help_common_options = {
            '--speak': 'say the msg instead of printing it',
            '--lang': 'change spoken language of the cmd',
        }

    def is_to_be_processed(self, msg: ZulipMsg) -> bool:
        return msg.is_valid_cmd(self.cmd_name)

    def process(self, msg: ZulipMsg):
        print(msg)
        return


class ZulipBotCmdRedditBase(ZulipBotCmdBase):
    def __init__(self, reddit: Reddit, cmd_name: str, help: str, help_args: str = ""):
        super().__init__(cmd_name, help, help_args=help_args)
        self.reddit = reddit
        self.reddit.read_only = True
        self.help_category = "reddit"

    def get_msg_status(self, submission: models.Submission) -> str:
        """return msg status with link to submission"""
        sr_name = submission.subreddit
        url = f"https://www.reddit.com{submission.permalink}"
        return f"from [r/{sr_name}]({url})"

    def get_subreddit_from_msg(self, msg: ZulipMsg) -> Union[str, models.Subreddit]:
        subreddit = msg.get_arg(1)
        if not subreddit:
            subreddit = self.reddit.random_subreddit()
        return subreddit

    def get_random_submission(self,
                              subreddit: Union[str, models.Subreddit],
                              limit: int = 100,
                              query: str = "",
                              sort: str = "rising") -> Optional[models.Submission]:
        """Warning: this method has a timeout in-between calls. Don't use it in loops."""
        if isinstance(subreddit, str):
            subr = self.reddit.subreddit(subreddit)
        else:
            subr = subreddit
        query_list = ["nsfw:no", f"subreddit:{subr}"]
        if query:
            query_list.append(query)
        q = " AND ".join(query_list)
        idx = random.randint(1, limit)
        submission = None
        for submission in subr.search(q, sort=sort, limit=idx):
            pass
        return submission

    def reply_with_random_post(self,
                               msg: ZulipMsg,
                               subreddit: Union[str, models.Subreddit],
                               query: str = ""):
        s = self.get_random_submission(subreddit, query=query)
        if s:
            msg.reply("{}\n\n{}".format(s.title, s.selftext),
                      status_str=self.get_msg_status(s))
        else:
            msg.reply(f"cannot find an media in r/{str(subreddit)}",
                      is_error=True)

    def reply_with_random_media(self,
                                msg: ZulipMsg,
                                subreddit: Union[str, models.Subreddit],
                                query: str = "url:jpg"):
        s = self.get_random_submission(subreddit, query=query)
        if s:
            msg.reply("[]({})".format(s.url),
                      fenced_code_block=False,
                      status_str=self.get_msg_status(s))
        else:
            msg.reply(f"cannot find an media in r/{str(subreddit)}",
                      is_error=True)

    def play_random_media_audio(self,
                                msg: ZulipMsg,
                                subreddit: Union[str, models.Subreddit],
                                query: str = "url:youtube"):
        s = self.get_random_submission(subreddit, query=query)
        if s:
            msg.reply(s.title, status_str=self.get_msg_status(s))
            MediaPlayer().play(s.url)
        else:
            msg.reply(f"cannot find an media in r/{str(subreddit)}",
                      is_error=True)

    def process(self, msg: ZulipMsg):
        print(msg)
        return


class ZulipBotCmdAudioBase(ZulipBotCmdBase):
    def __init__(self, cmd_name: str, help: str, help_args: str = ""):
        super().__init__(cmd_name, help, help_args=help_args)
        self.audio = Audio()
        self.player = MediaPlayer()
        self.help_category = "audio"


# --------------------------------------------------------------
# command classes: misc
# --------------------------------------------------------------
class ZulipBotCmdHelp(ZulipBotCmdBase):
    def __init__(self, cmds: list[ZulipBotCmdBase]):
        super().__init__("help", "display this help")
        self.cmds = cmds

    def process(self, msg: ZulipMsg):
        help_str = ""
        help_list_from_category = {}
        # commands help
        for cmd in self.cmds:
            help_list = help_list_from_category.get(cmd.help_category, [])
            help_list.append("!{:10s} {:25s} : {}".format(
                cmd.cmd_name, cmd.help_args, cmd.help))
            help_list_from_category[cmd.help_category] = help_list
        # common options
        help_list = []
        for option, description in self.help_common_options.items():
            help_list.append("{:10s} : {}".format(option, description))
        help_list_from_category['common options'] = help_list
        # print
        for category in help_list_from_category.keys():
            help_str += f"\n\n{category}:\n  "
            help_str += "\n  ".join(sorted(help_list_from_category[category]))
        msg.reply(help_str)


class ZulipBotCmdRepeat(ZulipBotCmdBase):
    def __init__(self, cmds: list[ZulipBotCmdBase]):
        super().__init__("repeat", "repeat last command")
        self.cmds = cmds
        self.prev_cmd_msg: Optional[ZulipMsg] = None

    def get_cmd(self, cmd_name: str) -> Optional[ZulipBotCmdBase]:
        for cmd in self.cmds:
            if cmd.cmd_name == cmd_name:
                return cmd

    def is_to_be_processed(self, msg: ZulipMsg) -> bool:
        cmd_name_list = [cmd.cmd_name for cmd in self.cmds]
        return msg.is_valid_cmd(cmd_name_list)

    def process(self, msg: ZulipMsg):
        if msg.is_valid_cmd(self.cmd_name):
            if self.prev_cmd_msg:
                cmd = self.get_cmd(self.prev_cmd_msg.get_arg(0))
                if cmd:
                    cmd.process(self.prev_cmd_msg)
            else:
                msg.reply("no previous command", is_error=True)
        else:
            self.prev_cmd_msg = msg


class ZulipBotCmdBot(ZulipBotCmdBase):
    def __init__(self, bot_dict: dict):
        super().__init__("bot", "robot info and actions",
                         help_args="on|off|info")
        self.bot_dict = bot_dict

    def process(self, msg: ZulipMsg):
        subcmd = msg.get_arg(1)
        if subcmd == "on":
            self.bot_dict['running'] = True
            msg.reply("robot is ON")
        elif subcmd == "off":
            self.bot_dict['running'] = False
            msg.reply("robot is OFF")
        elif subcmd == "info":
            d = self.bot_dict.copy()
            msg.reply(json.dumps(d, indent=4))


class ZulipBotCmdAlias(ZulipBotCmdBase):
    def __init__(self, cmds: list[ZulipBotCmdBase]):
        super().__init__("a", "create/run aliases",
                         help_args="[ALIAS_NAME] [--create]")
        self.cmds = cmds
        self.prev_cmd_msg: Optional[ZulipMsg] = None
        self.alias_to_cmd = {}

    def get_cmd(self, cmd_name: str) -> Optional[ZulipBotCmdBase]:
        for cmd in self.cmds:
            if cmd.cmd_name == cmd_name:
                return cmd

    def is_to_be_processed(self, msg: ZulipMsg) -> bool:
        cmd_name_list = [cmd.cmd_name for cmd in self.cmds]
        return msg.is_valid_cmd(cmd_name_list)

    def create_alias(self, alias: str, msg: ZulipMsg):
        if not alias:
            msg.reply("alias is empty", is_error=True)
            return
        if self.prev_cmd_msg:
            if self.prev_cmd_msg.get_arg(0) != self.cmd_name:
                self.alias_to_cmd[alias] = self.prev_cmd_msg
                msg.reply(f"alias {alias} to {self.prev_cmd_msg.raw_content}")
            else:
                msg.reply(
                    f"previous command is {self.cmd_name}", is_error=True)
        else:
            msg.reply("no previous command", is_error=True)

    def process(self, msg: ZulipMsg):
        if msg.is_valid_cmd(self.cmd_name):
            alias = msg.get_arg(1)
            create = msg.get_option("create", False)
            if create:
                self.create_alias(alias, msg)
            else:
                if alias in self.alias_to_cmd:
                    msg = self.alias_to_cmd[alias]
                    cmd = self.get_cmd(msg.get_arg(0))
                    if cmd:
                        cmd.process(msg)
                else:
                    list_str = "aliases:"
                    for alias in self.alias_to_cmd:
                        list_str += f"\n{alias:10s} {self.alias_to_cmd[alias].raw_content}"
                    msg.reply(list_str)
        else:
            self.prev_cmd_msg = msg


class ZulipBotCmdGnagnagna(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("gnagnagna",
                         "reply 'gnagnagna' everytime someone talks",
                         help_args="@**SOMEONE**|off")
        self.full_name = "off"

    def is_to_be_processed(self, msg: ZulipMsg) -> bool:
        return msg.is_valid()

    def process(self, msg: ZulipMsg):
        if msg.is_valid_cmd(self.cmd_name):
            self.full_name = msg.get_full_name_from_handle(msg.get_arg(-1))
        elif msg.msg['sender_full_name'] == self.full_name:
            msg.reply(
                "gnagnagna, j'm'appelle {}, a gnagnagna".format(self.full_name))


class ZulipBotCmdWeather(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("weather", "print current weather")

    async def print_weather(self, msg: ZulipMsg, city: str = "Rennes, Brittany, France"):
        client = python_weather.Client()
        weather = await client.find(city)
        cw = weather.current
        msg.reply("{}\n  temp: {}c\n  feels_like: {}c\n  humidity: {}%\n  sky: {}\n  wind: {}".format(
            cw.observation_point, cw.temperature, cw.feels_like,
            cw.humidity, cw.sky_text, cw.wind_display))
        await client.close()

    def process(self, msg: ZulipMsg):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.print_weather(msg))


# --------------------------------------------------------------
# command classes: audio
# --------------------------------------------------------------
class ZulipBotCmdAudio(ZulipBotCmdAudioBase):
    def __init__(self):
        super().__init__("audio", "get audio info, set output",
                         help_args="get|set IDX")

    def process(self, msg: ZulipMsg):
        subcmd = msg.get_arg(1)
        if subcmd == "set":
            idx = int(msg.get_arg(2))
            info = self.audio.set_output(idx)
            if info:
                msg.reply(info)
        else:
            msg.reply(self.audio.get_info())


class ZulipBotCmdVolume(ZulipBotCmdAudioBase):
    def __init__(self):
        super().__init__("vol", "change volume",
                         help_args="INT")

    def process(self, msg: ZulipMsg):
        idx = int(msg.get_arg(1))
        volume = self.audio.volume_set(idx)
        msg.reply(f"volume {volume}%")


class ZulipBotCmdSpeak(ZulipBotCmdAudioBase):
    def __init__(self):
        super().__init__("speak", "speak in french", help_args="TEXT")

    def process(self, msg: ZulipMsg):
        text = msg.get_arg(-1)
        self.player.speak(text, language=msg.get_option('lang', 'fr'))


class ZulipBotCmdPlay(ZulipBotCmdAudioBase):
    def __init__(self, reddit: Optional[Reddit] = None):
        super().__init__(
            "play", "play audio from url or r/listentothis", help_args="[URL]")
        self.reddit_cmd = None
        if reddit:
            self.reddit_cmd = ZulipBotCmdRedditBase(reddit, '', '')

    def process(self, msg: ZulipMsg):
        url = msg.get_arg(1)
        if url:
            self.player.play(url)
        elif self.reddit_cmd:
            self.reddit_cmd.play_random_media_audio(msg, 'listentothis')


class ZulipBotCmdStop(ZulipBotCmdAudioBase):
    def __init__(self):
        super().__init__("stop", "stop player")

    def process(self, _: ZulipMsg):
        self.player.stop()


# --------------------------------------------------------------
# command classes: reddit
# --------------------------------------------------------------
class ZulipBotCmdJoke(ZulipBotCmdRedditBase):
    def __init__(self, reddit: Reddit):
        super().__init__(reddit, "joke", "joke from reddit r/dadjokes")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_post(msg, "dadjokes")


class ZulipBotCmdAww(ZulipBotCmdRedditBase):
    def __init__(self, reddit: Reddit):
        super().__init__(reddit, "aww", "picture from reddit r/aww")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_media(msg, "aww", query="url:jpg")


class ZulipBotCmdGif(ZulipBotCmdRedditBase):
    def __init__(self, reddit: Reddit):
        super().__init__(reddit, "gif", "gif from reddit r/gif")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_media(msg, "gif", query="url:gif")


class ZulipBotCmdRedPost(ZulipBotCmdRedditBase):
    def __init__(self, reddit: Reddit):
        super().__init__(reddit, "redpost",
                         "post from reddit", help_args="[SUBREDDIT]")

    def process(self, msg: ZulipMsg):
        subreddit = self.get_subreddit_from_msg(msg)
        self.reply_with_random_post(msg, subreddit)


class ZulipBotCmdRedPic(ZulipBotCmdRedditBase):
    def __init__(self, reddit: Reddit):
        super().__init__(reddit, "redpic",
                         "picture from reddit", help_args="[SUBREDDIT]")

    def process(self, msg: ZulipMsg):
        subreddit = self.get_subreddit_from_msg(msg)
        self.reply_with_random_media(msg, subreddit, query="url:jpg")


class ZulipBotCmdRedGif(ZulipBotCmdRedditBase):
    def __init__(self, reddit: Reddit):
        super().__init__(reddit, "redgif",
                         "gif from reddit", help_args="[SUBREDDIT]")

    def process(self, msg: ZulipMsg):
        subreddit = self.get_subreddit_from_msg(msg)
        self.reply_with_random_media(msg, subreddit, query="url:gif")


class ZulipBotCmdRedPlay(ZulipBotCmdRedditBase):
    def __init__(self, reddit: Reddit):
        super().__init__(reddit, "redplay",
                         "play audio from reddit", help_args="[SUBREDDIT]")

    def process(self, msg: ZulipMsg):
        subreddit = self.get_subreddit_from_msg(msg)
        self.play_random_media_audio(msg, subreddit, query="url:youtube")
