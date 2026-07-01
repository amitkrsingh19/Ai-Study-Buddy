from graph.state import State
from memory.long_term import store_notes


def memory_writer_node(state: State):
    notes = state.get('notes', {})
    topic = state.get('topic', '')
    level = state.get('level', '')
    current_day = state.get('current_day', 1)

    print("MEMORY WRITER NODE")

    try:
        success = store_notes(notes, topic, level, current_day)
        return {"memory_saved": success}

    except Exception as e:
        return {"errors": [str(e)], "memory_saved": False}