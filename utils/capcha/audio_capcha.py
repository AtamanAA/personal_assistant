import os
import time

import requests

from variables import BASE_DIR
from .audio_solve import AudioSolve


class AudioCapchaSolve:
    """
    Solve audio capcha
    """
    def __init__(self, page, capcha_frame):
        self.page = page
        self.capcha_frame = capcha_frame
        self.audio_file_dir = os.path.join(BASE_DIR, "audio_capcha_files")
        self.audio_file_name = "audio_capcha.wav"

        self.audio_challenge_bottom_locator = "#captcha__audio__button"
        self.audio_file_locator = ".audio-captcha-track"
        self.play_bottom_locator = 'xpath://*[@id="captcha__audio"]/div[1]/button'
        self.reload_bottom_locator = '#captcha__reload__button'

    def _get_audio_file_source(self):
        audio_file_element = self.capcha_frame.ele(self.audio_file_locator)
        audio_file_source = audio_file_element.attrs.get("src", None)
        return audio_file_source

    def _save_audio_file(self):
        audio_url = self._get_audio_file_source()
        if audio_url:
            if not os.path.exists(self.audio_file_dir):
                os.makedirs(self.audio_file_dir)

            file_path = os.path.join(self.audio_file_dir, self.audio_file_name)

            # Clean file before writing new content
            if os.path.exists(file_path):
                os.remove(file_path)

            # Download the audio file
            response = requests.get(audio_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Audio file saved as '{file_path}'")
            else:
                print("Failed to download audio file.")
        else:
            print("Audio file source not found.")

    def solve_audio_capcha(self):
        self.capcha_frame.ele(self.audio_challenge_bottom_locator).click()
        time.sleep(2)

        self._save_audio_file()

        audio_file_path = f"{self.audio_file_dir}/{self.audio_file_name}"
        numbers = AudioSolve(audio_file_path=audio_file_path).get_numbers_from_audio()
        print(f"Numbers to input: {numbers}")

        input_boxes = self.capcha_frame.eles('.audio-captcha-inputs')
        print(f"Find {len(input_boxes)} input boxes")
        if len(numbers) == len(input_boxes):

            self.capcha_frame.ele(self.play_bottom_locator).click()
            time.sleep(5)

            for i in range(len(input_boxes)):
                input_boxes[i].input(numbers[i])
                time.sleep(3)
            return True

        return None




