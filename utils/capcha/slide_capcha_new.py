import base64
import time

from utils.capcha.image_solve import ImageSolve
from variables import BASE_DIR
from DrissionPage.common import Actions
import random

from pyclick.humancurve import HumanCurve

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
        self.puzzle_challenge_bottom_locator = "#captcha__puzzle__button"

        self.action = Actions(self.capcha_frame)
        self.debug_action = Actions(self.page)
        self.cursor_debug = False

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
        time.sleep(random.uniform(2, 5))
        slider_handle = self.capcha_frame.ele('.slider')
        x_position = cx
        y_position = random.randint(20, 40)  # Y offset only for emulate human beheiver
        full_duration = random.uniform(4 / 255, 6 / 255) * x_position

        offset_x_1_step = 0.6 * x_position
        offset_y_1_step = 0.4 * y_position
        duration_1_step = 0.3 * full_duration

        offset_x_2_step = 0.3 * x_position
        offset_y_2_step = 0.3 * y_position
        duration_2_step = 0.4 * full_duration

        offset_x_3_step = x_position - offset_x_1_step - offset_x_2_step + random.randint(8, 15)
        offset_y_3_step = y_position - offset_y_1_step - offset_y_2_step + random.randint(5, 8)
        duration_3_step = full_duration - duration_1_step - duration_2_step - random.uniform(0.2, 0.5)

        offset_x_4_step = x_position - offset_x_1_step - offset_x_2_step - offset_x_3_step
        offset_y_4_step = y_position - offset_y_1_step - offset_y_2_step - offset_y_3_step
        duration_4_step = full_duration - duration_1_step - duration_2_step - duration_3_step

        print("Start move slider. Target offset:", x_position, y_position)

        if self.cursor_debug:
            # Actions for debug
            self._move_to_element_for_curve(action=self.debug_action, element=slider_handle,
                                            duration=random.uniform(0.9, 1.8))

            self._move_for_curve(action=self.debug_action, target_x=offset_x_1_step, target_y=offset_y_1_step, duration=duration_1_step)
            self._move_for_curve(action=self.debug_action, target_x=offset_x_2_step, target_y=offset_y_2_step, duration=duration_2_step)
            self._move_for_curve(action=self.debug_action, target_x=offset_x_3_step, target_y=offset_y_3_step, duration=duration_3_step)
            self._move_for_curve(action=self.debug_action, target_x=offset_x_4_step, target_y=offset_y_4_step, duration=duration_4_step)

            time.sleep(3)

        self.action.scroll(delta_y=random.randint(100, 300)).wait(random.uniform(0.8, 1.5))
        self._move_to_element_for_curve(action=self.action, element=slider_handle, duration=random.uniform(0.9, 1.8))
        self.action.hold(slider_handle).wait(random.uniform(0.8, 1.5))

        self._move_for_curve(action=self.action, target_x=offset_x_1_step, target_y=offset_y_1_step, duration=duration_1_step)
        self._move_for_curve(action=self.action, target_x=offset_x_2_step, target_y=offset_y_2_step, duration=duration_2_step)
        self._move_for_curve(action=self.action, target_x=offset_x_3_step, target_y=offset_y_3_step, duration=duration_3_step)
        self._move_for_curve(action=self.action, target_x=offset_x_4_step, target_y=offset_y_4_step, duration=duration_4_step)

        self.action.release()

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
        puzzle_challenge_bottom = self.capcha_frame.ele(self.puzzle_challenge_bottom_locator)

        if self.cursor_debug:
            # Actions for debug
            self._move_to_element_for_curve(action=self.debug_action, element=puzzle_challenge_bottom, duration=random.uniform(0.8, 1.5))
            time.sleep(3)

        self._move_to_element_for_curve(action=self.action, element=puzzle_challenge_bottom,
                                        duration=random.uniform(0.8, 1.5))
        self.action.click()

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
    def _move_to_element_for_curve(action, element, duration=0.5):
        current_x = int(action.curr_x)
        current_y = int(action.curr_y)
        target_x = int(element.rect.click_point[0])
        target_y = int(element.rect.click_point[1])
        curve = HumanCurve([current_x, current_y], [target_x, target_y]).generateCurve()
        for point in curve:
            action.move(offset_x=int(point[0] - action.curr_x), offset_y=int(point[1] - action.curr_y), duration=(duration / len(curve)))

    @staticmethod
    def _move_for_curve(action, target_x, target_y, duration=0.5):
        current_x = int(action.curr_x)
        current_y = int(action.curr_y)
        target_x = int(target_x)
        target_y = int(target_y)
        curve = HumanCurve([current_x, current_y], [current_x + target_x, current_y + target_y]).generateCurve(offsetBoundaryX=20, offsetBoundaryY=10, targetPoints=20)
        for point in curve:
            action.move(offset_x=int(point[0] - action.curr_x), offset_y=int(point[1] - action.curr_y), duration=(duration / len(curve)))



    @staticmethod
    def save_image(data, filename):
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(data))


if __name__ == '__main__':
    try:
        pass
    except Exception as error:
        print(error)
