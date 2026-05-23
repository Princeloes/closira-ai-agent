import os
import json
from src.state_manager import StateManager
from src.orchestrator import ClosiraOrchestrator

def run_scenario_1_in_sop(provider: str, output_dir: str):
    """Scenario 1: Customer asks an in-SOP question."""
    state = StateManager()
    orch = ClosiraOrchestrator(provider=provider)
    
    transcript = []
    transcript.append("# Test Transcript: 1. In-SOP Question\n")
    transcript.append("Demonstrates answering an in-SOP question accurately using only SOP facts.\n")
    
    question = "What are your Botox prices?"
    transcript.append(f"**Customer**: {question}")
    
    response = orch.process_message(state, question)
    transcript.append(f"**AI Agent**: {response}\n")
    
    # Internal state metadata
    transcript.append("## Internal State Metadata")
    transcript.append(f"- **Stage**: {state.stage}")
    transcript.append(f"- **Escalated**: {state.escalated}")
    transcript.append(f"- **Escalation Reason**: {state.escalation_reason}")
    transcript.append(f"- **SOP Gaps Logged**: {state.sop_gaps}")
    transcript.append(f"- **Lead Details**: {json.dumps(state.qualification_responses)}")
    
    write_transcript(output_dir, "1_in_sop_question.md", transcript)

def run_scenario_2_out_of_scope(provider: str, output_dir: str):
    """Scenario 2: Customer asks something out of SOP scope."""
    state = StateManager()
    orch = ClosiraOrchestrator(provider=provider)
    
    transcript = []
    transcript.append("# Test Transcript: 2. Out-of-Scope Question\n")
    transcript.append("Demonstrates acknowledging a knowledge gap and escalating to a human rather than hallucinating.\n")
    
    question = "Do you offer teeth whitening?"
    transcript.append(f"**Customer**: {question}")
    
    response = orch.process_message(state, question)
    transcript.append(f"**AI Agent**: {response}\n")
    
    # Internal state metadata
    transcript.append("## Internal State Metadata")
    transcript.append(f"- **Stage**: {state.stage}")
    transcript.append(f"- **Escalated**: {state.escalated}")
    transcript.append(f"- **Escalation Reason**: {state.escalation_reason}")
    transcript.append(f"- **SOP Gaps Logged**: {state.sop_gaps}")
    transcript.append(f"- **Lead Details**: {json.dumps(state.qualification_responses)}")
    
    write_transcript(output_dir, "2_out_of_scope.md", transcript)

def run_scenario_3_escalation(provider: str, output_dir: str):
    """Scenario 3: Customer expresses frustration / complaint."""
    state = StateManager()
    orch = ClosiraOrchestrator(provider=provider)
    
    transcript = []
    transcript.append("# Test Transcript: 3. Escalation Trigger\n")
    transcript.append("Demonstrates immediate sentiment detection and escalation for complaints/medical safety concerns.\n")
    
    question = "I want to file a complaint about my last treatment. I got a bad rash on my face."
    transcript.append(f"**Customer**: {question}")
    
    response = orch.process_message(state, question)
    transcript.append(f"**AI Agent**: {response}\n")
    
    # Internal state metadata
    transcript.append("## Internal State Metadata")
    transcript.append(f"- **Stage**: {state.stage}")
    transcript.append(f"- **Escalated**: {state.escalated}")
    transcript.append(f"- **Escalation Reason**: {state.escalation_reason}")
    transcript.append(f"- **SOP Gaps Logged**: {state.sop_gaps}")
    transcript.append(f"- **Lead Details**: {json.dumps(state.qualification_responses)}")
    
    write_transcript(output_dir, "3_escalation_trigger.md", transcript)

def run_scenario_4_qualification(provider: str, output_dir: str):
    """Scenario 4: Complete lead qualification workflow."""
    state = StateManager()
    orch = ClosiraOrchestrator(provider=provider)
    
    transcript = []
    transcript.append("# Test Transcript: 4. Lead Qualification\n")
    transcript.append("Demonstrates structured lead qualification questions to gather and store customer data.\n")
    
    turns = [
        "Can I book a Botox session?",
        "Jane Doe",
        "Botox",
        "No, this is my first time",
        "Saturday morning at 10am"
    ]
    
    for turn in turns:
        transcript.append(f"**Customer**: {turn}")
        response = orch.process_message(state, turn)
        transcript.append(f"**AI Agent**: {response}\n")
        
    # Internal state metadata
    transcript.append("## Internal State Metadata")
    transcript.append(f"- **Stage**: {state.stage}")
    transcript.append(f"- **Escalated**: {state.escalated}")
    transcript.append(f"- **Lead Details Collected**:")
    transcript.append(json.dumps(state.qualification_responses, indent=2))
    
    write_transcript(output_dir, "4_lead_qualification.md", transcript)

def run_scenario_5_summary(provider: str, output_dir: str):
    """Scenario 5: Complete lead qualification followed by summary generation."""
    state = StateManager()
    orch = ClosiraOrchestrator(provider=provider)
    
    transcript = []
    transcript.append("# Test Transcript: 5. Conversation Summary\n")
    transcript.append("Demonstrates generating a structured JSON summary at the end of a session detailing intents, details, gaps, and recommendations.\n")
    
    turns = [
        "Can I schedule an appointment?",
        "Jane Doe",
        "Botox",
        "No, I haven't done it before",
        "Saturday morning at 10am"
    ]
    
    for turn in turns:
        transcript.append(f"**Customer**: {turn}")
        response = orch.process_message(state, turn)
        transcript.append(f"**AI Agent**: {response}\n")
        
    # Generate summary
    summary_json = orch.generate_session_summary(state)
    
    transcript.append("## Session End - Structured Summary (Stage 4)")
    transcript.append("```json")
    transcript.append(summary_json)
    transcript.append("```")
    
    write_transcript(output_dir, "5_conversation_summary.md", transcript)

def write_transcript(output_dir: str, filename: str, transcript: list):
    """Helper to write transcript list to file."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(transcript))
    print(f"Generated transcript: {filepath}")

def run_all_tests(provider: str, output_dir: str = "test_transcripts"):
    """Runs all 5 scenarios and outputs transcripts."""
    print(f"Running automated test scenarios using provider: {provider}...")
    run_scenario_1_in_sop(provider, output_dir)
    run_scenario_2_out_of_scope(provider, output_dir)
    run_scenario_3_escalation(provider, output_dir)
    run_scenario_4_qualification(provider, output_dir)
    run_scenario_5_summary(provider, output_dir)
    print("All test transcripts successfully generated!")
