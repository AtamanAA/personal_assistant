import base64
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from variables import BASE_DIR
from .image_solve import ImageSolve

DEMO_URL = "https://www.geetest.com/en/demo"


class SlideCapchaSolve:
    """
    Solve slide capcha
    Main resource: https://filipvitas.medium.com/how-to-solve-geetest-slider-captcha-with-js-ac764c4e9905

    # TODO: update scenario after debug
    Base scenario:
    1. Go to the target web page
    2. Download capcha pictures
    3. Find the difference between original image and capcha image and calculate center position diff
    4. Calculate the centre position puzzle image
    5. Calculate the distance the slider moves: center position diff - center position puzzle
    6. Move the slider. Use a few steps with pauses and also use y coordinate to move.
    """
    def __init__(self, driver, capcha_frame):
        self.driver = driver
        self.capcha_frame = capcha_frame
        if self.driver and self.capcha_frame:
            self.driver.switch_to.frame(capcha_frame)

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

    def move_slider(self, cx, cy):
        print("Find slider handle")

        # Locate the slider handle
        slider_handle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.slider'))
        )

        x_position = cx
        y_position = 0
        print("Debug Initial mouse position:", x_position, y_position)

        print("Start move slider")

        action = ActionChains(self.driver).move_to_element(slider_handle).click_and_hold()
        # action.move_by_offset(x_position, 20).release().perform()

        # action.move_by_offset(10, 0).move_by_offset(10, 0).move_by_offset(x_position - 20, 0).release().perform()
        action.move_by_offset(10, 5).perform()
        time.sleep(1)
        action.move_by_offset(10, 10).perform()
        time.sleep(1)
        action.move_by_offset(x_position - 20, 5).perform()
        time.sleep(1)
        action.release().perform()
        # time.sleep(3)

    def solve_captcha(self):
        print("Start Solve Capcha")

        images = self._get__slider_capcha_images()
        print(f"Get {len(images)} capcha images")

        # Save the images
        self.image_solver.save_slider_capcha_images(images)
        # cx, cy = self._find_target_centre_position()

        cx = self.image_solver.find_puzzle_offset()

        cy = 20

        self.move_slider(cx=cx, cy=cy)

        print("Finish solve Capcha")

    def save_image(data, filename):
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(data))

    def start_solve(self):
        # self._get_url()
        self.solve_captcha()
        time.sleep(5)
        self.driver.quit()


if __name__ == '__main__':
    try:
        pass
    except Exception as error:
        print(error)
