import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Choose default provider based on available keys, fallback to mock
    if OPENAI_API_KEY:
        DEFAULT_PROVIDER = "openai"
    elif ANTHROPIC_API_KEY:
        DEFAULT_PROVIDER = "anthropic"
    else:
        DEFAULT_PROVIDER = "mock"
        
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
    
    # Path to SOP data file
    SOP_PATH = os.getenv("SOP_PATH", "sop.json")
