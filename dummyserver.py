from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()
def convert(log: dict) -> str:
    return ", ".join(f"{k}: {v}" for k, v in log.items())
# In-memory log storage
crm_requests: List[str] = []
risk_alert_requests: List[str] = []

@app.post("/crm")
async def receive_crm(data: dict):
    log = convert(data)
    crm_requests.append(log)
    print("Received CRM:", data)
    return {"status": "success", "echo": data}

@app.post("/risk_alert")
async def receive_risk_alert(data: dict):
    log = convert(data)
    risk_alert_requests.append(log)
    print("Received Risk Alert:", data)
    return {"status": "success", "echo": data}

@app.get("/logs")
async def get_logs():
    return {
        "crm": crm_requests[-20:],  # Return last 20 CRM logs
        "risk_alert": risk_alert_requests[-20:]  # Return last 20 alerts
    }

if __name__ == "__main__":
    uvicorn.run("dummyserver:app", port=8008, reload=True)
