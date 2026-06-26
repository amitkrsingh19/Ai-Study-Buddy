import json
from langchain_core.tools import tool
from tavily import errors
from configs.config import settings

tavily_client = settings.tavily_client

#create a tool
@tool
def calculator(expression:str)-> str:
  """Useful for executing mathematical expressions. Input should be a valid python math expression string."""
  return str(eval(expression))

@tool
def search_web(query: str)->str:
  """Useful when you need to answer questions about current events or when you lack specific knowledge."""
  try:
    web_response = tavily_client.search(query,
                                        search_depth="advanced")
    
    contents = []
    sources = []
    for result in web_response.get('results',[]):
      contents.append(result['content'])
      sources.append(result['url'])
    
    results = json.dumps({"contents":contents,"sources":sources})
    return results
    
  except errors.BadRequestError as e:
    print(f"Exception {e} Occured While Searching the Web")
    return f'Search Failed :{e}'