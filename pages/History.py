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

# Initialize session state variables
if 'selected_images' not in st.session_state:
    st.session_state.selected_images = []
    
if 'compare_buttons' not in st.session_state:
    st.session_state.compare_buttons = {}

# Retrieves database information from the API
def fetch_database_info():
    response = requests.get(DATABASE_INFO_ENDPOINT)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch database info.")
        return {}

# Shows the database information in the sidebar
def show_database_info():
    st.sidebar.header("Database Information")

    db_info = fetch_database_info()

    if not db_info:
        st.sidebar.write("Failed to fetch database info.")
        return

    st.sidebar.write(f"Connected Database: {db_info.get('database_name', 'N/A')}")
    st.sidebar.write(f"SSD 1B Records: {db_info.get('ssd_1b_records', 'N/A')}")
    st.sidebar.write(f"SDXL Records: {db_info.get('sdxl_records', 'N/A')}")

# Clears the database
def clear_database():
    response = requests.post(CLEAR_DB_ENDPOINT)
    if response.status_code == 200:
        st.sidebar.success("Database cleared successfully!")
    else:
        st.sidebar.error("Failed to clear database.")

# Exports the records to a JSON file
def export_records(records):
    json_data = json.dumps(records)
    st.sidebar.success(f"History ready for download!")
    st.sidebar.download_button("Download Exported History", data=json_data, file_name=EXPORT_FILENAME, mime="application/json")


# Imports records from a JSON file
def import_records(uploaded_file):
    records = json.load(uploaded_file)
    response = requests.post(IMPORT_ENDPOINT, json=records)
    if response.status_code == 200:
        st.sidebar.success("History imported successfully!")
    else:
        st.sidebar.error("Failed to import history.")

# Fetches the image records from the API
def fetch_records():
    response = requests.get(HISTORY_ENDPOINT)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch image history.")
        return []



def display_selected_images():
    if len(st.session_state.selected_images) == 2:
        col1, col2 = st.columns(2)
        with col1:
            image_obj = Image.open(st.session_state.selected_images[0])
            st.image(image_obj, caption="Comparison Image 1", use_column_width=True)
        with col2:
            image_obj = Image.open(st.session_state.selected_images[1])
            st.image(image_obj, caption="Comparison Image 2", use_column_width=True)
        st.write("---")


# Displays all records
def display_record(record):
    col1, col2 = st.columns(2)
    
    with col1:
        # Display the datetime for the record at the top
        st.write(f"Created on: {record.get('timestamp', 'N/A')}")

        st.write(f"Prompt: {record['prompt']}")
        negative_prompt = record.get('negative_prompt')
        if negative_prompt is not None:
            st.write(f"Negative Prompt: {negative_prompt}")
            st.markdown("<span style='color: #0AC2FF;'>SSD 1B Record</span>", unsafe_allow_html=True)
        else:
            st.write("NA")
            # Highlight SDXLImageRecord entry (since it doesn't have a negative prompt)
            st.markdown("<span style='color: #FF0AC2;'>SDXL Record</span>", unsafe_allow_html=True)
        
        # Button for comparison
        button_key = f"compare_{record['image_path']}"
        if button_key not in st.session_state.compare_buttons:
            st.session_state.compare_buttons[button_key] = False

        if st.session_state.compare_buttons[button_key] or st.button("Add to Compare", key=button_key):
            if record["image_path"] not in st.session_state.selected_images:
                st.session_state.selected_images.append(record["image_path"])
                if len(st.session_state.selected_images) > 2:
                    st.session_state.selected_images.pop(0)
            st.session_state.compare_buttons[button_key] = True


    with col2:
        image_obj = Image.open(record["image_path"])
        st.image(image_obj, caption="Generated Image", use_column_width=True)
    st.write("---")


# Main page structure
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

    # Display a clear button if two images are selected
    if len(st.session_state.selected_images) == 2:
        if st.button("Clear Comparison Images"):
            st.session_state.selected_images = []
            for key in st.session_state.compare_buttons:
                st.session_state.compare_buttons[key] = False


    # Show selected images for comparison
    display_selected_images()
    
    for record in records:
        display_record(record)


# If running as a standalone page (useful for testing)
if __name__ == "__main__":
    show()
