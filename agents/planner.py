import json

from graph.state import State
from configs.config import settings

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from rich.console import Console
from rich.table import Table
from rich import box

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

    print("RESPONSE TYPE:", type(response))
    print("RESPONSE:", response)

    ## make sure to send a dict to extract subtopic
    print("IS DICT:", isinstance(response, dict))
    if isinstance(response,dict):

      ## get the title from day1 to send it as subtopic to researcher node
      subtopic = response['days'][0]['title']

      subtopics = [day['title'] for day in response['days']]

      print("SUBTOPIC:", subtopic)
      ## return study_plan with subtopics to the state
      return {"study_plan" : response, 
              "subtopic" : subtopic,
              "subtopics":subtopics,
              "current_day" : 1}
    
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


## this function draw a table using rich library
def json_to_display_table(data:dict):
  console = Console(record =True)

  if isinstance(data,dict):
    table = Table(title='Planner-Agent-Response',title_style="green",box= box.ROUNDED,show_header=True, header_style="bold magenta")
    table.add_column("Day", style="bold yellow", justify="center", width=15)
    table.add_column("Topic & Details", style="white", width=30)
    table.add_column("Objectives & Tasks", style="green", width=40)
    table.add_column("Resources", style="magenta", width=35)
    table.add_column("Time", style="bold blue", justify="right", width=15)

    for day_info in data["days"]:
        # Format Topic column with Title
        topic_cell = f"[bold text_box_theme]{day_info['title']}[/]"

        # Format Objectives and Tasks into a combined actionable checklist
        objectives_list = "\n".join([f"• {obj}" for obj in day_info["objectives"]])
        tasks_list = "\n".join([f"❑ {task}" for task in day_info["tasks"]])
        actions_cell = f"[bold underline]Objectives:[/]\n{objectives_list}\n\n[bold underline]Tasks:[/]\n{tasks_list}"

        # Format Resources into a list
        resources_cell = "\n".join([f"🔗 {res}" for res in day_info["resources"]])

        # Append the fully styled row to the table grid
        table.add_row(
            f"#{day_info['day']}",
            topic_cell,
            actions_cell,
            resources_cell,
            f"{day_info['duration_hours']} hrs"
        )
  console.print(table)
  console.save_html('planner_agent_response.html')
