import json

from langgraph.graph import StateGraph, START, END

from graph.state import State
from agents.planner import planner_node
from agents.researcher import researcher_node

graph_builder = StateGraph(State)

graph_builder.add_node("planner_agent", planner_node)
graph_builder.add_node("researcher_agent", researcher_node)

graph_builder.add_edge(START, "planner_agent")
graph_builder.add_edge("planner_agent", "researcher_agent")
graph_builder.add_edge("researcher_agent", END)

graph = graph_builder.compile()

