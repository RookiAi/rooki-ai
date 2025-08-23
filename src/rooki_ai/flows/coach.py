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
        route_with_context = {"context": crew_inputs, "route": route}
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
        """
        try:
            print(f"Executing category agent crew for user {user_id}")
            user_message = context.get("user_message", "")
            print(f"User message: {user_message}")

            # Create and execute the category crew
            crew = CategoryDraftCrew()
            result = crew.crew().kickoff(
                inputs={"user_id": user_id, "user_message": user_message}
            )

            # Handle various result types
            if result is None:
                message = "I apologize, but I couldn't generate a personalized response at this time."
            elif isinstance(result, str):
                message = result
            elif hasattr(result, "raw"):
                message = str(result.raw)
            else:
                message = str(result)

            print(f"Category agent result: {message[:100]}...")

            return StandupCoachResponse(
                message=message,
                actions=[],
                effects=[],
                keyboard=[],
                state_patch=StatePatch(focus=FocusState(kind="category")),
            )
        except Exception as e:
            print(f"Error in category agent: {str(e)}")
            # Fallback response
            return StandupCoachResponse(
                message="I understand you want a more serious tone. Rooki AI provides enterprise-ready social media monitoring for startup founders. Our platform analyzes trending topics 24/7, delivering critical alerts via Telegram and supporting email requests for comprehensive content strategy.",
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
