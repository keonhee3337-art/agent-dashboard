"""
Agent Dashboard — Keonhee's HQ
Pixel-art style cards showing status of each active Claude terminal.
Polls agents/status.json every 3 seconds.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

import streamlit as st

# ---------------------------------------------------------------------------
# Path resolution — works locally and on Streamlit Cloud
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent          # tools/agent-dashboard/
_PROJECT_ROOT = _HERE.parent.parent              # MCP_Agentic AI/
STATUS_FILE = _PROJECT_ROOT / "agents" / "status.json"

# ---------------------------------------------------------------------------
# Agent config
# ---------------------------------------------------------------------------
AGENTS = [
    {"name": "GEO",        "icon": "🌐", "project": "geo-agency"},
    {"name": "Lead Intel", "icon": "🔍", "project": "lead-intelligence"},
    {"name": "SME Diag",   "icon": "🏭", "project": "sme-diagnostic-ai"},
    {"name": "Consulting", "icon": "📊", "project": "consulting-emulation"},
    {"name": "Next Role",  "icon": "🎯", "project": "next-ai-role"},
]

STATUS_COLORS = {
    "working": "#FFD700",   # gold
    "idle":    "#555566",   # dark gray
    "done":    "#00CC66",   # green
}

STATUS_LABELS = {
    "working": "● WORKING",
    "idle":    "○ IDLE",
    "done":    "✓ DONE",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_status() -> dict:
    """Read status.json. Returns empty dict if missing or malformed."""
    if not STATUS_FILE.exists():
        return {}
    try:
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def relative_time(iso_str: str) -> str:
    """Convert ISO timestamp to human-readable relative time."""
    try:
        dt = datetime.fromisoformat(iso_str)
        # Make naive datetime timezone-aware (local time assumed)
        now = datetime.now()
        diff = int((now - dt).total_seconds())
        if diff < 10:
            return "just now"
        if diff < 60:
            return f"{diff}s ago"
        if diff < 3600:
            return f"{diff // 60}m ago"
        return f"{diff // 3600}h ago"
    except Exception:
        return "—"


def render_card(agent: dict, agent_status: dict) -> None:
    """Render a single agent card."""
    status = agent_status.get("status", "idle")
    task = agent_status.get("task", "Idle")
    updated = agent_status.get("updated_at", "")

    color = STATUS_COLORS.get(status, STATUS_COLORS["idle"])
    label = STATUS_LABELS.get(status, "○ IDLE")
    time_ago = relative_time(updated) if updated else "—"

    # Pixel-art card via HTML/CSS
    card_html = f"""
    <div style="
        background: #1a1a2e;
        border: 2px solid {color};
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 8px;
        font-family: 'Courier New', monospace;
        box-shadow: 0 0 8px {color}44;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 1.1em; color: #ffffff; font-weight: bold;">
                {agent['icon']} {agent['name']}
            </span>
            <span style="
                background: {color}22;
                color: {color};
                border: 1px solid {color};
                border-radius: 2px;
                padding: 2px 8px;
                font-size: 0.75em;
                font-weight: bold;
                letter-spacing: 1px;
            ">{label}</span>
        </div>
        <div style="color: #aaaacc; font-size: 0.85em; margin-bottom: 6px;">
            {task}
        </div>
        <div style="color: #666688; font-size: 0.75em;">
            {agent['project']} · {time_ago}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Keonhee HQ",
    page_icon="🖥️",
    layout="centered",
)

# Dark background
st.markdown("""
<style>
    .stApp { background-color: #0d0d1a; }
    .block-container { padding-top: 2rem; max-width: 600px; }
    h1, h2, h3 { font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main render loop
# ---------------------------------------------------------------------------
st.markdown("## 🖥️ KEONHEE HQ")
st.markdown("<div style='color: #555577; font-family: monospace; font-size: 0.85em; margin-bottom: 1.5rem;'>Agent Status Dashboard — live every 3s</div>", unsafe_allow_html=True)

status_data = load_status()

# Summary bar
working = sum(1 for a in AGENTS if status_data.get(a["name"], {}).get("status") == "working")
done    = sum(1 for a in AGENTS if status_data.get(a["name"], {}).get("status") == "done")
idle    = len(AGENTS) - working - done

summary_html = f"""
<div style="
    background: #111128;
    border: 1px solid #333355;
    border-radius: 4px;
    padding: 10px 16px;
    margin-bottom: 1.5rem;
    font-family: monospace;
    font-size: 0.85em;
    color: #888899;
    display: flex;
    gap: 24px;
">
    <span style="color: #FFD700;">● {working} working</span>
    <span style="color: #00CC66;">✓ {done} done</span>
    <span style="color: #555566;">○ {idle} idle</span>
    <span style="margin-left: auto; color: #444455;">↻ auto-refresh</span>
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)

# Agent cards
for agent in AGENTS:
    agent_status = status_data.get(agent["name"], {})
    render_card(agent, agent_status)

# Refresh counter (drives rerun)
if "tick" not in st.session_state:
    st.session_state.tick = 0

st.session_state.tick += 1
time.sleep(3)
st.rerun()
