import asyncio

from dedalus_labs import AsyncDedalus, DedalusRunner
from dedalus_labs.utils.streaming import stream_async
from dotenv import load_dotenv

load_dotenv()


async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    response = await runner.run(
        input="Startup founder",
        model="openai/gpt-4o-mini",
        mcp_servers=["hinsonsidan/tweet-mcp"],
    )

    print(response.final_output)


if __name__ == "__main__":
    asyncio.run(main())
