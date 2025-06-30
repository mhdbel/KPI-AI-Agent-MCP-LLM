import requests
import pandas as pd
from src.config import load_secrets

def load_data_from_powerbi(source_config: dict) -> pd.DataFrame:
    """Fetch data from Power BI using the API."""
    try:
        api_url = (
            f"https://api.powerbi.com/v1.0/myorg/datasets/ "
            f"{source_config['dataset_id']}/tables/"
            f"{source_config['table_name']}/rows"
        )
        headers = {
            "Authorization": f"Bearer {source_config['access_token']}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data.get("value", []))
    except Exception as e:
        return pd.DataFrame()