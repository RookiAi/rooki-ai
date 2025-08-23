from pydantic import BaseModel
from typing import  List, Literal 

from rooki_ai.models.voice_profile import ContentMetrics, GuardrailItem, PillarItem

class VoiceProfileRequest(BaseModel):
    x_handle: str
    pillar: int = 3
    guardrail: int = 3



class VoiceProfileResponse(BaseModel):
    positioning: str
    tone: Literal['direct', 'helpful', 'witty', 'professional', 'educational']
    pillars: List[PillarItem]
    guardrails: List[GuardrailItem]
    post_metrics: ContentMetrics
    reply_metrics: ContentMetrics
    quoted_metrics: ContentMetrics
    long_form_text_metrics: ContentMetrics
