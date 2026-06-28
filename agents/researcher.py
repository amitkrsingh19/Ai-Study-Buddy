import json

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from graph.state import State
from configs.config import settings
from tools.agent_tools import search_web, calculator
from memory.short_term import ShortTermMemory

## instance of ShortTermMemory
short_term_memory = ShortTermMemory()

## llm instance
llm = settings.mistral_agent

## initialize a parser instance
parser = JsonOutputParser()

## The list of tools
tools = [search_web, calculator]

## system instruction prompt : for structured output
system_instruction = """You are an expert research assistant and note-taker.
  Your job is to read raw web content and distill it into 
  clean, structured study notes for a learner.
  
  Your ONLY output must be valid JSON — no prose, no markdown 
  fences, no explanation outside the JSON.
  
  Respond with this exact schema:
  {{
    "subtopic": string
    "summary": string,
    "key_concepts": [string],
    "important_facts": [string],
    "study_tips": [string],
    "sources_used": [string]
  }}
  
  
  Rules:
  - summary must be 3-5 sentences maximum
  - key_concepts must have 3-5 items
  - important_facts must have 3-5 items  
  - study_tips must have 2-3 items
  - Never invent facts not present in the provided content
  - If content is insufficient, say so in summary field"""

human_prompt = """Subtopic: {subtopic}

  Raw content:
  {tavily_results}
  
  Level: {level} 

  Then output ONLY the JSON notes — no reasoning in response."""  

## researcher agent : takes state -> notes to the state
def researcher_node(state:State):
  chat_history = state['chat_history'] 

  print("RESEARCHER agent")
  subtopic = state['subtopic']
  level = state['level']

  try:
    ## invoke tavily tool and send input to the chain
    search_result = search_web.invoke({"query":subtopic})

    tavily_parsed = json.loads(search_result)

    sources = tavily_parsed['sources']

    filled_prompt = human_prompt.format(
      subtopic = subtopic,
      level = level,
      tavily_results = search_result)
    ## create a chat prompt template
    messages =[
    SystemMessage(content=system_instruction),
    *chat_history,
    HumanMessage(content = filled_prompt)
  ]
    ## invoke the chain
    response = llm.invoke(messages)

    ## parser the output as json
    llm_parsed = parser.invoke(response.content) # type:ignore
    ## return response as notes
    return {"notes":llm_parsed, "sources": llm_parsed['sources_used']}
  
  except Exception as e:
    return {"errors":[str(e)]}




