import os

from app.core.models.browser import Browser
from app.core.schema.browser_schema import BrowserResponse, ProcessName
from app.settings import get_app_settings
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import FileResponse

config = get_app_settings()
router_name = 'Browser'
router_description = 'APIs to control Selenium driven browser'
openapi_tag = {'name': router_name, 'description': router_description}
router = APIRouter(prefix = '/browser', tags = [router_name])


@router.get("/open-url",
            summary = 'Launch URL in the Selenium driven Chrome Browser',
            response_model = BrowserResponse,
            response_model_exclude_unset = True)
async def open_url(url: str = Query(
    'https://en.wikipedia.org/wiki/Special:Random',
    description = 'URL to be opened in the Selenium driven Chrome Browser')):
    try:
        browser = Browser().browser
        browser.get(url)
        return BrowserResponse(response_message = f"Successfully launched '{browser.title}' on Selenium driven Chrome browser")
    except Exception as e:
        error_message = f"Could not open URL due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)

@router.get("/google-login",
            summary = 'Log into Google Account using Selenium driven Chrome Browser',
            response_model = BrowserResponse,
            response_model_exclude_unset = True)
async def google_login():
    try:
        browser_object = Browser(google_login_flag = True)
        is_login_successful = browser_object.google_login()
        message = f"Successfully logged into Google Account!" if is_login_successful\
            else "Failed to log into Google Account!"
        return BrowserResponse(response_message = message)
    except Exception as e:
        error_message = f"Could not log into Google Account due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)

@router.get("/screenshot",
            summary = 'Save screenshot of Selenium driven Chrome browser',
            response_model_exclude_unset = True)
def get_screenshot():
    try:
        browser = Browser().browser
        screenshot_path = os.path.join(os.path.abspath(config.SCREENSHOTS_FOLDER), 'screenshot.png')
        browser.get_screenshot_as_file(screenshot_path)
        return FileResponse(screenshot_path, media_type = 'application/octet-stream', filename = 'screenshot.png')
    except Exception as e:
        error_message = f"Could capture screenshot due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)

@router.get("/kill/{process_name}",
            summary = 'Kill all instances of chromedriver.exe and/or chrome.exe',
            response_model = BrowserResponse,
            response_model_exclude_unset = True)
async def kill_chrome_instances(process_name: ProcessName):
    try:
        response_message = "Incorrect path parameter!"
        if process_name == ProcessName.CHROMEDRIVER:
            result = os.system("taskkill /f /im chromedriver.exe")
            response_message = 'All instances of chromedriver.exe killed!' if result == 0 else 'No instances of chromedriver.exe to kill'
        elif process_name == ProcessName.CHROME:
            result = os.system("taskkill /f /im chrome.exe")
            response_message = 'All instances of chrome.exe killed!' if result == 0 else 'No instances of chrome.exe to kill'
        elif process_name == ProcessName.BOTH:
            chromedriver_result = os.system("taskkill /f /im chromedriver.exe")
            chrome_result = os.system("taskkill /f /im chrome.exe")
            if chromedriver_result == 0 and chrome_result != 0:
                response_message = 'All instances of chromedriver.exe killed, but no instances of chrome.exe to kill!'
            elif chrome_result == 0 and chromedriver_result != 0:
                response_message = 'All instances of chrome.exe killed, but no instances of chromedriver.exe to kill!'
            elif chrome_result == 0 and chrome_result == 0:
                response_message = 'All instances of chromedriver.exe and chrome.exe killed!'
            else:
                response_message = 'No instances of chromedriver.exe and chrome.exe to kill!'
        return BrowserResponse(response_message = response_message)
    except Exception as e:
        error_message = f"Could not kill processes due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)
