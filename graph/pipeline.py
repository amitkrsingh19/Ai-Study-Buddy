from langgraph.checkpoint.memory import InMemorySaver

from langgraph.graph import StateGraph, START, END

from graph.state import State
from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.input_parser import input_parser_node, input_router

graph_builder = StateGraph(State)
checkpointer= InMemorySaver()

graph_builder.add_node("input_parser", input_parser_node)
graph_builder.add_node("planner_agent", planner_node)
graph_builder.add_node("researcher_agent", researcher_node)

graph_builder.add_edge(START, "input_parser")
graph_builder.add_conditional_edges("input_parser",input_router,{
  "planner_agent":"planner_agent",
    END : END
})
graph_builder.add_edge("planner_agent", "researcher_agent")
graph_builder.add_edge("researcher_agent", END)

graph = graph_builder.compile(checkpointer=checkpointer)

