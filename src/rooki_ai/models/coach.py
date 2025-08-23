
from pydantic import BaseModel
from typing import Literal


class RouteAnswer(BaseModel):
    route: Literal['overview_agent', 'category_agent', 'chat_agent']
    reason: str
