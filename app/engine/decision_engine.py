# Should the dog act or stay quiet?

# This file determines whether the agent should: act (suggest something, engage) or stay passive (ambient presence);
# Uses: mood, emotional state, user availability, time since last interaction

from datetime import datetime
from app.graph.state import PetState


# --- CONFIG ---
MIN_INTERACTION_INTERVAL_MIN = 2  
HIGH_LONELINESS_THRESHOLD = 0.7
HIGH_ENERGY_THRESHOLD = 0.75


def minutes_since_last_interaction(state: PetState, current_time: datetime) -> float:
    if not state.last_interaction_time:
        return float("inf")

    delta = current_time - state.last_interaction_time
    return delta.total_seconds() / 60


def should_act(state: PetState, current_time: datetime) -> bool:
    """
    Core decision logic: should the agent initiate an action?
    """

    # --- Avoid too frequent interactions ---
    if minutes_since_last_interaction(state, current_time) < MIN_INTERACTION_INTERVAL_MIN:
        return False

    # --- If user is busy, act only if strongly needed ---
    if state.user_availability == "busy":
        if state.loneliness > HIGH_LONELINESS_THRESHOLD:
            return True
        return False

    # --- If user is free ---
    if state.user_availability == "free":
        # playful dog wants interaction
        if state.mood == "playful":
            return True

        # bored or lonely → suggest something
        if state.loneliness > 0.5:
            return True

        # high energy → engage
        if state.energy > HIGH_ENERGY_THRESHOLD:
            return True

    return False