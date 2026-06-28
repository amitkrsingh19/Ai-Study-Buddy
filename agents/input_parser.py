from graph.state import State
from langgraph.graph import END

from memory.short_term import short_term_memory


## check for reset or restart intent
reset_keywords = [
    "start over", "restart", "reset",
    "new topic", "start fresh", "clear",
    "forget everything", "begin again"
]

## filter the intent of user
learning_intent_keywords = [
    "learn", "study", "teach", "explain",
    "understand", "help me with", "tell me about",
    "how does", "what is", "course", "plan",
    "beginner", "advanced", "intermediate"
  ]

## the phrases  
filler = [
    "i want to learn", "i want to study",
    "teach me", "help me with", "help me learn",
    "tell me about", "explain", "as a",
    "beginner", "medium", "advanced",      
    "basic", "intermediate", "expert"
  ]

## filter levels from input
levels = {"Beginner" : ["beginner", "basic", "new", "novice", "start"],
          "Medium" : ["medium", "intermediate", "some experience"],
          "Advanced" : ["advanced", "expert", "experienced", "senior"] }


## parse the user input and intent before invoking whole graph
def input_parser_node(state: State):

  ## get the raw user input from state
  user_input = state['raw_input']

  
  if any(keyword in user_input for keyword in reset_keywords):
    short_term_memory.empty()
    return {"needs_clarification":True,"clarification_message": "Starting fresh! What would you like to learn?"}

  ##  check if user really intent to learn
  found_intent = any(keyword in user_input.lower() for keyword in learning_intent_keywords)

  topic = user_input.lower()

  if found_intent:
  
    level = "Beginner" ## default level

    ## loop through levels keyword and return level_name
    for level_name,keywords in levels.items():
      if any(value.lower() in user_input.lower() for value in keywords ):
        level = level_name
        break

    ## take the existing topic
    existing_topic = state.get("topic",None)
    ## parse the topic from phrases
    for phrase in filler:
      topic = topic.replace(phrase,"")
    
    if existing_topic != topic:
      short_term_memory.empty()

    topic = topic.strip().title()

    return {
    "topic": topic,
    "level": level,
    "needs_clarification": False  
}
  
  return {"needs_clarification": True, "clarification_message":"Hi! I'm your study buddy. What topic would you like to learn today?"}


def input_router(state: State):
  if state['needs_clarification'] :
    return END
  else:
    return "planner_agent"