"""
Agent Dashboard — Keonhee's HQ
Reads status from Railway API server (STATUS_SERVER_URL env var).
Falls back to local agents/status.json if not set.

Status colors:
  green  (#00CC44) — working / done
  red    (#FF3355) — needs human action (blocked)
  gray   (#555566) — idle / not running
"""

import sys
import os
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
STATUS_SERVER_URL = os.environ.get("STATUS_SERVER_URL", "").rstrip("/")
_HERE = Path(__file__).resolve().parent
STATUS_FILE = _HERE / "agents" / "status.json"   # local fallback

AGENTS = [
    {"name": "GEO",        "icon": "🌐", "project": "geo-agency"},
    {"name": "Lead Intel", "icon": "🔍", "project": "lead-intelligence"},
    {"name": "SME Diag",   "icon": "🏭", "project": "sme-diagnostic-ai"},
    {"name": "Consulting", "icon": "📊", "project": "consulting-emulation"},
    {"name": "Next Role",  "icon": "🎯", "project": "next-ai-role"},
    {"name": "Discord Bot","icon": "💬", "project": "tools/discord-bot"},
]

STATUS_CONFIG = {
    "working": {"color": "#00CC44", "label": "● WORKING"},
    "blocked": {"color": "#FF3355", "label": "⚠ NEEDS ACTION"},
    "idle":    {"color": "#555566", "label": "○ IDLE"},
    "done":    {"color": "#00CC44", "label": "✓ DONE"},
}
DEFAULT_CONFIG = STATUS_CONFIG["idle"]

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_status() -> dict:
    # Try Railway server first
    if STATUS_SERVER_URL:
        try:
            req = urllib.request.Request(f"{STATUS_SERVER_URL}/status", method="GET")
            with urllib.request.urlopen(req, timeout=4) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            pass  # fall through to local file

    # Local file fallback
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    return {}


def relative_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        diff = int((datetime.now() - dt).total_seconds())
        if diff < 10:   return "just now"
        if diff < 60:   return f"{diff}s ago"
        if diff < 3600: return f"{diff // 60}m ago"
        return f"{diff // 3600}h ago"
    except Exception:
        return "—"


def render_card(agent: dict, agent_status: dict) -> None:
    status  = agent_status.get("status", "idle")
    task    = agent_status.get("task", "Not running")
    updated = agent_status.get("updated_at", "")

    cfg      = STATUS_CONFIG.get(status, DEFAULT_CONFIG)
    color    = cfg["color"]
    label    = cfg["label"]
    time_ago = relative_time(updated) if updated else "—"
    glow     = f"0 0 12px {color}55" if status in ("working", "blocked") else "none"

    st.markdown(f"""
    <div style="
        background: #141420;
        border: 2px solid {color};
        border-radius: 6px;
        padding: 18px 20px;
        margin-bottom: 10px;
        font-family: 'Courier New', monospace;
        box-shadow: {glow};
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:1.05em; color:#ffffff; font-weight:bold; letter-spacing:0.5px;">
                {agent['icon']}&nbsp;&nbsp;{agent['name']}
            </span>
            <span style="
                background:{color}1a;
                color:{color};
                border:1.5px solid {color};
                border-radius:3px;
                padding:3px 10px;
                font-size:0.72em;
                font-weight:bold;
                letter-spacing:1.5px;
            ">{label}</span>
        </div>
        <div style="color:#ccccdd; font-size:0.88em; line-height:1.5; margin-bottom:8px; min-height:1.4em;">
            {task}
        </div>
        <div style="color:#44445a; font-size:0.72em;">
            {agent['project']} &nbsp;·&nbsp; {time_ago}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Keonhee HQ", page_icon="🖥️", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #0a0a14; }
    .block-container { padding-top: 2rem; max-width: 620px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🖥️ KEONHEE HQ")

status_data = load_status()

working = sum(1 for a in AGENTS if status_data.get(a["name"], {}).get("status") == "working")
blocked = sum(1 for a in AGENTS if status_data.get(a["name"], {}).get("status") == "blocked")
idle    = len(AGENTS) - working - blocked

st.markdown(f"""
<div style="background:#0f0f1e; border:1px solid #222233; border-radius:5px;
    padding:10px 18px; margin-bottom:1.5rem; font-family:monospace;
    font-size:0.82em; display:flex; gap:20px; align-items:center;">
    <span style="color:#00CC44;">● {working} working</span>
    <span style="color:#FF3355;">⚠ {blocked} blocked</span>
    <span style="color:#555566;">○ {idle} idle</span>
    <span style="margin-left:auto; color:#333344; font-size:0.9em;">↻ 3s</span>
</div>
""", unsafe_allow_html=True)

for agent in AGENTS:
    render_card(agent, status_data.get(agent["name"], {}))

if "tick" not in st.session_state:
    st.session_state.tick = 0
st.session_state.tick += 1
time.sleep(3)
st.rerun()
