import streamlit as st

st.set_page_config(page_title="Cloudy with a Chance of Revenue", layout="wide")

st.title("Cloudy with a Chance of Revenue")
st.markdown(
    """
    Upload historical time series data, review merged weather covariates,
    approve training, review feature importance, then generate a forecast.
    """
)

if "job_id" not in st.session_state:
    st.session_state.job_id = None

st.info("Use the sidebar pages to walk through each stage of the pipeline.")
if st.session_state.job_id:
    st.success(f"Current job: `{st.session_state.job_id}`")
