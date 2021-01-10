from typing import Dict

from pydantic import BaseModel


class SpellCheckResponse(BaseModel):
    incorrect_words: Dict[str, Dict[str, str]]
