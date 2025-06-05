from agents import intent, email_agent, json_agent, pdf_agent, action_router
import json

class Tools:
    def __init__(self,logger,logalert):
        self.logger=logger
        self.logalert=logalert

    def agent_intent(self,text):
        agent=intent.IntentClassifier()
        return agent.classify(text)
    
    def agent_pdf(self,pdf_path):
        try:
            self.logger.info(f"Loaded PDF from {pdf_path}")
            agent=pdf_agent.PDFAgent(pdf_path=pdf_path)
            text,metadata = agent.process()
            # self.store.store_document(text,metadata)
            status="Unflagged"
            if metadata.get("flags"):
                status="Flagged"
                self.logger.info(f"Agent processed input. Status: {status}")
                anomalies =metadata.get("flags", [])
                self.logalert.append(anomalies)
                self.logger.warning(f"Anomalies found: {anomalies}")
            else:
                self.logger.info(f"Agent processed input. Status: {status}")
            return {"text":text,"metadata":metadata,"response":metadata.get("response",{})}
        except Exception as e:
            self.logger.exception(f"Error processing {pdf_path}: {str(e)}")
            return {"status": "error", "message": str(e)}
    def agent_email(self,file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                email_text = f.read()
            agent=email_agent.EmailAgent()
            self.logger.info(f"Loaded Email from {email_text}")
            data=agent.trigger_action(email_text)
            self.logger.info(f"Agent processed input. Status: {data.get('respond',{})}")
            
            if data["respond"]=="Urgent":
                self.logalert.append(data["summary"])
                self.logger.warning(f"Urgent response to: {data["summary"]}")
            
            # self.store.self.store_document(email_text,data)
            return {"text":email_text,"metadata":data,"response":data.get('response')}
        except Exception as e:
            self.logger.exception(f"Error processing the Email: {str(e)}")
            return {"status": "error", "message": str(e)}
    def agent_json(self,json_path):
        try:
            with open(json_path, 'r') as f:
                json_data = json.load(f)
            self.logger.info(f"Loaded JSON from {json_path}")
            agent = json_agent.JSONAgent()
            data, result = agent.process(json_data)
            self.logger.info(f"Agent processed input. Status: {result.get('status')}")
            # self.store.self.store_document(data, response)

            if result.get("status") == "invalid":              
                anomalies = result.get("anomalies", [])
                self.logalert.append(anomalies)
                self.logger.warning(f"Anomalies found: {anomalies}")
            
            
            return {"text":str(data),"metadata":result,"response":result}

        except Exception as e:
            self.logger.exception(f"Error processing {json_path}: {str(e)}")
            return None, {"status": "error", "message": str(e)}