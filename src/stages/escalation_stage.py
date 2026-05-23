import json
from src.llm_client import LLMClient
from src.state_manager import StateManager

class EscalationStage:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def run(self, state: StateManager) -> bool:
        """
        Runs the escalation detection.
        Returns True if the session was escalated, False otherwise.
        """
        # Rule 1: Programmatic check for > 2 unanswered questions
        if state.unanswered_count > 2:
            state.escalate_session("More than 2 unanswered/out-of-scope questions")
            return True

        # Rule 2: LLM-based sentiment, medical query, pricing negotiation, and human request check
        system_prompt = """You are an AI safety and escalation supervisor for Bloom Aesthetics Clinic. 
Your sole task is to analyze the conversation history and determine if the customer's last message requires immediate handoff to a human agent.

Strict Escalation Criteria:
1. COMPLAINTS & ANGER: Sentiment is angry, frustrated, complaining about past experiences, treatments, or customer service.
2. MEDICAL CONCERNS: The customer asks a medical question, reports side effects (e.g. rashes, swelling, infections, pain), or details private medical histories.
3. PRICING NEGOTIATION: The customer asks for discounts, attempts to negotiate pricing, or requests cheaper alternatives than the standard fees.
4. EXPLICIT HUMAN HANDOFF: The customer explicitly asks for a human, a manager, an agent, or a staff member.

Response Format:
You MUST output a valid JSON object only. Do not output any markdown formatting, backticks, or other text.
Format:
{
  "escalate": true,
  "reason": "Brief explanation of which criteria was met (e.g. 'Customer is asking to negotiate prices')"
}
OR if no escalation criteria are met:
{
  "escalate": false,
  "reason": null
}"""
        
        try:
            response_str = self.llm_client.generate(system_prompt, state.history, response_json=True)
            data = json.loads(response_str)
            if data.get("escalate", False):
                state.escalate_session(data.get("reason", "Escalated by safety supervisor"))
                return True
        except Exception:
            # Safe fallback: check keywords if JSON parsing or LLM fails
            last_msg = state.history[-1]["content"].lower() if state.history else ""
            for complaint_kw in ["complaint", "complain", "angry", "frustrated", "bad service", "sue"]:
                if complaint_kw in last_msg:
                    state.escalate_session(f"Complaint keyword detected: '{complaint_kw}'")
                    return True
            for medical_kw in ["rash", "swelling", "pain", "infection", "allergic", "hurt", "medical", "doctor"]:
                if medical_kw in last_msg:
                    state.escalate_session("Medical safety concern detected")
                    return True
            for negotiate_kw in ["discount", "negotiate", "cheaper", "deal", "special price"]:
                if negotiate_kw in last_msg:
                    state.escalate_session("Pricing negotiation detected")
                    return True
            for human_kw in ["human", "agent", "manager", "staff", "person", "representative"]:
                if human_kw in last_msg:
                    state.escalate_session("Handoff to human requested")
                    return True

        return False
