from typing import TypedDict, Optional, Annotated
import operator

class State(TypedDict):
  topic:str                       # user input
  level: str                      # beginner/medium/advanced
  subtopic : Optional[str]        # single subtopic from content
  subtopics: Optional[list[str]]  # output from planner agent 
  current_day : Optional[int]     # current day of plan
  study_plan : Optional[dict]     # planner output 
  notes: Optional[dict]           # researcher output / ChromaDB retrieval
  sources : Optional[list]        # URLs from Tavily
  memory_saved : Optional[bool]   # bool confirming ChromaDB write
  quiz_questions: Optional[list]  # list of questions from quiz node
  user_answers: Optional[list]    # list of answers from user
  feedback : Optional[list[str]]  # per-question feedback from evaluator
  scores : Optional[list[int]]    # int 0-100 from evaluator
  force_refresh: Optional[bool]   # set True by retry_tracker_node
  retries: int                    # int, starts at 0, max 2
  errors: Annotated[list[str],operator.add] # any node's error message