from typing import List, Optional

from pydantic import BaseModel


class FileInputResponse(BaseModel):
    response_message: str
    all_files: Optional[List[str]] = None
    deleted_files: Optional[List[str]] = None
