import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
from src.data_pipeline import load_data, load_data_powerbi
from src.eda import generate_eda_report, plot_kpi_distribution
from src.ahp_module import AHPAnalysis
from src.config import load_secrets

st.set_page_config(
    page_title="Remote Fix KPI Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    secrets = load_secrets()
    openai.api_key = secrets["OPENAI_API_KEY"]
    
    # SIDEBAR: Data Source Configuration
    st.sidebar.header("Data Source Configuration")
    data_source = st.sidebar.radio(
        "Select Data Source",
        ["CSV Files", "Power BI"],
        index=0,
        help="Choose between CSV files or Power BI datasets."
    )
    
    q1_df, q4_df = None, None
    
    # Load data based on source
    if data_source == "CSV Files":
        try:
            q1_path = "KPI AI Agent Advanced/data/Q1 2025.csv" # Corrected path
            q4_path = "KPI AI Agent Advanced/data/Q4 2024.csv" # Corrected path
            q1_df, q1_summary = load_data(q1_path)
            q4_df, q4_summary = load_data(q4_path)
        except FileNotFoundError as e:
            st.error(f"File not found: {e.filename}. Please ensure the data files are in the 'KPI AI Agent Advanced/data/' directory and match the specified names.")
            return
        except Exception as e:
            st.error(f"Error loading CSV files: {str(e)}")
            return
    else:
        with st.sidebar.expander("Power BI Settings"):
            dataset_id = st.text_input(
                "Dataset ID",
                value=secrets["POWERBI_DATASET_ID"]
            )
            table_q1 = st.text_input("Q1 Table Name", "cases_Q1_current_year")
            table_q4 = st.text_input("Q4 Table Name", "cases_Q4_2024")
            access_token = st.text_input(
                "Access Token",
                value=secrets["POWERBI_ACCESS_TOKEN"],
                type="password"
            )
            
            if st.button("Load Power BI Data"):
                if not dataset_id or not access_token:
                    st.error("Dataset ID and Access Token are required.")
                    return
                
                source_config = {
                    "dataset_id": dataset_id,
                    "access_token": access_token,
                    "table_name": table_q1
                }
                q1_df, _ = load_data_powerbi(source_config)
                
                source_config["table_name"] = table_q4
                q4_df, _ = load_data_powerbi(source_config)
                
                if q1_df.empty or q4_df.empty:
                    st.error("Power BI returned empty datasets.")
                    return
    
    # Proceed only if data is loaded
    if q1_df is not None and q4_df is not None:
        st.title("Remote Fix KPI Analysis Dashboard")
        
        # DATA SUMMARY
        st.header("📊 Data Overview")
        st.write("Q1 Summary:", q1_summary)
        st.write("Q4 Summary:", q4_summary)
        
        # EDA WITH LLM EXPLANATIONS
        st.header("🔍 Exploratory Data Analysis")
        eda_profile, eda_explanation = generate_eda_report(q1_df)
        st.write("EDA Explanation:", eda_explanation)
        
        # KPI DISTRIBUTION PLOT
        st.header("📈 KPI Distribution Comparison")
        numeric_cols = list(q1_df.select_dtypes(include="number").columns)
        selected_kpi = st.selectbox(
            "Select KPI",
            numeric_cols,
            index=0,
            key="kpi_selector"
        )
        
        if selected_kpi not in q4_df.columns:
            st.error(f"KPI '{selected_kpi}' not found in Q4 data.")
        else:
            try:
                fig, plot_explanation = plot_kpi_distribution(q1_df, q4_df, selected_kpi)
                st.pyplot(fig, use_container_width=True)
                st.write("Plot Explanation:", plot_explanation)
            except Exception as e:
                st.error(f"Plotting error: {str(e)}")
        
        # AHP DECISION ANALYSIS
        st.header("🎯 AHP Decision Analysis")
        st.write("Adjust criteria importance using the sliders below:")
        
        # Default criteria comparisons
        default_comparisons = {
            ('Case Complexity', 'Staffing Levels'): 3,
            ('Case Complexity', 'Process Changes'): 5,
            ('Case Complexity', 'Technology Adjustments'): 7,
            ('Staffing Levels', 'Process Changes'): 3,
            ('Staffing Levels', 'Technology Adjustments'): 5,
            ('Process Changes', 'Technology Adjustments'): 3
        }
        
        # Create sliders for each comparison pair
        custom_weights = {}
        for pair in default_comparisons:
            label = f"{pair[0]} vs {pair[1]}"
            default_val = default_comparisons[pair]
            slider = st.slider(
                label,
                1, 9,
                default_val,
                key=f"slider_{pair[0]}_{pair[1]}",
                help="1 (Equal) to 9 (Extremely More Important)"
            )
            custom_weights[pair] = slider
        
        try:
            ahp = AHPAnalysis(custom_weights)
            st.write("AHP Explanation:", ahp.get_explanation())
            
            # What-If Analysis
            st.subheader("What-If Scenario")
            new_weight = st.slider(
                "Adjust 'Case Complexity' weight",
                0.0,
                1.0,
                0.5,
                key="whatif_slider"
            )
            # Example: Modify one criteria pair
            modified_weights = custom_weights.copy()
            modified_weights[('Case Complexity', 'Process Changes')] = int(new_weight * 9)
            new_weights = ahp.get_what_if(modified_weights)
            st.write("New Priorities:", new_weights)
            
        except ValueError as e:
            st.error(str(e))
        
        # LLM-POWERED CHATBOT
        st.header("💬 AI Assistant")
        user_query = st.text_area("Ask a question about the analysis:")
        if st.button("Submit Query"):
            if user_query:
                context = (
                    f"Q1 Summary: {q1_summary}\n"
                    f"Q4 Summary: {q4_summary}\n"
                    f"AHP Report: {ahp.criteria.report()}"
                )
                prompt = f"Context:\n{context}\n\nQuestion: {user_query}"
                response = query_llm(prompt)
                st.write("Answer:", response)
    else:
        st.warning("No data loaded. Configure data sources and try again.")

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

if __name__ == "__main__":
    main()