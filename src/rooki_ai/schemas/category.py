# src/rooki_ai/models/tweet_context.py
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from rooki_ai.schemas.id import schema_id  # your tiny decorator


@schema_id("TweetContext@v1")
class TweetContext(BaseModel):
    user_id: str
    user_message: str
    trending_topics: List[str]
    mcp_examples: List[str]
    insights_summary: str  # <- the LLM produces this
    brand_constraints: Dict[str, Any] = {}
    voice_profile: Optional[Dict[str, Any]] = None


@schema_id("TweetDraft@v1")
class TweetDraft(BaseModel):
    prelude: str  # one conversational sentence
    tweet: str  # the final tweet
