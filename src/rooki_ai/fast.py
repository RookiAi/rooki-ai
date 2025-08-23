import os
import logging
from typing import Dict, Optional, Any

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

from rooki_ai.main import run
from rooki_ai.models import VoiceProfileRequest, VoiceProfileResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Guide API")

# In-memory store to track concurrent jobs
voice_guide_jobs = {}

class VoiceProfileRequest(BaseModel):
    x_handle: str
    config: Optional[Dict[str, int]] = None

def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")):
    """
    Verify the API key provided in the request header.
    
    Args:
        x_api_key: API key from the X-API-Key header
        
    Returns:
        str: The verified API key
        
    Raises:
        HTTPException: If the API key is missing or invalid
    """
    api_key = os.environ.get("FASTAPI_SERVER_KEY", "test-api-key")
    if not x_api_key or x_api_key != api_key:
        logger.warning(f"Invalid API key attempt: {x_api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    return x_api_key

@app.post("/v1/voice/profile", response_model=VoiceProfileResponse)
async def create_voice_profile(
    request: VoiceProfileRequest,
    x_api_key: str = Header(..., description="API Key for authentication")
):
    """
    Create a voice profile for a Twitter handle.
    
    Args:
        request: Voice profile request with Twitter handle and optional config
        x_api_key: API key for authentication
        
    Returns:
        VoiceProfileResponse: The generated voice profile
        
    Raises:
        HTTPException: If there's an error creating the voice profile
    """
    # Verify API key
    verify_api_key(x_api_key)
    
    # Check for concurrent runs
    if request.x_handle in voice_guide_jobs and voice_guide_jobs[request.x_handle]["status"] == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another compute run is already active for {request.x_handle}"
        )
    
    try:
        # Run the crew to generate the voice guide
        result = run(x_handle=request.x_handle, config=request.config)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Failed to generate voice profile"
            )
        
        return result
    
    except Exception as e:
        # Handle various error types
        if "Invalid format" in str(e):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid format: {str(e)}"
            )
        elif "Invalid manifest" in str(e) or "invalid influencer" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid data: {str(e)}"
            )
        else:
            logger.error(f"Error generating voice profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )