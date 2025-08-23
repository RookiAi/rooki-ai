from typing import Annotated, Literal

from pydantic import BaseModel

# Define RouteAnswer as a simple string type with validation
RouteAnswer = Annotated[
    Literal["overview_agent", "category_agent", "chat_agent"],
    "Must be one of: 'overview_agent', 'category_agent', or 'chat_agent'",
]
