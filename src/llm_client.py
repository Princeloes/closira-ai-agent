import json
import re
from typing import List, Dict, Any, Optional
from src.config import Config

class LLMClient:
    def __init__(self, provider: Optional[str] = None):
        # Choose provider: explicit, or fallback to config
        self.provider = provider or Config.DEFAULT_PROVIDER
        
        self.openai_client = None
        self.anthropic_client = None
        
        if self.provider == "openai":
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def generate(self, system_prompt: str, messages: List[Dict[str, str]], response_json: bool = False) -> str:
        """
        Generates a completion from the selected provider.
        If response_json is True, asks/expects JSON output.
        """
        if self.provider == "openai":
            return self._generate_openai(system_prompt, messages, response_json)
        elif self.provider == "anthropic":
            return self._generate_anthropic(system_prompt, messages, response_json)
        else:
            return self._generate_mock(system_prompt, messages, response_json)

    def _generate_openai(self, system_prompt: str, messages: List[Dict[str, str]], response_json: bool) -> str:
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            
        kwargs = {
            "model": Config.OPENAI_MODEL,
            "messages": formatted_messages,
            "temperature": 0.0
        }
        if response_json:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = self.openai_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _generate_anthropic(self, system_prompt: str, messages: List[Dict[str, str]], response_json: bool) -> str:
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
            
        # If response_json is requested, append a hint for Claude
        system_content = system_prompt
        if response_json:
            system_content += "\nCRITICAL: You must return valid JSON only. Do not wrap your response in markdown formatting or backticks (e.g. do not write ```json ... ```). Start your response with '{'."
            
        response = self.anthropic_client.messages.create(
            model=Config.ANTHROPIC_MODEL,
            max_tokens=1024,
            temperature=0.0,
            system=system_content,
            messages=formatted_messages
        )
        content = response.content[0].text
        
        # Strip markdown code blocks if Claude still returned them
        if response_json:
            content = content.strip()
            if content.startswith("```"):
                # Remove starting markdown block
                content = re.sub(r"^```(?:json)?\n", "", content)
                content = re.sub(r"\n```$", "", content)
            content = content.strip()
        return content

    def _generate_mock(self, system_prompt: str, messages: List[Dict[str, str]], response_json: bool) -> str:
        """
        A deterministic mock LLM that parses the prompt and last message to return
        the expected responses for the Closira Bloom Aesthetics Clinic task.
        """
        last_message = messages[-1]["content"] if messages else ""
        last_message_lower = last_message.lower().strip()
        
        # 1. Determine task type by system prompt analysis
        if "summary" in system_prompt.lower():
            # Conversation Summary Stage (Stage 4)
            # Find the history and gaps from prompt or serialize a mock summary
            # We can extract state parameters from prompt if needed, or return a standard structured JSON
            return json.dumps({
                "intent": "Inquiry and booking request for aesthetics treatment",
                "details_collected": {
                    "name": "Jane Doe",
                    "treatment_interest": "Botox",
                    "prior_treatment": "No",
                    "preferred_schedule": "Saturday morning at 10am"
                },
                "sop_gaps": ["Customer asked about dental/teeth whitening treatments which are not offered"],
                "recommended_action": "Schedule Jane Doe for a free Botox consultation on Saturday morning and send confirmation details."
            })

        elif "escalation" in system_prompt.lower() or "sentiment" in system_prompt.lower():
            # Escalation Stage Detection
            escalate = False
            reason = None
            
            if any(word in last_message_lower for word in ["complaint", "complain", "angry", "frustrated", "bad service", "sue", "terrible"]):
                escalate = True
                reason = "Complaint / Angry sentiment detected"
            elif any(word in last_message_lower for word in ["rash", "swelling", "pain", "infection", "allergic", "hurt", "medical"]):
                escalate = True
                reason = "Medical safety concern / Side effects question"
            elif any(word in last_message_lower for word in ["discount", "negotiate", "cheaper", "negotiation", "deal", "special price"]):
                escalate = True
                reason = "Pricing negotiation attempted"
            elif any(phrase in last_message_lower for phrase in ["speak to human", "agent", "human", "representative", "person"]):
                escalate = True
                reason = "Explicit request for human agent Handoff"
                
            return json.dumps({"escalate": escalate, "reason": reason})

        elif "faq" in system_prompt.lower():
            # FAQ Answering Stage
            # Check for Out-of-Scope (gap) questions
            out_of_scope_keywords = ["teeth whitening", "dental", "massage", "haircut", "nails", "pricing negotiation", "discount", "open sunday", "teeth"]
            is_out_of_scope = any(word in last_message_lower for word in out_of_scope_keywords)
            
            if is_out_of_scope:
                return json.dumps({
                    "answered": False,
                    "response": "I apologize, but we do not offer teeth whitening or other non-aesthetic treatments at Bloom Aesthetics Clinic. Our services are limited to Botox, Fillers, and Consultations. Would you like me to connect you to a clinic manager?"
                })
                
            # Check for standard Botox questions
            if "botox" in last_message_lower:
                return json.dumps({
                    "answered": True,
                    "response": "At Bloom Aesthetics Clinic, our Botox treatments start from £200. Bookings can be made via WhatsApp or our website. We require a 24-hour cancellation notice. Would you like to schedule a free consultation to discuss further?"
                })
            # Check for Filler questions
            elif "filler" in last_message_lower:
                return json.dumps({
                    "answered": True,
                    "response": "Our dermal Fillers start from £250. Bookings are available via WhatsApp or our website. We have a 24-hour cancellation policy. Let me know if you would like to book an appointment!"
                })
            # Check for Hours questions
            elif "hours" in last_message_lower or "when are you open" in last_message_lower or "open" in last_message_lower:
                return json.dumps({
                    "answered": True,
                    "response": "Bloom Aesthetics Clinic is open Monday to Saturday, from 9 am to 7 pm. We are closed on Sundays. Would you like to schedule a booking during these hours?"
                })
            # Default fallback
            else:
                return json.dumps({
                    "answered": True,
                    "response": "Welcome to Bloom Aesthetics Clinic! We offer Botox (from £200), Fillers (from £250), and free consultations. We are open Mon-Sat, 9am-7pm. How can I help you today?"
                })

        elif "qualification" in system_prompt.lower() or "extract" in system_prompt.lower():
            # Lead Qualification Extraction Stage
            # In mock mode, check what data is in the user message
            extracted_value = None
            valid = True
            
            # Simple extraction rules
            if "name is" in last_message_lower:
                extracted_value = last_message.split("name is")[-1].strip().strip(".").title()
            elif "i am" in last_message_lower:
                extracted_value = last_message.split("i am")[-1].strip().strip(".").title()
            elif len(last_message.split()) <= 2 and not any(w in last_message_lower for w in ["yes", "no", "botox", "filler"]):
                extracted_value = last_message.strip().title()
                
            if "botox" in last_message_lower:
                extracted_value = "Botox"
            elif "filler" in last_message_lower:
                extracted_value = "Fillers"
            elif "consult" in last_message_lower:
                extracted_value = "Consultations"
                
            if "yes" in last_message_lower:
                extracted_value = "Yes"
            elif "no" in last_message_lower:
                extracted_value = "No"
                
            if any(time_word in last_message_lower for time_word in ["saturday", "monday", "pm", "am", "clock", "morning", "afternoon"]):
                extracted_value = last_message.strip()
                
            return json.dumps({"extracted_value": extracted_value, "valid": valid})
            
        else:
            # Fallback chat response
            return "I'm sorry, I encountered an internal error. Please let me connect you to a human manager."
