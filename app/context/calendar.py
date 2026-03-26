from datetime import datetime
from typing import List, Tuple


# (start, end, status, label)
CALENDAR_SLOTS: List[Tuple[str, str, str, str]] = [
    ("07:00", "09:00", "free", "Morning routine"),
    ("09:00", "12:00", "busy", "Deep work"),
    ("12:00", "13:00", "free", "Lunch break"),
    ("13:00", "17:00", "busy", "Meetings / work"),
    ("17:00", "20:00", "free", "Exercise / walk"),
    ("20:00", "22:00", "busy", "Family / tasks"),
    ("22:00", "07:00", "sleeping", "Sleep time"),
]


def get_simulated_calendar_view(
    current_time: datetime | None = None, slot_seconds: int = 30
) -> tuple[List[Tuple[str, str, str, str]], int, str]:
    """
    Simulate a moving calendar where one slot becomes active every `slot_seconds`.
    Returns (slots, active_index, mood).
    """
    now = current_time or datetime.utcnow()
    active_index = int(now.timestamp() // slot_seconds) % len(CALENDAR_SLOTS)
    _start, _end, status, _label = CALENDAR_SLOTS[active_index]

    if status == "sleeping":
        mood = "sleeping"
    elif status == "busy":
        mood = "need_attention"
    else:
        mood = "ready_for_walk"

    return CALENDAR_SLOTS, active_index, mood
