import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
EMAIL_CONFIG = {
    "address": os.getenv("EMAIL_ADDRESS"),
    "password": os.getenv("EMAIL_PASSWORD")
}