import streamlit as st

from app.frontend import api_client

st.header("Stage 1: Upload & preprocess")

with st.form("upload_form"):
    name = st.text_input("Name", value="Jane Doe")
    email = st.text_input("Email", value="jane@example.com")
    business = st.text_input("Business name", value="Example Co")
    lat = st.number_input("Latitude", value=51.5, format="%.4f")
    lon = st.number_input("Longitude", value=-0.12, format="%.4f")
    datetime_column = st.text_input("Datetime column", value="timestamp")
    target_column = st.text_input("Target column", value="value")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    submitted = st.form_submit_button("Upload & merge")

if submitted:
    if uploaded is None:
        st.error("Please upload a CSV file.")
    else:
        csv_content = uploaded.getvalue().decode("utf-8")
        payload = {
            "user_metadata": {
                "name": name,
                "email": email,
                "business_name": business,
                "location_lat": lat,
                "location_lon": lon,
            },
            "csv_content": csv_content,
            "datetime_column": datetime_column,
            "target_column": target_column,
        }
        try:
            result = api_client.preprocess(payload)
            st.session_state.job_id = result["job_id"]
            st.session_state.validation_summary = result["validation_summary"]
            st.success(f"Job created: {result['job_id']}")
            st.json(result["validation_summary"])
        except Exception as exc:
            st.error(f"Preprocess failed: {exc}")
