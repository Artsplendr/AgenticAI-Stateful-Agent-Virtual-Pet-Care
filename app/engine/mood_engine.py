# Keeps a simple, time-driven state cycle for the virtual dog.

from datetime import datetime
from app.graph.state import PetState
from app.context.calendar import get_simulated_calendar_view

# --- CONFIGURABLE PARAMETERS ---
STATE_CHANGE_INTERVAL_SECONDS = 30

def update_emotional_state(state: PetState, current_time: datetime) -> PetState:
    """
    Kept as a no-op for compatibility with graph node wiring.
    """
    return state


def update_mood(state: PetState) -> PetState:
    """
    Set dog mood from simulated calendar slot.
    """
    slots, slot_index, mood = get_simulated_calendar_view(
        current_time=datetime.utcnow(), slot_seconds=STATE_CHANGE_INTERVAL_SECONDS
    )
    state.mood = mood
    state.current_slot_index = slot_index
    state.current_calendar_status = slots[slot_index][2]
    return state