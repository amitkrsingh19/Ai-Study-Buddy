import sys
import os

## to run app.py from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import uuid

from ui.components.sidebar import render_sidebar
from ui.components.chat import render_chat_history
from graph.pipeline import graph
from memory.short_term import short_term_memory
from ui.handlers.slash_commands import is_slash_command, handle_slash_command


## initialize the stream session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if 'uid' not in st.session_state:
    st.session_state.uid = str(uuid.uuid4()) ## uuid initialization

if 'topic' not in st.session_state: ## topic initialization
    st.session_state.topic = None

if 'level' not in st.session_state: ## level initialization
    st.session_state.level = None

if 'current_day' not in st.session_state: ## current_day initialization
    st.session_state.current_day = 1

if 'quiz_submitted' not in st.session_state: ## quiz_submitted initialization - bool
    st.session_state.quiz_submitted = False

if 'pending_quiz_answers' not in st.session_state:
    st.session_state.pending_quiz_answers = None

if 'quiz_ready' not in st.session_state:
    st.session_state.quiz_ready = False

if 'followup_submitted' not in st.session_state:
    st.session_state.followup_submitted = False

if 'pending_followup' not in st.session_state:
    st.session_state.pending_followup = None

## render sidebar function
render_sidebar()

## title of the page
st.title("Ai-Study-Buddy")

## created configuration with uuid
config = {"configurable": {"thread_id": st.session_state.uid}}

## render all the chat 
render_chat_history(st.session_state.messages)

## handle quiz submission and resume if quiz_submitted
if st.session_state.quiz_submitted:

    ## take the quiz submission
    answers_dict = st.session_state.pending_quiz_answers

    user_answers = [
        {"id": qid, "answer": ans} for qid, ans in answers_dict.items() # type: ignore
    ]

    with st.spinner("Evaluating your answers..."):
        ## update graph state with user_answers
        graph.update_state(config=config, values={"user_answers": user_answers}) # type: ignore
        state = graph.invoke(
            None,
            config=config # type: ignore
        )
        
        ## check if the session is complete
        current_day = state.get('current_day', 1)
        subtopics = state.get('subtopics', [])
        is_complete = current_day > len(subtopics)

        ## remove the just-answered quiz from history so it stops rendering
        st.session_state.messages = [
            m for m in st.session_state.messages if m['type'] != 'quiz'
        ]
    st.session_state.quiz_submitted = False
    st.session_state.pending_quiz_answers = None
    st.session_state.current_day = state.get('current_day', 1)

    ## Update score in streamlit state
    if state.get('scores',[]):
        st.session_state.messages.append({
            "role": "ai",
            "type": "score",
            "content": {
                "scores": state.get('scores', []),
                "feedback": state.get('feedback', [])
            }
        })

    if is_complete:
        st.session_state.messages.append({
            "role": "ai",
            "type": "text",
            "content": "🎉 **Congratulations!** You've completed your entire 5-day study plan! Type a new topic to start learning something else."
        })
        st.session_state.session_complete = True

    else:
        ## then re-studied notes if retry happened
        if state.get('notes'):
            st.session_state.messages.append({
                "role": "ai",
                "type": "notes",
                "content": state['notes']
            })

        ## render new quiz   
        if state.get('quiz_questions'):
            st.session_state.messages.append({
                "role": "ai",
                "type": "quiz",
                "content": {
                    "subtopic": state.get('subtopic', ''),
                    "questions": state['quiz_questions']
                }
            })

    ## rerun method
    st.rerun()

## when user: ready for quiz
elif st.session_state.quiz_ready:

    with st.spinner("Preparing your quiz..."):
        ## Resume the graph to generate quiz 
        state = graph.invoke(None, config=config) # type: ignore

    st.session_state.quiz_ready = False

    st.session_state.messages = [
        m for m in st.session_state.messages if m['type'] != 'quiz'
    ]
    
    ## retrieve the questions
    if state.get('quiz_questions'):
        st.session_state.messages.append({
            "role": "ai",
            "type": "quiz",
            "content": {
                "subtopic": state.get('subtopic', ''),
                "questions": state['quiz_questions']
            }
        })

    st.rerun()

