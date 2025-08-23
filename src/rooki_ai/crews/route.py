from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os

from rooki_ai.tools import TweetHistoryStorageTool, SupabaseUserTweetsStorageUrlTool, JSONSchemaValidatorTool
from rooki_ai.models import VoiceProfileResponse

def _get_env_var(var_name, default=None):
    """Get environment variable or return default."""
    env = os.environ.get(var_name, default)
    return env

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
        # Tools for corpus_agent
        supabase_tool = SupabaseUserTweetsStorageUrlTool() 
        tweet_history_tool = TweetHistoryStorageTool()

        json_schema_validator_tool = JSONSchemaValidatorTool(
            schema=VoiceProfileResponse.model_json_schema()
        )
        
        return {
            'corpus_agent': [supabase_tool, tweet_history_tool],
            'metrics_agent': [],
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
    def fetch_data_task(self) -> Task:
        """Task for fetching data from Supabase."""
        return Task(
            config=self.tasks_config['fetch_data_task'],
            expected_output="TweetDataOut",
            description="""
            You are retrieving Twitter data for user {x_handle}.
            
            Your task is to fetch the tweet data from Supabase:
            
            1. Use the SupabaseUserTweetsStorageUrlTool to fetch the storage URL for this Twitter handle:
               storage_url = SupabaseUserTweetsStorageUrlTool(x_handle="{x_handle}")
            
            2. Then, use the TweetHistoryStorageTool to fetch the tweet history data using that URL:
               tweet_data = TweetHistoryStorageTool(storage_url=storage_url)
            
            3. Return the full tweet_data object containing:
               - posts: Array of tweet objects
               - replies: Array of reply tweet objects
               - quotes: Array of quote tweet objects
               
            Your response should be the complete tweet_data object, preserving all original data.
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
            
            Use the tweet_data that were computed in the previous task.
            """
        )

    @crew
    def crew(self) -> Crew:
        """Create the Voice Guide generator crew."""
        memory = _get_env_var('CREWAI_MEMORY', 'false').lower() == 'true'
        max_rpm = int(_get_env_var('CREWAI_MAX_RPM', '30'))
        
        return Crew(
            agents=[self.corpus_agent(), self.metrics_agent(), self.synth_agent()],
            tasks=[self.fetch_data_task(), self.load_corpus_task(), self.compute_metrics_task(), self.compute_voices_task(), self.synthesize_voice_guide_task()],
            process=Process.sequential,
            memory=memory,
            max_rpm=max_rpm,
            verbose=True
        )
