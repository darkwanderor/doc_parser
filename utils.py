import os
import requests
def detect_format(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return "pdf"
    elif ext == ".txt":
        return "email"
    elif ext == ".json":
        return "json"
    else:
        return "unknown"


def route_to_agent(format_type,file_path,tools):
    if format_type == "pdf":
        return tools.agent_pdf(file_path)
    elif format_type == "email":
        return tools.agent_email(file_path)
    elif format_type == "json":
        return tools.agent_json(file_path)
    else:
        raise ValueError(f"Unsupported format: {format_type}")
    
import json
import copy

def safe_json_dumps(obj):
    try:
        return json.dumps(obj)
    except (ValueError, TypeError):
        return json.dumps(clean_for_json(copy.deepcopy(obj)))

def clean_for_json(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return "[Circular Reference]"
    seen.add(obj_id)

    if isinstance(obj, dict):
        return {k: clean_for_json(v, seen) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(i, seen) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(clean_for_json(i, seen) for i in obj)
    elif isinstance(obj, set):
        return [clean_for_json(i, seen) for i in obj]  # Convert set to list
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)
