import re

from langchain_core.output_parsers import JsonOutputParser

from graph.state import State
from configs.config import settings

## llm instance
llm = settings.mistral_agent

## initialize a parser instance
parser = JsonOutputParser()

## system instruction prompt : for structured evaluation output
system_instruction = """You are an expert evaluator for learner quiz answers.
Your job is to compare user answers against correct answers and provide
constructive feedback.

Your ONLY output must be valid JSON — no prose, no markdown
fences, no explanation outside the JSON.

Respond with this exact schema:
{{
  "results": [
    {{
      "id": string,
      "is_correct": boolean,
      "feedback": string
    }}
  ],
  "score": int
}}

Rules:
- score must be the percentage of correct answers (0-100)
- feedback must be 1-2 sentences, encouraging but honest
- If incorrect, feedback must briefly explain the correct concept
- If correct, feedback must be a short positive reinforcement
- Never invent information not present in the quiz questions"""

human_prompt = """Quiz Questions and Correct Answers:
{quiz_data}

User's Answers:
{user_answers_data}

Evaluate each answer and output ONLY the JSON result — no reasoning in response."""


## evaluator agent : takes quiz_questions + user_answers -> scores + feedback to state
def evaluator_node(state: State):
    print("EVALUATOR NODE")

    quiz_questions = state.get('quiz_questions', [])
    user_answers = state.get('user_answers', [])

    try:
        ## build answer lookup by id
        answer_lookup = {ans['id']: ans['answer'] for ans in user_answers}

        results = []
        correct_count = 0

        for q in quiz_questions:
            user_ans = answer_lookup.get(q['id'], '')
            is_correct = normalize(user_ans) == normalize(q['correct_answer'])

            if is_correct:
                correct_count += 1

            results.append({
                "id": q['id'],
                "question": q['question'],
                "is_correct": is_correct,
                "correct_answer": q['correct_answer'],
                "user_answer": user_ans,
                "explanation": q.get('explanation', '')
            })

        
        score = int((correct_count / len(quiz_questions)) * 100) if quiz_questions else 0

        feedback = [
            f"✅ Correct! {r['explanation']}" if r['is_correct']
            else f"❌ Incorrect. {r['explanation']}"
            for r in results
        ]
        print("FEEDBACK BUILT:", len(feedback))

        scores = state.get('scores', []) or []
        scores.append(score)
        print(f"score generated: {score}")
        return {
            "scores": scores,
            "feedback": feedback
        }

    except Exception as e:
        print("EVALUATOR CRASHED:", str(e))
        return {"errors": [str(e)], "scores": state.get('scores', []) or [], "feedback": []}
    


def normalize(text):
    return re.sub(r'[^\w\s]', '', text).strip().lower()

