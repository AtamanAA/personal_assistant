import base64
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from variables import BASE_DIR
from .image_solve import ImageSolve

DEMO_URL = "https://www.geetest.com/en/demo"


class SlideCapchaSolveNew:
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
    def __init__(self, page, capcha_frame):
        self.page = page
        self.capcha_frame = capcha_frame

        self.image_solver = ImageSolve(
            capcha_image_path=f"{BASE_DIR}/slide_capcha_img/capcha.png",
            puzzle_image_path=f"{BASE_DIR}/slide_capcha_img/puzzle.png"
        )

    def _get__slider_capcha_images(self):
        images = self.capcha_frame.run_js('''
            (function() {
                console.log('Script started');
                const canvases = document.querySelectorAll('.toggled canvas');
                const images = [];
                console.log(images);
                canvases.forEach(canvas => {
                    console.log('Processing canvas');
                    const dataURL = canvas.toDataURL('image/png').replace(/^data:image\/png;base64,/, '');
                    images.push(dataURL);
                });
                console.log('Script finished');
                return images;
            })();
        ''', as_expr=True)
        print("Get capcha images")
        return images

    def move_slider(self, cx):
        print("Find slider handle")
        time.sleep(3)
        slider_handle = self.capcha_frame.ele('.slider')
        x_position = cx
        y_position = 10  # Fix y offset only for emulate human beheiver
        print("Start move slider. Target offset:", x_position, y_position)
        slider_handle.drag(x_position, y_position, 2)
        print("Finish move slider")

    def solve_captcha(self):
        print("Start Solve Capcha")
        images = self._get__slider_capcha_images()
        print(f"Get {len(images)} capcha images")

        self.image_solver.save_slider_capcha_images(images)
        cx = self.image_solver.find_puzzle_offset()

        self.move_slider(cx=cx)

        print("Finish solve Capcha")

    @staticmethod
    def save_image(data, filename):
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(data))

    def start_solve(self):
        # self._get_url()
        self.solve_captcha()
        time.sleep(5)


if __name__ == '__main__':
    try:
        pass
    except Exception as error:
        print(error)
