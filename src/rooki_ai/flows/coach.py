from typing import Any, Dict, List, Optional

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from litellm import completion
from pydantic import BaseModel, Field

from rooki_ai.crews import RouteCrew
from rooki_ai.crews.category.category import CategoryDraftCrew
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
        # route = RouteCrew().crew().kickoff(inputs=crew_inputs)
        route = "category_agent"  # Temporary hardcoded route for testing
        print(f"Selected route: {route}")

        # Return both the context and the route string
        route_with_context = {"context": chat_background, "route": route}
        return route_with_context

    @listen(identify_route)
    def reply(self, route_with_context):
        route_obj = route_with_context["route"]
        context = route_with_context["context"]
        user_id = getattr(self.state, "user_id", None)

        print(f"Selected agent: {route_obj}")

        # Debug the exact value and type of route_obj
        print(f"Selected agent: '{route_obj}' (type: {type(route_obj)})")

        # Strip whitespace and normalize to handle potential format issues
        if hasattr(route_obj, "raw"):
            route = str(route_obj.raw).strip().lower()
        else:
            route = str(route_obj).strip().lower()

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
        message = (
            CategoryDraftCrew().crew().kickoff(inputs={"user_id": user_id, **context})
        )

        return StandupCoachResponse(
            message=str(message),
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

        # Execute LLM call for chat response
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an marketing intern talking to your manager about your work.",
                },
                {
                    "role": "user",
                    "content": f"Provide a comprehensive overview based on this context: {context}. Reply in conversational tone (no programming details about context). Keep answer short and precise",
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

        # Execute LLM call for overview response
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an marketing intern talking to your manager about your work.",
                },
                {
                    "role": "user",
                    "content": f"Provide a comprehensive overview based on this context: {context}. Reply in conversational tone (no programming details about context). Keep answer short and precise",
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
