import pandas as pd
import requests
from src.config import load_secrets

def load_data(file_path: str, sample_size: int = None) -> tuple[pd.DataFrame, str]:
    """
    Load data from a CSV file and generate an LLM-based summary.
    
    Args:
        file_path (str): Path to the CSV file.
        sample_size (int, optional): Number of rows to sample for large datasets.
    
    Returns:
        tuple: (DataFrame, LLM-generated summary)
    """
    try:
        df = pd.read_csv(file_path)
        if sample_size and len(df) > sample_size:
            df = df.sample(sample_size, random_state=42)
        
        summary_stats = df.describe(include='all').to_string()[:500]  # Limit to 500 characters
        llm_summary = get_data_summary(summary_stats)
        return df, llm_summary
    except FileNotFoundError:
        raise ValueError("Error: File not found.")
    except pd.errors.EmptyDataError:
        raise ValueError("Error: The file is empty or corrupted.")

def load_data_powerbi(source_config: dict) -> tuple[pd.DataFrame, dict]:
    """
    Fetch data from Power BI using the API with pagination.
    
    Args:
        source_config (dict): Configuration dictionary with dataset_id, table_name, and access_token.
    
    Returns:
        tuple: (DataFrame, metadata about the dataset)
    """
    required_keys = {"dataset_id", "table_name", "access_token"}
    if not required_keys.issubset(source_config.keys()):
        raise ValueError(f"Missing required keys in source_config: {required_keys - source_config.keys()}")
    
    try:
        api_url = (
            f"https://api.powerbi.com/v1.0/myorg/datasets/"
            f"{source_config['dataset_id']}/tables/"
            f"{source_config['table_name']}/rows"
        )
        headers = {
            "Authorization": f"Bearer {source_config['access_token']}",
            "Content-Type": "application/json"
        }
        
        all_data = []
        skip = 0
        top = 1000  # Fetch 1000 rows at a time
        while True:
            paginated_url = f"{api_url}?$skip={skip}&$top={top}"
            logging.info(f"Fetching data from Power BI: {paginated_url}")
            response = requests.get(paginated_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            rows = data.get("value", [])
            if not rows:
                break
            all_data.extend(rows)
            skip += top
        
        df = pd.DataFrame(all_data)
        metadata = {
            "columns": list(df.columns),
            "row_count": len(df),
            "data_types": {col: str(df[col].dtype) for col in df.columns}
        }
        logging.info("Data fetched successfully.")
        return df, metadata
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        logging.error(f"Error loading data from Power BI: {str(e)}")
    return pd.DataFrame(), {}
