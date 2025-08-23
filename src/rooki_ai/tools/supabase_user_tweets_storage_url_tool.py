import os
import httpx
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
    
    supabase_url: Optional[str] = Field(
        default=None, 
        description="Supabase URL (falls back to SUPABASE_URL env var)"
    )
    supabase_key: Optional[str] = Field(
        default=None,
        description="Supabase API key (falls back to SUPABASE_KEY env var)"
    )
    
    def _get_env_var(self, var_name, default=None):
        """Get environment variable or return default."""
        return os.environ.get(var_name, default)
        
    def _run(self, x_handle: str) -> str:
        """
        Query Supabase to get the storage_url for a given x_handle.
        
        Args:
            x_handle: The Twitter handle to look up in the voice table
            
        Returns:
            The storage URL for the given handle
            
        Raises:
            ValueError: If no record is found or if credentials are missing
            Exception: For other errors such as HTTP issues
        """
        # Get credentials from instance or environment variables in this priority:
        # 1. Instance variables (if provided during initialization)
        # 2. Environment variables with standard names
        # 3. Environment variables with alternative names (for DATABASE_URL)
        url = self.supabase_url or self._get_env_var("SUPABASE_URL") or self._get_env_var("DATABASE_URL")
        key = self.supabase_key or self._get_env_var("SUPABASE_KEY") or self._get_env_var("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url:
            raise ValueError("Supabase URL not provided. Set SUPABASE_URL or DATABASE_URL environment variable.")
        
        if not key:
            raise ValueError("Supabase API key not provided. Set SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY environment variable.")
        
        # Construct the API endpoint for the voice table
        api_endpoint = f"{url}/rest/v1/voice"
        
        # Set up headers for Supabase API
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        # Query parameters to filter by x_handle
        params = {
            "select": "storage_url",
            "x_handle": f"eq.{x_handle}"
        }
        
        try:
            # Make the request to Supabase
            with httpx.Client() as client:
                response = client.get(api_endpoint, headers=headers, params=params)
                response.raise_for_status()
                
                # Parse the JSON response
                data = response.json()
                
                if not data:
                    raise ValueError(f"No record found for x_handle: {x_handle}")
                
                # Extract the storage_url from the first result
                storage_url = data[0].get("storage_url")
                
                if not storage_url:
                    raise ValueError(f"Record found for {x_handle}, but storage_url is missing")
                
                return storage_url
                
        except httpx.HTTPError as e:
            raise Exception(f"Error querying Supabase: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")
    
    async def _arun(self, x_handle: str) -> str:
        """
        Asynchronously query Supabase to get the storage_url for a given x_handle.
        
        Args:
            x_handle: The Twitter handle to look up in the voice table
            
        Returns:
            The storage URL for the given handle
        """
        # Get credentials from instance or environment variables in this priority:
        # 1. Instance variables (if provided during initialization)
        # 2. Environment variables with standard names
        # 3. Environment variables with alternative names (for DATABASE_URL)
        url = self.supabase_url or self._get_env_var("SUPABASE_URL") or self._get_env_var("DATABASE_URL")
        key = self.supabase_key or self._get_env_var("SUPABASE_KEY") or self._get_env_var("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url:
            raise ValueError("Supabase URL not provided. Set SUPABASE_URL or DATABASE_URL environment variable.")
        
        if not key:
            raise ValueError("Supabase API key not provided. Set SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY environment variable.")
        
        # Construct the API endpoint for the voice table
        api_endpoint = f"{url}/rest/v1/voice"
        
        # Set up headers for Supabase API
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        # Query parameters to filter by x_handle
        params = {
            "select": "storage_url",
            "x_handle": f"eq.{x_handle}"
        }
        
        try:
            # Make the request to Supabase
            async with httpx.AsyncClient() as client:
                response = await client.get(api_endpoint, headers=headers, params=params)
                response.raise_for_status()
                
                # Parse the JSON response
                data = response.json()
                
                if not data:
                    raise ValueError(f"No record found for x_handle: {x_handle}")
                
                # Extract the storage_url from the first result
                storage_url = data[0].get("storage_url")
                
                if not storage_url:
                    raise ValueError(f"Record found for {x_handle}, but storage_url is missing")
                
                return storage_url
                
        except httpx.HTTPError as e:
            raise Exception(f"Error querying Supabase: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")
