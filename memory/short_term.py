from langchain_core.messages import HumanMessage, AIMessage

## short term memory class
class ShortTermMemory:
  def __init__(self):
    self.MAX_MESSAGES = 10
    self.history = []

  def add_message(self,role,content):
    if role == "user":
      self.history.append(HumanMessage(content = content))
    elif role == "assistant":
      self.history.append(AIMessage(content = content))

    else:
      raise ValueError(f"Unknown role: {role}")

    if len(self.history) > self.MAX_MESSAGES:
      self.history = self.history[-self.MAX_MESSAGES:]

  def get_history(self):
    return self.history.copy()


  def empty(self):
    self.history = []


short_term_memory = ShortTermMemory()