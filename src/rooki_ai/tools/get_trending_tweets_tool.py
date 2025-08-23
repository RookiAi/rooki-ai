import json
from typing import Any, Dict, List

import httpx
from crewai.tools import BaseTool


class GetTrendingTweetsTool(BaseTool):
    """Tool for fetching trending tweets data from a provided URL.

    This tool allows agents to fetch trending tweets data from a provided URL
    and return the data in a format suitable for analysis.
    """

    name: str = "GetTrendingTweetsTool"
    description: str = "Fetch trending tweets data from a provided URL"

    def _run(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch trending tweets data from the provided URL.

        Args:
            url: URL to the JSON file containing trending tweets data

        Returns:
            List of tweet data objects

        Raises:
            Exception: If there's an error fetching or parsing the data
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()

                # Handle different response formats
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = response.json()
                else:
                    # Try to parse as JSON anyway
                    try:
                        data = response.json()
                    except json.JSONDecodeError:
                        # Try to parse as JSONL
                        lines = response.text.strip().split("\n")
                        data = [json.loads(line) for line in lines if line.strip()]

                # Normalize the response structure
                if isinstance(data, dict):
                    # If it's a single object, convert to list
                    if "tweets" in data:
                        return data["tweets"]
                    return [data]
                elif isinstance(data, list):
                    return data
                else:
                    raise ValueError(f"Unexpected data format: {type(data)}")

        except httpx.HTTPError as e:
            raise Exception(f"Error fetching trending tweets: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing trending tweets: {str(e)}")

    async def _arun(self, url: str) -> List[Dict[str, Any]]:
        """
        Asynchronously fetch trending tweets data from the provided URL.

        Args:
            url: URL to the JSON file containing trending tweets data

        Returns:
            List of tweet data objects

        Raises:
            Exception: If there's an error fetching or parsing the data
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Handle different response formats
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = response.json()
                else:
                    # Try to parse as JSON anyway
                    try:
                        data = response.json()
                    except json.JSONDecodeError:
                        # Try to parse as JSONL
                        lines = response.text.strip().split("\n")
                        data = [json.loads(line) for line in lines if line.strip()]

                # Normalize the response structure
                if isinstance(data, dict):
                    # If it's a single object, convert to list
                    if "tweets" in data:
                        return data["tweets"]
                    return [data]
                elif isinstance(data, list):
                    return data
                else:
                    raise ValueError(f"Unexpected data format: {type(data)}")

        except httpx.HTTPError as e:
            raise Exception(f"Error fetching trending tweets: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing trending tweets: {str(e)}")
