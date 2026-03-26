# This UI displays the dog, shows current mood, displays speech bubbles, auto-refreshes (ambient behavior), visual emotional feedback

import streamlit as st
import streamlit.components.v1 as components
import time
import sys
import os
import base64
from pathlib import Path

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.builder import build_graph
from app.memory.store import load_state, save_state, normalize_state
from app.context.calendar import CALENDAR_SLOTS

# --- CONFIG ---
REFRESH_INTERVAL = 30  # seconds

# --- PAGE SETUP ---
st.set_page_config(page_title="🐶 Ambient Virtual Pet Care", layout="centered")

st.title("🐶 Ambient Virtual Pet Care")
st.caption("Your stateful AI companion")

# Hide any legacy bottom bubble block from older UI versions.
st.markdown(
    """
    <style>
      .main .block-container {
        max-width: 2400px; /* ~30% wider than previous setting */
        width: 98vw;
        padding: 10px 14px;
      }
      div[style*="margin-top:20px"][style*="padding:15px"][style*="border-radius:15px"] {
        display: none !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- LOAD STATE ---
state = load_state()
graph = build_graph()

# --- RUN ONE STEP ---
state = normalize_state(graph.invoke(state))
save_state(state)

# --- UI HELPERS ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_BY_MOOD = {
    "need_attention": "need-attention-dog.mp4",
    "ready_for_walk": "ready-for-walk-dog.mp4",
    "sleeping": "sleeping-dog.mp4",
}
VIDEO_FRAME_HEIGHT_BY_MOOD = {
    "ready_for_walk": 640,
    "need_attention": 680,
    "sleeping": 820,
}


def get_background_color(mood):
    return {
        "ready_for_walk": "#FFF3CD",
        "need_attention": "#D1ECF1",
        "sleeping": "#E6E6FA",
    }.get(mood, "#FFFFFF")


def mood_label(mood: str) -> str:
    return mood.replace("_", " ").title()


def resolve_video_path(mood: str) -> Path | None:
    filename = VIDEO_BY_MOOD.get(mood)
    if not filename:
        return None

    video_path = PROJECT_ROOT / "assets" / filename
    return video_path if video_path.exists() else None


def render_calendar_panel(slots, mood: str, current_index: int) -> int:
    frame_height = VIDEO_FRAME_HEIGHT_BY_MOOD.get(mood, 720)
    # Keep calendar compact: include explicit trailing spacer visibility.
    estimated_content_height = (len(slots) * 58) + 76
    panel_height = min(frame_height, estimated_content_height)
    rows = []
    for idx, (start, end, status, label) in enumerate(slots):
        is_current = idx == current_index
        is_last = idx == len(slots) - 1

        status_color = "#FADBD8" if status == "busy" else "#D5F5E3"
        if status == "sleeping":
            status_color = "#E8DAEF"

        border = "2px solid #1f2937" if is_current else "1px solid #d1d5db"
        row_margin_bottom = 0 if is_last else 10
        rows.append(
            f"""
            <div style="padding:10px 12px; border-radius:10px; border:{border};
                        margin-bottom:{row_margin_bottom}px; background:{status_color};">
                <div style="font-weight:600; font-size:14px; white-space:nowrap;">{start} - {end}</div>
                <div style="font-size:13px; white-space:nowrap;">{label} • {status.title()}</div>
            </div>
            """
        )

    html = f"""
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        background: transparent;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .calendar-wrap {{
        height: auto;
        overflow: visible;
        padding: 14px 14px 10px 14px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        border-bottom: 2px solid #d1d5db;
        background: #ffffff;
        box-sizing: border-box;
      }}
      .calendar-title {{
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 10px;
      }}
    </style>
    <div class="calendar-wrap">
      <div class="calendar-title">Personal Calendar</div>
      {''.join(rows)}
      <div style="height:10px;"></div>
    </div>
    """
    components.html(html, height=panel_height + 16, scrolling=False)
    return panel_height


@st.cache_data(show_spinner=False)
def read_video_base64(video_file: str) -> str:
    with open(video_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def render_ambient_video(video_path: Path, mood: str, frame_height: int | None = None):
    video_b64 = read_video_base64(str(video_path))
    if frame_height is None:
        frame_height = VIDEO_FRAME_HEIGHT_BY_MOOD.get(mood, 720)
    components.html(
        f"""
        <style>
          html, body {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
          }}
          .video-wrap {{
            width: 100%;
            height: 100%;
            background: #000;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
          }}
          .video-wrap video {{
            width: 100%;
            height: 100%;
            display: block;
            object-fit: contain;
            object-position: center center;
          }}
        </style>
        <div class="video-wrap">
        <video
            autoplay
            muted
            loop
            playsinline
            preload="auto"
        >
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4" />
        </video>
        </div>
        """,
        height=frame_height,
        scrolling=False,
    )


# --- DISPLAY ---
bg_color = get_background_color(state.mood)
video_path = resolve_video_path(state.mood)

st.markdown(
    f"""
    <div style="background-color:{bg_color}; padding:30px; border-radius:20px; text-align:center;">
        <h3>State: {mood_label(state.mood)}</h3>
        <div style="
            margin-top:12px;
            padding:12px 14px;
            border-radius:12px;
            background-color:rgba(255,255,255,0.82);
            box-shadow:0px 1px 4px rgba(0,0,0,0.08);
            display:inline-block;
            max-width:92%;
            font-size:1.2em;
        ">
            💬 {getattr(state, "last_message", "I am here with you.")}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if video_path and video_path.exists():
    left_col, right_col = st.columns([1.575, 2.425], gap="medium")
    with left_col:
        shared_panel_height = render_calendar_panel(
            CALENDAR_SLOTS, state.mood, getattr(state, "current_slot_index", 0)
        )
    with right_col:
        render_ambient_video(video_path, state.mood, shared_panel_height)
else:
    st.warning(
        "Mood video not found for this state. Add files in assets/: "
        "need-attention-dog.mp4, ready-for-walk-dog.mp4, sleeping-dog.mp4."
    )

# --- AUTO REFRESH ---
time.sleep(REFRESH_INTERVAL)
st.rerun()