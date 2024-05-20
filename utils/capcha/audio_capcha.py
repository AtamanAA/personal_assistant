import os
import time
import random

import requests

from variables import BASE_DIR
from .audio_solve import AudioSolve
from DrissionPage.common import Actions


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
        time.sleep(random.uniform(2, 4))
        ac = Actions(self.capcha_frame)

        audio_challenge_bottom = self.capcha_frame.ele(self.audio_challenge_bottom_locator)
        ac.move_to(audio_challenge_bottom).click()
        ac.move(300, 100, duration=2.2)
        ac.move(200, 150, duration=1.3)
        time.sleep(random.uniform(2, 4))

        self._save_audio_file()

        audio_file_path = f"{self.audio_file_dir}/{self.audio_file_name}"
        numbers = AudioSolve(audio_file_path=audio_file_path).get_numbers_from_audio()
        print(f"Numbers to input: {numbers}")

        input_boxes = self.capcha_frame.eles('.audio-captcha-inputs')
        print(f"Find {len(input_boxes)} input boxes")

        if len(numbers) == len(input_boxes):
            # TODO: find first input box position and move mouse to the centre this box
            ac.move(300, 100)
            ac.move(200, 150)

            # TODO: find mouse init position, find play bottom position and move to centre this element
            play_audio_bottom = self.capcha_frame.ele(self.play_bottom_locator)
            ac.move_to(play_audio_bottom).wait(random.uniform(1, 2)).click()

            time.sleep(random.uniform(4, 6))
            # TODO: Debug and modification for human behavior
            for i in range(len(input_boxes)):
                input_box = self.capcha_frame.run_js("return document.activeElement")

                ac.move_to(input_box, duration=random.uniform(0.5, 1.5)).wait(random.uniform(0.5, 1.5)).click()
                time.sleep(random.uniform(0.2, 0.5))
                # ac.move(random.randint(50, 100), random.randint(50, 100), duration=random.uniform(0.2, 0.5))
                input_box.input(numbers[i])

                # js_script = f"""
                #     (function(numbers) {{
                #         let input_box = document.activeElement;
                #         input_box.value = {numbers[i]};
                #         let event = new Event('input', {{ bubbles: true }});
                #         input_box.dispatchEvent(event);
                #     }})(arguments[0]);
                # """
                # self.capcha_frame.run_js(js_script)
                time.sleep(random.uniform(2.5, 3.5))

            return True

        return None




