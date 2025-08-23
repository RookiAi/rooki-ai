| Method | Path                     | Summary                                         | Auth   |
| ------ | ------------------------ | ----------------------------------------------- | ------ |
| POST   | **/v1/standup/prep**     | Build daily research pack & drafts (sync/async) | Bearer |
| POST   | **/v1/standup/coach**    | Chat with context; route suggestions            | Bearer |
| GET    | **/v1/standup/overview** | Read-only daily/weekly status + drafts          | Bearer |
| POST   | **/v1/drafts/generate**  | Generate or iterate a draft                     | Bearer |

[Report formation process](https://www.notion.so/Report-formation-process-257c299fe9af80fa9435c01bcc18cb11?pvs=21)

# POST /v1/standup/prep

**Summary:** Prepares the day’s report for a given voice profile:

1. Rank **user’s own trending tweets** and classify into **7 categories** (provided).
2. Pull **global trending on X**, cluster into **10 categories** (provided) and pick **3 interesting topics** (auto or provided).
3. For each category, **draft an original post**.
4. For each category, **select 7 top-profile tweets** and **draft replies**.
5. For each category, **select 3 tweets with a clear angle** and **draft quote-retweets**.

**Auth:** `FASTAPI_SERVER_KEY` from env

**Idempotency:** Supported via `Idempotency-Key` header (per UVP+date)

### Headers

- `Idempotency-Key`? (string) — dedupe repeated runs for the same day.

### Request (application/json)

```json
{
  "user_voice_profile_id": "UVP_123",
  "date": "2025-08-22",
  "sources": {
    "user_trending_url": "the supabase storage url",
    "global_trending": "the supabase storage url"
  },
  "selection": {
    "reply_per_category": 7,
    "quote_per_category": 3,
    "top_profile_weights": {
      // explicit, deterministic ranking
      "followers": 0.6,
      "engagement_rate": 0.4
    }
  }
}
```

**200 OK (sync mode or when job completes)**

```json
{
  "prep_id": "PRP_20250822_001",
  "status": "completed",
  "date": "2025-08-22",
  "user_voice_profile_id": "UVP_123",
  "user_trending": {
    "categories": [
      {
        "label": "Governance",
        "summary": "Your governance threads drove the highest replies...",
        "items": [
          {
            "tweet_id": "1958...1337",
            "url": "https://x.com/.../status/1958...1337",
            "metrics": {
              "likes": 120,
              "reposts": 35,
              "replies": 28,
              "eng_rate": 0.042
            }
          }
        ],
        "original_post": {
          "text": "DReps thrive when KPIs are explicit. This week I’m testing a 3-metric dashboard—want in?",
          "meta": { "chars": 117 }
        },
        "reply_candidates": [
          /* up to 7 items with drafted replies */
        ],
        "quote_candidates": [
          /* up to 3 items with drafted quotes */
        ]
      }
      // ... 6 more categories
    ]
  },
  "global_trending": {
    "categories": [
      /* 10 labeled clusters with summaries */
    ],
    "interesting": ["Hydra L2", "Stablecoin HK", "Governance KPIs"]
  },
  "notes": [
    "Top profiles ranked by followers(0.6)+7d engagement_rate(0.4).",
    "All drafts ≤ 280 chars; mentions disabled per request."
  ]
}
```

### Errors (common)

- `400 invalid_request` — counts do not match (e.g., not exactly 7 user categories or 10 global categories).
- `401 unauthorized` — bearer missing/invalid.
- `403 x_context_missing` — BFF token reference not found/expired.
- `409 already_prepared` — idempotent collision for same UVP+date+key.
- `422 validation_error` — bad weights, negative limits, etc.
- `429 rate_limited` — exceeded daily prep limit.
- `500/502/503` — upstream X API or drafting engine failures.

## **POST /v1/standup/coach**

**Summary:** Single chat entrance for Telegram (or any chat). Detects intent and either answers normally or routes internally to overview/drafting; returns a conversational message plus structured actions.

**Auth:** Bearer • **Rate limit:** 30/min per user • **Idempotency:** Yes - dedupe by `chat.message_id`

**Request (application/json):**

```json
{
  "user_voice_profile_id": "VOI_123",
  "chat": {
    "platform": "telegram",
    "chat_id": "123456",
    "message_id": "789012",
    "text": "make it punchier and add a KPI",
    "callback": null
  },
  "date": "2025-08-22"
}
```

**200 OK:**

```json
{
  "message": "Tightened the draft and framed a KPI angle. Want another pass or publish?",
  "actions": [
    { "kind": "iterate", "draft_id": "dr_003" },
    { "kind": "overview", "voice_id": "VOI_123" }
  ],
  "effects": [
    {
      "type": "generated_draft",
      "draft": {
        "draft_id": "dr_003",
        "text": "DReps juggle proposal volume, time, and comms. Track KPIs, ship faster. #Cardano",
        "meta": { "chars": 128, "platform_max": 280 }
      },
      "source": { "draft_id": "dr_001" }
    }
  ],
  "keyboard": [
    { "label": "↺ Iterate", "callback_data": "iterate:dr_003" },
    { "label": "🗓 Overview", "callback_data": "overview" },
    { "label": "✅ Publish", "callback_data": "publish:dr_003" }
  ],
  "state_patch": { "focus": { "kind": "draft", "draft_id": "dr_003" } }
}
```

**Notes:**

- May internally call **/v1/standup/overview** or **/v1/drafts/generate**, but remains the single public chat entry.
- Responses can include suggestions aligned to “Standup” user stories (iterate, reminders, post handoff).

## GET /v1/standup/overview

**Summary:** Read-only snapshot for today (or a given date): drafts + daily/weekly target status for the voice profile.

**Auth:** Bearer • **Rate limit:** 60/min per user • **Idempotency:** N/A (read).

**Path params:** _none_

**Query params:**

- `user_voice_profile_id` (string, required) — the voice profile to summarize.
- `date`? (ISO date, default=today) — day to summarize.

**Headers:** _none_

**200 OK:**

```json
{
  "date": "2025-08-22",
  "user_voice_profile_id": "VOI_123",
  "targets": {
    "daily": {
      "original_update_count": 0,
      "reply_count": 1,
      "niche_reply_count": 0
    },
    "weekly": { "long_form_count": 1 }
  },
  "today_drafts": [
    { "draft_id": "dr_041", "type": "post", "text": "..." },
    {
      "draft_id": "dr_039",
      "type": "reply",
      "target_tweet_id": "1958...9337",
      "text": "..."
    }
  ]
}
```

**Notes:**

- Target shapes mirror your `DailyTarget` and `WeeklyTarget` models (read-only here).
- Designed to support “Get target progress” and “Get all suggestions” user stories.

**Errors:** see standard table.

## POST /v1/drafts/generate

**Summary:** Generate a new tweet (post/reply/quote/thread) or **redraft** an existing draft using the current text and an extra user prompt, in the style referenced by `voice_id`.

**Auth:** `FASTAPI_SERVER_KEY` from env

**Request (application/json)**

```json
{
  "type": "post", // "post" | "reply" | "quote" | "thread"
  "target_tweet_id": null, // required for "reply" or "quote"
  "user_voice_profile": "uuid", // voice to use (see Notes on resolution)
  // REDRAFT mode when either 'source' or 'user_prompt' is present:
  "source": {
    "draft_id": "dr_001",
    "body": "Current draft text here...",
    "context": {
      // optional (reply/quote/thread continuity)
      "in_reply_to_id": null,
      "quote_tweet_id": null,
      "media": []
    }
  },
  "user_prompt": "Make it punchier, reference #Cardano governance."
}
```

**Field rules & validation**

- `type` ∈ {`post`,`reply`,`quote`,`thread`}.
- If `type` ∈ {`reply`,`quote`} ⇒ `target_tweet_id` is **required** (422 if missing).
- `voice_id` must be a valid UUID referring to a **voice** (and its associations like pillars/guardrails/templates). **404** if not found; **403** if caller not authorized to use this voice.
- **Mode selection:**
  - **Generate** when both `source` and `user_prompt` are **absent**.
  - **Redraft** when either `source` **or** `user_prompt` is present; if both present, rewrite `source.body` guided by `user_prompt`.
- Optional length/style guards (if you later add `constraints`) should be enforced **post-generation** (trim at sentence boundaries where possible). (Template allows such constraint notes.)

**200 OK**

```json
{
  "draft": {
    "draft_id": "dr_002",
    "type": "post",
    "text": "Governance moves when KPIs are clear. Keep it measurable. #Cardano",
    "meta": {
      "chars": 96,
      "platform_max": 280,
      "policy_safe": true,
      "pillar_fit": { "education": 0.9, "governance": 0.8 }
    }
  },
  "notes": [
    "Kept within 280 chars.",
    "Aligned to voice pillars and guardrails."
  ]
}
```

(Example response style aligned with prior FastAPI drafts/generate section.)

**Errors**

- **400 — Bad Request:** malformed JSON / invalid enum combination.
- **401 — Unauthorized / 403 — Forbidden:** bad/insufficient credentials.
- **404 — Not Found:** `user_voice_profile` does not exist/accessible.
- **415 — Unsupported Media Type:** missing `application/json`.
- **422 — Unprocessable Entity:** semantic validation errors (e.g., missing `target_tweet_id` for replies/quotes).
- **5xx — Server/Upstream errors:** model/tool transient failures.
