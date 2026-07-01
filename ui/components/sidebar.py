import streamlit as st
import uuid
from memory.short_term import short_term_memory
from ui.handlers.slash_commands import _handle_restart

def render_sidebar():
  with st.sidebar:
    st.header("📊 Session Info")
    st.divider()

    if st.session_state.get('session_complete', False):
      st.success("✅ 5-Day Plan Complete!")

    st.markdown(f"**Topic:** {st.session_state.get('topic', 'Not started')}")

    st.divider()

    st.markdown(f"**Level:** {st.session_state.get('level', '—')}")

    st.divider()
    
    current_day = st.session_state.get('current_day', 1)
    display_day = min(current_day, 5)
    
    st.markdown(f"**Progress:** Day {display_day} of 5")
    st.progress(display_day / 5)

    st.divider()
    memory_count = len(short_term_memory.get_history())
    st.progress(memory_count / 10 , text="Memory Uses")
    st.caption(f"{memory_count} / 10 messages")

    st.divider()
    if st.button("🔄 Start Over"):
        _handle_restart()
        st.rerun()