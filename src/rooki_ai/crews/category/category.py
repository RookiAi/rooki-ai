import os
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from rooki_ai.models import VoiceProfileResponse
from rooki_ai.tools import (
    JSONSchemaValidatorTool,
    SupabaseUserTweetsStorageUrlTool,
    SuperbaseGetVoiceTool,
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
        """Initialize tools for agents with optimized caching."""
        # Create a single instance of the tool with caching enabled
        get_voice_tool = (
            SuperbaseGetVoiceTool()
        )  # Remove cache_timeout parameter if not supported

        # Return tools for all defined agents to avoid reference errors
        return {
            "tweet_draft_agent": [get_voice_tool],
            "tweet_refine_agent": [
                get_voice_tool
            ],  # Keep this to avoid KeyError when referenced
        }

    @agent
    def tweet_draft_agent(self) -> Agent:
        """Tweet draft agent for generating personalized tweets."""
        tools = self._initialize_tools()["tweet_draft_agent"]
        return Agent(
            config=self.agents_config["tweet_draft_agent"], tools=tools, verbose=True
        )

    @agent
    def tweet_refine_agent(self) -> Agent:
        """Refine tweet agent."""
        tools = self._initialize_tools()["tweet_refine_agent"]
        return Agent(
            config=self.agents_config["tweet_refine_agent"], tools=tools, verbose=True
        )

    @task
    def draft_demo_tweet(self) -> Task:
        """Task for generating a personalized tweet draft."""
        return Task(
            config=self.tasks_config["draft_demo_tweet"],
            expected_output="str",
            description="""
            TWEET PERSONALIZATION TASK: Create a tweet that incorporates both user's voice profile and adapts to their specific request.
            
            STEP 1: Get voice profile data
            Try to retrieve the voice profile:
            ```
            try:
                voice_profile = SuperbaseGetVoiceTool(user_id="{user_id}")
                print(f"Successfully retrieved voice profile for user: {user_id}")
            except Exception as e:
                print(f"Error retrieving voice profile: {str(e)}")
                voice_profile = {{"tone": "professional", "positioning": "tech startup"}}
            ```
            
            STEP 2: Understand user's request
            The user message is: "{user_message}"
            
            STEP 2.1: Determine the requested tone adjustment
            Analyze if the user is requesting a tone change. Common requests include:
            - More formal/serious: Use professional language, focus on business value, shorter sentences, fewer decorative elements
            - More casual/fun: Use conversational language, emphasize engagement, include relevant emojis
            - More technical: Include specific metrics, use industry terminology, focus on functionality
            - More simple: Use clear, straightforward language, avoid jargon, explain concepts simply
            
            STEP 3: Draft a tweet about Rooki that:
            - Positions Rooki as an AI social media solution for busy startup founders
            - Emphasizes 24/7 trend monitoring and important alerts via Telegram
            - Mentions ability to handle longer content requests via email
            - ADAPTS TONE based on user's message and profile

            STEP 4: STRUCTURE YOUR RESPONSE IN TWO PARTS:
            
            PART 1: Write ONE natural language sentence that directly responds to "{user_message}". 
            This should be a conversational reply as if you're speaking to the user, not an intro to the tweet.
            Examples:
            - If they asked for a serious tone: "Professional communication is essential for reaching enterprise clients."
            - If they asked about a feature: "Rooki's alert system ensures you never miss trending conversations in your industry."
            
            PART 2: On a new line, add your tweet suggestion that:
            - Matches the voice profile characteristics
            - Follows the tone requested in the user's message
            - Contains the key points about Rooki from STEP 3
            
            DO NOT use generic templates or standard marketing language.
            DO NOT use hashtags unless they're part of the user's voice profile pattern.
            DO NOT return a fixed template. Make sure your response is unique and personalized to:
            1. The user's specific voice profile retrieved from the database
            2. The specific user message: "{user_message}"
            """,
        )

    @task
    def refine_demo_tweet(self) -> Task:
        """Task for refining the tweet draft."""
        return Task(
            config=self.tasks_config["refine_demo_tweet"],
            expected_output="str",  # Changed from "RouteAnswer" to "str"
            description="""
            You are refining a tweet draft based on user feedback.
            
            The Core content will be below:
            - startup founders are busy people, because they are building things that people want, and have no time to manage their social media presence, they dont have time to doom scroll and reply to trending topics related to their business
            - Rooki is an AI intern that every fast moving startup must hire, Rooki learns the business's Positioning Statement and Tone Characteristics. Rooki can doom scroll for 24 hours identifying key trends and conversations to engage with.
            - every day Rooki will message you on telegram when there is something important to address to post on social media
            - you can also email Rooki if you want the intern to write a longterm tweet or change the positioning statement.
            
            You are refining a tweet to highlight how Rooki can be every startup's social media manager.
            
            Tune the voice with user's voice profile:
            1. First, retrieve the complete voice profile details: voice_profile = SuperbaseGetVoiceTool(user_id="{user_id}")
            2. If the voice profile contains tone information, use that tone style (formal/informal, direct/conversational)
            3. If the voice profile contains positioning information, incorporate that into your message
            4. Adapt to any specific guidance on emoji usage, sentence structure, and writing style found in the profile
            
            STRUCTURE YOUR RESPONSE IN TWO PARTS:
            
            PART 1: Write ONE natural language sentence that directly responds to "{user_message}". 
            This should be a conversational reply as if you're speaking to the user, not an intro to the tweet.
            Examples:
            - If they asked for a serious tone: "Professional communication is essential for reaching enterprise clients."
            - If they asked about a feature: "Rooki's alert system ensures you never miss trending conversations in your industry."
            
            PART 2: On a new line, add your refined tweet suggestion that:
            - Better matches the voice profile characteristics
            - More closely follows the tone requested in the user's message
            - Contains the key points about Rooki mentioned above
            
            DO NOT use generic templates or standard marketing language.
            DO NOT use hashtags unless they're part of the user's voice profile pattern.
            DO NOT return a fixed template. Make sure your response is unique and personalized to:
            1. The user's specific voice profile retrieved from the database
            2. The specific user message: "{user_message}"
            """,
        )

    @crew
    def crew(self) -> Crew:
        """Create the tweet draft crew."""
        # Use default max_rpm to avoid potential rate limit issues
        max_rpm = int(_get_env_var("CREWAI_MAX_RPM", "30"))

        try:
            # For reliability, only use the draft agent and task
            return Crew(
                agents=[self.tweet_draft_agent()],
                tasks=[self.draft_demo_tweet()],
                process=Process.sequential,
                memory=False,
                max_rpm=max_rpm,
                verbose=True,  # Enable verbose for debugging
            )
        except Exception as e:
            print(f"Error creating crew: {str(e)}")
            # Return a fallback response that includes both parts: natural language + tweet
            return "Social media management is crucial for startups in today's competitive landscape.\n\nRooki AI streamlines social media for busy startup founders by monitoring trends 24/7, sending important alerts via Telegram, and handling content creation so you can focus on building your business."
