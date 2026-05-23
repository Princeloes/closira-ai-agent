import json
from typing import Optional
from src.llm_client import LLMClient
from src.state_manager import StateManager

class QualificationStage:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        
        # Sequence of keys to collect and their corresponding prompts
        self.questions = [
            ("name", "First, could you please tell me your full name?"),
            ("treatment_interest", "Great! Which treatment are you looking to book? We offer Botox (from £200), Fillers (from £250), or a free Consultation."),
            ("prior_treatment", "Have you had this type of aesthetics treatment before? (Yes/No)"),
            ("preferred_schedule", "What is your preferred day and time for the appointment? (We are open Mon–Sat, 9 am–7 pm)")
        ]

    def extract_value(self, field: str, user_message: str) -> Optional[str]:
        """Uses the LLM to extract the requested field from the user's message."""
        system_prompt = f"""You are an information extraction assistant for Bloom Aesthetics Clinic.
Extract the value for the field '{field}' from the customer's message.

Extraction Guideline:
- Field 'name': Extract the person's name (e.g. 'Jane Doe').
- Field 'treatment_interest': Identify which treatment they want. It MUST be one of: 'Botox', 'Fillers', or 'Consultations'.
- Field 'prior_treatment': Determine if they have had treatment before. Try to resolve to 'Yes' or 'No' based on the text.
- Field 'preferred_schedule': Extract the preferred booking date/time/window mentioned by the customer.

Response Format:
You MUST output a valid JSON object only. Do not output any markdown formatting, backticks, or other text.
Format:
{{
  "extracted_value": "the extracted value or null if not mentioned or invalid",
  "valid": true
}}"""

        messages = [{"role": "user", "content": user_message}]
        try:
            response_str = self.llm_client.generate(system_prompt, messages, response_json=True)
            data = json.loads(response_str)
            if data.get("valid", False):
                return data.get("extracted_value")
        except Exception:
            pass
        return None

    def get_current_question(self, step: int) -> str:
        """Returns the prompt for the current step."""
        if 0 <= step < len(self.questions):
            return self.questions[step][1]
        return ""

    def run(self, state: StateManager) -> str:
        """
        Runs the lead qualification flow.
        Returns the next message to send to the customer.
        """
        # If we are starting lead qualification
        if state.stage == "faq":
            state.stage = "qualification"
            state.qualification_step = 0
            
        step = state.qualification_step
        last_message = state.history[-1]["content"] if state.history else ""
        
        # If we have already asked a question, try to extract the answer
        if step > 0:
            prev_field = self.questions[step - 1][0]
            extracted = self.extract_value(prev_field, last_message)
            if extracted:
                state.qualification_responses[prev_field] = extracted
            else:
                # If extraction failed, store the raw text as fallback to avoid blocking
                state.qualification_responses[prev_field] = last_message.strip()

        # Check if there are more questions to ask
        if step < len(self.questions):
            question_text = self.get_current_question(step)
            state.qualification_step += 1
            return question_text
        else:
            # All questions answered! Set stage to completed
            state.stage = "completed"
            
            name = state.qualification_responses.get("name", "there")
            treatment = state.qualification_responses.get("treatment_interest", "your treatment")
            schedule = state.qualification_responses.get("preferred_schedule", "your preferred time")
            
            return f"Thank you for providing those details, {name}! I have recorded your booking request for {treatment} on {schedule}. A clinic member will contact you shortly to confirm the appointment. Have a wonderful day!"
