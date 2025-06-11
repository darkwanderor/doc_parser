# 🧠 Alertra: Intelligent Business Document Router & Alert System

**Alertra** is a LangGraph-powered orchestration framework that ingests business documents and messages—PDFs, JSON payloads, and Emails—automatically classifies and summarizes them, and triggers downstream actions (CRM tickets, risk alerts) based on detected intent and anomalies. Built with Gemini-2.0-flash, LangGraph, FastAPI, and Redis.

---

## 📌 Key Features

- **Format Detection**: Automatically detects PDF, Email (plain text), or JSON inputs.  
- **Intent Classification**: LLM-driven classification into `Invoice`, `RFQ`, `Complaint`, `Regulation`, or `Fraud Risk`.  
- **Summarization Engine**: Concise 2–4 bullet summaries via Gemini-2.0-flash.  
- **Email Reply Suggestions**: Draft replies when email input is detected.  
- **Anomaly Flagging**: Flags schema mismatches, high-value invoices, policy violations (e.g. GDPR).  
- **Automated Routing**: Simulated REST calls (`POST /crm`, `POST /risk_alert`) based on business logic.  
- **Modular Agents**: Separate PDF, Email, and JSON agents, orchestrated via LangGraph state transitions.  
- **Persistent Memory**: Stores raw and processed data + embeddings in Redis for traceability.

---

## 🏗 Architecture

```
[Input File] 
     ↓ Detect Format 
[Format Detection Node]
     ↓ Route to Agent
┌──────────────────────┐   ┌───────────────────┐   ┌─────────────────┐
│ PDF Processor Agent  │   │ Email Processor   │   │ JSON Processor  │
└──────────────────────┘   └───────────────────┘   └─────────────────┘
     ↓ Parsed Text & Metadata
[Intent Classification Node (Gemini-2.0-flash)]
     ↓ Intent + Flags
[Business Agent Node (Gemini-2.0-flash Post-Processing)]
     ↓ Trigger Actions
┌──────────────┐  ┌─────────────────────┐
│  POST /crm   │  │  POST /risk_alert   │
└──────────────┘  └─────────────────────┘
     ↓ Store in Redis (vector + metadata)
```

---

## 🔁 Workflow Examples

### 1. PDF Invoice → High-Value Alert

**Raw Output**  
```json
{
  "file_path":"temp_files/INV-9842.pdf",
  "format":"pdf",
  "text":"...invoice content...",
  "intent":"Invoice",
  "metadata":{
    "total_amount":15750.00,
    "flags":["High value invoice: $15,750.00"]
  }
}
```

**Triggered Action**  
```http
POST /crm
Content-Type: application/json

{
  "summary": "Unusually high invoice needs review",
  "customer_id": "CUST-1022",
  "invoice_id": "INV-9842",
  "amount": 15750.00,
  "priority": "high"
}
```

---

### 2. Urgent Complaint Email → CRM Ticket

**Raw Output**  
```json
{
  "file_path":"temp_files/complaint_urgent.txt",
  "format":"email",
  "text":"Dear team, our servers are down...",
  "intent":"Complaint",
  "metadata":{
    "flags":["urgent"]
  }
}
```

**Triggered Action**  
```http
POST /crm
Content-Type: application/json

{
  "summary": "Urgent complaint about service downtime",
  "sender": "client@example.com",
  "priority": "critical"
}
```

> **Reply Suggestion**  
> “We sincerely apologize for the inconvenience. Our team is investigating the issue and will update you shortly.”

---

### 3. JSON Webhook → Schema Mismatch Alert

**Raw Output**  
```json
{
  "file_path":"temp_files/webhook_payload.json",
  "format":"json",
  "text":"...",
  "intent":"Fraud Risk",
  "metadata":{
    "flags":["Missing customer ID","No timestamp"]
  }
}
```

**Triggered Action**  
```http
POST /risk_alert
Content-Type: application/json

{
  "issue": "Missing customer ID and timestamp",
  "severity": "high",
  "data": { /* original_payload */ }
}
```

---

## 🚀 Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/darkwanderor/doc_parser.git
   cd doc_parser
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Redis** (Docker)  
   ```bash
   docker run -p 6379:6379 redis
   ```

4. **Start the API**  
   ```bash
   uvicorn api:app_api --reload
   ```

5. **Submit a file**  
   ```bash
   curl -X POST http://localhost:8000/process/ -F "file=@temp_files/sample.pdf"
   ```

---

## 📁 Folder Structure

```
doc_parser /
    ├── agents
    │   ├── action_router.py
    │   ├── email_agent.py
    │   ├── intent.py
    │   ├── json_agent.py
    │   └── pdf_agent.py
    ├── api.py
    ├── chatbot.py
    ├── database.py
    ├── dummyserver.py
    ├── main.py
    ├── README.md
    ├── requirements.txt
    ├── redis-docker-compose.yml
    ├── server_app.py
    ├── tools.py
    └── utils.py
```

---

## 🛠 Tech Stack

- **LLM & Prompting**: Gemini-2.0-flash  
- **Workflow Orchestration**: LangGraph (with TypedDict state)  
- **Web Framework**: FastAPI  
- **Storage & Memory**: Redis (vector + metadata)  
- **Parsing**: pdfplumber, Python stdlib (json)  
- **Environment**: python-dotenv, logging  

---

## 📜 API Endpoints

| Method | Endpoint                    | Description                                  |
|--------|-----------------------------|----------------------------------------------|
| POST   | `/process/`                 | Upload file & run full LangGraph pipeline    |
| POST   | `/crm`                      | Simulate CRM ticket creation                 |
| POST   | `/risk_alert`               | Simulate compliance/risk alert               |

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

**Hemant Sharma**  
[GitHub: darkwanderor](https://github.com/darkwanderor)