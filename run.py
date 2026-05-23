import argparse
import sys
import json
from src.state_manager import StateManager
from src.orchestrator import ClosiraOrchestrator
from test_scenarios import run_all_tests

# ANSI colors for premium terminal styling
CLR_HEADER = "\033[95m"
CLR_USER = "\033[94m"
CLR_AGENT = "\033[92m"
CLR_WARN = "\033[93m"
CLR_FAIL = "\033[91m"
CLR_END = "\033[0m"
CLR_BOLD = "\033[1m"

def print_banner():
    banner = f"""
{CLR_HEADER}{CLR_BOLD}=============================================================
             CLOSIRA CUSTOMER ASSISTANT v1.0
          SMB: Bloom Aesthetics Clinic - Booking Bot
============================================================={CLR_END}
Welcome to Bloom Aesthetics Clinic booking system!
Interactive modes:
  * Chat to explore the FAQ system
  * Type 'book' or 'appointment' to trigger lead qualification
  * Type 'exit' to end session and output summary
  * Type a complaint or out-of-scope service (e.g. teeth whitening) to see escalation

System will default to Mock LLM if no API keys are found.
-------------------------------------------------------------
"""
    print(banner)

def run_chat_loop(provider: str):
    print_banner()
    
    state = StateManager()
    try:
        orch = ClosiraOrchestrator(provider=provider)
    except Exception as e:
        print(f"{CLR_FAIL}Error initializing orchestrator: {e}{CLR_END}")
        sys.exit(1)
        
    print(f"{CLR_WARN}Status: Using '{orch.llm_client.provider}' LLM backend.{CLR_END}\n")
    print(f"{CLR_AGENT}{CLR_BOLD}AI Agent{CLR_END}: Hello! Welcome to Bloom Aesthetics Clinic. How can I help you today?")
    
    while True:
        try:
            user_input = input(f"\n{CLR_USER}{CLR_BOLD}You{CLR_END}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in ["exit", "quit"]:
            print(f"\n{CLR_WARN}Session ended by user. Generating final summary...{CLR_END}")
            break
            
        # Process message
        response = orch.process_message(state, user_input)
        print(f"{CLR_AGENT}{CLR_BOLD}AI Agent{CLR_END}: {response}")
        
        # Check if conversation is escalated or completed
        if state.escalated:
            print(f"\n{CLR_FAIL}{CLR_BOLD}[SYSTEM ALERT] Session Escalated to Human Agent!{CLR_END}")
            print(f"{CLR_FAIL}Reason: {state.escalation_reason}{CLR_END}")
            break
            
        if state.stage == "completed":
            print(f"\n{CLR_WARN}{CLR_BOLD}[SYSTEM ALERT] Lead Qualification Completed!{CLR_END}")
            break
            
    # Generate and print the summary at session end
    print(f"\n{CLR_HEADER}{CLR_BOLD}=================== CONVERSATION SUMMARY ==================={CLR_END}")
    summary = orch.generate_session_summary(state)
    print(summary)
    print(f"{CLR_HEADER}{CLR_BOLD}============================================================{CLR_END}")

def main():
    parser = argparse.ArgumentParser(description="Closira AI Support Workflow Orchestrator")
    parser.add_argument("--chat", action="store_true", help="Start an interactive chat session")
    parser.add_argument("--test", action="store_true", help="Run the 5 automated test scenarios and output transcripts")
    parser.add_argument("--provider", type=str, choices=["openai", "anthropic", "mock"], help="Override default LLM provider")
    
    args = parser.parse_args()
    
    # Resolve provider
    provider = args.provider
    
    if args.test:
        run_all_tests(provider or "mock")
    elif args.chat:
        run_chat_loop(provider)
    else:
        parser.print_help()
        print("\nExample commands:")
        print("  python run.py --chat                 # Start interactive chat")
        print("  python run.py --test                 # Generate test transcripts in test_transcripts/")
        print("  python run.py --chat --provider mock # Run interactive chat using local Mock engine")

if __name__ == "__main__":
    main()
