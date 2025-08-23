from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from litellm import completion
from pydantic import BaseModel, Field

from rooki_ai.crews import RouteCrew
from rooki_ai.models.api import StandupCoachResponse
from rooki_ai.utils.get_chat_background import get_chat_background

load_dotenv()


class CoachState(BaseModel):
    user_id: str | None = None


class CoachFlow(Flow[CoachState]):
    model = "gpt-4o-mini"

    @start()
    def identify_route(self):
        print("Starting flow")

        # works with typed state
        flow_id = getattr(self.state, "id", None)
        print(f"Flow State ID: {flow_id}")

        # inputs passed to kickoff(...) are merged into state
        user_id = getattr(self.state, "user_id", None)
        print(f"Using user_id: {user_id}")

        chat_background = get_chat_background(user_id)
        print(f"Chat background: {chat_background}")

        # Include user_id in the inputs passed to RouteCrew
        crew_inputs = {"user_id": user_id, **chat_background}
        route = RouteCrew().crew().kickoff(inputs=crew_inputs)
        route_with_context = {"context": chat_background, "route": route}

        return route_with_context

    # @listen(generate_city)
    # def generate_fun_fact(self, random_city):
    #     response = completion(
    #         model=self.model,
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": f"Tell me a fun fact about {random_city}",
    #             },
    #         ],
    #     )

    #     fun_fact = response["choices"][0]["message"]["content"]
    #     # Store the fun fact in our state
    #     self.state["fun_fact"] = fun_fact
    #     return fun_fact

    @listen(identify_route)
    def reply(self, route_with_context):
        route = route_with_context["route"]
        context = route_with_context["context"]

        response = StandupCoachResponse(message=route)
        return response
