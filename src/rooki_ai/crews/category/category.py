import os
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from rooki_ai.models import VoiceProfileResponse
from rooki_ai.tools import (
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
        return {
            "tweet_draft_agent": [],
        }

    @agent
    def tweet_draft_agent(self) -> Agent:
        """Route agent."""
        tools = self._initialize_tools()["tweet_draft_agent"]
        return Agent(
            config=self.agents_config["tweet_draft_agent"], tools=tools, verbose=True
        )

    @task
    def draft_demo_tweet(self) -> Task:
        """Task for selecting a routing agent"""
        return Task(
            config=self.tasks_config["draft_demo_tweet"],
            expected_output="RouteAnswer",
            description="""
            You are drafting a tweet to highlight how Rooki can be every startup's social media manager.
            Use the context provided to determine the best course of action.
            - startup founders are busy people, because they are building things that people want, and have no time to manage their social media presence, they dont have time to doom scroll and reply to trending topics related to their business
            - Rooki is an AI intern that every fast moving startup must hire, Rooki learns the business's Positioning Statement and Tone Characteristics. Rooki can doom scroll for 24 hours identifying key trends and conversations to engage with.
            - every day Rooki will message you on telegram when there is something important to address to post on social media
            - you can also email Rooki if you want the intern to write a longterm tweet or change the positioning statement.
            """,
        )

    @crew
    def crew(self) -> Crew:
        """Create the Voice Guide generator crew."""
        memory = _get_env_var("CREWAI_MEMORY", "false").lower() == "true"
        max_rpm = int(_get_env_var("CREWAI_MAX_RPM", "30"))

        return Crew(
            agents=[self.tweet_draft_agent()],
            tasks=[self.draft_demo_tweet()],
            process=Process.sequential,
            memory=memory,
            max_rpm=max_rpm,
            verbose=True,
        )
