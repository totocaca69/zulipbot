import subprocess

from gtts import gTTS


class Audio(object):
    def __init__(self):
        """audio functions (output, volume etc)"""
        self.volume = 50

    def get_sink_indexes(self) -> list:
        indexes = []
        for line in self.get_info().split("\n"):
            if line:
                indexes.append(line.split()[0])
        return indexes

    def get_info(self) -> str:
        p = subprocess.run(
            ['pactl', 'list', 'short', 'sinks'], capture_output=True)
        return p.stdout.decode('utf-8')

    def set_output(self, index: int) -> str:
        p = subprocess.run(['pactl', 'set-default-sink', str(index)])
        if p.returncode == 0:
            return f"sink {index} has been set"
        else:
            return f"sink {index} does not exist"

    def volume_set(self, volume_pct: int) -> int:
        volume_pct = max(min(volume_pct, 100), 0)
        for index in self.get_sink_indexes():
            _ = subprocess.run(['pactl', 'set-sink-volume',
                               str(index), f"{volume_pct}%"])
        return volume_pct


class MediaPlayer(object):
    def play(self, url: str, stop_before_play: bool = True):
        if stop_before_play:
            self.stop()
        subprocess.Popen(["cvlc", "--quiet", "--no-loop", "--play-and-exit",
                          "--no-video", url])

    def stop(self):
        subprocess.run(['pkill', 'vlc'])

    def speak(self, text: str, language: str = 'en'):
        file_name = "speak.mp3"
        myobj = gTTS(text=text, lang=language, slow=False)
        myobj.save(file_name)
        self.play(file_name, stop_before_play=False)
