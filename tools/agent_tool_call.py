import sys
import os
from dotenv import load_dotenv
from langchain_ollama.chat_models import ChatOllama
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
import json
from tools.agent_tools import calculator,search_web
from pyfiglet import figlet_format

# load env file
load_dotenv()

CYAN_BLUE = "\033[36m" 
RESET = "\033[0m" 
MODEL = 'mistral:latest'


# prompt template for the LLM
system_instruction = """You are a helpful mathematical and research assistant. 

Follow these strict rules:
1. IF the user provides a math problem or expression, you MUST use the `calculator` tool to solve it. Do not try to do the math in your head.
2. IF the user asks for factual information or top lists, you MUST use the `search_web` tool.
3. IF the user simply greets you, says 'thank you', or makes small talk, you must respond with normal text and DO NOT output any JSON or tool calls.

Always return the final answer to the user after using a tool."""


tools = [calculator, search_web]

#create a chat model
model = ChatOllama(model=MODEL,temperature = 0.5)

# gemini model
#model = ChatGoogleGenerativeAI(model='gemini-2.5-flash',temperature = 0.5, api_key=os.getenv('GEMINI_API_KEY'))
# bind the tool and llm with create_agent
agent = create_agent(model, tools=tools, 
                    system_prompt=system_instruction)

def agent_call():
  print("="*70)
  model_name = figlet_format(MODEL, font='slant')
  print(model_name)
  print("="*70)
  print(f"{CYAN_BLUE}🦜 LangChain Terminal Tool-Calling Client Initialized.")
  print("Type 'exit' or 'quit' to end the session.")
  print(F"Try asking: 'Ask to calculate or You can ask me to Search anything from the Web'{RESET}")
  print("="*70)

  messages = []
  while True:
    try:
      user_input = input("Provide Input Using a whitespace to the Calculator else search from the web:")
      user_input = user_input.strip()
      if user_input in ['exit','quit']:
        print('exiting...')
        break  
      
      messages.append(HumanMessage(content=user_input))

      full_chat_history = display_output(messages[-1])

    except KeyboardInterrupt:
      print("\n Session interrupted")
      write_output_to_file(full_chat_history)
      sys.exit(0)
      
    except Exception as e:
      print(f"Error : {e}")
  # if the user directly turn of the terminal ,save the output  
  write_output_to_file(full_chat_history)



# save json to the file
# ---------------------
def write_output_to_file(full_chat_history):
  try:
    with open('chat_history2.json', 'w', encoding='utf-8') as f:
      json.dump(full_chat_history, f, indent=4)
  except TypeError as e:
    print(f'\nError serializing history to JSON: {e}')



# display stream ouputs on by one
# -------------------------------
def display_output(message) -> list[dict]:
  # Create fullchat history list
  full_chat_history = [{'Tools_available':['calculator','Search Web']}]

  # create a stream for output
  stream = agent.stream({"messages":message}, stream_mode="values")
  response = {'User':[],'Agent':[]}
  print('-'*70)
    # Display the Input & Outputs in Stream
  for snapshot in stream:
    messages_list = snapshot.get('messages')
    if not messages_list:
      continue
        
    last_message = messages_list[-1]

    #if Aimesssage in the stream, Append it in Agent  
    if isinstance(last_message, AIMessage):
      if last_message.content:
        print(f"Agent: {last_message.content}")
        response['Agent'].append({'content': last_message.content,
                                 'usage':last_message.usage_metadata['total_tokens']})
        continue
      response['Agent'].append({'tool_calls': [last_message.tool_calls[0]['name'] if last_message.tool_calls else [None]]})
        
        # if HumanMessage append in User
    elif isinstance(last_message, HumanMessage):
      print(f"User: {last_message.content}")
      response['User'].append(last_message.content)

  print('-'*70)
  full_chat_history.append(response)

  return full_chat_history


# run the agent
if __name__=="__main__":
  agent_call()