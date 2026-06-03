import streamlit as st

from app.frontend import api_client

st.header("Stage 3: Forecast")

job_id = st.session_state.get("job_id")
if not job_id:
    st.warning("Upload data first.")
    st.stop()

horizon = st.slider("Forecast horizon (days)", min_value=1, max_value=30, value=7)

if st.button("Run forecast"):
    try:
        result = api_client.run_forecast(job_id, horizon=horizon)
        st.session_state.forecast = result
        st.success("Forecast complete.")
        st.json(result)
    except Exception as exc:
        st.error(f"Forecast failed: {exc}")
