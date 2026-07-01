from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from graph.state import State
from configs.config import settings

## llm instance
llm = settings.mistral_agent

## initialize a parser instance
parser = JsonOutputParser()

## system instruction prompt : for structured quiz output
system_instruction = """You are an expert quiz creator for learners.
Your job is to read study notes and create quiz questions that test
understanding of the key concepts.

Your ONLY output must be valid JSON — no prose, no markdown
fences, no explanation outside the JSON.

Respond with this exact schema:
{{
  "subtopic": string,
  "questions": [
    {{
      "id": string,
      "question": string,
      "options": [string],
      "correct_answer": string,
      "explanation": string
    }}
  ]
}}

Rules:
- Create exactly 5 questions
- Each question must have exactly 4 options
- correct_answer must exactly match one of the options
- Base questions ONLY on the provided notes, never invent facts
- explanation must be 1-2 sentences explaining why the answer is correct
- Vary difficulty: two easy, two medium, one harder question
- Questions must test understanding, not just memorization of exact wording"""
human_prompt = """Subtopic: {subtopic}
Level: {level}

Study Notes:
Summary: {summary}
Key Concepts: {key_concepts}
Important Facts: {important_facts}

Create a quiz based ONLY on the notes above.
Output ONLY the JSON quiz — no reasoning in response."""


## quiz agent : takes notes from state -> quiz_questions to state
def quiz_node(state: State):
    print("QUIZ NODE")

    notes = state.get('notes', {})
    level = state.get('level', '')
    subtopic = state.get('subtopic', '')

    try:
        ## build human prompt with notes content
        filled_prompt = human_prompt.format(
            subtopic=subtopic,
            level=level,
            summary=notes.get('summary', ''),
            key_concepts=", ".join(notes.get('key_concepts', [])),
            important_facts=", ".join(notes.get('important_facts', []))
        )

        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=filled_prompt)
        ]

        ## invoke llm
        response = llm.invoke(messages)

        ## parse response into dict
        parsed = parser.invoke(response)

        quiz_questions = parsed.get('questions', [])

        return {"quiz_questions": quiz_questions}

    except Exception as e:
        return {"errors": [str(e)], "quiz_questions": []}