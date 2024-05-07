import os

from dotenv import load_dotenv

load_dotenv()

DOC_STUDIO_EMAIL = os.getenv("DOC_STUDIO_EMAIL", "test_email@gmail.com")
DOC_STUDIO_PASSWORD = os.getenv("DOC_STUDIO_PASSWORD", "test_password")
