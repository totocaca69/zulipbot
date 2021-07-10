import os

from gtts import gTTS
import pulsectl


class AudioPlayer(object):
    def __init__(self, use_pulsectl: bool = True):
        """audio functions

        use_pulsectl=False will help with multi threading issues"""
        self.pulseaudio = None
        if use_pulsectl:
            self.pulseaudio = pulsectl.Pulse('zulipbot', connect=False)
            self.pulseaudio.connect(autospawn="True")
            self.volume_set(50)

    # ----------------------------------------------------------
    # pulseaudio: volume and sound
    # ----------------------------------------------------------
    def audio_get_info(self, sink_idx_only: int = -1) -> str:
        if not self.pulseaudio:
            return ""
        info = ""
        for sink in self.pulseaudio.sink_list():
            if sink_idx_only == -1 or sink_idx_only == sink.index:
                info += "idx={} vol={}% \t{}\n".format(
                    sink.index, int(sink.volume.values[0]*100), sink.description)
        return info

    def audio_set_output(self, index: int) -> str:
        if not self.pulseaudio:
            return ""
        for sink in self.pulseaudio.sink_list():
            if sink.index == index:
                self.pulseaudio.default_set(sink)
        return self.audio_get_info(sink_idx_only=index)

    def volume_up(self) -> int:
        if not self.pulseaudio:
            return -1
        sink = self.pulseaudio.sink_list()[0]
        volume = self.pulseaudio.volume_get_all_chans(sink)
        volume += 0.1
        return self.volume_set(int(volume*100))

    def volume_down(self) -> int:
        if not self.pulseaudio:
            return -1
        sink = self.pulseaudio.sink_list()[0]
        volume = self.pulseaudio.volume_get_all_chans(sink)
        volume -= 0.1
        return self.volume_set(int(volume*100))

    def volume_set(self, volume_pct: int) -> int:
        if not self.pulseaudio:
            return -1
        if volume_pct < 0:
            volume_pct = 0
        elif volume_pct > 100:
            volume_pct = 100
        volume = float(volume_pct)/100
        for sink in self.pulseaudio.sink_list():
            self.pulseaudio.volume_set_all_chans(sink, volume)
        return volume_pct

    def volume_mute(self):
        return self.volume_set(0)

    # ----------------------------------------------------------
    # VLC
    # ----------------------------------------------------------
    def play(self, url: str, stop_before_play: bool = True):
        if stop_before_play:
            self.stop()
        cmd = "cvlc --quiet --no-loop --play-and-exit --no-video {}&".format(
            url)
        os.system(cmd)

    def stop(self):
        os.system("pkill vlc")

    def speak(self, text: str, language: str = 'en'):
        file_name = "speak.mp3"
        myobj = gTTS(text=text, lang=language, slow=False)
        myobj.save(file_name)
        self.play(file_name, stop_before_play=False)
