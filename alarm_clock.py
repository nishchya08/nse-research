
# Python  Alarm clock

import time
import datetime
import pygame

def set_alarm(alarm_time):
    print(f"Alarm set for {alarm_time}")
    sound_file = "mixkit-classic-alarm-995.wav"
    is_running = True

    while is_running:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(current_time)
        time.sleep(1)

        if current_time == alarm_time:
            print(" Wake up!")


            pygame.mixer.init()
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            is_running = False


if __name__ == "__main__":
    alarm_time = input("Enter the alarm time in (HH:MM:SS): ")
    set_alarm(alarm_time)