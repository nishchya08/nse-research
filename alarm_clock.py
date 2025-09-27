import time
import datetime
import pygame
import os

def set_alarm(alarm_time):
    print(f"Alarm set for {alarm_time}")
    sound_file = os.path.join(os.path.dirname(__file__), "mixkit-classic-alarm-995.wav")
    is_running = True

    while is_running:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(current_time, end="\r")
        time.sleep(1)

        if current_time == alarm_time:
            print("\n⏰ Wake up!")

            # Initialize mixer
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()

            # Keep program alive until playback finishes
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            is_running = False
            pygame.mixer.music.stop()
            pygame.mixer.quit()

if __name__ == "__main__":
    alarm_time = input("Enter the alarm time (HH:MM:SS): ").strip()
    set_alarm(alarm_time)
