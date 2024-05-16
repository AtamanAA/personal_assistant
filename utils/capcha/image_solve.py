import base64
import os
import shutil

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pixelmatch.contrib.PIL import pixelmatch
from skimage.color import rgb2gray, rgba2rgb, gray2rgb
from skimage.feature import match_template
from skimage.io import imread, imshow

from variables import BASE_DIR, DEBUG

DEMO_URL = "https://www.geetest.com/en/demo"


class ImageSolve:
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
    def __init__(self, capcha_image_path: str, puzzle_image_path: str):
        self.capcha_image_path = capcha_image_path
        self.puzzle_image_path = puzzle_image_path

    @staticmethod
    def save_slider_capcha_images(images: list) -> bool:
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
        return True

    def _find_puzzle_centre_position(self):

        # Load original and captcha images
        # original_image = Image.open(f'{BASE_DIR}/slide_capcha_img/puzzle.png')
        original_image = Image.open(self.puzzle_image_path)
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
        return cx

    @staticmethod
    def _crop_puzzle_image(image):
        # Convert OpenCV image (numpy.ndarray) to PIL Image
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Convert the image to grayscale
        img_gray = image_pil.convert('L')

        # Get the bounding box of the non-empty region
        bbox = img_gray.getbbox()

        # Crop the image using the bounding box
        cropped_img = image_pil.crop(bbox)

        # Save or display the cropped image
        # cropped_img.show()  # Display the cropped image
        # cropped_img.save('cropped_image.png')  # Save the cropped image

        return cropped_img

    def _find_puzzle_borders(self):
        image = cv2.imread(self.puzzle_image_path, cv2.IMREAD_UNCHANGED)

        # Remove alpha channel if present
        if image.shape[2] == 4:
            image = image[:, :, :3]

        # Convert the image to RGB format for PIL
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Convert the image to grayscale
        img_gray = image_pil.convert('L')

        # Get the bounding box of the non-empty region
        bbox = img_gray.getbbox()
        if bbox:
            # left, upper, right, lower = bbox
            return bbox
        return (0, 0, image.shape[1], image.shape[0])

    def _find_puzzle_bottom_border(self):
        return 100

    def _find_target_centre_position(self):
        # Load image
        img = imread(self.capcha_image_path)
        img = img[:, :, :3]  # Remove alpha channel
        img_gs = rgb2gray(img)

        left, upper, right, lower = self._find_puzzle_borders()
        img_gs = img_gs[upper - 5:lower + 5, :]  # Crop image by puzzle borders

        # img_gs = img_gs[40:, :]  # Additional crop

        # Plot
        if DEBUG:
            fig, ax = plt.subplots(1, 2, figsize=(16, 8))
            ax[0].imshow(img)
            ax[0].set_title("Title")
            ax[0].set_axis_off()
            ax[1].imshow(img_gs, cmap='gray')
            ax[1].set_title("Title")
            ax[1].set_axis_off()
            plt.show()

        # Get a template image and match it with the grayscale image
        puzzle_image = imread(self.puzzle_image_path)
        puzzle_image = puzzle_image[:, :, :3]  # Remove alpha channel
        crop_img_template = self._crop_puzzle_image(image=puzzle_image)

        # # Convert crop_img_template to a NumPy array if it's a PIL Image
        # if isinstance(crop_img_template, Image.Image):
        #     crop_img_template = np.array(crop_img_template)
        #
        # # Convert crop_img_template to RGBA if it's not already
        # if crop_img_template.shape[2] == 3:
        #     crop_img_template = np.dstack([crop_img_template, np.ones_like(crop_img_template[:, :, 0]) * 255])
        #
        # # Get the dimensions of crop_img_template
        # height, width, _ = crop_img_template.shape
        #
        # # Create a black image with 30% transparency
        # black_image = np.zeros((height, width, 4), dtype=np.uint8)
        # black_image[:, :, 3] = 255  # 76 = 30% of 255
        #
        # # Convert black_image to BGRA
        # black_image = cv2.cvtColor(black_image, cv2.COLOR_BGR2BGRA)
        #
        # # Combine the images
        # combined_image = cv2.addWeighted(black_image, 1, crop_img_template, 0.2, 0)
        #
        # cv2.imwrite(f"{BASE_DIR}/slide_capcha_img/combined_image.png", combined_image)

        # Convert the combined image to grayscale
        # img_template_gs = cv2.cvtColor(combined_image, cv2.COLOR_BGR2GRAY)

        img_template_gs = rgb2gray(crop_img_template)

        # img_template_gs = img_template_gs[40:, :]  # Additional crop

        # Plot
        if DEBUG:
            fig, ax = plt.subplots(1, 2, figsize=(16, 8))
            ax[0].set_axis_off()
            ax[1].imshow(img_template_gs, cmap='gray')
            ax[1].set_title("puzzle_test")
            ax[1].set_axis_off()
            plt.show()

        result = match_template(img_gs, img_template_gs)

        if DEBUG:
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
        if DEBUG:
            plt.gca().add_patch(rect)
            plt.title('Grayscale Image with Bounding Box around Wally')
            plt.axis('off')
            plt.show()

        # Calculate centre rectangle
        cx = int(y + template_width / 2)
        return cx

    def find_puzzle_offset(self) -> int:
        puzzle_centre_position = self._find_puzzle_centre_position()
        target_centre_position = self._find_target_centre_position()
        result = target_centre_position - puzzle_centre_position
        return result


if __name__ == '__main__':
    try:
        puzzle_offset = ImageSolve(
            capcha_image_path=f"{BASE_DIR}/slide_capcha_img/capcha.png",
            puzzle_image_path=f"{BASE_DIR}/slide_capcha_img/puzzle.png").find_puzzle_offset()
        print(f"Puzzle offset: {puzzle_offset}")
    except Exception as error:
        print(error)
