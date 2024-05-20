import base64
import time

from utils.capcha.image_solve import ImageSolve
from variables import BASE_DIR
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


DEMO_URL = "https://www.geetest.com/en/demo"


class SlideCapchaSolveStealth:

    def __init__(self, driver, capcha_frame):
        self.driver = driver
        self.capcha_frame = capcha_frame
        if self.driver and self.capcha_frame:
            self.driver.switch_to.frame(capcha_frame)

        self.puzzle_challenge_bottom_locator = "#captcha__puzzle__button"

        self.image_solver = ImageSolve(
            capcha_image_path=f"{BASE_DIR}/slide_capcha_img/capcha.png",
            puzzle_image_path=f"{BASE_DIR}/slide_capcha_img/puzzle.png"
        )

    def _get__slider_capcha_images(self):
        images = self.driver.execute_script('''
            const canvases = document.querySelectorAll('.toggled canvas');
            const images = [];
            canvases.forEach(canvas => {
                const dataURL = canvas.toDataURL('image/png').replace(/^data:image\/png;base64,/, '');
                images.push(dataURL);
            });
            return images;
        ''')
        print("Get capcha images")
        return images

    def move_slider(self, cx):
        print("Find slider handle")
        time.sleep(random.uniform(2, 5))
        slider_handle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.slider'))
        )

        x_position = cx
        y_position = random.randint(10, 20)  # Y offset only for emulate human beheiver
        print("Start move slider. Target offset:", x_position, y_position)

        action = ActionChains(self.driver).move_to_element(slider_handle).click_and_hold()
        action.move_by_offset(10, 5).perform()
        time.sleep(1)
        action.move_by_offset(10, 10).perform()
        time.sleep(1)
        action.move_by_offset(x_position - 20, 5).perform()
        time.sleep(1)
        action.release().perform()

        print("Finish move slider")

    def get_puzzle_offset(self):
        images = self._get__slider_capcha_images()
        print(f"Get {len(images)} capcha images")
        self.image_solver.save_slider_capcha_images(images)
        result = self.image_solver.find_puzzle_offset_by_images()
        return result

    def solve_captcha(self):
        print("Start Solve Capcha")

        puzzle_challenge_bottom = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self.puzzle_challenge_bottom_locator))
        )

        ActionChains(self.driver).move_to_element(puzzle_challenge_bottom).click()

        cx = self.get_puzzle_offset()
        print(f"Puzzle offset: {cx}")
        self.move_slider(cx=cx)
        print("Finish solve Capcha")

    @staticmethod
    def save_image(data, filename):
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(data))


if __name__ == '__main__':
    try:
        pass
    except Exception as error:
        print(error)
