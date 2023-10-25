import streamlit as st
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime
import uuid

API_ENDPOINT = "http://127.0.0.1:8000/generate-image/"

# Page info
st.set_page_config(page_title="SSD-1B UI", page_icon="🚀")

# Sidebar UI
st.sidebar.title("Parameters")
prompt = st.sidebar.text_input("Prompt:", "An astronaut riding a green horse")
neg_prompt = st.sidebar.text_input("Negative Prompt:", "ugly, blurry, poor quality")
execute_button = st.sidebar.button("Execute")

# Main UI
if execute_button:
    with st.spinner("Generating image..."):
        # Make a POST request to the API
        response = requests.post(API_ENDPOINT, json={"prompt": prompt, "negative_prompt": neg_prompt})
        
        # Inside the if block where you handle the response:
        if response.status_code == 200:
            # Convert the response content to a PIL Image
            image_obj = Image.open(BytesIO(response.content))

            # Generate a unique filename
            unique_filename = datetime.now().strftime("generated_image_%Y%m%d_%H%M%S.png")

            # Save the image with the unique filename
            image_obj.save(unique_filename)

            # Display the image in Streamlit
            st.image(unique_filename, caption="Generated Image", use_column_width=True)

            # Provide the download button with the unique filename
            st.download_button("Download Image", unique_filename, file_name=unique_filename)

        else:
            st.error(f"Failed to generate image. API responded with: {response.text}")


