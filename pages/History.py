import streamlit as st
import requests
import json
from PIL import Image

HISTORY_ENDPOINT = "http://127.0.0.1:8000/all-records/"
CLEAR_DB_ENDPOINT = "http://127.0.0.1:8000/clear-database/"
EXPORT_FILENAME = "image_history.json"
IMPORT_ENDPOINT = "http://127.0.0.1:8000/import-records/"
DATABASE_INFO_ENDPOINT = "http://127.0.0.1:8000/database-info/"

st.set_page_config(page_title="SSD-1B History", page_icon=":infinity:")


def fetch_database_info():
    response = requests.get(DATABASE_INFO_ENDPOINT)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch database info.")
        return {}

def show_database_info():
    st.sidebar.header("Database Information")

    db_info = fetch_database_info()

    if not db_info:
        st.sidebar.write("Failed to fetch database info.")
        return

    st.sidebar.write(f"Connected Database: {db_info.get('database_name', 'N/A')}")
    st.sidebar.write(f"Total Records: {db_info.get('total_records', 'N/A')}")




def clear_database():
    response = requests.post(CLEAR_DB_ENDPOINT)
    if response.status_code == 200:
        st.sidebar.success("Database cleared successfully!")
    else:
        st.sidebar.error("Failed to clear database.")

def export_records(records):
    json_data = json.dumps(records)
    st.sidebar.success(f"History ready for download!")
    st.sidebar.download_button("Download Exported History", data=json_data, file_name=EXPORT_FILENAME, mime="application/json")


def import_records(uploaded_file):
    records = json.load(uploaded_file)
    response = requests.post(IMPORT_ENDPOINT, json=records)
    if response.status_code == 200:
        st.sidebar.success("History imported successfully!")
    else:
        st.sidebar.error("Failed to import history.")


def fetch_records():
    response = requests.get(HISTORY_ENDPOINT)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch image history.")
        return []

def display_record(record):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Prompt: {record['prompt']}")
        st.write(f"Negative Prompt: {record['negative_prompt']}")
    with col2:
        image_obj = Image.open(record["image_path"])
        st.image(image_obj, caption="Generated Image", use_column_width=True)
    st.write("---")

def show():
    st.title("History Page")

    

    st.sidebar.header("Database Actions")

    uploaded_file = st.sidebar.file_uploader("Import your JSON history to view previous sessions", type=["json"])
    
    if uploaded_file:
        import_records(uploaded_file)
    
    records = fetch_records()
    if st.sidebar.button("Export History"):
        export_records(records)
    
    st.sidebar.divider()

    if st.sidebar.button("Clear Database"):
        clear_database()
    
    st.sidebar.divider()

    # Show database information
    show_database_info()
    
    for record in records:
        display_record(record)


# If running as a standalone page (useful for testing)
if __name__ == "__main__":
    show()

