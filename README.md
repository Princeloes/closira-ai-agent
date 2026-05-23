# Closira AI Agent Support Workflow

An intelligent customer support and lead qualification workflow built for **Bloom Aesthetics Clinic** (an SMB client on the Closira platform). 

This application simulates customer conversations across four core stages (FAQ, Lead Qualification, Escalation Detection, and Summarization). It supports OpenAI (GPT-4o), Anthropic (Claude-3.5), and a local deterministic Mock engine for offline evaluation.

---

## Features

1. **Stage 1: FAQ Grounding**: Answers queries strictly matching the clinic's SOP. Detects out-of-scope inquiries to log them as knowledge gaps.
2. **Stage 2: Lead Qualification**: Asks 2-3 structured questions to capture customer contact details, interested service, previous experience, and booking slot.
3. **Stage 3: Safety & Escalation Detection**: Real-time filters for complaint detection, medical concerns/safety queries, pricing negotiation, and human handoff requests.
4. **Stage 4: CRM Summary**: Automatically compiles conversational intents, collected lead details, and procedure gaps into a clean JSON summary at session end.
5. **No API Keys Required by Default**: Includes a fallback Mock LLM mode that allows testing the complete state machine offline.

---

## Installation & Setup

### 1. Clone/Navigate to Directory
Ensure you are inside the project root:
```bash
cd closira_ai_agent
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys (Optional)
If you want to run the workflow using live OpenAI or Anthropic models, create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your-openai-api-key
# OR
ANTHROPIC_API_KEY=your-anthropic-api-key
```
*Note: If no keys are specified, the system will fall back to the Mock provider to run offline.*

---

## How to Run

### Interactive CLI Chat Mode
To start a live conversation with the AI Agent in the terminal, run:
```bash
python run.py --chat
```
- Type standard inquiries (e.g., *"What are your hours?"*, *"What are your Botox prices?"*).
- Type *"book"* to start lead qualification.
- Type *"exit"* or *"quit"* to close the session and review the final summary.

### Run Automated Tests & Generate Transcripts
To run all 5 expected scenario tests and generate the Markdown transcript files in the `test_transcripts/` directory, run:
```bash
python run.py --test
```
This generates the following deliverables:
- `test_transcripts/1_in_sop_question.md`
- `test_transcripts/2_out_of_scope.md`
- `test_transcripts/3_escalation_trigger.md`
- `test_transcripts/4_lead_qualification.md`
- `test_transcripts/5_conversation_summary.md`

### Override Provider
To test a specific backend explicitly:
```bash
python run.py --chat --provider mock
python run.py --chat --provider openai
python run.py --chat --provider anthropic
```

---

## Project Structure

```
closira_ai_agent/
│
├── README.md               # Setup and instructions
├── prompt_design.md        # Prompt engineering choices & system prompts
├── requirements.txt        # Package dependencies
├── sop.json                # Clinic SOP parameters
├── run.py                  # CLI entrypoint
├── test_scenarios.py       # Auto-test script
│
├── src/
│   ├── __init__.py
│   ├── config.py           # Config and environment loader
│   ├── sop_manager.py      # SOP parser and formatting
│   ├── state_manager.py    # Session history and state transitions
│   ├── llm_client.py       # Wrapper for OpenAI/Anthropic/Mock
│   │
│   └── stages/             # Individual workflow logic
│       ├── __init__.py
│       ├── faq_stage.py            # Stage 1
│       ├── qualification_stage.py  # Stage 2
│       ├── escalation_stage.py     # Stage 3
│       └── summary_stage.py        # Stage 4
│
└── test_transcripts/       # Auto-generated transcripts
```

---

## Trade-offs & Known Limitations

- **Session Persistence**: Currently, the conversation state is stored in memory (`StateManager` instance). In a production deployment, this would be backed by a persistent database (e.g. Redis or PostgreSQL) using unique session IDs.
- **Context Window Growth**: Since the full conversation history is sent to the LLM on each turn for context, very long chat logs will consume more tokens. In production, chat histories should be pruned or summarized after 10-15 turns.
- **Mock Mode Strictness**: The Mock LLM relies on regex and keyword checks. While perfect for testing the core state machine, it doesn't possess the conversational flexibility of a real LLM.
