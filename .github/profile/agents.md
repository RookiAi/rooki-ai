### Agent

1. **CorpusAgent**
   - Goal: Fetch & normalize tweets from Supabase manifest; output cleaned text samples + stats.
   - LLM: small/fast, `temperature=0.0` (used minimally for light classification if needed).
   - Tools: `SupabaseStorageTool`, `JSONLReaderTool`, `TextNormalizeTool`.
2. **MetricsAgent**
   - Goal: Compute style metrics from samples; optionally enrich with **influencer metrics**; output a **StyleProfile** vector.
   - LLM: not required (pure Python metric tool), or `temperature=0.0` for any heuristic labeling.
   - Tools: `StyleMetricsTool`, `InfluencerMetricsTool` (optional, reads cached metrics file/table).
3. **SynthAgent**
   - Goal: Generate the final **VoiceProfileResponse** (positioning, tone, pillars+weights, guardrails, templates) using the StyleProfile and influencers. Must produce schema-valid JSON only.
   - LLM: flagship (low temp `0.1`), JSON mode or tool-enforced schema.
   - Tools: `JSONSchemaValidatorTool`, `TemplateLibraryTool` (optional prompt snippets).
