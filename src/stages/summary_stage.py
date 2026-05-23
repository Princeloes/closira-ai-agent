import json
from src.llm_client import LLMClient
from src.state_manager import StateManager

class SummaryStage:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def run(self, state: StateManager) -> str:
        """
        Generates a structured JSON summary of the conversation.
        """
        # Convert state metadata to string format for prompting
        history_str = ""
        for msg in state.history:
            history_str += f"{msg['role'].upper()}: {msg['content']}\n"
            
        gaps_str = ", ".join(state.sop_gaps) if state.sop_gaps else "None"
        responses_str = json.dumps(state.qualification_responses, indent=2)
        
        system_prompt = f"""You are an executive assistant for Bloom Aesthetics Clinic. 
Your task is to generate a structured JSON summary of the conversation at the end of the customer session.

Metadata Context:
- SOP Gaps logged during session: {gaps_str}
- Lead Qualification Details collected: {responses_str}

Please review the chat transcript below and extract:
1. Customer Intent: What was the customer trying to achieve (e.g. book an appointment, ask about services, file a complaint)?
2. Key Details Collected: Verify and structure the details collected (Name, Treatment Interest, Prior Treatment History, Preferred Schedule).
3. SOP Gaps Identified: List any questions the customer asked that the SOP could not answer.
4. Recommended Next Action: What should the clinic staff do next?

Chat Transcript:
{history_str}

Response Format:
You MUST output a valid JSON object only. Do not output any markdown formatting, backticks, or other text.
Format:
{{
  "intent": "Brief description of the customer's intent",
  "details_collected": {{
    "name": "Jane Doe or null",
    "treatment_interest": "Botox/Fillers/Consultations or null",
    "prior_treatment": "Yes/No or null",
    "preferred_schedule": "e.g. Saturday at 10am or null"
  }},
  "sop_gaps": [
    "List of questions asked that were not in the SOP"
  ],
  "recommended_action": "Detailed recommendation for the clinic staff (e.g. 'Call customer to confirm Botox appointment for Saturday 10am')"
}}"""

        try:
            # Generate using LLM
            # Since we pass an empty list for messages, we can just put a simple message to satisfy the LLM client
            messages = [{"role": "user", "content": "Generate the conversation summary now."}]
            response_str = self.llm_client.generate(system_prompt, messages, response_json=True)
            
            # Verify it parses as JSON to ensure safety
            json_data = json.loads(response_str)
            return json.dumps(json_data, indent=2)
        except Exception:
            # Safe local fallback if LLM/parsing fails
            fallback_summary = {
                "intent": "Inquiry or booking request",
                "details_collected": state.qualification_responses,
                "sop_gaps": state.sop_gaps,
                "recommended_action": "Contact client to address outstanding questions and finalize booking details." if not state.escalated else f"Escalate immediately: {state.escalation_reason}"
            }
            return json.dumps(fallback_summary, indent=2)
