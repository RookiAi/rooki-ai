# API v1 — Endpoints (FastAPI)

| Method   | Path                  | Summary                                                                              | Notes                                                       |
| -------- | --------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| **POST** | **/v1/voice/profile** | Compute a Voice Guide from the Supabase corpus (manifest URL) + optional influencers | Core compute-only endpoint. Only callable from Next.js BFF. |

## POST `/v1/voice/profile`

**Summary:** Read the tweets history from Supabase **URL**, which can get from `tweets_history` table with `x_handle`. Compute metrics + suggested Voice Guide (positioning, tone, pillars, guardrails), and return the suggestion. (No persistence)

**Auth:** `FASTAPI_SERVER_KEY` from env

**Request** `application/json`

```json
{
  "x_handle": "hinsonsidan",
  "config": {
    "pillar": 3,
    "guardrail": 3
  }
}
```

**200 OK**

```json
{
  "positioning": "For builders who need X, Brand is the Y that delivers Z.",
  "tone": "direct",
  "pillars": [
    { "pillar": "build-in-public", "weighting": 0.5 },
    { "pillar": "market-insights", "weighting": 0.3 },
    { "pillar": "hiring", "weighting": 0.2 }
  ],
  "guardrails": [
    { "type": "do", "guardrail": "be concrete" },
    { "type": "dont", "guardrail": "no price predictions" }
  ],
  "post_metrics": {
    "avg_sentence_len": 15.1,
    "imperative_pct": 0.22,
    "emoji_rate": 0.01
  },
  "reply_metrics": {
    "avg_sentence_len": 15.1,
    "imperative_pct": 0.22,
    "emoji_rate": 0.01
  },
  "quoted_metrics": {
    "avg_sentence_len": 15.1,
    "imperative_pct": 0.22,
    "emoji_rate": 0.01
  },
  "long_form_text_metrics": {
    "avg_sentence_len": 15.1,
    "imperative_pct": 0.22,
    "emoji_rate": 0.01
  }
}
```

**Errors**

- 401/403 (bad or missing BFF service token)
- 409 (another compute run already active)
- 415 (bad `format`)
- 422 (invalid manifest, unreadable parts, influencer handles invalid)

**Notes**

- Output fields map to your `voice` + children tables (`voice_pillar`, `voice_guardrail`, `voice_influencer`, `voice_context`) which the **BFF** will persist later.
- Store the final `tweets_storage_url` in `voice` for traceability/versioning.
- CrewAI Config

### Crew

```json
# Pseudocode (minimal)
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel

corpus_agent = Agent(
  role="Corpus Loader",
  goal="Load & normalize tweets from Supabase manifest",
  tools=[SupabaseStorageTool(), JSONLReaderTool(), TextNormalizeTool()],
  verbose=False, memory=False, temperature=0.0
)

metrics_agent = Agent(
  role="Metrics Analyzer",
  goal="Compute style metrics; blend influencer weights",
  tools=[StyleMetricsTool(), InfluencerMetricsTool()],
  verbose=False, memory=False, temperature=0.0
)

synth_agent = Agent(
  role="Voice Synthesizer",
  goal="Produce schema-valid Voice Guide JSON using metrics and influencers",
  tools=[TemplateLibraryTool(), JSONSchemaValidatorTool(schema=VoiceProfileResponse.schema())],
  verbose=False, memory=False, temperature=0.1
)

t1 = Task(agent=corpus_agent, description="LoadCorpus", expected_output=CorpusOut)
t2 = Task(agent=metrics_agent, description="ComputeStyleMetrics", expected_output=StyleProfile, context=[t1])
t3 = Task(agent=synth_agent, description="SynthesizeVoiceGuide", expected_output=VoiceProfileResponse, context=[t2])

voice_profile_crew = Crew(
  agents=[corpus_agent, metrics_agent, synth_agent],
  tasks=[t1, t2, t3],
  process=Process.sequential,
  max_rpm=30, # safety
)

```

### Flow (inputs/outputs wiring)

1. **LoadCorpus** → returns `CorpusOut(samples, count, time_range)`
2. **ComputeStyleMetrics**(CorpusOut, influencers) → returns `StyleProfile`
3. **SynthesizeVoiceGuide**(StyleProfile, influencers) → returns `VoiceProfileResponse` (validated)
   Return `VoiceProfileResponse` as the HTTP 200 payload of `POST /v1/voice/profile`.
