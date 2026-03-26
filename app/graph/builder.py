# This file builds the LangGraph workflow, connects all nodes in the correct order, defines the execution flow (edges), returns a runnable graph    

from langgraph.graph import StateGraph, END

from app.graph.state import PetState
from app.graph.nodes import (
    node_update_mood,
    node_generate_behavior,
    node_finalize,
)


def build_graph():
    """
    Builds and compiles the LangGraph state machine.
    """

    # Initialize graph with state schema
    graph = StateGraph(PetState)

    # --- Add nodes ---
    graph.add_node("mood", node_update_mood)
    graph.add_node("behavior", node_generate_behavior)
    graph.add_node("finalize", node_finalize)

    # --- Define edges (execution flow) ---
    graph.set_entry_point("mood")
    graph.add_edge("mood", "behavior")
    graph.add_edge("behavior", "finalize")
    graph.add_edge("finalize", END)

    # Compile graph
    return graph.compile()