import json
import pprint

class JSONAgent:
    def __init__(self):
        self.alert_log = []

        self.required_schema = {
            "event_id": str,
            "event_type": str,
            "timestamp": str,
            "company.name": str,
            "company.industry": str,
            "invoice.invoice_id": str,
            "invoice.amount": float,
            "invoice.currency": str,
            "invoice.due_date": str,
            "policy_terms": str
        }

    def get_nested_value(self, data, key_path):
        """Fetch nested key from dot notation (e.g., payload.user_id)."""
        keys = key_path.split('.')
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data

    def validate_json(self, data):
        anomalies = []

        for key_path, expected_type in self.required_schema.items():
            value = self.get_nested_value(data, key_path)
            if value is None:
                anomalies.append(f"Missing field: {key_path}")
            elif not isinstance(value, expected_type):
                anomalies.append(
                    f"Type mismatch: {key_path} (expected {expected_type.__name__}, got {type(value).__name__})"
                )

        return anomalies

    def process(self, webhook_data):
        anomalies = self.validate_json(webhook_data)

        result = {
            "alert_id":webhook_data["event_id"],
            "status": "valid" if not anomalies else "invalid",
            "anomalies": anomalies,
            
            
        }

        if anomalies:
            self.alert_log.append({
                
                "alert": "Anomaly detected in webhook data",
                "details": anomalies
            })

        return webhook_data,result

    def get_alert_log(self):
        return self.alert_log


if __name__ == "__main__":
    agent = JSONAgent()

    with open('test_jsons/sample4.json', 'r') as f:
        json_data = json.load(f)

    response = agent.process(json_data)
    pprint.pprint(response)
    # print("Status:", response["status"])
    # print("Anomalies:")
    # for a in response["anomalies"]:
    #     print(" -", a)

    # print("\nAlert Log:")
    # alert_log = agent.get_alert_log()
    # #json_data["alert_log"] = alert_log
    # print(json.dumps(alert_log, indent=2))

    # pprint.pprint(json_data)
