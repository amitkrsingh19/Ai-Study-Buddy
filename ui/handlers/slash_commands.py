import streamlit as st
import uuid

from memory.short_term import short_term_memory


def is_slash_command(prompt: str) -> bool:
    return prompt.strip().startswith("/")


def handle_slash_command(prompt: str):
    command = prompt.strip().lower()

    ## append the user's command to chat history for visibility
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})

    if command == "/help":
        _handle_help()

    elif command == "/progress":
        _handle_progress()

    elif command == "/memory":
        _handle_memory()

    elif command == "/sources":
        _handle_sources()

    elif command == "/restart":
        _handle_restart()

    else:
        _handle_unknown(command)


def _handle_help():
    message = """📚 **Available Commands:**

`/help` — show this command list\n
`/progress` — see your current day, topic, and score history\n
`/memory` — view what's in short-term conversation memory\n
`/sources` — see source links for current subtopic\n
`/restart` — start a completely new session\n

💡 Tip: Just type your topic normally to start learning!"""

    st.session_state.messages.append({"role": "ai", "type": "text", "content": message})


def _handle_progress():
    topic = st.session_state.get('topic') or "Not started"
    level = st.session_state.get('level') or "—"
    current_day = st.session_state.get('current_day', 1)
    memory_count = len(short_term_memory.get_history())

    message = f"""📊 **Your Progress:**

**Topic:** {topic}
**Level:** {level}
**Day:** {current_day} of 5

**Memory usage:** {memory_count}/10 messages"""

    st.session_state.messages.append({"role": "ai", "type": "text", "content": message})


def _handle_memory():
    history = short_term_memory.get_history()

    if not history:
        message = "🧠 Short-term memory is currently empty."
    else:
        lines = []
        for msg in history:
            role = "👤 You" if msg.type == "human" else "🤖 Assistant"
            preview = msg.content[:100] + ("..." if len(msg.content) > 100 else "")
            lines.append(f"**{role}:** {preview}")

        message = "🧠 **Current Short-Term Memory:**\n\n" + "\n\n".join(lines)

    st.session_state.messages.append({"role": "ai", "type": "text", "content": message})


def _handle_sources():
    ## find the most recent notes message
    notes_messages = [m for m in st.session_state.messages if m['type'] == 'notes']

    if not notes_messages:
        message = "🔗 No sources available yet. Start learning a topic first!"
    else:
        latest_notes = notes_messages[-1]['content']
        sources = latest_notes.get('sources_used', [])

        if not sources:
            message = "🔗 No sources were recorded for the current subtopic."
        else:
            lines = [f"- {url}" for url in sources]
            message = f"🔗 **Sources for {latest_notes.get('subtopic', 'current topic')}:**\n\n" + "\n".join(lines)

    st.session_state.messages.append({"role": "ai", "type": "text", "content": message})


def _handle_restart():
    short_term_memory.empty()
    st.session_state.messages = []
    st.session_state.topic = None
    st.session_state.level = None
    st.session_state.current_day = 1
    st.session_state.uid = str(uuid.uuid4())
    st.session_state.quiz_submitted = False
    st.session_state.quiz_ready = False
    st.session_state.pending_quiz_answers = None
    st.session_state.followup_submitted = False
    st.session_state.pending_followup = None

    st.session_state.messages.append({
        "role": "ai",
        "type": "stream",
        "content": "🔄 Session restarted! What would you like to learn today?"
    })


def _handle_unknown(command: str):
    message = f"❓ Unknown command: `{command}`\n\nType `/help` to see available commands."
    st.session_state.messages.append({"role": "ai", "type": "stream", "content": message})