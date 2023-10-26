#!/bin/bash

# Execute the streamlit command
streamlit run SSD-1B.py &

# Execute the uvicorn command
uvicorn api:app --reload


