import os

from gtts import gTTS


class AudioPlayer(object):
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
