import os
import httpx
import re
import psycopg2
import asyncio
import asyncpg
from typing import Optional
from crewai.tools import BaseTool
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class SupabaseUserTweetsStorageUrlTool(BaseTool):
    """Tool for querying Supabase to get tweet storage URLs.
    
    This tool connects to a Supabase database and queries the voice table
    to find the storage_url for a given Twitter handle (x_handle).
    """
    
    name: str = "SupabaseUserTweetsStorageUrlTool"
    description: str = "Get tweet storage URL from Supabase for a Twitter handle"
    
    def _get_env_var(self, var_name, default=None):
        """Get environment variable or return default."""
        return os.environ.get(var_name, default)
        
    def _run(self, x_handle: str) -> str:
        """
        Query Supabase to get the storage_url for a given x_handle using direct PostgreSQL connection.
        
        Args:
            x_handle: The Twitter handle to look up in the voice table
            
        Returns:
            The storage URL for the given handle
            
        Raises:
            ValueError: If no record is found or if credentials are missing
            Exception: For other errors such as database connection issues
        """
        # Get PostgreSQL connection string from environment variables or use default
        db_url = self._get_env_var("DATABASE_URL")       
        print(f"Connecting to PostgreSQL database with handle: {x_handle}")
            
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            # Query the voice table for the storage_url (lowercase table name)
            query = "SELECT storage_url FROM public.\"Voice\" WHERE x_handle = %s"
            cursor.execute(query, (x_handle,))
            
            # Fetch the result
            result = cursor.fetchone()
            
            # Close the database connection
            cursor.close()
            conn.close()
            
            if not result:
                raise ValueError(f"No record found for x_handle: {x_handle}")
                
            storage_url = result[0]
            
            if not storage_url:
                raise ValueError(f"Record found for {x_handle}, but storage_url is missing")
            
            print(f"Successfully retrieved storage_url for {x_handle}")
            return storage_url
                
        except psycopg2.Error as e:
            raise Exception(f"Error connecting to PostgreSQL database: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")
    

    async def _arun(self, x_handle: str) -> str:
        """
        Asynchronously query Supabase to get the storage_url for a given x_handle using direct PostgreSQL connection.
        
        Args:
            x_handle: The Twitter handle to look up in the voice table
            
        Returns:
            The storage URL for the given handle
            
        Raises:
            ValueError: If no record is found or if credentials are missing
            Exception: For other errors such as database connection issues
        """
        # Get PostgreSQL connection string from environment variables or use default
        db_url = self._get_env_var("DATABASE_URL")       
        print(f"Connecting to PostgreSQL database asynchronously with handle: {x_handle}")
            
        try:
            # Connect to the PostgreSQL database asynchronously
            conn = await asyncpg.connect(db_url)
            
            # Query the voice table for the storage_url (lowercase table name)
            query = "SELECT storage_url FROM public.\"Voice\" WHERE x_handle = $1"
            result = await conn.fetchrow(query, x_handle)
            
            # Close the database connection
            await conn.close()
            
            if not result:
                raise ValueError(f"No record found for x_handle: {x_handle}")
                
            storage_url = result['storage_url']
            
            if not storage_url:
                raise ValueError(f"Record found for {x_handle}, but storage_url is missing")
            
            print(f"Successfully retrieved storage_url for {x_handle} (async)")
            return storage_url
                
        except asyncpg.PostgresError as e:
            raise Exception(f"Error connecting to PostgreSQL database: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")
