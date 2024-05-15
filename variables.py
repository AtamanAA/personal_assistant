import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = str(pathlib.Path(__file__).parent.resolve())

DEBUG = int(os.getenv("DEBUG", "0"))

DOC_STUDIO_EMAIL = os.getenv("DOC_STUDIO_EMAIL", "test_email@gmail.com")
DOC_STUDIO_PASSWORD = os.getenv("DOC_STUDIO_PASSWORD", "test_password")

UEFA_EMAIL = os.getenv("UEFA_EMAIL", "uefa_example_email@gmail.com")
UEFA_PASSWORD = os.getenv("UEFA_PASSWORD", "uefa_example_password")
