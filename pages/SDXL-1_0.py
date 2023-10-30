import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import io

# FastAPI endpoint URL
API_ENDPOINT = "http://127.0.0.1:8000/sdxl-gen/"

st.set_page_config(page_title="SDXL-1.0 UI", page_icon=":infinity:")

def generate_and_display_image(prompt):
    try:
        # Make a POST request to the FastAPI endpoint
        headers = {"Content-Type": "text/plain"}
        response = requests.post(API_ENDPOINT, data=prompt, headers=headers)
        response_data = response.json()

        # Check if the response is successful
        if response.status_code == 200:
            # Convert the base64 image to an Image object
            image_data = base64.b64decode(response_data["image"])
            image = Image.open(io.BytesIO(image_data))

            # Display the image and its metadata
            st.image(image, caption="Generated Image", use_column_width=True)
            st.markdown(f"""
            **Time taken for generation:** 
            ### {response_data['generation_time']:.2f} seconds
            """, unsafe_allow_html=True)

        else:
            st.error(f"Error: {response.text}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def fetch_sdxl_records():
    # URL to your FastAPI endpoint for fetching SDXL records
    SDXL_RECORDS_URL = "http://127.0.0.1:8000/sdxl-records/"
    response = requests.get(SDXL_RECORDS_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.sidebar.warning("Failed to fetch SDXL records.")
        return []


def show():
    st.title("SDXL 1.0 UI")

    # Sidebar for user input
    st.sidebar.image("assets/SDXL.png", use_column_width=True)
    st.sidebar.header("Settings")
    prompt = st.sidebar.text_area("Enter your prompt:", "An astronaut riding a green horse")

    # When the button is pressed, generate and display the image in the main area
    if st.sidebar.button("Generate Image"):
            generate_and_display_image(prompt)

    # Refresh the history in the sidebar for SDXL
    st.sidebar.header("Recent SDXL Image History")
    sdxl_records = fetch_sdxl_records()
    for record in sdxl_records:
        col1, col2 = st.sidebar.columns([1, 3])
        with col1:
            image_obj = Image.open(record["image_path"])  # Directly open the local image file
            col1.image(image_obj, use_column_width=True)
        with col2:
            col2.markdown(f"**Prompt:** {record['prompt']}")
        st.sidebar.divider()

        

if __name__ == "__main__":
    show()
