from graph.state import State


def next_day_node(state: State):
    print("NEXT DAY NODE")

    current_day = state.get('current_day', 1)
    subtopics = state.get('subtopics', [])

    new_day = current_day + 1

    if new_day > len(subtopics):
        return {"current_day": new_day}

    next_subtopic = subtopics[new_day - 1]

    return {
        "current_day": new_day,
        "subtopic": next_subtopic,
        "retries": 0,
        "force_refresh": False,
        "notes": None,
        "quiz_questions": [],
        "user_answers": [],
        "scores": []
    }