## if user asks for follow-up questions
elif st.session_state.followup_submitted:

    followup_question = st.session_state.pending_followup

    with st.chat_message('user'):
        st.write(followup_question)

    st.session_state.messages.append({"role": "user", "type": "text", "content": followup_question})

    with st.chat_message('assistant'):
        with st.spinner("Thinking..."):
            short_term_memory.add_message("user", followup_question)

            ## direct LLM call using chat history — no need to run full graph
            from langchain_core.messages import SystemMessage, HumanMessage
            from configs.config import settings

            ## llm instance
            llm = settings.mistral_agent
            chat_history = short_term_memory.get_history()

            ## system prompt
            followup_system = """You are a helpful study assistant. 
            Answer the learner's follow-up question clearly and concisely 
            based on the conversation context. Keep response under 150 words."""

            ## a list of messages with prompt + chat history for context
            messages = [
                SystemMessage(content=followup_system),
                *chat_history
            ]

            ## invoke llm if user asks followups
            response = llm.invoke(messages)
            answer_text = response.content

            short_term_memory.add_message("assistant", answer_text)
    
    ## append the texts to state for rendering
    st.session_state.messages.append({"role": "ai", "type": "text", "content": answer_text})

    ## set followup_submitted : False
    st.session_state.followup_submitted = False
    st.session_state.pending_followup = None

    ## rerun 
    st.rerun()

st.caption("💡 Type /help to see available commands")

## handle new topic input
if prompt := st.chat_input("Enter the topic you want to learn today..."):
    if is_slash_command(prompt):
        handle_slash_command(prompt)
        st.rerun()

    else:
        with st.chat_message('user'):
            st.write(prompt)

        st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})

        with st.chat_message('assistant'):
            with st.status("Thinking...") as status:
                status.update(label="🔍 Searching Web 🌐...", state='running')

                ## add prompt to short term memory 
                short_term_memory.add_message("user", prompt)

                status.update(label="⚙️ Running agents... this may take a moment", state='running')
                
                ## invoke graph
                state = graph.invoke(
                    {"raw_input": prompt, "chat_history": short_term_memory.get_history()}, # type: ignore
                    config=config)  # type:ignore
                
                status.update(label="🕵🏻 Summarising Plans...", state='running')

                st.session_state.current_day = state.get('current_day', 1)
                st.session_state.topic = state.get('topic')
                st.session_state.level = state.get('level')

                ## get the notes
                notes = state.get('notes', {})
                if notes:
                    ## add response to short term memory
                    short_term_memory.add_message('assistant', notes.get('summary', " "))

                status.update(label="✅ Done!", state='complete')

        if state.get('notes'):
            st.caption(f"📅 Day {st.session_state.current_day} of 5 — {state.get('subtopic', '')}")
            st.progress(st.session_state.current_day / 5)

        ## append messages for rendering
        if state.get('needs_clarification', False):
            st.session_state.messages.append({"role": "ai", "type": "text", "content": state['clarification_message']})

        else:
            if state.get('study_plan', None):
                st.session_state.messages.append({
                    "role": "ai",
                    "type": "table", 
                    "content": state['study_plan']})

            if state.get('notes', None):
                st.session_state.messages.append({
                    "role": "ai", 
                    "type": "notes", 
                    "content": state['notes']}
                )

            if state.get('quiz_questions'):
                st.session_state.messages.append({
                    "role": "ai",
                    "type": "quiz",
                    "content": {
                        "subtopic": state.get('subtopic', ''),
                        "questions": state['quiz_questions']
                    }
                })
            
            if state.get('errors'):
                st.error(f"Something went wrong: {state['errors'][-1]}")

        st.rerun()
