from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Career Intelligence Engine", layout="wide")
st.title("Career Intelligence Engine")

output_path = Path("data/outputs/ranked_jobs.json")

if not output_path.exists():
    st.warning("No ranked job output found yet. Run the pipeline first.")
    st.stop()

data = json.loads(output_path.read_text(encoding="utf-8"))

for item in data:
    with st.container():
        st.subheader(f"{item['rank']}. {item['job']['title']} @ {item['job']['company']}")
        st.write(f"**Tier:** {item['tier']} | **Score:** {item['score']['total']}")
        st.write(f"**Location:** {item['job']['location']}")
        st.write(f"**Problem:** {item['likely_business_problem']}")
        st.write(f"**Positioning Angle:** {item['positioning_angle']}")
        st.write(f"**Matched Skills:** {', '.join(item['score']['matched_skills']) or 'none'}")
        st.write(f"**Matched Tools:** {', '.join(item['score']['matched_tools']) or 'none'}")
        st.divider()