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
class RouteCrew:
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
            "route_agent": [],
        }

    @agent
    def route_agent(self) -> Agent:
        """Route agent."""
        tools = self._initialize_tools()["route_agent"]
        return Agent(
            config=self.agents_config["route_agent"], tools=tools, verbose=True
        )

    @task
    def route_task(self) -> Task:
        """Task for selecting a routing agent"""
        return Task(
            config=self.tasks_config["route_task"],
            expected_output="RouteAnswer",
            description="""
            You are routing the user request to the appropriate service based on the input parameters.

            Use the context provided to determine the best course of action.
            - User ID: {user_id}
            - {messages}: for the past 50 messages from the chat with user
            - {convo_summary}: the current conversation summary
            - {suggested_categories}: the suggested categories for the user
            
            IMPORTANT: Return ONLY ONE of these strings as your final answer (without quotes or any other text):
            - overview_agent
            - category_agent
            - chat_agent
            """,
        )

    @crew
    def crew(self) -> Crew:
        """Create the Voice Guide generator crew."""
        memory = _get_env_var("CREWAI_MEMORY", "false").lower() == "true"
        max_rpm = int(_get_env_var("CREWAI_MAX_RPM", "30"))

        return Crew(
            agents=[self.route_agent()],
            tasks=[self.route_task()],
            process=Process.sequential,
            memory=memory,
            max_rpm=max_rpm,
            verbose=True,
        )
