from .get_trending_tweets_tool import GetTrendingTweetsTool
from .json_schema_validator_tool import JSONSchemaValidatorTool
from .supabase_get_voice_tool import SuperbaseGetVoiceTool
from .supabase_user_tweets_storage_url_tool import SupabaseUserTweetsStorageUrlTool
from .tweet_history_storage_tool import TweetHistoryStorageTool

# from .jsonl_reader_tool import JSONLReaderTool
# from .text_normalize_tool import TextNormalizeTool
# from .style_metrics_tool import StyleMetricsTool
# from .influencer_metrics_tool import InfluencerMetricsTool

# Creating a mock TemplateLibraryTool as it wasn't implemented yet
# from langchain.tools import BaseTool
# class TemplateLibraryTool(BaseTool):
#     name = "TemplateLibraryTool"
#     description = "Provides template snippets for voice guide creation"

#     def _run(self, template_type: str = None):
#         """Provide template snippets for the requested template type."""
#         templates = {
#             "positioning": "For {audience} who need {need}, {brand} is the {category} that delivers {benefit}.",
#             "guardrail_do": "Use concrete examples to illustrate points.",
#             "guardrail_dont": "Avoid making price predictions or financial advice.",
#             "tweet": "Just shipped {feature}! {benefit} #buildinpublic",
#             "thread": "1/ {topic} thread 🧵\n\n{key_point_1}\n\n2/ {key_point_2}\n\n3/ {key_point_3}",
#             "reply": "Thanks for sharing! {acknowledgment}. {follow_up_question}",
#         }

#         if template_type and template_type in templates:
#             return {"template": templates[template_type]}

#         return {"templates": templates}

__all__ = [
    "TweetHistoryStorageTool",
    "SupabaseUserTweetsStorageUrlTool",
    "JSONSchemaValidatorTool",
    "GetTrendingTweetsTool",
    "SuperbaseGetVoiceTool",
    # "JSONLReaderTool",
    # "TextNormalizeTool",
    # "StyleMetricsTool",
    # "InfluencerMetricsTool",
    # "TemplateLibraryTool"
]
