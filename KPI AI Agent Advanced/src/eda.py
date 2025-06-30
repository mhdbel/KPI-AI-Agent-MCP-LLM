import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas_profiling import ProfileReport
import openai

def generate_eda_report(df: pd.DataFrame) -> tuple[ProfileReport, str]:
    profile = ProfileReport(df, explorative=True)
    explanation = get_eda_explanation(profile.to_json())
    return profile, explanation

def get_eda_explanation(profile_json: str) -> str:
    prompt = f"Explain this dataset's profile:\n{profile_json}"
    return query_llm(prompt)

def plot_kpi_distribution(q1_df: pd.DataFrame, q4_df: pd.DataFrame, kpi: str) -> tuple[plt.Figure, str]:
    fig = plot_kpi(q1_df, q4_df, kpi)
    explanation = explain_plot(fig, kpi)
    return fig, explanation

def plot_kpi(q1_df: pd.DataFrame, q4_df: pd.DataFrame, kpi: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.kdeplot(q1_df[kpi], ax=ax, label="Q1", shade=True)
    sns.kdeplot(q4_df[kpi], ax=ax, label="Q4", shade=True)
    ax.set_title(f"{kpi} Distribution Comparison")
    ax.legend()
    return fig

def explain_plot(fig: plt.Figure, kpi: str) -> str:
    prompt = f"Explain this plot for '{kpi}':\n{plt.gcf().canvas.tostring_rgb()}"
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