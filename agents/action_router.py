# # agents/action_router.py
# import requests

# def route_action(agent_output):
#     # Example rules
#     if agent_output.get("urgency") == "high" and agent_output.get("tone") == "angry":
#         response = requests.post("http://localhost:8000/crm/escalate", json=agent_output)
#         return "escalated"
#     elif agent_output.get("invoice_flag"):
#         requests.post("http://localhost:8000/finance/risk_alert", json=agent_output)
#         return "invoice flagged"
#     return "logged"
