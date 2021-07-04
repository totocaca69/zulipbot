import asyncio
import random
import re
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

    def get_random_submission(self,
                              subreddit: Union[str, models.Subreddit],
                              limit: int = 100,
                              query: str = "",
                              sort: str = "hot") -> Optional[models.Submission]:
        """Warning: this method has a timeout in-between calls. Don't use it in loops."""
        if isinstance(subreddit, str):
            subr = self.reddit.subreddit(subreddit)
        else:
            subr = subreddit
        query = "nsfw:no subreddit:{} {}".format(str(subr), query)
        idx = random.randint(1, limit)
        submission = None
        for submission in subr.search(query, sort=sort, limit=idx):
            pass
        return submission

    def reply_with_random_post(self,
                               msg: ZulipMsg,
                               subreddit: Union[str, models.Subreddit],
                               query: str = ""):
        s = self.get_random_submission(subreddit, query=query)
        if s:
            msg.reply("{}\n\n{}".format(s.title, s.selftext))
        else:
            msg.reply("cannot find an post in subreddit={}'".format(subreddit),
                      is_error=True)

    def reply_with_random_media(self,
                                msg: ZulipMsg,
                                subreddit: Union[str, models.Subreddit],
                                query: str = "url:jpg"):
        s = self.get_random_submission(subreddit, query=query)
        if s:
            msg.reply("[]({})".format(s.url), fenced_code_block=False)
        else:
            msg.reply("cannot find an media in subreddit={}'".format(subreddit),
                      is_error=True)

    def process(self, msg: ZulipMsg):
        print(msg)
        return


class ZulipBotCmdAudioBase(ZulipBotCmdBase):
    def __init__(self, cmd_name: str, help: str, help_args: str = ""):
        super().__init__(cmd_name, help, help_args=help_args)
        self.audio = AudioPlayer()
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
        for cmd in self.cmds:
            help_list = help_list_from_category.get(cmd.help_category, [])
            help_list.append("!{:10s} {:20s} : {}".format(
                cmd.cmd_name, cmd.help_args, cmd.help))
            help_list_from_category[cmd.help_category] = help_list
        for category in help_list_from_category.keys():
            help_str += f"\n\n{category}:\n  "
            help_str += "\n  ".join(sorted(help_list_from_category[category]))
        msg.reply(help_str)


class ZulipBotCmdCoucou(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("coucou", "reply 'coucou'")

    def process(self, msg: ZulipMsg):
        msg.reply("coucou")


class ZulipBotCmdGnagnagna(ZulipBotCmdBase):
    def __init__(self):
        super().__init__("gnagnagna",
                         "reply 'gnagnagna' everytime someone talks",
                         help_args="[@**someone** | off]")
        self.full_name = "off"

    def is_to_be_processed(self, msg: ZulipMsg):
        return msg.is_valid()

    def process(self, msg: ZulipMsg):
        if msg.is_valid_cmd(self.cmd_name):
            m = re.match(r".* @\*\*(.*)\*\*", msg.msg['content'])
            if m:
                self.full_name = m.group(1)
            else:
                self.full_name = 'off'
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
class ZulipBotCmdSpeak(ZulipBotCmdAudioBase):
    def __init__(self):
        super().__init__("speak", "speak in french", help_args="[french_text]")

    def process(self, msg: ZulipMsg):
        text = " ".join(msg.msg['content'].split()[1:])
        self.audio.speak(text, language='fr')


class ZulipBotCmdPlay(ZulipBotCmdAudioBase):
    def __init__(self):
        super().__init__("play", "play audio", help_args="[url]")

    def process(self, msg: ZulipMsg):
        url = " ".join(msg.msg['content'].split()[1:])
        self.audio.play(url)


class ZulipBotCmdStop(ZulipBotCmdAudioBase):
    def __init__(self):
        super().__init__("stop", "stop audio")

    def process(self, _: ZulipMsg):
        self.audio.stop()


# --------------------------------------------------------------
# command classes: reddit
# --------------------------------------------------------------
class ZulipBotCmdJoke(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "joke", "joke from reddit r/dadjokes")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_post(msg, "dadjokes")


class ZulipBotCmdAww(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "aww", "picture from reddit r/aww")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_media(msg, "aww", query="url:jpg")


class ZulipBotCmdGif(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "gif", "gif from reddit r/gif")

    def process(self, msg: ZulipMsg):
        self.reply_with_random_media(msg, "aww", query="url:gif")


class ZulipBotCmdRedPost(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "redpost",
                         "post from reddit", help_args="[subreddit]")

    def process(self, msg: ZulipMsg):
        args = msg.msg['content'].split()
        subreddit = args[1] if len(
            args) > 1 else self.reddit.random_subreddit()
        self.reply_with_random_post(msg, subreddit)


class ZulipBotCmdRedPic(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "redpic",
                         "picture from reddit", help_args="[subreddit]")

    def process(self, msg: ZulipMsg):
        args = msg.msg['content'].split()
        subreddit = args[1] if len(
            args) > 1 else self.reddit.random_subreddit()
        self.reply_with_random_media(msg, subreddit, query="url:jpg")


class ZulipBotCmdRedGif(ZulipBotCmdRedditBase):
    def __init__(self, reddit):
        super().__init__(reddit, "redgif",
                         "gif from reddit", help_args="[subreddit]")

    def process(self, msg: ZulipMsg):
        args = msg.msg['content'].split()
        subreddit = args[1] if len(
            args) > 1 else self.reddit.random_subreddit()
        self.reply_with_random_media(msg, subreddit, query="url:gif")
