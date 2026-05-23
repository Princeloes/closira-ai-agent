from typing import List, Dict, Any, Optional

class StateManager:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.stage: str = "faq"  # stages: "faq", "qualification", "escalated", "completed"
        
        # Lead qualification state (Stage 2)
        self.qualification_step: int = 0
        self.qualification_responses: Dict[str, Any] = {
            "name": None,
            "treatment_interest": None,
            "prior_treatment": None,
            "preferred_schedule": None
        }
        
        # Escalation tracking (Stage 3)
        self.unanswered_count: int = 0
        self.escalated: bool = False
        self.escalation_reason: Optional[str] = None
        
        # SOP gap tracking (Stage 4)
        self.sop_gaps: List[str] = []

    def add_message(self, role: str, content: str):
        """Appends a message to the chat history."""
        self.history.append({"role": role, "content": content})

    def escalate_session(self, reason: str):
        """Flags the conversation as escalated with a reason."""
        self.escalated = True
        self.stage = "escalated"
        self.escalation_reason = reason

    def log_sop_gap(self, question: str):
        """Logs an out-of-scope question asked by the customer."""
        self.sop_gaps.append(question)
        self.unanswered_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Dumps current state to a dictionary."""
        return {
            "stage": self.stage,
            "qualification_step": self.qualification_step,
            "qualification_responses": self.qualification_responses,
            "unanswered_count": self.unanswered_count,
            "escalated": self.escalated,
            "escalation_reason": self.escalation_reason,
            "sop_gaps": self.sop_gaps,
            "history_length": len(self.history)
        }
