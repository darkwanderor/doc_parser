import re
import pdfplumber
import requests
class PDFAgent:
    

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""
        self.total_amount = None
        self.flags = []
        self.COMPLIANCE_KEYWORDS = ["gdpr", "fda", "hipaa", "ccpa", "pci-dss"]

    def extract_text(self):
        """Extract text from the PDF."""
        full_text = ""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        self.text = full_text
        return full_text

    def parse_invoice_data(self):
        """Extract and flag total amount from invoice."""
        text = self.text.replace('\n', ' ').replace('\r', ' ')
        total_patterns = [
            r'total\s+due[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'(?:^|\s)total[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'TOTAL\s+DUE[:\s]*\$?\s*([\d,]+\.?\d*)',
            r'^total\s*\$?\s*([\d,]+\.?\d*)',
            r'total.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'total\s+due[:\s]*([\d,]+\.?\d*)\s*(?:EUR)?',
        ]

        for pattern in total_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                total_str = matches[-1].replace(',', '').replace('$', '').strip()
                try:
                    self.total_amount = float(total_str)
                    break
                except ValueError:
                    continue

        if self.total_amount is None:
            amount_patterns = [
                r'(\d{1,3}(?:,\d{3})*\.\d{2})\s*$',
                r'\$\s*(\d{1,3}(?:,\d{3})*\.\d{2})',
            ]
            amounts = []
            for pattern in amount_patterns:
                matches = re.findall(pattern, self.text, re.MULTILINE)
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        amounts.append(amount)
                    except ValueError:
                        continue
            if amounts:
                self.total_amount = max(amounts)

        if self.total_amount:
            if self.total_amount > 10000:
                self.flags.append(f"Invoice total exceeds $10,000: ${self.total_amount:,.2f}")
            

    def parse_compliance(self):
        cont=0
        """Flag compliance terms in PDF."""
        for keyword in self.COMPLIANCE_KEYWORDS:
            if keyword.lower() in self.text.lower():
                cont=1
                self.flags.append(f"Contains compliance term: {keyword.upper()}")
        return cont
        

    def process(self):
        """Run the full PDF analysis pipeline."""
        self.extract_text()
        self.parse_invoice_data()
        violations=self.parse_compliance()
        if self.total_amount:
            type="Invoice"
        elif violations:
            type="Regulation"
        else:
            type="other"
        response={}
        for flag in self.flags:
            
            if "exceeds" in flag.lower():

                # Critical invoice → Risk alert
                response={ 
                "issue": flag, 
                "severity": "high", 
                "amount": {self.total_amount} 
            }


            elif "compliance" in flag.lower():

                # Compliance flag → Risk alert
                response={ 
                "issue": flag, 
                "data_classification": "compliance", 
                "severity": "critical" 
            }
        return self.text[:1000],{
            "pdf_path": self.pdf_path,
            # "text_snippet": self.text[:1000],  # Limit output snippet
            "total_amount": self.total_amount,
            "type":type,
            "flags": self.flags,
            "response": response
        }
    

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_agent.py <path_to_pdf>")
    else:
        agent = PDFAgent(sys.argv[1])
        result = agent.process()


        #print(f"\nPDF File: {result['pdf_path']}")
        # print(f"\nPDF Content Snippet:\n{result['text_snippet']}\n")
        print(result)
