import os
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from rooki_ai.models import VoiceProfileResponse
from rooki_ai.tools import (
    GetTrendingTweetsTool,
    JSONSchemaValidatorTool,
    SupabaseUserTweetsStorageUrlTool,
    TweetHistoryStorageTool,
)


def _get_env_var(var_name, default=None):
    """Get environment variable or return default."""
    env = os.environ.get(var_name, default)
    return env


@CrewBase
class CategoryDraftCrew:
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
        get_trending_tweets_tool = GetTrendingTweetsTool()

        return {
            "category_classification_agent": [get_trending_tweets_tool],
            "top_tweets_identifier_agent": [get_trending_tweets_tool],
        }

    @agent
    def category_classification_agent(self) -> Agent:
        """Route agent."""
        tools = self._initialize_tools()["category_classification_agent"]
        return Agent(
            config=self.agents_config["category_classification_agent"],
            tools=tools,
            verbose=True,
        )

    @agent
    def top_tweets_identifier_agent(self) -> Agent:
        """Route agent."""
        tools = self._initialize_tools()["top_tweets_identifier_agent"]
        return Agent(
            config=self.agents_config["top_tweets_identifier_agent"],
            tools=tools,
            verbose=True,
        )

    @task
    def category_classification_task(self) -> Task:
        """Task for selecting a routing agent"""
        return Task(
            config=self.tasks_config["category_classification_task"],
            expected_output="RouteAnswer",
            description="""
            Use the GetTrendingTweetsTool to fetch the tweet history data using that URL:
            url = "https://raw.githubusercontent.com/RookiAi/rooki-app/refs/heads/main/public/tweets/Ycombinator.json"
            tweet_data = GetTrendingTweetsTool(url=url)

            You are classifying trending tweets into categories based on their content.
            """,
        )

    @task
    def identify_top_tweet_task(self) -> Task:
        """Task for selecting a routing agent"""
        return Task(
            config=self.tasks_config["identify_top_tweet_task"],
            expected_output="RouteAnswer",
            description="""
            Use the GetTrendingTweetsTool to fetch the tweet history data using that URL:
            url = "https://raw.githubusercontent.com/RookiAi/rooki-app/refs/heads/main/public/tweets/Ycombinator.json"
            tweet_data = GetTrendingTweetsTool(url=url)

            You are identifying the top tweets from a list of trending tweets.
            """,
        )

    @crew
    def crew(self) -> Crew:
        """Create the Voice Guide generator crew."""
        memory = _get_env_var("CREWAI_MEMORY", "false").lower() == "true"
        max_rpm = int(_get_env_var("CREWAI_MAX_RPM", "30"))

        return Crew(
            agents=[
                self.category_classification_agent(),
                self.top_tweets_identifier_agent(),
            ],
            tasks=[self.category_classification_task(), self.identify_top_tweet_task()],
            process=Process.sequential,
            memory=memory,
            max_rpm=max_rpm,
            verbose=True,
        )
