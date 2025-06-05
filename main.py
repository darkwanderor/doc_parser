from langgraph.graph import StateGraph
import json
from typing import TypedDict
from tools import Tools
import logging
import redis
import copy
from IPython.display import Image
import os
from database import RedisVectorStore
from utils import detect_format,route_to_agent,safe_json_dumps
from langgraph.graph import StateGraph, END
import pprint
import warnings
import requests
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logalert = [] 
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=False)
store = RedisVectorStore(redis_client)
store.clear_database()

tools=Tools(logger,logalert)

class State(TypedDict):
    file_path: str
    format: str
    text: str
    intent: str
    metadata: dict
    response:dict
#define nodes
def format_detection_node(state: State) -> State:
    format_type = detect_format(state["file_path"])
    state["format"] = format_type
    return state
def processing_node(state: State) -> State:
    result = route_to_agent(state["format"], state["file_path"],tools)
    state["text"] = result["text"]
    state["metadata"] = result["metadata"]
    state["response"]=result["response"]
    return state
def intent_classification_node(state: State) -> State:
    intent = tools.agent_intent(text=state["text"])
    state["intent"] = intent["text"]
    return state
def storage_node(state: State) -> State:
    # Store the document and metadata in Redis or another storage
    store.store_document(state["text"], {
        "format": state["format"],
        "intent": state["intent"],
        **state["metadata"]
    })
    return state
def alert(state:State) -> State:
    mapping = {
        "RFQ": "crm",
        "Complaint": "crm",
        "Invoice": "crm",
        "Regulation": "risk_alert",
        "Fraud Risk": "risk_alert"
    }
    intent_text = state['intent']
    # Lowercase version for case-insensitive matching
    intent_lower = intent_text.lower()
    
    # Find a matching key by checking if it is contained in intent_text
    matched_key = None
    for key in mapping.keys():
        if key.lower() in intent_lower:
            matched_key = key
            break

    if matched_key is None:
        raise ValueError(f"Unknown intent: {intent_text}")
    metadata=state.get("metadata",{})
    url = f"http://localhost:8008/{mapping[matched_key]}"
    if(state.get("response",{})):
        json_data = copy.deepcopy(state.get("response",{}))
        print("json: ",json_data)
        try:
            response = requests.post(url, json=json_data)
            print("Status Code:", response.status_code)
            print("Response JSON:", response.json())
        except Exception as e:
            print("Error sending alert:", e)
    return state
        
    

graph = StateGraph(State)
graph.add_node("format_detection", format_detection_node)
graph.add_node("processing", processing_node)
graph.add_node("intent_classification", intent_classification_node)
graph.add_node("alert", alert)
graph.add_node("storage", storage_node)

graph.set_entry_point("format_detection")
graph.add_edge("format_detection", "processing")
graph.add_edge("processing", "intent_classification")
graph.add_edge("intent_classification", "alert")
graph.add_edge("alert", "storage")

graph.add_edge("storage", END)
# Compile the graph
app = graph.compile()
# png_data = app.get_graph().draw_png()

# with open("graph_image.png", "wb") as f:
#     f.write(png_data)

# # Display the image in IPython/Jupyter notebook

# Image(png_data)
initial_state = {"file_path": "test_pdfs/micro.pdf"}
final_state = app.invoke(initial_state)
pprint.pprint(final_state)
print(logalert)