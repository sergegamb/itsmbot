import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://support.agneko.com/api/v3/")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "your_auth_token_here")


TICKETS_PER_PAGE = 5 # Define how many tickets to show per page