from typing import Any, Dict, List, Literal
from pydantic import BaseModel

class PillarItem(BaseModel):
    pillar: str
    weighting: float

class GuardrailItem(BaseModel):
    type: Literal['do', 'dont']
    guardrail: str

class CorpusOut(BaseModel):
    text: str
    metadata: Dict[str, Any]
    type: Literal['post', 'reply', 'quote', 'long_form']

class StyleProfile(BaseModel):
    tone_distribution: Dict[str, float]
    topic_distribution: Dict[str, float]
    engagement_metrics: Dict[str, float]
    content_patterns: Dict[str, List[str]]

class VoiceGuideSuggestion(BaseModel):
    positioning: str
    tone: str
    pillars: List[PillarItem]
    guardrails: List[GuardrailItem]
    metrics: Dict[str, Dict[str, float]]