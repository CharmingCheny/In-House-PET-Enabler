# data_preprocess/data_object_utils.py
import requests

def get_data_object_metadata(dtm_url: str, data_object_id: str) -> dict:
    """
    Call DTM API to obtain data object metadata
    """
    url = f"{dtm_url}/framework/data-object/{data_object_id}"
    try:
        response = requests.get(url, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        res = response.json()
        if res.get("code") != "00":
            raise Exception(f"DTM Error: {res.get('message')}")
        return res["data"]
    except Exception as e:
        print(f"Failed to get metadata: {e}")
        raise
