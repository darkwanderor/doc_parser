from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class IntentClassifier:
    def __init__(self, model_name="gemini-1.5-flash", temperature=0.7):
        # Set up the prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""
Given the following document text, classify its business intent into one of the following categories:
- RFQ
- Complaint
- Invoice
- Regulation
- Fraud Risk

Document Text:
{text}

Intent:"""
        )

        # Initialize the LLM
        self.llm = GoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            convert_system_message_to_human=True
        )

        # Set up the LLMChain
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def classify(self, text: str) -> str:
        """Classifies the intent of the given document text."""
        return self.chain.invoke({"text": text})
