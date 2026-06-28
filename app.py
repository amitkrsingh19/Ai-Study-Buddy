import streamlit as st
import time
import json

import uuid

from graph.pipeline import graph
from memory.short_term import short_term_memory

## initialize the stream session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if 'uid' not in st.session_state:
    st.session_state.uid = str(uuid.uuid4())

if 'topic' not in st.session_state:
    st.session_state.topic = None

if 'level' not in st.session_state:
    st.session_state.level = None

if 'current_day' not in st.session_state:
    st.session_state.current_day = 1

tab_labels = {
    "summary":         "📝 Summary",
    "key_concepts":    "💡 Key Concepts",
    "important_facts": "📌 Facts",
    "study_tips":      "🎯 Tips",
    "sources_used":    "🔗 Sources"
}


def chat_stream(message):
    if isinstance(message, str):
        user_input = f"User: {message}...Great choice"
        for ch in user_input:
            yield ch
            time.sleep(0.02)
    
    elif isinstance(message , dict):
        json_lines = json.dumps(message, indent=2).splitlines()
        for line in json_lines:
            yield line + '\n'
            time.sleep(0.1)

with st.sidebar:
    st.header("📊 Session Info")
    st.divider()
    st.markdown(f"Topic : {st.session_state.get('topic','Not started')}")
    st.divider()
    st.markdown(f"Level : {st.session_state.get('level','--')}")
    st.divider()
    st.markdown(f"Current Day : {st.session_state.get('current_day',1)}")
    st.progress(st.session_state.current_day / 5, text="Day Progress")

    st.divider()
    memory_count = len(short_term_memory.get_history())
    st.progress(memory_count / 10 , text="Memory Uses")
    st.caption(f"{memory_count} / 10 messages")

    st.divider()
    if st.button("🔄 Start Over"):
        short_term_memory.empty()
        st.session_state.messages = []
        st.session_state.topic = None
        st.session_state.level = None
        st.session_state.current_day = 1
        st.session_state.uid = str(uuid.uuid4()) 
        st.rerun()

st.title("Ai-Study-Buddy")


config = {"configurable":{"thread_id":st.session_state.uid}}

for message in st.session_state.messages:
    with st.chat_message(message['role']):

        if message['type'] =='table':
            for day_info in message['content']['days']:
                objectives_text = "\n".join([f"- {item}" for item in day_info['objectives']])
                resources_text  = "\n".join([f"- {item}" for item in day_info['resources']])
                tasks_text      = "\n".join([f"- {item}" for item in day_info['tasks']])
                with st.expander(f"📅 Day {day_info['day']} — {day_info['title']} : ⏱ {day_info['duration_hours']} hrs"):
                    st.markdown(f"📌 **Objectives**\n\n{objectives_text}")
                    st.markdown(f"📚 **Resources**\n\n{resources_text}")
                    st.markdown(f"✅ **Tasks**\n\n{tasks_text}")

        elif message['type'] == 'notes':
            content = message['content']
            st.markdown(f"### 📚 {content['subtopic']}")

            tabs = st.tabs([tab_labels[key] for key in tab_labels])

            for tab, (key, label) in zip(tabs, tab_labels.items()):
                with tab:
                    value = content[key]
                    if key == "summary":
                        st.markdown(value)
                    elif key == "sources_used":
                        for url in value:
                            st.link_button(url, url)
                    elif key == "study_tips":
                        st.markdown("\n".join([f"{i+1}. {item}" for i, item in enumerate(value)]))
                    else:
                        st.markdown("\n\n".join([f"- {item}" for item in value]))
        else:
            st.write(message['content'])

if prompt := st.chat_input("Enter the topic you want to learn today..."):
    with st.chat_message('user'):
        st.write(prompt)

    st.session_state.messages.append({"role":"user","type" : "text", "content":prompt})

    with st.chat_message('assistant'):
        with st.status("Thinking...") as status:
            status.update(label="🔍 Searching Web 🌐...")
            short_term_memory.add_message("user",prompt)

            state = graph.invoke({"raw_input": prompt,"chat_history":short_term_memory.get_history()}, config = config)  # type:ignore

            st.session_state.current_day = state.get('current_day',1)
            st.session_state.topic = state.get('topic')
            st.session_state.level = state.get('level')

            notes = state.get('notes',{})
            if notes:
                short_term_memory.add_message('assistant',notes.get('summary'," "))
                
            status.update(label="🕵🏻 Summarising Plans...")
        status.update(label ="✅ Done!", state='complete')

        st.caption(f"📅 Day {st.session_state.current_day} of 5 — {state.get('subtopic','')}")
        st.progress(st.session_state.current_day / 5)
        

    if state.get('needs_clarification',False) :
        st.session_state.messages.append({"role":"ai", "type":"text","content":state['clarification_message']})

            
    else:
        if state.get('study_plan',None):
            st.session_state.messages.append({"role" : "ai", "type" : "table", "content" : state['study_plan']})
                

        if state.get('notes', None):    
            st.session_state.messages.append({"role":"ai", "type":"notes","content":state['notes']})
                
        if state.get('errors'):
            st.error(f"Something went wrong: {state['errors'][-1]}")

    st.rerun()
    