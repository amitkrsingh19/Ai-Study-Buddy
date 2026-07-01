from graph.state import State
from memory.long_term import retrieve_notes


def memory_reader_node(state: State):
    subtopic = state.get('subtopic', '')
    force_refresh = state.get('force_refresh', False)

    print("MEMORY READER NODE")

    # bypass cache if retry forced fresh research
    if force_refresh:
        return {"notes": None, "force_refresh": False}

    try:
        notes = retrieve_notes(subtopic)
        if notes:
            print(f"Memory hit for: {subtopic}")
            return {"notes": notes}
        else:
            print(f"Memory miss for: {subtopic}")
            return {"notes": None}

    except Exception as e:
        return {"errors": [str(e)], "notes": None}