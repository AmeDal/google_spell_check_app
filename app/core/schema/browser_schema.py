from enum import Enum

from pydantic import BaseModel


class BrowserResponse(BaseModel):
    response_message: str

class ProcessName(str, Enum):
    CHROMEDRIVER = "Chrome Driver"
    CHROME = "Chrome"
    BOTH = "Both"
