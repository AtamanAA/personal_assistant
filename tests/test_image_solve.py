import os
from personal_assistant.utils.capcha.image_solve import ImageSolve
from variables import BASE_DIR
from .data.puzzle_images.expect_puzzle_move import EXPECT_PUZZLE_MOVE


class TestImageSolve:

    def test_find_puzzle_offset(self):
        tolerance = 5
        image_data_dir = os.path.join(BASE_DIR, "tests/data/puzzle_images")

        actual_puzzle_move = {}

        for image_folder in os.listdir(image_data_dir):
            folder_path = os.path.join(image_data_dir, image_folder)

            # Check if it is a directory to avoid any files in the main directory
            if os.path.isdir(folder_path):
                capcha_image_path = os.path.join(folder_path, "capcha.png")
                puzzle_image_path = os.path.join(folder_path, "puzzle.png")

                # Ensure the files exist before proceeding
                if os.path.exists(capcha_image_path) and os.path.exists(puzzle_image_path):
                    actual_puzzle_offset = ImageSolve(
                        capcha_image_path=capcha_image_path,
                        puzzle_image_path=puzzle_image_path
                    ).find_puzzle_offset_by_images()
                    actual_puzzle_move[image_folder] = actual_puzzle_offset

        diff = {}
        for key, value in EXPECT_PUZZLE_MOVE.items():
            diff[key] = actual_puzzle_move[key] - value

        print(diff)
        no_valid_count = 0
        for value in diff.values():
            if abs(value) >= tolerance:
                no_valid_count += 1

        effectiveness = int(((len(diff) - no_valid_count) / len(diff)) * 100)
        assert effectiveness > 50
