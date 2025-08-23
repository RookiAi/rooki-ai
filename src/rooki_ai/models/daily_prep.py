from typing import Any, Dict, List

from pydantic import BaseModel


class Tweets(BaseModel):
    tweets: List[Dict[str, Any]]


# class CategorizedTopTweets(BaseModel):
