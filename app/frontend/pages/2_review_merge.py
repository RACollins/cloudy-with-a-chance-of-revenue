import streamlit as st

from app.frontend import api_client

st.header("Stage 1 review: Approve merged data")

job_id = st.session_state.get("job_id")
if not job_id:
    st.warning("Upload data first.")
    st.stop()

summary = st.session_state.get("validation_summary")
if summary:
    st.subheader("Validation summary")
    st.json(summary)

if st.button("Approve training"):
    try:
        result = api_client.approve_merge(job_id)
        st.success(f"Training started: {result.get('sagemaker_training_job_name')}")
    except Exception as exc:
        st.error(f"Could not start training: {exc}")
