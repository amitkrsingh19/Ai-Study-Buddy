# graph/router.py

from graph.state import State
from langgraph.graph import END


def route_after_memory(state: State):
    notes = state.get('notes')
    if notes is None:
        return "researcher_node"
    else:
        return "quiz_node"


def route_after_evaluation(state: State):
    scores = state.get('scores', [])
    retries = state.get('retries', 0)
    current_day = state.get('current_day', 1)
    subtopics = state.get('subtopics', [])

    last_score = scores[-1] if scores else 0

    ## fail and retries remaining
    if last_score < 60 and retries < 2:
        return "retry_tracker_node"

    ## pass or retries exhausted — check if more days remain
    if current_day < len(subtopics):
        return "next_day_node"

    ## last day done
    return END


def route_after_input(state: State):
    if state.get('needs_clarification', False):
        return END
    else:
        return "planner_node"