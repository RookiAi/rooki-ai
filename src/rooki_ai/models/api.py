from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from rooki_ai.models.voice_profile import (
    ContentMetrics,
    GuardrailItem,
    PillarItem,
    VoiceTone,
)


class VoiceProfileRequest(BaseModel):
    x_handle: str
    pillar: int = 3
    guardrail: int = 3


class VoiceProfileResponse(BaseModel):
    positioning: str
    tone: VoiceTone
    pillars: List[PillarItem]
    guardrails: List[GuardrailItem]
    post_metrics: ContentMetrics
    reply_metrics: ContentMetrics
    quoted_metrics: ContentMetrics
    long_form_text_metrics: ContentMetrics


# Standup Coach API Models
class ChatInfo(BaseModel):
    platform: str
    chat_id: str
    message_id: str
    text: str
    callback: Optional[str] = None


class StandupCoachRequest(BaseModel):
    user_voice_profile_id: str
    chat: ChatInfo
    date: str


class ActionItem(BaseModel):
    kind: str
    draft_id: Optional[str] = None
    voice_id: Optional[str] = None


class DraftMeta(BaseModel):
    chars: int
    platform_max: int


class Draft(BaseModel):
    draft_id: str
    text: str
    meta: DraftMeta


class DraftSource(BaseModel):
    draft_id: str


class GeneratedDraftEffect(BaseModel):
    type: Literal["generated_draft"]
    draft: Draft
    source: DraftSource


class KeyboardButton(BaseModel):
    label: str
    callback_data: str


class FocusState(BaseModel):
    kind: str
    draft_id: Optional[str] = None


class StatePatch(BaseModel):
    focus: FocusState


class StandupCoachResponse(BaseModel):
    message: str
    actions: List[ActionItem]
    effects: List[Union[GeneratedDraftEffect, Dict[str, Any]]]
    keyboard: List[KeyboardButton]
    state_patch: Optional[StatePatch] = None
