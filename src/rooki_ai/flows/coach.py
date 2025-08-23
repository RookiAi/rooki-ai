from typing import Any, Dict, List, Optional

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from litellm import completion
from pydantic import BaseModel, Field

from rooki_ai.crews import RouteCrew
from rooki_ai.models.api import FocusState, StandupCoachResponse, StatePatch
from rooki_ai.utils.get_chat_background import get_chat_background

load_dotenv()


class CoachState(BaseModel):
    user_id: str | None = None
    user_message: str | None = None


class CoachFlow(Flow[CoachState]):
    model = "gpt-4o-mini"

    @start()
    def identify_route(self):
        print("Starting flow")
        # Debug the entire state to see what's available
        print(f"Full state: {vars(self.state)}")

        # inputs passed to kickoff(...) are merged into state
        user_id = getattr(self.state, "user_id", None)
        user_message = getattr(self.state, "user_message", None)
        print(f"User ID: {user_id}, User Message: {user_message}")

        chat_background = get_chat_background(user_id)

        # Include user_id and user_message in the inputs passed to RouteCrew
        crew_inputs = {
            "user_id": user_id,
            # Default to an empty string if user_message is None
            "user_message": user_message if user_message is not None else "",
            **chat_background,
        }

        # Debug what's being passed to RouteCrew
        print(f"Passing to RouteCrew: {crew_inputs}")

        # The route is now directly a string like "overview_agent", "category_agent", or "chat_agent"
        route = RouteCrew().crew().kickoff(inputs=crew_inputs)
        print(f"Selected route: {route}")

        # Return both the context and the route string
        route_with_context = {"context": chat_background, "route": route}
        return route_with_context

    @listen(identify_route)
    def reply(self, route_with_context):
        route = route_with_context["route"]
        context = route_with_context["context"]
        user_id = getattr(self.state, "user_id", None)

        print(f"Selected agent: {route}")

        if route == "category_agent":
            return self._handle_category_agent(context, user_id)
        elif route == "chat_agent":
            return self._handle_chat_agent(context, user_id)
        elif route == "overview_agent":
            return self._handle_overview_agent(context, user_id)
        else:
            # Fallback for unexpected route values
            return StandupCoachResponse(
                message=f"Unrecognized route: {route}",
                actions=[],
                effects=[],
                keyboard=[],
            )

    def _handle_category_agent(self, context, user_id):
        """
        Handle category-specific content execution via a crew.
        This will eventually be replaced with a proper crew implementation.
        """
        print(f"Executing category agent crew for user {user_id}")

        # Placeholder for crew execution - to be implemented later
        # Example: CategoryCrew().crew().kickoff(inputs={"user_id": user_id, **context})

        return StandupCoachResponse(
            message="I'll help you work with this category. (Placeholder for category crew execution)",
            actions=[],
            effects=[],
            keyboard=[],
            state_patch=StatePatch(focus=FocusState(kind="category")),
        )

    def _handle_chat_agent(self, context, user_id):
        """
        Handle general chat interactions via a direct LLM call.
        """
        print(f"Executing chat agent LLM for user {user_id}")

        # Try to get user_message from state first
        user_message = getattr(self.state, "user_message", None)

        # If not available in state, extract from context
        if not user_message:
            user_message = "How can I help you today?"
            if context and "messages" in context and context["messages"]:
                user_message = context["messages"][-1].get("content", user_message)
            if context and "user_message" in context:
                user_message = context["user_message"]

        recent_message = user_message

        # Execute LLM call for chat response
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant responding to a general query.",
                },
                {
                    "role": "user",
                    "content": recent_message,
                },
            ],
        )

        chat_response = response["choices"][0]["message"]["content"]

        return StandupCoachResponse(
            message=chat_response,
            actions=[],
            effects=[],
            keyboard=[],
            state_patch=StatePatch(focus=FocusState(kind="chat")),
        )

    def _handle_overview_agent(self, context, user_id):
        """
        Handle overview requests via a direct LLM call with summary-oriented prompting.
        """
        print(f"Executing overview agent LLM for user {user_id}")

        # Generate a comprehensive summary based on context
        summary_context = "your conversation history"
        if context and "convo_summary" in context:
            summary_context = context["convo_summary"]

        # Execute LLM call for overview response
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that provides clear summaries and overviews.",
                },
                {
                    "role": "user",
                    "content": f"Provide a comprehensive overview based on this context: {summary_context}",
                },
            ],
        )

        overview_response = response["choices"][0]["message"]["content"]

        return StandupCoachResponse(
            message=overview_response,
            actions=[],
            effects=[],
            keyboard=[],
            state_patch=StatePatch(focus=FocusState(kind="overview")),
        )
