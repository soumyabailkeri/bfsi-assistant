from langchain.tools import tool
import httpx

@tool
def assess_loan_risk(age: int, income: float, loan_amount: float, employment_years: int, applicant_name: str) -> str:
    """
    Assess the credit risk for a loan applicant.
    Use this tool when a user wants to check loan eligibility or risk assessment.
    """
    try:
        # First get a token from mybank API
        response = httpx.post(
            "http://127.0.0.1:8000/api/token/",
            json={"username": "soumya", "password": "your_password_here"}
        )
        # Call creditrisk API
        risk_response = httpx.post(
            "http://127.0.0.1:8001/loan/apply",
            json={
                "applicant_name": applicant_name,
                "age": age,
                "income": income,
                "loan_amount": loan_amount,
                "employment_years": employment_years
            }
        )
        data = risk_response.json()
        return f"Risk Assessment: {data['risk_label']} with score {data['risk_score']}%"
    except Exception as e:
        return f"Risk assessment service unavailable. Error: {str(e)}"

@tool
def get_banking_info(topic: str) -> str:
    """
    Get general banking and financial information.
    Use this for questions about banking concepts, loan types, interest rates etc.
    """
    banking_knowledge = {
        "loan_types": "Common loan types include: Home Loans (8-9% interest), Personal Loans (10-24%), Car Loans (7-9%), Education Loans (8-15%), Business Loans (10-18%).",
        "credit_score": "Credit scores range from 300-900 in India. Above 750 is excellent, 700-750 is good, 650-700 is fair, below 650 is poor.",
        "kyc": "KYC (Know Your Customer) requires: Aadhaar card, PAN card, address proof, and income proof for banking services.",
        "fixed_deposit": "Fixed Deposits offer 5-7.5% interest rates typically. Senior citizens get 0.25-0.5% extra. TDS applies above Rs.40,000 interest per year.",
        "remittance": "International remittances can be done via SWIFT, NEFT, RTGS, or services like Western Union. RBI regulates foreign remittances under FEMA.",
    }
    topic_lower = topic.lower()
    for key, value in banking_knowledge.items():
        if any(word in topic_lower for word in key.split('_')):
            return value
    return f"I can provide information about: loan types, credit scores, KYC requirements, fixed deposits, and remittances."