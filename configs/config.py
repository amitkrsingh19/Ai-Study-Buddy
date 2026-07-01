from dotenv import load_dotenv
import os
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from functools import cached_property
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from chromadb.utils import embedding_functions

# create a class to store env variables and cached llm instance
class Settings:
  def __init__(self):
    load_dotenv()
    self.MISTRAL_MODEL : str = "mistral-large-latest"
    self.MISTRAL_API_KEY : str = os.getenv('MISTRAL_API_KEY','')
    self.LOCAL_MODEL : str ="mistral:latest"
    self.MODEL : str = "meta/llama-3.1-70b-instruct" # os.getenv('MISTRAL_MODEL','mistral:latest')
    self.GEMINI_API_KEY : str = os.getenv('GEMINI_API_KEY','')
    self.NVIDIA_API_KEY : str = os.getenv('NVIDIA_API_KEY','')
    self.TAVILY_API_KEY : str =os.getenv('TAVILY_API_KEY','')

  ## local mistral:latest initialization
  @cached_property
  def mistral_agent(self) -> ChatMistralAI:
    return ChatMistralAI(model= self.MISTRAL_MODEL ,api_key= self.MISTRAL_API_KEY ,temperature=0.2) 
  
  ## nvidia hosted mistral agent initialization
  @cached_property
  def nvidia_agent(self) -> ChatNVIDIA:
    return ChatNVIDIA(
            model=self.MODEL,
            api_key= self.NVIDIA_API_KEY,
            temperature = 0.3
        )
    #return ChatOllama(model = self.MODEL, temperature = 0.4)
  
  ## tavily client initialization
  @cached_property
  def tavily_client(self):
    from tavily import TavilyClient
    return TavilyClient(self.TAVILY_API_KEY)
  
  ## gemini agent initialization
  @cached_property
  def gemini_agent(self)->ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model = 'gemini-flash-2.5', temperature=0.2, api_key = self.GEMINI_API_KEY)
  
  ## embedding function initialization  
  @cached_property
  def embedding_model(self):
    return embedding_functions.OllamaEmbeddingFunction(
  url="http://localhost:11434",
  model_name ='nomic-embed-text'
)

settings = Settings()
