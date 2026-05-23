from src.state_manager import StateManager
from src.llm_client import LLMClient
from src.sop_manager import SOPManager
from src.stages.faq_stage import FAQStage
from src.stages.qualification_stage import QualificationStage
from src.stages.escalation_stage import EscalationStage
from src.stages.summary_stage import SummaryStage

class ClosiraOrchestrator:
    def __init__(self, provider: str = None):
        self.llm_client = LLMClient(provider=provider)
        self.sop_manager = SOPManager()
        
        self.faq_stage = FAQStage(self.llm_client, self.sop_manager)
        self.qualification_stage = QualificationStage(self.llm_client)
        self.escalation_stage = EscalationStage(self.llm_client)
        self.summary_stage = SummaryStage(self.llm_client)

    def process_message(self, state: StateManager, user_message: str) -> str:
        """
        Receives a new user message, updates state, evaluates escalation rules,
        routes to either FAQ or Qualification, and returns the agent's response.
        """
        # 1. Add user message to history
        state.add_message("user", user_message)

        # 2. Run Escalation Detection (Stage 3)
        if self.escalation_stage.run(state):
            response = f"I apologize, but I need to refer you to a member of our clinic team to assist you further. [Reason: {state.escalation_reason}]. A manager will reach out shortly."
            state.add_message("assistant", response)
            return response

        # 3. Handle conversation based on current stage
        if state.stage == "qualification":
            # Continue lead qualification
            response = self.qualification_stage.run(state)
            state.add_message("assistant", response)
            return response
            
        elif state.stage == "completed":
            # Already finished, just redirect
            response = "Your booking request is being processed. A member of our staff will reach out to you shortly."
            state.add_message("assistant", response)
            return response

        # Default stage is "faq"
        # Determine if customer wants to book or if it's an FAQ question
        is_booking_intent = self._check_booking_intent(user_message)
        
        if is_booking_intent:
            # Transition to qualification stage
            response = self.qualification_stage.run(state)
            state.add_message("assistant", response)
            return response
        else:
            # Run FAQ answering (Stage 1)
            # The FAQ stage will set answered = False if out of scope
            initial_count = state.unanswered_count
            faq_response = self.faq_stage.run(state)
            
            # If unanswered count increased, an out-of-scope question was detected
            if state.unanswered_count > initial_count:
                # Trigger immediate escalation for out-of-scope questions as per instructions
                state.escalate_session(f"Out-of-scope question asked: '{user_message}'")
                response = f"I apologize, but we do not offer that service or have that information in our procedures. Because this is outside my scope, I am handing you over to a clinic manager who can assist you. A team member will follow up shortly."
                state.add_message("assistant", response)
                return response
                
            state.add_message("assistant", faq_response)
            return faq_response

    def generate_session_summary(self, state: StateManager) -> str:
        """Runs the Summary Stage (Stage 4) to compile the conversation summary."""
        return self.summary_stage.run(state)

    def _check_booking_intent(self, message: str) -> bool:
        """Determines if the customer is expressing intent to book an appointment."""
        booking_keywords = ["book", "booking", "schedule", "appointment", "reserve", "slot", "consultation", "treatment"]
        msg_lower = message.lower()
        return any(kw in msg_lower for kw in booking_keywords)
