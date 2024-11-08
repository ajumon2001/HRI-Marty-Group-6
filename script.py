from martypy import Marty
import time


marty = Marty("wifi", "192.168.130.234")
marty.get_ready()
marty.set_volume(50)
print("speaking")
marty.speak_openai("Hello there kiddo, how are you? Would you like to hear a bedtime story? Once upon a time, there was a friendly robot named Marty who loved to dance and make new friends. Marty lived in a magical workshop where all sorts of amazing inventions came to life. Every day, Marty would practice new dance moves and share them with the other robots. One day, Marty learned a very special dance that made everyone smile. And from that day on, Marty became known as the happiest dancing robot in the whole workshop. The end! Did you enjoy that story?", blocking=True)
# marty.speak("I'm sorry, I didn't catch that. Can you please repeat?")
time.sleep(150)