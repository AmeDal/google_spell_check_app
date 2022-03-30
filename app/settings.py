import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    # FastAPI App Configurations
    FAST_API_HOST: str = '0.0.0.0'
    FAST_API_PORT: int = 8000
    FAST_API_WORKERS: int = max(1, min(os.cpu_count() // 1.5, 5))
    FAST_API_RELOAD: bool = True
    FAST_API_TITLE: str = 'Google Spell-Check App'
    FAST_API_VERSION: str = '1.0'
    FAST_API_DESCRIPTION: str = '### Run spell checking by loading words into Google Sheets'

    # Local File Paths
    UPLOAD_FOLDER: str = 'resources/uploads'
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = ['csv', 'txt', 'xls', 'xlsx']
    SCREENSHOTS_FOLDER: str = 'screenshots'

    # Chrome Configurations
    PROXY: bool = None
    HEADLESS: bool = False
    # The following url is least likely to give captcha prompts. https://gist.github.com/ikegami-yukino/51b247080976cb41fe93#gistcomment-3455633
    GOOGLE_LOGIN_URL = 'https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?redirect_uri=https%3A%2F%2Fdevelopers.google.com%2Foauthplayground&prompt=consent&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email&access_type=offline&flowName=GeneralOAuthFlow'

    # Google Spell Check Configurations
    CREDENTIALS_JSON_PATH: str = './api_credentials/google_sheets_credentials.json'
    # GOOGLE_USERNAME_ENV: str = 'ADD AS ENVIVRONMENT VARIABLE'
    # GOOGLE_PASSWORD_ENV: str = 'ADD AS ENVIVRONMENT VARIABLE'
    SHEET_NAME: str = 'Input Sheet'
    # Load BLACKLIST_WORDS and WHITELIST_WORDS
    try:
        with open(os.path.abspath('./resources/word_list/blacklist_words.txt'), 'r') as f:
            BLACKLIST_WORDS = set([i.strip('\n') for i in f.readlines()])
    except:
        BLACKLIST_WORDS = set()
    try:
        with open(os.path.abspath('./resources/word_list/whitelist_words.txt'), 'r') as f:
            WHITELIST_WORDS = set([i.strip('\n') for i in f.readlines()])
    except:
        WHITELIST_WORDS = set()


    # Miscellaneous Configurations
    FILE_WRITE_BUFFER_SIZE = 16384


@lru_cache()
def get_app_settings() -> Settings:
    return Settings()
