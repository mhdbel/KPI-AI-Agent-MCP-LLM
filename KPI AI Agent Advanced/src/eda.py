import pandas as pd
from pandas_profiling import ProfileReport
from src.config import query_llm

def generate_eda_report(df: pd.DataFrame, sample_size: int = None) -> tuple[ProfileReport, str]:
    """
    Generate an EDA report and LLM-based explanation.
    
    Args:
        df (pd.DataFrame): Input dataset.
        sample_size (int, optional): Number of rows to sample for large datasets.
    
    Returns:
        tuple: (ProfileReport, LLM-generated explanation)
    """
    if sample_size and len(df) > sample_size:
        df = df.sample(sample_size, random_state=42)
    
    profile = ProfileReport(df, explorative=True)
    summary = (
        f"Dataset Overview:\n{profile.get_description()['table']}\n"
        f"Missing Values:\n{profile.get_description()['missing']}\n"
        f"Correlations:\n{profile.get_description()['correlations']}"
    )
    explanation = get_eda_explanation(summary)
    return profile, explanation

def get_eda_explanation(profile_summary: str) -> str:
    """
    Generate an LLM-based explanation of the EDA report.
    
    Args:
        profile_summary (str): Summary of the EDA report.
    
    Returns:
        str: LLM-generated explanation.
    """
    prompt = (
        f"Explain this dataset's profile in simple terms:\n"
        f"{profile_summary}\n"
        "Highlight any key insights, such as missing values, correlations, or unusual patterns."
    )
    return query_llm(prompt)
