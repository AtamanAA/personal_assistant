import base64
import os
import shutil
import time

import cv2
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from variables import BASE_DIR

DEMO_URL = "https://www.geetest.com/en/demo"


class SlideCapchaSolve:
    """
    Solve slide capcha
    Main resource: https://filipvitas.medium.com/how-to-solve-geetest-slider-captcha-with-js-ac764c4e9905

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

    @staticmethod
    def _save_slider_capcha_images(images):
        names = ['capcha.png', 'puzzle.png', 'original.png']
        for name, image_data in zip(names, images):
            image_data = image_data.replace('data:image/png;base64,', '')
            image_bytes = base64.b64decode(image_data)
            file_path = f'{BASE_DIR}/slide_capcha_img/{name}'

            # Remove existing file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)

            # Save the new image
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
        print("Save capcha images")

    # @staticmethod
    # def _save_images_for_second_step(images):
    #     names = ['captcha_2.png', 'puzzle_2.png', 'original_2.png']
    #     for name, image_data in zip(names, images):
    #         image_data = image_data.replace('data:image/png;base64,', '')
    #         image_bytes = base64.b64decode(image_data)
    #         file_path = f'slide_capcha_img/{name}'
    #
    #         # Remove existing file if it exists
    #         if os.path.exists(file_path):
    #             os.remove(file_path)
    #
    #         # Save the new image
    #         with open(file_path, 'wb') as f:
    #             f.write(image_bytes)
    #     print("Save capcha images")
    #
    # def _save_diff_image(self):
    #     # Load original and captcha images
    #     original_image = Image.open('slide_capcha_img/original.png')
    #     captcha_image = Image.open('slide_capcha_img/captcha.png')
    #
    #     # Get the size of the images
    #     width, height = original_image.size
    #
    #     # Create a diff image
    #     img_diff = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    #
    #     # Compute image difference
    #     mismatch = pixelmatch(original_image, captcha_image, img_diff, includeAA=True)
    #
    #     # Save the difference image
    #     img_diff.save('./slide_capcha_img/diff.png')
    #     print("Write_picture_diffing")
    #
    # @staticmethod
    # def _update_diff_image():
    #     # Copy the original diff image to a new file
    #     shutil.copyfile('./slide_capcha_img/diff.png', './slide_capcha_img/diff_original.png')
    #
    #     # Load the original diff image
    #     src_image = cv2.imread('./slide_capcha_img/diff_original.png')
    #
    #     # Convert to grayscale
    #     src_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)
    #
    #     # Apply threshold to eliminate noise
    #     _, dst = cv2.threshold(src_gray, 127, 255, cv2.THRESH_BINARY)
    #
    #     # Define kernel for erosion and dilation
    #     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    #
    #     # Erode to fill white gaps
    #     dst = cv2.erode(dst, kernel, iterations=1)
    #
    #     # Dilate to revert the effects of erosion
    #     dst = cv2.dilate(dst, kernel, iterations=1)
    #
    #     # Save the processed image back to diff.png
    #     cv2.imwrite('./slide_capcha_img/diff.png', dst)
    #
    #     print("Locate_diff")
    #
    # def _find_diff_position(self):
    #     # Read the diff image
    #     src_image = cv2.imread('./slide_capcha_img/diff.png')
    #
    #     # Convert to grayscale
    #     src_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)
    #
    #     # Thresholding
    #     _, dst = cv2.threshold(src_gray, 150, 255, cv2.THRESH_BINARY_INV)
    #
    #     # Find contours
    #     contours, _ = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    #     # Get the first contour
    #     contour = contours[0]
    #
    #     # Calculate moments
    #     moment = cv2.moments(contour)
    #     cx = int(moment['m10'] / moment['m00'])
    #     cy = int(moment['m01'] / moment['m00'])
    #
    #     print("Diff position:", cx, cy)
    #
    #     # Draw contour and center
    #     cv2.drawContours(src_image, [contour], 0, (255, 0, 0), thickness=cv2.FILLED)
    #     cv2.circle(src_image, (cx, cy), 3, (0, 0, 255), thickness=cv2.FILLED)
    #     # cv2.putText(src_image, 'center', (cx + 4, cy + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), thickness=1)
    #     cv2.putText(src_image, 'center', (cx + 4, cy + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), thickness=1)
    #
    #     # Write the modified image back to diff.png
    #     cv2.imwrite('./slide_capcha_img/diff.png', src_image)
    #     print("FIND target puzzle center")
    #     return cx, cy

    def _find_puzzle_centre_position(self):

        # Load original and captcha images
        original_image = Image.open(f'{BASE_DIR}/slide_capcha_img/puzzle.png')
        # empty_image = Image.open('slide_capcha_img/puzzle.png')

        # Get the size of the images
        width, height = original_image.size

        empty_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        empty_img.save(f'{BASE_DIR}/slide_capcha_img/empty_img.png')

        # Create a diff image
        img_diff = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        # Compute image difference
        mismatch = pixelmatch(original_image, empty_img, img_diff, includeAA=True)

        # Save the difference image
        img_diff.save(f'{BASE_DIR}/slide_capcha_img/puzzle_diff.png')
        print("Write_puzzle_dif_img")



        # Copy the original diff image to a new file
        shutil.copyfile(f'{BASE_DIR}/slide_capcha_img/puzzle_diff.png', f'{BASE_DIR}/slide_capcha_img/puzzle_diff_original.png')

        # Load the original diff image
        src_image = cv2.imread(f'{BASE_DIR}/slide_capcha_img/puzzle_diff_original.png')

        # Convert to grayscale
        src_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)

        # Apply threshold to eliminate noise
        _, dst = cv2.threshold(src_gray, 127, 255, cv2.THRESH_BINARY)

        # Define kernel for erosion and dilation
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        # Erode to fill white gaps
        dst = cv2.erode(dst, kernel, iterations=1)

        # Dilate to revert the effects of erosion
        dst = cv2.dilate(dst, kernel, iterations=1)

        # Save the processed image back to diff.png
        cv2.imwrite(f'{BASE_DIR}/slide_capcha_img/puzzle_diff.png', dst)

        print("Locate_puzzle_diff")

        # Read the diff image
        src_image = cv2.imread(f'{BASE_DIR}/slide_capcha_img/puzzle_diff.png')

        # Convert to grayscale
        src_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)

        # Thresholding
        _, dst = cv2.threshold(src_gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get the first contour
        contour = contours[0]

        # Calculate moments
        moment = cv2.moments(contour)
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])

        print("Diff position:", cx, cy)

        # Draw contour and center
        cv2.drawContours(src_image, [contour], 0, (255, 0, 0), thickness=cv2.FILLED)
        cv2.circle(src_image, (cx, cy), 3, (0, 0, 255), thickness=cv2.FILLED)
        cv2.putText(src_image, 'center', (cx + 4, cy + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), thickness=1)

        # Write the modified image back to diff.png
        cv2.imwrite(f'{BASE_DIR}/slide_capcha_img/puzzle_diff.png', src_image)
        print("FIND initial puzzle center")
        return cx, cy


    def _find_target_centre_position(self):

        # Load original and captcha images
        original_image = Image.open(f'{BASE_DIR}/slide_capcha_img/capcha.png')
        # empty_image = Image.open('slide_capcha_img/puzzle.png')

        # Get the size of the images
        width, height = original_image.size

        empty_grey_img = Image.new("RGBA", (width, height), (67, 82, 94, 255))
        empty_grey_img.save(f'{BASE_DIR}/slide_capcha_img/capcha_empty_img.png')

        # Create a diff image
        img_diff = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        # Compute image difference
        # mismatch = pixelmatch(original_image, empty_img, img_diff, includeAA=True)
        mismatch = pixelmatch(original_image, empty_grey_img, img_diff, includeAA=True,
                              alpha=0.1, aa_color=[255, 255, 0], diff_color=[255, 0, 0], diff_mask=False,
                              fail_fast=False)

        # Save the difference image
        img_diff.save(f'{BASE_DIR}/slide_capcha_img/capcha_diff.png')



        img_diff = Image.open(f'{BASE_DIR}/slide_capcha_img/capcha_diff.png')

        empty_red_img = Image.new("RGBA", (width, height), (255, 0, 0, 255))
        empty_red_img.save(f'{BASE_DIR}/slide_capcha_img/capcha_red_empty_img.png')

        img_diff_2_step = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        mismatch = pixelmatch(img_diff, empty_red_img, img_diff_2_step, includeAA=True,
                              alpha=0.1, aa_color=[255, 255, 0], diff_color=[255, 0, 0], diff_mask=False,
                              fail_fast=False)

        img_diff_2_step.save(f'{BASE_DIR}/slide_capcha_img/capcha_diff_step_2.png')

        print("Write_capcha_dif_img")



        # Copy the original diff image to a new file
        shutil.copyfile(f'{BASE_DIR}/slide_capcha_img/capcha_diff_step_2.png', f'{BASE_DIR}/slide_capcha_img/capcha_diff_original.png')

        # Load the original diff image
        src_image = cv2.imread(f'{BASE_DIR}/slide_capcha_img/capcha_diff_original.png')

        # Convert to grayscale
        src_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)

        # Apply threshold to eliminate noise
        _, dst = cv2.threshold(src_gray, 127, 255, cv2.THRESH_BINARY)

        # Define kernel for erosion and dilation
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        # Erode to fill white gaps
        dst = cv2.erode(dst, kernel, iterations=1)

        # Dilate to revert the effects of erosion
        dst = cv2.dilate(dst, kernel, iterations=1)

        # Save the processed image back to diff.png
        cv2.imwrite(f'{BASE_DIR}/slide_capcha_img/capcha_diff_step_2.png', dst)

        print("Locate_capcha_diff")

        # Read the diff image
        src_image = cv2.imread(f'{BASE_DIR}/slide_capcha_img/capcha_diff_step_2.png')

        # Convert to grayscale
        src_gray = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)

        # Thresholding
        _, dst = cv2.threshold(src_gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get the first contour
        contour = contours[0]

        # Calculate moments
        moment = cv2.moments(contour)
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])

        print("Diff position:", cx, cy)

        # Draw contour and center
        cv2.drawContours(src_image, [contour], 0, (255, 0, 0), thickness=cv2.FILLED)
        cv2.circle(src_image, (cx, cy), 3, (0, 0, 255), thickness=cv2.FILLED)
        cv2.putText(src_image, 'center', (cx + 4, cy + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), thickness=1)

        # Write the modified image back to diff.png
        cv2.imwrite(f'{BASE_DIR}/slide_capcha_img/capcha_diff_step_2.png', src_image)
        print("FIND target center")
        return cx, cy

    def move_slider(self, cx, cy):
        print("Find slider handle")

        # self.driver.switch_to.frame(self.capcha_frame)

        # Locate the slider handle
        slider_handle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.slider'))
        )

        # # Get the handle bounding box
        # handle = slider_handle.rect

        initial_puzzle_position_x, _ = self._find_puzzle_centre_position()

        # x_position = cx - initial_puzzle_position_x
        # y_position = 0
        # print("Debug Initial mouse position:", x_position, y_position)

        x_position = cx
        y_position = cy

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
        time.sleep(3)


    def solve_captcha(self):
        print("Start Solve Capcha")

        images = self._get__slider_capcha_images()

        # Save the images
        self._save_slider_capcha_images(images)
        # self._find_target_centre_position()
        # self._save_diff_image()
        # self._update_diff_image()
        # cx, cy = self._find_diff_position()

        cx = 100
        cy = 25

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
        # SlideCapchaSolve().start_solve()
        SlideCapchaSolve(driver=None, capcha_frame=None)._find_target_centre_position()
    except Exception as error:
        print(error)
