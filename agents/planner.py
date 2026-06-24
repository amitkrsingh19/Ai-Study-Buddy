from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.chat_models import ChatOllama
from langchain.messages import SystemMessage
from typing import TypedDict
import json
from dotenv import load_dotenv
import os
load_dotenv()

#load the env variable
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
MODEL = 'mistral:latest'

#llm = ChatGoogleGenerativeAI(model='gemini-flash-2.5',temperature=0.2, api_key=GEMINI_KEY)

## system prompt for the output
system_instruction = """
You are an expert curriculum designer. 
Your ONLY output must be valid JSON — no prose, no markdown fences, no explanation.
Respond with a JSON object matching this exact schema: 
{ "topic": string, "level": string, "days":
[{ "day": int, "title": string, "objectives": [string],
"resources": [string], "tasks": [string], "duration_hours": float } ] }
"""
## prompt with human input to feed llm
human_instruction = """
Create a 5-day learning plan for the topic: {topic}
Learner level: {level}
Make each day progressively harder. Include 2-3 objectives, 2 resources, and 2 tasks per day.
"""

# create a chat prompt template 
chat_prompt_template = ChatPromptTemplate.from_messages([
  (SystemMessage(content = system_instruction)),
  ('human',human_instruction)
])

# langgraph state 
class State(TypedDict):
  topic :str
  level :str
  raw_output :str
  parsed_plan: dict
  error:str

#llm.bind(response_format={"type": "json_object"})

def planner_agent(user_inputs):
  llm = ChatOllama(model=MODEL,temperature = 0.2)
  parser = StrOutputParser()
  # create a chain with prompt template
  chain = chat_prompt_template | llm | parser

  try:
    response = chain.invoke(user_inputs)

    json_result = json.loads(response)
    #save_result(json_result)
    json_to_display_table(json_result)

  except json.JSONDecodeError as e:
    print(e)
  
  except Exception as e:
    print(e)


def save_result(result):
  try:
    with open('planner_agent.json','w',encoding='utf-8') as f:
      json.dump(result,f , indent=4)
  except Exception as e:
    print(e)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


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



if __name__ =="__main__":
  user_inputs = {"topic":"JAVA Programming","level":"medium"}
  planner_agent(user_inputs)