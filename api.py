# api.py
from fastapi import FastAPI, UploadFile, File
import os
import uuid
from main import app  # replace with your LangGraph app import

app_api = FastAPI()

@app_api.post("/process/")
async def process_file(file: UploadFile = File(...)):
    file_ext = file.filename.split('.')[-1]
    file_path = f"temp_files/{uuid.uuid4()}.{file_ext}"
    os.makedirs("temp_files", exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Initial state to run through LangGraph
    state = {"file_path": file_path}
    result = app.invoke(state)
    return result
