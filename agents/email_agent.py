from dotenv import load_dotenv
import os
import json
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import time
import re
# Load API key from .env file


class EmailAgent:
    def __init__(self):
        load_dotenv("venv/.env")
        self.model = GoogleGenerativeAI(model="gemini-2.0-flash")
        self.prompt_template = ChatPromptTemplate.from_messages([
    ("system", 
     """You are a professional AI assistant that extracts structured information from business emails.
Your task is to analyze the **content and wording** of the email and return a JSON object with the following fields:

- "sender": Extract from email header or sign-off.
- "urgency": One of ["low", "medium", "high"]. Consider the use of words like "urgent", "immediate", "asap", and emotional tone.
- "tone": One of ["polite", "threatening", "escalation", "neutral"]. Base it on expressions of frustration, pressure, or politeness.
- "summary": A short summary of the core request or problem in 1–2 sentences.
- "reply": an appropriate,polite,professional,responsible reply suggestion
Only return a **valid JSON** object, no explanations or extra text.
"""),
    ("human", "{email}")
])

    def process_email(self, email_text: str) -> dict:
        """Send email text to LLM and return parsed response."""
        formatted_prompt = self.prompt_template.format(email=email_text)
        response = self.model.invoke(str(formatted_prompt))
        # match = re.search(r'json\s*\{.*?\}\s*', response,re.DOTALL)
        # dict_str = match.group(0)
        
        json_like = re.search(r'\{.*\}', response, re.DOTALL)
        if json_like:
            try:
                data = json.loads(json_like.group())
                return data
            except:
                pass

    def trigger_action(self, email_text):
        parsed_data=self.process_email(email_text)
        """Simulate decision and action based on urgency and tone."""
        sender = parsed_data.get("sender", "unknown")
        urgency = parsed_data.get("urgency", "low").lower()
        tone = parsed_data.get("tone", "neutral").lower()
        issue = parsed_data.get("summary", "")
        response=""
        if urgency == "high" or tone in ["escalation", "threatening"]:
            parsed_data["respond"]="Urgent"
            response={
                 "sender":sender,
                 "issue":issue
            }
            
        else:
            parsed_data["respond"]="Routine"
            response={}
            print(f"\n✅ Routine Email from {sender} - Logged and Closed.")
        parsed_data["response"]=response
        return parsed_data

    def run(self, email_text: str):
        """Main runner method: process → trigger action"""
        data = self.process_email(email_text)
        if data:
            self.trigger_action(data)


# --------- Test Script ---------

if __name__ == "__main__":
    a=time.time()
    file_path = "test_emails/sample5.txt"
    with open(file_path, 'r', encoding='utf-8') as f:
                
                email_text = f.read()
    agent = EmailAgent()
    data=agent.trigger_action(email_text)
    print(data)
    b=time.time()
    print(f"time taken was {b-a} sec")
