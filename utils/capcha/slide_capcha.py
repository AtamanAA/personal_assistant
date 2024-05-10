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

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from skimage.feature import match_template
from skimage.io import imread, imshow
from skimage.color import rgb2gray
from matplotlib.patches import Circle
from skimage import transform


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
        print("Start save capcha image")
        directory = f'{BASE_DIR}/slide_capcha_img/'

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

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

    def _find_target_centre_position_2(self):
        img_rgb = cv.imread(f'{BASE_DIR}/slide_capcha_img/capcha.png')
        assert img_rgb is not None, "file could not be read, check with os.path.exists()"
        img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
        cv.imwrite(f'{BASE_DIR}/slide_capcha_img/img_gray.png', img_gray)

        template = cv.imread(f'{BASE_DIR}/slide_capcha_img/puzzle.png', cv.IMREAD_GRAYSCALE)
        assert template is not None, "file could not be read, check with os.path.exists()"
        w, h = template.shape[::-1]
        cv.imwrite(f'{BASE_DIR}/slide_capcha_img/template.png', template)

        res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        cv.imwrite(f'{BASE_DIR}/slide_capcha_img/res.png', img_rgb)

    def _find_target_centre_position_3(self):
        # Load image
        # img = imread(f'{BASE_DIR}/slide_capcha_img/capcha.png')
        img = imread(f'{BASE_DIR}/slide_capcha_img/capcha.png')[:, :, :3]  # Remove alpha channel
        img_gs = rgb2gray(img)

        # Plot
        fig, ax = plt.subplots(1, 2, figsize=(16, 8))
        ax[0].imshow(img)
        ax[0].set_title("Original Image of Where's Wally?")
        ax[0].set_axis_off()
        ax[1].imshow(img_gs, cmap='gray')
        ax[1].set_title("Grayscale Image of Where's Wally?")
        ax[1].set_axis_off()
        plt.show()

        # Get a template image and match it with the grayscale image
        # img_template = img_gs[100:120, 80:100]

        img_template = imread(f'{BASE_DIR}/slide_capcha_img/puzzle.png')[:, :, :3]  # Remove alpha channel
        img_template_gs = rgb2gray(img_template)
        # img_template_gs = img_template_gs[82:142, 2:62]

        img_template_gs = img_template_gs[13:73, 2:62]

        # img_template_gs = img_gs[100:120, 80:100]

        # Plot
        fig, ax = plt.subplots(1, 2, figsize=(16, 8))
        # ax[0].imshow(img)
        # ax[0].set_title("puzzle_test")
        ax[0].set_axis_off()
        ax[1].imshow(img_template_gs, cmap='gray')
        ax[1].set_title("puzzle_test")
        ax[1].set_axis_off()
        plt.show()


        result = match_template(img_gs, img_template_gs)
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        ax.imshow(result, cmap='viridis')
        ax.set_title("Result of Template Matching")
        ax.set_axis_off()
        plt.show()

        # Getting the max
        x, y = np.unravel_index(np.argmax(result), result.shape)
        imshow(img_gs)
        template_width, template_height = img_template_gs.shape
        rect = plt.Rectangle((y, x), template_height, template_width, color='red',
                             fc='none')
        plt.gca().add_patch(rect)
        plt.title('Grayscale Image with Bounding Box around Wally')
        plt.axis('off')
        plt.show()

        return True

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
        # SlideCapchaSolve(driver=None, capcha_frame=None)._find_target_centre_position()
        SlideCapchaSolve(driver=None, capcha_frame=None)._find_target_centre_position_3()
    except Exception as error:
        print(error)
