from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Interaction(BaseModel):
    timestamp: datetime
    type: str  # "suggestion", "user_response", etc.
    content: str


class PetState(BaseModel):
    # --- Visual/behavior state ---
    mood: str = "ready_for_walk"
    current_slot_index: int = 0
    current_calendar_status: str = "free"

    # --- Timing context ---
    last_interaction_time: Optional[datetime] = None

    # --- Memory ---
    interaction_history: List[Interaction] = Field(default_factory=list)

    # --- Runtime flags/messages used by graph + UI ---
    should_act: bool = False
    last_message: Optional[str] = None

    # --- Metadata ---
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def update_timestamp(self):
        self.last_updated = datetime.utcnow()