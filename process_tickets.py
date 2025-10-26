import sys
import os
import csv
import json
import uuid
from pathlib import Path
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# --- Pydantic Schemas ---
# Define enums to enforce strict categories
class IssueType(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"

class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Channel(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    CHAT = "chat"
    UNKNOWN = "unknown"

class StatusSuggestion(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

# Define the nested 'entities' model
class Entities(BaseModel):
    amount: Optional[float] = Field(default=None, description="Billing amount mentioned")
    invoice_period: Optional[str] = Field(default=None, description="Invoice or billing period")
    ticket_id: Optional[str] = Field(default=None, description="Existing ticket ID")
    device: Optional[str] = Field(default=None, description="Device model (e.g., modem, router)")
    address_move: Optional[bool] = Field(default=None, description="Is the user asking to move address?")

# Define the main extraction schema
class TicketExtraction(BaseModel):
    issue_type: IssueType
    urgency: Urgency
    channel: Channel
    entities: Entities
    summary: str = Field(description="A brief summary of the user's issue")
    status_suggestion: StatusSuggestion

# --- System Prompt ---
SYSTEM_PROMPT = """
You are an expert support ticket analysis system. Your task is to extract structured data 
from a user's support ticket and format it *exactly* according to the 
provided Pydantic schema.

- Analyze the user's intent, tone, and specific details.
- `issue_type`: Classify the main problem.
- `urgency`: Infer from the user's language (e.g., "urgent" -> high).
- `channel`: Identify how the user contacted us (e.g., "contacted them by phone" -> phone). If not mentioned, use "unknown".
- `entities`: Extract specific details. If a detail is not present, use `null`.
- `summary`: Provide a concise summary *in English*.
- `status_suggestion`: Suggest a logical next step.
"""

def setup_logging():
    """Creates the log directory and file."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "outputs.jsonl"
    return log_file

def main(csv_file_path: Path):
    """
    Main processing loop. Reads CSV, calls LLM, and logs results.
    """
    # 1. Setup Environment and LLM
    load_dotenv()
    if os.getenv("GOOGLE_API_KEY") is None:
        print("Error: GOOGLE_API_KEY not found in .env file.", file=sys.stderr)
        sys.exit(1)

    log_file_path = setup_logging()
    run_id = str(uuid.uuid4())

    # Initialize LLM and prompt
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(TicketExtraction)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Please extract the following ticket text:\n\n```{text}```"),
    ])
    chain = prompt | structured_llm

    print(f"Processing {csv_file_path.name}... Logging to {log_file_path}")

    # 2. Open log file in append mode
    with log_file_path.open('a', encoding='utf-8') as log_f:
        # 3. Read CSV file
        try:
            with csv_file_path.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 4. Process each row
                for row in reader:
                    source_text = row.get('sikayet')
                    source_id = row.get('user_id')

                    if not source_text:
                        continue

                    print(f"\n--- Processing {source_id} ---")
                    
                    try:
                        # Call the chain
                        result: TicketExtraction = chain.invoke({"text": source_text})

                        # 5. Log to stdout (pretty-printed)
                        print(result.model_dump_json(indent=2))

                        # 6. Log to JSONL file
                        log_entry = {
                            "run_id": run_id,
                            "source_id": source_id,
                            **result.model_dump() # Add Pydantic data
                        }
                        
                        # Use ensure_ascii=False for Turkish in summary if needed
                        log_f.write(json.dumps(log_entry) + "\n")

                    except Exception as e:
                        print(f"Error processing {source_id}: {e}", file=sys.stderr)

        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_file_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\n--- Done. Results appended to {log_file_path} ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_tickets.py <path_to_csv_file>", file=sys.stderr)
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    main(csv_path)
