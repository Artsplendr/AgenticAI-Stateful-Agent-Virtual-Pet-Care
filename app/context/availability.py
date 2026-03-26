# Simulates user availability based on time cycles.
# Keeps the system deterministic and demo-friendly
# Acts as a plug-in point for future real integrations (calendar, activity tracking).
# Simulate a simple rhythm:
# - 3 minutes busy
# - 3 minutes free
# - repeats continuously

from datetime import datetime


def get_simulated_availability(current_time: datetime) -> str:
    """
    Simulates user availability based on time.

    Pattern:
    - 3 minutes busy
    - 3 minutes free
    - repeats continuously
    """

    minute = current_time.minute

    # Every 6-minute cycle
    if (minute % 6) < 3:
        return "busy"
    else:
        return "free"


def is_user_free(current_time: datetime) -> bool:
    return get_simulated_availability(current_time) == "free"