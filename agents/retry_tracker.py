# agents/retry_tracker.py

from graph.state import State


def retry_tracker_node(state: State):
    print("RETRY TRACKER NODE")

    retries = state.get('retries', 0)
    scores = state.get('scores', [])
    last_score = scores[-1] if scores else 0

    new_retries = retries + 1

    return {
        "retries": new_retries,
        "force_refresh": True,
        "errors": [f"Retry {new_retries} triggered — score was {last_score}%, re-studying subtopic"]
    }