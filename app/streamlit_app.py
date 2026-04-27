from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Career Intelligence Engine",
    page_icon="🧠",
    layout="wide",
)


DATA_PATH = Path("data/outputs/ranked_jobs.json")


def load_data() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def tier_badge(tier: str) -> str:
    if tier == "HIGH":
        return "🟢 HIGH"
    if tier == "MEDIUM":
        return "🟡 MEDIUM"
    return "🔴 LOW"


def score_label(score: float) -> str:
    if score >= 5:
        return "Strong Target"
    if score >= 4:
        return "Good Target"
    if score >= 3:
        return "Possible Target"
    return "Weak Target"


data = load_data()

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
            margin-bottom: 0rem;
        }
        .subtitle {
            font-size: 1rem;
            opacity: 0.75;
            margin-bottom: 1.5rem;
        }
        .job-card {
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 18px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            background: rgba(255,255,255,0.035);
        }
        .small-muted {
            opacity: 0.72;
            font-size: 0.9rem;
        }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            margin-right: 0.3rem;
            margin-bottom: 0.3rem;
            font-size: 0.82rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🧠 Career Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A decision system that ranks job opportunities, classifies hiring intent, and surfaces positioning strategy.</div>',
    unsafe_allow_html=True,
)

if not data:
    st.warning("No ranked job output found. Run: `python run_pipeline.py --greenhouse stripe`")
    st.stop()


# -----------------------------
# Flatten data for filters/table
# -----------------------------
rows = []
for item in data:
    job = item.get("job", {})
    score = item.get("score", {})
    dna = item.get("job_dna", {})

    rows.append(
        {
            "Rank": item.get("rank"),
            "Tier": item.get("tier"),
            "Score": score.get("total", 0),
            "Title": job.get("title"),
            "Company": job.get("company"),
            "Location": job.get("location"),
            "Hiring Intent": dna.get("hiring_intent"),
            "Operator Type": dna.get("operator_type"),
            "Primary Signal": dna.get("primary_signal"),
            "Matched Skills": ", ".join(score.get("matched_skills", [])),
            "Matched Tools": ", ".join(score.get("matched_tools", [])),
            "URL": job.get("url"),
        }
    )

df = pd.DataFrame(rows)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Control Panel")

tier_options = sorted(df["Tier"].dropna().unique().tolist())
selected_tiers = st.sidebar.multiselect(
    "Tier",
    tier_options,
    default=[tier for tier in ["HIGH", "MEDIUM"] if tier in tier_options],
)

intent_options = sorted(df["Hiring Intent"].dropna().unique().tolist())
selected_intents = st.sidebar.multiselect(
    "Hiring Intent",
    intent_options,
    default=intent_options,
)

operator_options = sorted(df["Operator Type"].dropna().unique().tolist())
selected_operators = st.sidebar.multiselect(
    "Operator Type",
    operator_options,
    default=operator_options,
)

min_score = st.sidebar.slider(
    "Minimum Score",
    min_value=0.0,
    max_value=float(max(df["Score"].max(), 6.0)),
    value=3.0,
    step=0.1,
)

search = st.sidebar.text_input("Search title/company/skills", "")

show_count = st.sidebar.slider("Jobs to display", 5, 50, 15)


filtered_df = df[
    (df["Tier"].isin(selected_tiers))
    & (df["Hiring Intent"].isin(selected_intents))
    & (df["Operator Type"].isin(selected_operators))
    & (df["Score"] >= min_score)
]

if search:
    q = search.lower()
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: q in " ".join(row.astype(str)).lower(), axis=1)
    ]

filtered_df = filtered_df.sort_values(["Score", "Rank"], ascending=[False, True])


# -----------------------------
# Top metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Jobs", len(df))

with col2:
    st.metric("Filtered Jobs", len(filtered_df))

with col3:
    st.metric("High Targets", int((filtered_df["Tier"] == "HIGH").sum()))

with col4:
    st.metric("Avg Score", round(filtered_df["Score"].mean(), 2) if len(filtered_df) else 0)


# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["🎯 Ranked Targets", "📊 Signal Table", "🧬 Job DNA Detail"])


