#!/usr/bin/env python
import sys
import warnings

from rooki_ai.crews import VoiceProfileCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(x_handle: str = "jinglescode"):
    """
    Run the voice profile crew.
    
    Args:
        x_handle: Twitter handle to analyze
        config: Optional configuration dict with pillar and guardrail settings
    
    Returns:
        VoiceProfileResponse object with the generated voice guide
    """

    # Construct inputs for the crew
    inputs = {
        'x_handle': x_handle,
        'pillar': 3,
        'guardrail': 3,
    }
    
    try:
        result = VoiceProfileCrew().crew().kickoff(inputs=inputs)
        print(f"Voice guide generated for {x_handle}: {result}")
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'x_handle': sys.argv[3] if len(sys.argv) > 3 else "hinson",
        'config': {
            "pillar": 3,
            "guardrail": 3,
        },
        'storage_url': f"twitter-corpus/{sys.argv[3] if len(sys.argv) > 3 else 'hinson'}.jsonl",
        'format': 'jsonl',
        'schema_version': '1.0'
    }
    try:
        VoiceProfileCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        VoiceProfileCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'x_handle': sys.argv[3] if len(sys.argv) > 3 else "hinson",
        'config': {
            "pillar": 3,
            "guardrail": 3,
        },
        'storage_url': f"twitter-corpus/{sys.argv[3] if len(sys.argv) > 3 else 'hinson'}.jsonl",
        'format': 'jsonl',
        'schema_version': '1.0'
    }
    
    try:
        VoiceProfileCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
