from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os

from rooki_ai.tools import TweetHistoryStorageTool, SupabaseUserTweetsStorageUrlTool, JSONSchemaValidatorTool
from rooki_ai.models import VoiceGuideSuggestion
# from rooki_ai.tools import (
#     JSONLReaderTool, TextNormalizeTool,
#     StyleMetricsTool, InfluencerMetricsTool,
#     JSONSchemaValidatorTool, TemplateLibraryTool
# )

def _get_env_var(var_name, default=None):
    """Get environment variable or return default."""
    return os.environ.get(var_name, default)

@CrewBase
class VoiceProfileCrew():
    """Voice Guide Generator Crew
    
    This crew analyzes Twitter data to generate a voice guide suggestion.
    The process involves three steps:
    1. Loading and normalizing tweet data
    2. Computing style metrics
    3. Synthesizing a voice guide based on the metrics
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    def _initialize_tools(self):
        """Initialize tools for agents."""
        # supabase_url = "https://sextklfkiyceqnptxejr.supabase.co/storage/v1/object/public/tweets/1497769093964783617/tweets_1497769093964783617_2025-08-22T17-53-32-251Z.json"
        # # supabase_url = _get_env_var('SUPABASE_URL')
        # supabase_key = _get_env_var('SUPABASE_KEY')
        # supabase_bucket = _get_env_var('SUPABASE_BUCKET', 'twitter-corpus')
        
        # Tools for corpus_agent
        supabase_tool = SupabaseUserTweetsStorageUrlTool() 
        tweet_history_tool = TweetHistoryStorageTool()
        # jsonl_reader_tool = JSONLReaderTool()
        # text_normalize_tool = TextNormalizeTool()
        
        # # Tools for metrics_agent
        # style_metrics_tool = StyleMetricsTool()
        # influencer_metrics_tool = InfluencerMetricsTool()
        
        # Tools for synth_agent
        # template_library_tool = TemplateLibraryTool()
        json_schema_validator_tool = JSONSchemaValidatorTool(
            schema=VoiceGuideSuggestion.model_json_schema()
        )
        
        return {
            'corpus_agent': [supabase_tool, tweet_history_tool],
            'metrics_agent': [supabase_tool, tweet_history_tool],
            'synth_agent': [json_schema_validator_tool]
            # 'corpus_agent': [supabase_tool, jsonl_reader_tool, text_normalize_tool],
            # 'metrics_agent': [style_metrics_tool, influencer_metrics_tool],
            # 'synth_agent': [template_library_tool, json_schema_validator_tool]
        }

    @agent
    def corpus_agent(self) -> Agent:
        """Corpus loading and normalization agent."""
        tools = self._initialize_tools()['corpus_agent']
        return Agent(
            config=self.agents_config['corpus_agent'],
            tools=tools,
            verbose=True
        )

    @agent
    def metrics_agent(self) -> Agent:
        """Style metrics computation agent."""
        tools = self._initialize_tools()['metrics_agent']
        return Agent(
            config=self.agents_config['metrics_agent'],
            tools=tools,
            verbose=True
        )

    @agent
    def synth_agent(self) -> Agent:
        """Voice guide synthesis agent."""
        tools = self._initialize_tools()['synth_agent']
        return Agent(
            config=self.agents_config['synth_agent'],
            tools=tools,
            verbose=True
        )

    @task
    def load_corpus_task(self) -> Task:
        """Task for loading and normalizing the Twitter corpus."""
        return Task(
            config=self.tasks_config['load_corpus_task'],
            expected_output="CorpusOut",
            description="""
            You are analyzing the Twitter profile for user {x_handle}.
            
            First, use the SupabaseUserTweetsStorageUrlTool to fetch the storage URL for this Twitter handle:
            storage_url = SupabaseUserTweetsStorageUrlTool(x_handle="{x_handle}")
            
            Then, use the TweetHistoryStorageTool to fetch the tweet history data using that URL:
            tweet_data = TweetHistoryStorageTool(storage_url=storage_url)
            """
        )

    @task
    def compute_metrics_task(self) -> Task:
        """Task for computing style metrics from the corpus."""
        return Task(
            config=self.tasks_config['compute_metrics_task'],
            expected_output="StyleProfile",
            description="""
            You are analyzing the Twitter profile for user {x_handle}.
            
            First, use the SupabaseUserTweetsStorageUrlTool to fetch the storage URL for this Twitter handle:
            storage_url = SupabaseUserTweetsStorageUrlTool(x_handle="{x_handle}")
            
            Then, use the TweetHistoryStorageTool to fetch the tweet history data using that URL:
            tweet_data = TweetHistoryStorageTool(storage_url=storage_url)
            posts = tweet_data["posts"]
            replies = tweet_data["replies"]
            quotes = tweet_data["quotes"]
            
            Compute style metrics for the entire corpus. Additionally, compute specific ContentMetrics for each content type:
            
            1. Analyze posts to compute post_metrics with:
            - avg_sentence_len: float - Average sentence length (words per sentence)
            - imperative_pct: float - Percentage of sentences using imperative voice (0.0 to 1.0) 
            - emoji_rate: float - Rate of emoji usage per word
            
            2. Analyze replies to compute reply_metrics with the same fields.
            3. Analyze quotes to compute quoted_metrics with the same fields.
            4. Analyze tweets longer than 280 characters to compute long_form_text_metrics with the same fields.
            
            Your response should include both the StyleProfile and the separate ContentMetrics for each content type.
            Return as a JSON object with the StyleProfile fields plus these additional fields:
            - post_metrics: ContentMetrics object
            - reply_metrics: ContentMetrics object
            - quoted_metrics: ContentMetrics object  
            - long_form_text_metrics: ContentMetrics object
            """
        )

    @task
    def synthesize_voice_guide_task(self) -> Task:
        """Task for synthesizing the voice guide from style metrics."""
        return Task(
            config=self.tasks_config['synthesize_voice_guide_task'],
            expected_output="VoiceGuideSuggestion",
            description="""
            You are analyzing the Twitter profile for user {x_handle}.
            
            First, use the SupabaseUserTweetsStorageUrlTool to fetch the storage URL for this Twitter handle:
            storage_url = SupabaseUserTweetsStorageUrlTool(x_handle="{x_handle}")

            Then, use the TweetHistoryStorageTool to fetch the tweet history data using that URL:
            tweet_data = TweetHistoryStorageTool(storage_url=storage_url)
            
            Use the style profile and content metrics that were computed in the previous task.
            The compute_metrics_task result contains a StyleProfile and ContentMetrics for each content type:
            - post_metrics: ContentMetrics for posts
            - reply_metrics: ContentMetrics for replies  
            - quoted_metrics: ContentMetrics for quotes
            - long_form_text_metrics: ContentMetrics for tweets longer than 280 characters
            
            Based on these metrics, create a voice guide suggestion following these steps:
            1. Review the StyleProfile to understand the user's writing style
            2. Use the specific ContentMetrics for each content type to inform your recommendations
            
            IMPORTANT: Before finalizing your response, you MUST validate your output using:
            validation_result = JSONSchemaValidatorTool(data=your_voice_guide_suggestion)
            
            If validation_result["valid"] is False, fix the errors and validate again until it passes.
            You must create exactly {pillar} pillars and {guardrail} do guardrails and {guardrail} dont guardrails.
            
            The output must strictly follow the VoiceGuideSuggestion schema with these fields:
            - positioning: string - A positioning statement in the format "For [audience] who need [need], [brand] is the [category] that delivers [benefit]"
            - tone: string - One of: "direct", "helpful", "witty", "professional", or "educational"
            - pillars: list of PillarItem - Each with "pillar" (string) and "weighting" (number)
            - guardrails: list of GuardrailItem - Each with "type" ("do" or "dont") and "guardrail" (string)
            - post_metrics: ContentMetrics - Use the post_metrics from the previous task
            - reply_metrics: ContentMetrics - Use the reply_metrics from the previous task
            - quoted_metrics: ContentMetrics - Use the quoted_metrics from the previous task
            - long_form_text_metrics: ContentMetrics - Use the long_form_text_metrics from the previous task
            
            Do not recalculate the metrics - use the pre-computed metrics from the previous task.
        """
        )

    @crew
    def crew(self) -> Crew:
        """Create the Voice Guide generator crew."""
        memory = _get_env_var('CREWAI_MEMORY', 'false').lower() == 'true'
        max_rpm = int(_get_env_var('CREWAI_MAX_RPM', '30'))
        
        return Crew(
            agents=[self.corpus_agent(), self.metrics_agent(), self.synth_agent()],
            tasks=[self.load_corpus_task(), self.compute_metrics_task(), self.synthesize_voice_guide_task()],
            process=Process.sequential,
            memory=memory,
            max_rpm=max_rpm,
            verbose=True
        )
