import glob
import os.path
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
    record_dir = "data/MediaPlayer/record"
    speak_dir = "data/MediaPlayer/speak"
    subprocess.run(["mkdir", "-p", record_dir])
    subprocess.run(["mkdir", "-p", speak_dir])

    def play(self, url: str, stop_before_play: bool = True):
        if stop_before_play:
            self.stop()
        path = f"{self.record_dir}/{url}.wav"
        if os.path.exists(path):
            url = path
        subprocess.Popen(["cvlc", "--quiet", "--no-loop", "--play-and-exit",
                          "--no-video", url])

    def record(self, file_name: str):
        cmd = f"arecord -D hw:2,0 -f S16_LE -r44100 -t wav -d 5"
        print(cmd.split() + [f"{self.record_dir}/{file_name}.wav"])
        subprocess.Popen(cmd.split() + [f"{self.record_dir}/{file_name}.wav"])

    def list_records(self) -> list[str]:
        r = []
        for path in glob.glob(f"{self.record_dir}/*.wav"):
            filename = path.split('/')[-1]
            r.append(filename.removesuffix('.wav'))
        return r

    def stop(self):
        subprocess.run(['pkill', 'vlc'])

    def speak(self, text: str, language: str = 'en'):
        file_name = f"{self.speak_dir}/speak.mp3"
        myobj = gTTS(text=text, lang=language, slow=False)
        myobj.save(file_name)
        self.play(file_name, stop_before_play=False)
