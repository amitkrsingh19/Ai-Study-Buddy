from langchain_core.tools import tool
from tavily import TavilyClient
from tavily import errors
import os


# tavily api key
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))


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
                                        include_answer=True,
                                        search_depth="advanced")
    
    return web_response.get('answer',str(web_response))
  
  except errors.BadRequestError as e:
    print(f"Exception {e} Occured While Searching the Web")
    return f'Search Failed :{e}'