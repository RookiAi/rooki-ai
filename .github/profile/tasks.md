### Task

- **Task T1 — LoadCorpus**

  - Input: `storage_url: str`, `format: Literal['jsonl']`, `schema_version: str`
  - Output (Pydantic):

    ```python
    class CorpusOut(BaseModel):
        samples: list[str]          # ~1–2k chars each
        count: int
        time_range: tuple[str,str] | None

    ```

  - Stop condition: manifest read and ≥N samples yielded (e.g., ≥300).

- **Task T2 — ComputeStyleMetrics**

  - Input: `CorpusOut`, `influencers: dict`, `options.recompute_metrics: bool`
  - Output:

    ```python
    class StyleProfile(BaseModel):
        avg_sentence_len: float
        imperative_pct: float
        emoji_rate: float
        hashtag_rate: float
        link_rate: float
        cadence: Literal['staccato','balanced','longform']
        influence_blend: dict[str, float]  # normalized weights per handle

    ```

- **Task T3 — SynthesizeVoiceGuide**

  - Input: `StyleProfile`, `influencers`
  - Output:

    ```python
    class VoiceGuideSuggestion(BaseModel):
        positioning: str
        tone: Literal['direct','helpful','witty','professional','educational']
        pillars: list[dict]  # { pillar: str, weighting: float } (weights sum≈1)
        guardrails: list[dict]  # { type: 'do'|'dont', guardrail: str }
        metrics: dict          # echo key metrics used

    ```

  - Guardrail: JSON schema validation + weight normalization.
