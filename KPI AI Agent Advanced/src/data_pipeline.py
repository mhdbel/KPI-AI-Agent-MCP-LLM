import pandas as pd
import openai
from src.powerbi import load_data_from_powerbi
from src.config import load_secrets

secrets = load_secrets()
openai.api_key = secrets["OPENAI_API_KEY"]

def load_data(file_path: str) -> tuple[pd.DataFrame, str]:
    df = pd.read_csv(file_path)
    llm_summary = get_data_summary(df)
    return df, llm_summary

def get_data_summary(df: pd.DataFrame) -> str:
    prompt = f"Summarize this dataset:\n{df.describe()}"
    return query_llm(prompt)

def get_preprocessing_suggestions(df: pd.DataFrame) -> str:
    prompt = f"Suggest preprocessing steps for this dataset:\n{df.head()}"
    return query_llm(prompt)

def query_llm(prompt: str) -> str:
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"