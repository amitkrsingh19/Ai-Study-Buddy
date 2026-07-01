## Graph Pipeline

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from graph.state import State
from graph.router import route_after_memory, route_after_evaluation, route_after_input

from agents.input_parser import input_parser_node
from agents.planner import planner_node
from agents.memory_reader import memory_reader_node
from agents.researcher import researcher_node
from agents.memory_writer import memory_writer_node
from agents.quiz import quiz_node
from agents.evaluator import evaluator_node
from agents.retry_tracker import retry_tracker_node
from agents.next_day import next_day_node


graph_builder = StateGraph(State)

## register all nodes
graph_builder.add_node("input_parser", input_parser_node)
graph_builder.add_node("planner_node", planner_node)
graph_builder.add_node("memory_reader_node", memory_reader_node)
graph_builder.add_node("researcher_node", researcher_node)
graph_builder.add_node("memory_writer_node", memory_writer_node)
graph_builder.add_node("quiz_node", quiz_node)
graph_builder.add_node("evaluator_node", evaluator_node)
graph_builder.add_node("retry_tracker_node", retry_tracker_node)
graph_builder.add_node("next_day_node", next_day_node)

## wire edges
graph_builder.add_edge(START, "input_parser")

graph_builder.add_conditional_edges(
    "input_parser",
    route_after_input,
    {
        "planner_node": "planner_node",
        END: END
    }
)

graph_builder.add_edge("planner_node", "memory_reader_node")

graph_builder.add_conditional_edges(
    "memory_reader_node",
    route_after_memory,
    {
        "researcher_node": "researcher_node",
        "quiz_node": "quiz_node"
    }
)

graph_builder.add_edge("researcher_node", "memory_writer_node")
graph_builder.add_edge("memory_writer_node", "quiz_node")
graph_builder.add_edge("quiz_node", "evaluator_node")


graph_builder.add_conditional_edges(
    "evaluator_node",
    route_after_evaluation,
    {
        "retry_tracker_node": "retry_tracker_node",
        "next_day_node": "next_day_node",
        END: END
    }
)

graph_builder.add_edge("retry_tracker_node", "researcher_node")
graph_builder.add_edge("next_day_node", "memory_reader_node")


## compile with checkpointer for session persistence
checkpointer = InMemorySaver()
graph = graph_builder.compile(
  checkpointer=checkpointer,
  interrupt_before=["quiz_node","evaluator_node"]
  )