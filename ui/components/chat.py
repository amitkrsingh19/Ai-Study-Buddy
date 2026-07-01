import time 

import streamlit as st
from .messages import render_table, render_notes, render_quiz, render_score

## chat streaming 
def chat_stream(message):
    if isinstance(message, str):
        for ch in message:
            yield ch
            time.sleep(0.001)

## render chat history by type
def render_chat_history(messages):
    for idx, message in enumerate(messages):
        with st.chat_message(message['role']):
            if message['type'] == 'table':
                render_table(message['content'])

            elif message['type'] == 'notes':
                render_notes(message['content'], message_id=idx)

            elif message['type'] == 'quiz':
                ## quiz returns answers when submitted
                answers = render_quiz(message['content'], message_id=idx)
                if answers and st.session_state.current_day  <=5:
                    st.session_state.pending_quiz_answers = answers
                    st.session_state.quiz_submitted = True
                    st.rerun() 
                    
            elif message['type'] == 'score':
                render_score(message['content'])

            elif message['type'] == 'stream':
                content = message['content']
                st.write_stream(chat_stream(content))
            else:
                st.write(message['content'])
