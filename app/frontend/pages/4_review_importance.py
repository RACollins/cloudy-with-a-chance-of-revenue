
import plotly.express as px
import streamlit as st

st.header("Stage 2 review: Feature importance")

job_id = st.session_state.get("job_id")
if not job_id:
    st.warning("Upload data first.")
    st.stop()

st.caption("Skeleton: load feature importance JSON from S3 in a later session.")

stub_features = [
    {"name": "temperature_2m_max", "importance": 0.35},
    {"name": "precipitation_sum", "importance": 0.28},
    {"name": "windspeed_10m_max", "importance": 0.15},
    {"name": "temperature_2m_min", "importance": 0.12},
    {"name": "value_lag_7", "importance": 0.10},
]

fig = px.bar(
    stub_features,
    x="importance",
    y="name",
    orientation="h",
    title="Weather & covariate importance (stub)",
)
st.plotly_chart(fig, use_container_width=True)
