import streamlit as st
import requests
from io import BytesIO
from PIL import Image

API_ENDPOINT = "http://127.0.0.1:8000/generate-image/"
HISTORY_ENDPOINT = "http://127.0.0.1:8000/image-records/"


def fetch_image_records():
    try:
        response = requests.get(HISTORY_ENDPOINT)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Error fetching image records: {str(e)}")
        return []


# Page info
st.set_page_config(page_title="SSD-1B UI", page_icon=":infinity:")
st.title(":infinity: SSD-1B API")
st.info("Enter your prompt in the sidebar")
header_image_path = "assets/SSD_1B.png"



# Sidebar UI
st.sidebar.image(header_image_path, use_column_width=True)
st.sidebar.title("Parameters")
prompt = st.sidebar.text_input("Prompt:", "An astronaut riding a green horse")
neg_prompt = st.sidebar.text_input("Negative Prompt:", "ugly, blurry, poor quality")
execute_button = st.sidebar.button("Execute")

# Refresh the history in the sidebar
st.sidebar.header("Recent Image History")
image_records = fetch_image_records()
for record in image_records:
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        image_obj = Image.open(record["image_path"])
        col1.image(image_obj, use_column_width=True)
    with col2:
        col2.markdown(f"**Prompt:** {record['prompt']}")
        col2.text(f"Negative Prompt: {record['negative_prompt']}")
    st.sidebar.divider()

# Main UI
if execute_button:
    with st.spinner("Generating image..."):
        # Make a POST request to the API
        response = requests.post(API_ENDPOINT, json={"prompt": prompt, "negative_prompt": neg_prompt})

        # Check for a valid response
        if response.status_code == 200:
            # Convert the response content to a PIL Image
            image_bytes = BytesIO(response.content)
            image_obj = Image.open(image_bytes)

            # Display the image in Streamlit
            st.image(image_obj, caption="Generated Image", use_column_width=True)

        else:
            st.error(f"Failed to generate image. API responded with: {response.text}")








