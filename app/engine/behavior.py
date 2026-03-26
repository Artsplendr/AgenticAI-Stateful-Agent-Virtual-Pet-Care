# What this file does: Generates the dog's response / suggestion
# Translates internal state -> natural language
# Uses deterministic text so mood + message always stay aligned.

from datetime import datetime
from app.graph.state import PetState, Interaction


def generate_behavior(state: PetState) -> str:
    """
    Generate state-aligned dog speech bubble text.
    This is deterministic to keep UI text perfectly matched with mood.
    """
    mood_message = {
        "sleeping": "Zzz... I am feeling sleepy. Let's rest together.",
        "need_attention": "I miss you... can we spend a moment together?",
        "ready_for_walk": "I am ready for a walk! Want to go outside?",
    }
    return mood_message.get(state.mood, "I am here with you.")

def create_interaction(state: PetState, message: str) -> Interaction:
    """
    Wraps a generated message into an interaction object.
    """

    return Interaction(
        timestamp=datetime.utcnow(),
        type="agent_message",
        content=message
    )


def update_history(state: PetState, interaction: Interaction) -> PetState:
    """
    Adds interaction to memory.
    """

    state.interaction_history.append(interaction)

    # Keep history manageable (last 50 entries)
    if len(state.interaction_history) > 50:
        state.interaction_history = state.interaction_history[-50:]

    return state