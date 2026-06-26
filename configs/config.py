from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from functools import cached_property

# create a class to store env variables and cached llm instance
class Settings:
  def __init__(self):
    load_dotenv()
    self.MODEL : str = "mistral:latest" # os.getenv('MISTRAL_MODEL','mistral:latest')
    self.GEMINI_API_KEY : str = os.getenv('GEMINI_API_KEY','')
    self.TAVILY_API_KEY : str =os.getenv('TAVILY_API_KEY','')

  @cached_property
  def mistral_agent(self) -> ChatOllama:
    return ChatOllama(model = self.MODEL, temperature = 0.4)
  
  @cached_property
  def tavily_client(self):
    from tavily import TavilyClient
    return TavilyClient(self.TAVILY_API_KEY)
  
  @cached_property
  def gemini_agent(self)->ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model = 'gemini-flash-2.5', temperature=0.2, api_key = self.GEMINI_API_KEY)
  

settings = Settings()