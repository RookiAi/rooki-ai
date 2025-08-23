import asyncio
import os
import re
from typing import Optional

import asyncpg
import httpx
import psycopg2
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()


class SuperbaseGetVoiceTool(BaseTool):
    """Tool for querying Supabase to get user's voice.

    This tool connects to a Supabase database and queries the voice table
    to find the storage_url for a given user_id.
    """

    name: str = "SuperbaseGetVoiceTool"
    description: str = "Get user's voice storage URL from Supabase for a user_id"

    def _get_env_var(self, var_name, default=None):
        """Get environment variable or return default."""
        return os.environ.get(var_name, default)

    def _run(self, user_id: str) -> str:
        """
        Query Supabase to get the storage_url for a given userId using asyncpg.
        Args:
            user_id: The user_id to look up in the voice table
        Returns:
            The voice profile for the given user_id
        Raises:
            ValueError: If no record is found or if credentials are missing
            Exception: For other errors such as database connection issues
        """
        # Get PostgreSQL connection string from environment variables or use default
        db_url = self._get_env_var("DATABASE_URL")

        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()

            # Query the voice table for the storage_url (lowercase table name)
            query = 'SELECT * FROM public."Voice" WHERE "userId" = %s'
            cursor.execute(query, (user_id,))

            # Fetch the result
            result = cursor.fetchone()

            # Close the database connection
            cursor.close()
            conn.close()

            return result

        except psycopg2.Error as e:
            raise Exception(f"Error connecting to PostgreSQL database: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    async def _arun(self, user_id: str) -> str:
        """
        Query Supabase to get the storage_url for a given user_id using asyncpg.
        Args:
            user_id: The user_id to look up in the voice table
        Returns:
            The voice profile for the given user_id
        Raises:
            ValueError: If no record is found or if credentials are missing
            Exception: For other errors such as database connection issues
        """

        # Get PostgreSQL connection string from environment variables or use default
        db_url = self._get_env_var("DATABASE_URL")
        print(
            f"Connecting to PostgreSQL database asynchronously with user_id: {user_id}"
        )

        try:
            # Connect to the PostgreSQL database asynchronously
            conn = await asyncpg.connect(db_url)

            # Query the voice table for the storage_url (lowercase table name)
            query = 'SELECT * FROM public."Voice" WHERE "userId" = $1'
            result = await conn.fetchrow(query, user_id)

            # Close the database connection
            await conn.close()

            if not result:
                raise ValueError(f"No record found for user_id: {user_id}")

            print(f"Successfully retrieved voice profile for {user_id} (async)")
            return result

        except asyncpg.PostgresError as e:
            raise Exception(f"Error connecting to PostgreSQL database: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")
