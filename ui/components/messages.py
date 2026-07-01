import streamlit as st

tab_labels = {
    "summary":         "📝 Summary",
    "key_concepts":    "💡 Key Concepts",
    "important_facts": "📌 Facts",
    "study_tips":      "🎯 Tips",
    "sources_used":    "🔗 Sources"
}

def render_table(content):
  for day_info in content['days']:
    objectives_text = "\n".join([f"- {item}" for item in day_info['objectives']])
    resources_text  = "\n".join([f"- {item}" for item in day_info['resources']])
    tasks_text      = "\n".join([f"- {item}" for item in day_info['tasks']])
    with st.expander(f"📅 Day {day_info['day']} — {day_info['title']} : ⏱ {day_info['duration_hours']} hrs"):
        st.markdown(f"📌 **Objectives**\n\n{objectives_text}")
        st.markdown(f"📚 **Resources**\n\n{resources_text}")
        st.markdown(f"✅ **Tasks**\n\n{tasks_text}")


def render_notes(content, message_id=None):
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

    ## follow-up question input
    followup = st.chat_input(
        "Ask a follow-up question about this topic...",
        key=f"followup_{message_id}"
    )
    if followup:
        st.session_state.pending_followup = followup
        st.session_state.followup_submitted = True
        st.rerun()

    ## ready for quiz button
    if st.button("✅ I'm ready for the Quiz", key=f"ready_{message_id}"):
        st.session_state.quiz_ready = True
        st.rerun()


def render_quiz(content, message_id):
    """
    Renders quiz questions inside a form.
    Returns submitted answers dict if form submitted, else None.
    """
    st.markdown(f"### 📝 Quiz Time! Test your understanding of **{content.get('subtopic', '')}**")

    with st.form(key=f"quiz_form_{message_id}"):
        selections = {}

        for i, question in enumerate(content.get('questions', []), start=1):
            st.markdown(f"**Question {i}: {question['question']}**")

            selected = st.radio(
                label="Select your answer",
                options=question['options'],
                key=f"q_{message_id}_{question['id']}",
                label_visibility="collapsed"
            )

            selections[question['id']] = selected
            st.divider()

        submitted = st.form_submit_button("✅ Submit Answers")

        if submitted:
            return selections

    return None

def render_score(content):
    scores = content.get('scores', [])
    feedback = content.get('feedback', [])
    last_score = scores[-1] if scores else 0

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(label="📊 Your Score", value=f"{last_score}%")

    if last_score >= 60:
        st.success("🎉 Great job! You passed this subtopic.")
    else:
        st.warning("📚 Let's review this topic again — re-studying now...")

    st.markdown("#### Feedback")
    for fb in feedback:
        if fb.startswith("✅"):
            st.success(fb)
        else:
            st.error(fb)
