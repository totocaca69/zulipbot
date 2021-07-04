import os


class AudioPlayer(object):
    def play(self, url: str):
        cmd = "cvlc --quiet --no-loop --play-and-exit --no-video {}&".format(
            url)
        os.system(cmd)

    def stop(self):
        os.system("pkill vlc")
