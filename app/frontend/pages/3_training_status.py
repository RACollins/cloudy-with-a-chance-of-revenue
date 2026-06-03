
import streamlit as st

from app.frontend import api_client

st.header("Stage 2: Training status")

job_id = st.session_state.get("job_id")
if not job_id:
    st.warning("Upload data first.")
    st.stop()

if st.button("Refresh status"):
    try:
        status = api_client.get_status(job_id)
        st.session_state.job_status = status
        st.json(status)
    except Exception as exc:
        st.error(f"Status check failed: {exc}")

if st.session_state.get("job_status"):
    job_status = st.session_state.job_status.get("job_status")
    if job_status == "AWAITING_FORECAST_APPROVAL":
        st.success("Training complete. Review feature importance next.")
    elif job_status == "TRAINING":
        st.info("Training in progress. Poll again in a few minutes.")
