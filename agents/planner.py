import json

from graph.state import State
from configs.config import settings

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# import llm instance from config
llm = settings.mistral_agent

## initialize json parser
parser = JsonOutputParser()

## system prompt for the output
system_instruction = """
You are an expert curriculum designer. 
Your ONLY output must be valid JSON — no prose, no markdown fences, no explanation.
Respond with a JSON object matching this exact schema: 
{{ "topic": string, "level": string, "days":
[{{ "day": int, "title": string, "objectives": [string],
"resources": [string], "tasks": [string], "duration_hours": float }} ] }}
"""


## prompt with human input to feed llm
human_instruction = """
Create a 5-day learning plan for the topic: {topic}
Learner level: {level}
Make each day progressively harder. Include 2-3 objectives, 2 resources, and 2 tasks per day.
"""

# create a chat prompt template 
chat_prompt_template = ChatPromptTemplate.from_messages([
  ('system',system_instruction),
  ('human',human_instruction)
])

## Planner agent node : creates study-plans
def planner_node(state:State):
  print("PLANNER STARTED")

  # takes topic & level from the state
  topic = state['topic']
  level = state['level']

  ## create node input from topic and level
  user_inputs = {"topic":topic, "level":level}

  ## create llm chain
  chain = chat_prompt_template | llm | parser
  
  try:
    ## get the response from chain
    response = chain.invoke(user_inputs)

    ## make sure to send a dict to extract subtopic
    print("IS DICT:", isinstance(response, dict))
    if isinstance(response,dict):

      ## get the title from day1 to send it as subtopic to researcher node
      subtopic = response['days'][0]['title']

      subtopics = [day['title'] for day in response['days']]

      ## return study_plan with subtopics to the state
      return {"study_plan" : response, 
              "subtopic" : subtopic,
              "subtopics":subtopics,
              "current_day" : 1,
              }
    
    else: 
      return {"errors": ["Planner returned invalid response"]}
    
  ## return exceptions as error if any
  except Exception as e:
    print("PLANNER ERROR:", str(e))
    return {"errors" : [str(e)]}


## this function saves result to a file
def save_result(result):
  try:
    with open('planner_agent.json','w',encoding='utf-8') as f:
      json.dump(result,f , indent=4)
  except Exception as e:
    print(e)
