# This file loads persisted state, runs the LangGraph pipeline in a loop, prints agent behavior, saves updated state after each cycle

import time
from datetime import datetime

from app.graph.builder import build_graph
from app.memory.store import load_state, save_state, normalize_state

# --- CONFIG ---
TICK_INTERVAL_SECONDS = 30


def run():
    print("🐶 Starting Ambient Pet Care Assistant...\n")

    # Load or initialize state
    state = load_state()

    # Build graph
    graph = build_graph()

    while True:
        print(f"\n⏱ Tick @ {datetime.utcnow().strftime('%H:%M:%S')}")

        # Run one cycle of the agent
        state = normalize_state(graph.invoke(state))

        # Print behavior if any
        last_message = getattr(state, "last_message", None)
        if last_message:
            print(f"🐶 Dog says: {last_message}")

        # Persist state
        save_state(state)

        # Wait for next cycle
        time.sleep(TICK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()