import base64
import time

from utils.capcha.image_solve import ImageSolve
from variables import BASE_DIR

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

    def get_puzzle_offset(self):
        images = self._get__slider_capcha_images()
        print(f"Get {len(images)} capcha images")

        self.image_solver.save_slider_capcha_images(images)
        # result = self.image_solver.find_puzzle_offset_by_image_data()
        result = self.image_solver.find_puzzle_offset_by_images()
        return result

    def solve_captcha(self):
        print("Start Solve Capcha")
        cx = self.get_puzzle_offset()
        print(f"Puzzle offset: {cx}")
        self.move_slider(cx=cx)

        # while True:
        #     cx = self.get_puzzle_offset()
        #     print(f"Puzzle offset: {cx}")
        #     if cx:
        #         self.move_slider(cx=cx)
        #         break
        #     # Refresh image
        #     self.capcha_frame.ele('#captcha__reload__button').click()
        #     print("Refresh images")
        #     time.sleep(5)
        #     continue

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
