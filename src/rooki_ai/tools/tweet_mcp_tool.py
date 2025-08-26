"""
Tool for generating tweets using the Tweet MCP server.
"""

import asyncio
import os
from typing import Annotated, Optional

from crewai.tools import BaseTool
from dedalus_labs import AsyncDedalus, DedalusRunner
from pydantic import BaseModel, Field


class TweetMCPToolSchema(BaseModel):
    """Schema for TweetMCPTool arguments"""

    input_prompt: str = Field(description="The input prompt to send to the MCP server")
    mcp_server: Optional[str] = Field(
        default=None, description="Optional custom MCP server to use"
    )


class TweetMCPTool(BaseTool):
    """
    Tool for generating tweets using the Tweet MCP server.

    This tool takes an input prompt and sends it to a Tweet MCP server,
    returning the generated response.
    """

    name: str = "TweetMCPTool"
    description: str = "Generate tweets using the Tweet MCP server"
    default_mcp_server: str = (
        "hinsonsidan/tweet-mcp"  # Renamed to avoid conflict with parameter name
    )
    model: str = "openai/gpt-4o-mini"
    args_schema: Annotated[type[TweetMCPToolSchema], Field()] = TweetMCPToolSchema

    def _run(self, input_prompt: str, mcp_server: Optional[str] = None) -> str:
        """
        Generate a tweet using the Tweet MCP server.

        Args:
            input_prompt: The input prompt to send to the MCP server
            mcp_server: Optional custom MCP server to use, defaults to hinsonsidan/tweet-mcp

        Returns:
            str: The generated tweet

        Raises:
            Exception: If there's an error generating the tweet
        """
        # Use the provided MCP server if available, otherwise use the default
        server = mcp_server if mcp_server is not None else self.default_mcp_server

        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                is_running_loop = True
            except RuntimeError:
                is_running_loop = False

            # If we're already in an event loop, use it
            if is_running_loop:
                # Create a new thread to run the async code without blocking the main thread
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.new_event_loop().run_until_complete(
                            self._async_generate_tweet(input_prompt, server)
                        )
                    )
                    return future.result()
            else:
                # No event loop running, we can create one
                return asyncio.run(self._async_generate_tweet(input_prompt, server))
        except Exception as e:
            raise Exception(f"Error generating tweet: {str(e)}")

    async def _async_generate_tweet(self, input_prompt: str, mcp_server: str) -> str:
        """Internal async helper to generate tweet."""
        client = AsyncDedalus()
        runner = DedalusRunner(client)

        try:
            response = await runner.run(
                input=input_prompt,
                model=self.model,
                mcp_servers=[mcp_server],
            )

            return response.final_output
        except Exception as e:
            raise Exception(f"Error from MCP server: {str(e)}")

    async def _arun(self, input_prompt: str, mcp_server: Optional[str] = None) -> str:
        """
        Asynchronously generate a tweet using the Tweet MCP server.

        Args:
            input_prompt: The input prompt to send to the MCP server
            mcp_server: Optional custom MCP server to use, defaults to hinsonsidan/tweet-mcp

        Returns:
            str: The generated tweet

        Raises:
            Exception: If there's an error generating the tweet
        """
        # Use the provided MCP server if available, otherwise use the default
        server = mcp_server if mcp_server is not None else self.default_mcp_server

        try:
            # Handle case where the agent might already be running in an async context
            result = await self._async_generate_tweet(input_prompt, server)
            return result
        except Exception as e:
            print(f"Error in _arun: {str(e)}")
            raise Exception(f"Error generating tweet: {str(e)}")
