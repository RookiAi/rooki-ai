from pydantic import BaseModel
from typing import Dict, List, Optional, Literal, Any

class VoiceProfileRequest(BaseModel):
    x_handle: str
    config: Optional[Dict[str, int]] = None

class PillarItem(BaseModel):
    pillar: str
    weighting: float

class GuardrailItem(BaseModel):
    type: Literal['do', 'dont']
    guardrail: str

class VoiceProfileResponse(BaseModel):
    positioning: str
    tone: Literal['direct', 'helpful', 'witty', 'professional', 'educational']
    pillars: List[PillarItem]
    guardrails: List[GuardrailItem]
    post_metrics: Dict[str, float]
    reply_metrics: Dict[str, float]
    quoted_metrics: Dict[str, float]
    long_form_text_metrics: Dict[str, float]
