import winsound
winsound.PlaySound("magnezone.wav",winsound.SND_ASYNC)

from playsound import PlaySound
PlaySound("magnezone.wav")

from pygame import mixer
mixer.init()
mixer.music.load("magnezone.wav")
mixer.music.play()



