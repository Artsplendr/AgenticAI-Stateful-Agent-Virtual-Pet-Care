# Defines graph nodes for the simplified ambient loop:
# rotate mood -> generate matching message -> persist.

from datetime import datetime

from app.graph.state import PetState
from app.engine.mood_engine import update_mood
from app.engine.behavior import (
    generate_behavior,
    create_interaction,
    update_history,
)


# --- NODE 1: Rotate mood every interval ---
def node_update_mood(state: PetState) -> PetState:
    state = update_mood(state)
    return state


# --- NODE 2: Generate state-matched message ---
def node_generate_behavior(state: PetState) -> PetState:
    message = generate_behavior(state)
    interaction = create_interaction(state, message)

    state = update_history(state, interaction)

    # update last interaction timestamp
    state.last_interaction_time = interaction.timestamp

    # store last message for UI/logging
    state.last_message = message

    return state


# --- NODE 3: Update timestamp ---
def node_finalize(state: PetState) -> PetState:
    state.update_timestamp()
    return state