with tab1:
    st.subheader("Ranked Career Targets")

    selected_records = filtered_df.head(show_count).to_dict("records")

    for row in selected_records:
        source_item = next((x for x in data if x.get("rank") == row["Rank"]), None)
        if not source_item:
            continue

        job = source_item.get("job", {})
        score = source_item.get("score", {})
        dna = source_item.get("job_dna", {})

        st.markdown('<div class="job-card">', unsafe_allow_html=True)

        left, right = st.columns([3, 1])

        with left:
            st.markdown(f"### {row['Rank']}. {job.get('title')} @ {job.get('company')}")
            st.markdown(
                f"**{tier_badge(source_item.get('tier'))}** · "
                f"**Score:** `{score.get('total')}` · "
                f"**{score_label(float(score.get('total', 0))) }**"
            )
            st.markdown(f'<div class="small-muted">{job.get("location") or "Location not listed"}</div>', unsafe_allow_html=True)

        with right:
            url = job.get("url")
            if url:
                st.link_button("Open Job", url)

        st.markdown("#### Company Need")
        st.write(source_item.get("likely_business_problem"))

        st.markdown("#### Positioning Angle")
        st.write(source_item.get("positioning_angle"))

        c1, c2, c3 = st.columns(3)
        c1.metric("Hiring Intent", dna.get("hiring_intent", "—"))
        c2.metric("Operator Type", dna.get("operator_type", "—"))
        c3.metric("Primary Signal", dna.get("primary_signal", "—"))

        st.markdown("#### Wrong-Hire Risk")
        st.warning(dna.get("wrong_hire_risk", "—"))

        st.markdown("#### Matched Evidence")
        skills = score.get("matched_skills", [])
        tools = score.get("matched_tools", [])
        roles = score.get("matched_titles", [])

        st.markdown("**Skills**")
        st.markdown(" ".join([f'<span class="pill">{x}</span>' for x in skills]) or "None", unsafe_allow_html=True)

        st.markdown("**Tools**")
        st.markdown(" ".join([f'<span class="pill">{x}</span>' for x in tools]) or "None", unsafe_allow_html=True)

        st.markdown("**Roles**")
        st.markdown(" ".join([f'<span class="pill">{x}</span>' for x in roles]) or "None", unsafe_allow_html=True)

        with st.expander("Proof Points Needed"):
            for proof in dna.get("proof_points_needed", []):
                st.write(f"- {proof}")

        st.markdown("</div>", unsafe_allow_html=True)


with tab2:
    st.subheader("Signal Table")
    st.dataframe(
        filtered_df[
            [
                "Rank",
                "Tier",
                "Score",
                "Title",
                "Company",
                "Location",
                "Hiring Intent",
                "Operator Type",
                "Matched Skills",
                "Matched Tools",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


with tab3:
    st.subheader("Job DNA Inspector")

    titles = filtered_df["Title"].tolist()
    selected_title = st.selectbox("Select a job", titles)

    selected_row = filtered_df[filtered_df["Title"] == selected_title].iloc[0]
    selected_item = next((x for x in data if x.get("rank") == selected_row["Rank"]), None)

    if selected_item:
        dna = selected_item.get("job_dna", {})
        score = selected_item.get("score", {})
        job = selected_item.get("job", {})

        st.markdown(f"## {job.get('title')} @ {job.get('company')}")
        st.markdown(f"**Score:** {score.get('total')} | **Tier:** {selected_item.get('tier')}")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### DNA Summary")
            st.write(f"**Hiring Intent:** {dna.get('hiring_intent')}")
            st.write(f"**Operator Type:** {dna.get('operator_type')}")
            st.write(f"**Primary Signal:** {dna.get('primary_signal')}")
            st.write(f"**Success Profile:** {dna.get('likely_success_profile')}")

        with c2:
            st.markdown("### Signal Scores")
            signal_scores = dna.get("signal_scores", {})
            if signal_scores:
                signal_df = pd.DataFrame(
                    [{"Signal": k, "Score": v} for k, v in signal_scores.items()]
                ).sort_values("Score", ascending=False)
                st.bar_chart(signal_df.set_index("Signal"))

        st.markdown("### Positioning Hook")
        st.success(dna.get("positioning_hook", "—"))

        st.markdown("### Wrong-Hire Risk")
        st.warning(dna.get("wrong_hire_risk", "—"))

        st.markdown("### Proof Points Needed")
        for proof in dna.get("proof_points_needed", []):
            st.write(f"- {proof}")