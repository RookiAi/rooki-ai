import logging
import os
from typing import Dict, Optional

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

from rooki_ai.crews.voice_profile.voice_profile import VoiceProfileCrew
from rooki_ai.models import VoiceProfileRequest, VoiceProfileResponse
from rooki_ai.utils.update_voice_config_in_supabase import (
    update_voice_config_in_supabase,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Guide API")

# In-memory store to track concurrent jobs
voice_guide_jobs = {}

# # Retry configuration
# MAX_RETRIES = int(os.environ.get("VOICE_PROFILE_MAX_RETRIES", "3"))
# RETRY_DELAY_BASE = float(os.environ.get("VOICE_PROFILE_RETRY_DELAY", "1.0"))


class VoiceProfileRequest(BaseModel):
    x_handle: str
    config: Optional[Dict[str, int]] = None


def verify_api_key(
    x_api_key: str = Header(..., description="API Key for authentication")
):
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
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


@app.post("/v1/voice/profile", response_model=VoiceProfileResponse)
async def create_voice_profile(
    request: VoiceProfileRequest,
    x_api_key: str = Header(..., description="API Key for authentication"),
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
    if (
        request.x_handle in voice_guide_jobs
        and voice_guide_jobs[request.x_handle]["status"] == "running"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another compute run is already active for {request.x_handle}",
        )

    pillar = request.config.get("pillar", 3) if request.config else 3
    guardrail = request.config.get("guardrail", 3) if request.config else 3

    try:
        # Run the crew to generate the voice guide
        # Construct inputs for the crew
        inputs = {
            "x_handle": request.x_handle,
            "pillar": pillar,
            "guardrail": guardrail,
        }

        try:
            result = VoiceProfileCrew().crew().kickoff(inputs=inputs)
            print(f"Voice guide generated for {request.x_handle}: {result}")
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Failed to generate voice profile",
                )

            import json

            if isinstance(result.raw, str):
                try:
                    result_dict = json.loads(result.raw)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract the JSON part
                    import re

                    json_match = re.search(r"({[\s\S]*})", result.raw)
                    if json_match:
                        try:
                            result_dict = json.loads(json_match.group(1))
                        except:
                            raise HTTPException(
                                status_code=500, detail="Failed to parse crew output"
                            )
                    else:
                        raise HTTPException(
                            status_code=500, detail="Failed to parse crew output"
                        )
            else:
                # If result.raw is already a dict, use it directly
                result_dict = result.raw

            positioning = result_dict.get("positioning", "N/A")
            tone = result_dict.get("tone", "N/A")
            voice_config = {
                "positioning": positioning,
                "tone": tone,
                "pillars": result_dict["pillars"],
                "guardrails": result_dict["guardrails"],
                "metrics": {
                    "post": {
                        **result_dict["post_metrics"],
                        "avg_sentence_len": result_dict["post_metrics"].get(
                            "avg_sentence_len", 15
                        ),
                        "imperative_pct": result_dict["post_metrics"].get(
                            "imperative_pct", 20
                        ),
                        "emoji_rate": result_dict["post_metrics"].get(
                            "emoji_rate", 0.05
                        ),
                    },
                    "reply": {
                        **result_dict["reply_metrics"],
                        "avg_sentence_len": result_dict["reply_metrics"].get(
                            "avg_sentence_len", 10
                        ),
                        "imperative_pct": result_dict["reply_metrics"].get(
                            "imperative_pct", 15
                        ),
                        "emoji_rate": result_dict["reply_metrics"].get(
                            "emoji_rate", 0.03
                        ),
                    },
                    "quoted": {
                        **result_dict["quoted_metrics"],
                        "avg_sentence_len": result_dict["quoted_metrics"].get(
                            "avg_sentence_len", 12
                        ),
                        "imperative_pct": result_dict["quoted_metrics"].get(
                            "imperative_pct", 18
                        ),
                        "emoji_rate": result_dict["quoted_metrics"].get(
                            "emoji_rate", 0.02
                        ),
                    },
                    "long_form": {
                        **result_dict["long_form_text_metrics"],
                        "avg_sentence_len": result_dict["long_form_text_metrics"].get(
                            "avg_sentence_len", 20
                        ),
                        "imperative_pct": result_dict["long_form_text_metrics"].get(
                            "imperative_pct", 10
                        ),
                        "emoji_rate": result_dict["long_form_text_metrics"].get(
                            "emoji_rate", 0.01
                        ),
                    },
                },
            }

            # Construct response using the parsed dictionary
            response = VoiceProfileResponse(
                positioning=result_dict["positioning"],
                tone=result_dict["tone"],
                pillars=result_dict["pillars"],
                guardrails=result_dict["guardrails"],
                post_metrics={
                    **result_dict["post_metrics"],
                    "avg_sentence_len": result_dict["post_metrics"].get(
                        "avg_sentence_len", 15
                    ),
                    "imperative_pct": result_dict["post_metrics"].get(
                        "imperative_pct", 20
                    ),
                    "emoji_rate": result_dict["post_metrics"].get("emoji_rate", 0.05),
                },
                reply_metrics={
                    **result_dict["reply_metrics"],
                    "avg_sentence_len": result_dict["reply_metrics"].get(
                        "avg_sentence_len", 10
                    ),
                    "imperative_pct": result_dict["reply_metrics"].get(
                        "imperative_pct", 15
                    ),
                    "emoji_rate": result_dict["reply_metrics"].get("emoji_rate", 0.03),
                },
                quoted_metrics={
                    **result_dict["quoted_metrics"],
                    "avg_sentence_len": result_dict["quoted_metrics"].get(
                        "avg_sentence_len", 12
                    ),
                    "imperative_pct": result_dict["quoted_metrics"].get(
                        "imperative_pct", 18
                    ),
                    "emoji_rate": result_dict["quoted_metrics"].get("emoji_rate", 0.02),
                },
                long_form_text_metrics={
                    **result_dict["long_form_text_metrics"],
                    "avg_sentence_len": result_dict["long_form_text_metrics"].get(
                        "avg_sentence_len", 20
                    ),
                    "imperative_pct": result_dict["long_form_text_metrics"].get(
                        "imperative_pct", 10
                    ),
                    "emoji_rate": result_dict["long_form_text_metrics"].get(
                        "emoji_rate", 0.01
                    ),
                },
            )

            # Update the voice config in Supabase
            update_success = update_voice_config_in_supabase(
                request.x_handle,
                result_dict["positioning"],
                result_dict["tone"],
                voice_config,
            )

            if not update_success:
                logger.warning(
                    f"Failed to update voice config in Supabase for {request.x_handle}"
                )

            return response
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    except Exception as e:
        # Handle various error types
        if "Invalid format" in str(e):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid format: {str(e)}",
            )
        elif "Invalid manifest" in str(e) or "invalid influencer" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid data: {str(e)}",
            )
        else:
            logger.error(f"Error generating voice profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}",
            )
