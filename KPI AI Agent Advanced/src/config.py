import streamlit as st

def load_secrets() -> dict:
    return {
        "OPENAI_API_KEY": st.secrets["OPENAI_API_KEY"],
        "POWERBI_ACCESS_TOKEN": st.secrets["POWERBI_ACCESS_TOKEN"],
        "POWERBI_DATASET_ID": st.secrets["POWERBI_DATASET_ID"]
    }