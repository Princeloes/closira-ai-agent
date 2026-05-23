import json
from src.llm_client import LLMClient
from src.state_manager import StateManager
from src.sop_manager import SOPManager

class FAQStage:
    def __init__(self, llm_client: LLMClient, sop_manager: SOPManager):
        self.llm_client = llm_client
        self.sop_manager = sop_manager

    def run(self, state: StateManager) -> str:
        """
        Processes the customer's last message against the SOP.
        If the question is out of scope, logs the gap and updates the unanswered counter.
        Returns the AI response.
        """
        last_message = state.history[-1]["content"] if state.history else ""
        sop_text = self.sop_manager.get_formatted_sop()
        
        system_prompt = f"""You are an AI assistant for Bloom Aesthetics Clinic. Your task is to answer the customer's question using ONLY the provided Standard Operating Procedures (SOP).

{sop_text}

Rules:
1. Grounding: Answer the question using ONLY facts explicitly stated in the SOP above.
2. Hallucination Prevention: If the customer asks about something NOT mentioned in the SOP (e.g. services we don't offer, opening hours not listed, specific discounts, or locations), you must set 'answered' to false. Do not try to make up an answer.
3. Keep the response professional, concise, and helpful.

Response Format:
You MUST output a valid JSON object only. Do not output any markdown formatting, backticks, or other text.
Format:
{{
  "answered": true,
  "response": "The detailed answer from the SOP"
}}
OR if the question is out of scope or cannot be answered using the SOP:
{{
  "answered": false,
  "response": "I apologize, but that is not covered by my current procedures. Let me consult with the clinic manager to check."
}}"""

        try:
            response_str = self.llm_client.generate(system_prompt, state.history, response_json=True)
            data = json.loads(response_str)
            
            if not data.get("answered", False):
                # Log the out-of-scope question as an SOP gap
                state.log_sop_gap(last_message)
                
            return data.get("response", "I'm sorry, I couldn't process your request. Let me refer this to our team.")
        except Exception:
            # Fallback in case of parse error
            state.log_sop_gap(last_message)
            return "I apologize, but I don't have that information in my procedures. Let me check with the clinic staff."
