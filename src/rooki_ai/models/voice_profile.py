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

class ContentMetrics(BaseModel):
    """
    Metrics describing text content characteristics.

    avg_sentence_len
    Average number of words per sentence (after cleaning URLs, keeping emojis/hashtags).
    Formula: total word tokens ÷ total sentences.
    Interpretation: ~15 words per sentence → medium cadence (typical web prose is ~12–18).

    imperative_pct
    Share of sentences written as commands/requests (imperative mood), e.g., “Join us,” “Subscribe now,” “Please read.”
    Formula: (# sentences classified imperative) ÷ (total sentences).
    Interpretation: 0.22 → 22% imperative; on the assertive/CTA-heavy side.

    emoji_rate
    Proportion of tokens that are emojis.
    Formula (token-based): (# emoji tokens) ÷ (total tokens).
    Interpretation: 0.01 → ~1% of tokens are emojis; light use.
    """
    avg_sentence_len: float
    imperative_pct: float
    emoji_rate: float

class VoiceGuideSuggestion(BaseModel):
    positioning: str
    tone: str
    pillars: List[PillarItem]
    guardrails: List[GuardrailItem]
    post_metrics: ContentMetrics
    reply_metrics: ContentMetrics
    quoted_metrics: ContentMetrics
    long_form_text_metrics: ContentMetrics
