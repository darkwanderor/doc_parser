# streamlit_app.py
import streamlit as st
import requests
import json

st.title("📄 Document Classifier Agent")

uploaded_file = st.file_uploader("Upload a document (.pdf, .json, .txt)", type=["pdf", "json", "txt"])
if uploaded_file is not None:
    st.write("Uploaded:", uploaded_file.name)
    
    # Send file to FastAPI
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    response = requests.post("http://localhost:8000/process/", files=files)

    if response.status_code == 200:
        result = response.json()
        st.success("Document processed ✅")
        st.json(result)
    else:
        st.error("Failed to process document ❌")
