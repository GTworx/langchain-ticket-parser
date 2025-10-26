# LangChain Structured Output Using Pydantic

This project demonstrates how to use LangChain with Pydantic for structured data extraction from text. It reads support tickets (in Turkish) from a CSV file, processes them using the Google Gemini 2.5 Flash model, and logs the validated, structured output to both the console and a JSONL file.

## ✨ Features

  * **Structured Data Extraction:** Uses Pydantic models to enforce a strict output schema from the LLM (e.g., enums for `issue_type`, `urgency`).
  * **Dual Logging:** Outputs results to `stdout` (pretty-printed JSON) and appends to `logs/outputs.jsonl` (JSONL format).
  * **Metadata Enrichment:** Automatically adds a unique `run_id` (UUID) and the `source_id` (from the CSV) to the JSONL log file for better traceability.
  * **Modern Environment:** Setup instructions provided for `uv`, the high-performance Python package manager.
  * **Secure API Key:** Uses a `.env` file to manage the `GOOGLE_API_KEY`, keeping it out of the source code.

## 📂 Project Structure

```
langchain-ticket-parser/
├── .env                # Stores your API key
├── .venv/              # Python virtual environment (managed by uv or venv)
├── logs/
│   └── outputs.jsonl   # Log file for structured output
├── process_tickets.py  # The main application script
└── support_tickets_minimal.csv # Input data
```

## ⚙️ Setup and Installation

These instructions assume you are on a Linux-based system like Ubuntu 24.04.

### Recommended (using `uv`)

1.  **Create the project directory:**

    ```bash
    mkdir langchain-ticket-parser
    cd langchain-ticket-parser
    ```

2.  **Install `uv` (if not already installed):**

    ```bash
    # Install curl if you don't have it
    sudo apt update
    sudo apt install curl

    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source your environment or restart your terminal for the 'uv' command
    source $HOME/.cargo/env 
    ```

3.  **Create the virtual environment and install packages:**

    ```bash
    # Create the venv using Python 3.12
    uv venv --python 3.12

    # Activate the venv
    source .venv/bin/activate

    # Install dependencies
    uv pip install "langchain==0.3.26" langchain-google-genai pydantic python-dotenv
    ```

4.  **Create your `.env` file:**
    Create a new file named `.env`:

    ```bash
    nano .env
    ```

    Add your Google API key to this file:

    ```env
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Add Project Files:**
    Ensure the `process_tickets.py` and `support_tickets_minimal.csv` files are present in your `langchain-ticket-parser` directory.

### Alternative (using standard `venv`)

1.  **Create and enter the directory:**
    ```bash
    mkdir langchain-ticket-parser
    cd langchain-ticket-parser
    ```
2.  **Create and activate the virtual environment:**
    ```bash
    sudo apt update
    sudo apt install python3.12-venv
    python3.12 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install packages:**
    ```bash
    pip install "langchain==0.3.26" langchain-google-genai pydantic python-dotenv
    ```
4.  **Create `.env` file:**
    Follow step 4 from the `uv` instructions above.
5.  **Add Project Files:**
    Ensure `process_tickets.py` and `support_tickets_minimal.csv` are present.

## 🏃‍♂️ Running the Script

Make sure your virtual environment is activated:

```bash
source .venv/bin/activate
```

Run the script, passing the CSV file as an argument:

```bash
python process_tickets.py support_tickets_minimal.csv
```

## 🏁 Expected Output

### 1\. Console (stdout)

You will see a pretty-printed JSON object for each ticket processed, directly in your terminal.

```bash
Processing support_tickets_minimal.csv... Logging to logs/outputs.jsonl

--- Processing CUST-001 ---
{
  "issue_type": "billing",
  "urgency": "high",
  "channel": "phone",
  "entities": {
    "amount": 200.0,
    "invoice_period": null,
    "ticket_id": null,
    "device": null,
    "address_move": null
  },
  "summary": "User called about a 200 TL overcharge on their bill and requests an urgent correction.",
  "status_suggestion": "in_progress"
}

--- Processing CUST-002 ---
{
  "issue_type": "technical",
  "urgency": "medium",
  "channel": "chat",
  ...
}
...
--- Done. Results appended to logs/outputs.jsonl ---
```

### 2\. Log File (`logs/outputs.jsonl`)

A `logs/` directory will be created (if it doesn't exist), and the `outputs.jsonl` file will contain one line of JSON for each record. This JSON includes the required `run_id` and `source_id` keys, in addition to the Pydantic model's data.

```json
{"run_id": "a1b2c3d4-...", "source_id": "CUST-001", "issue_type": "billing", "urgency": "high", "channel": "phone", "entities": {"amount": 200.0, "invoice_period": null, "ticket_id": null, "device": null, "address_move": null}, "summary": "User called about a 200 TL overcharge on their bill and requests an urgent correction.", "status_suggestion": "in_progress"}
{"run_id": "a1b2c3d4-...", "source_id": "CUST-002", "issue_type": "technical", "urgency": "medium", "channel": "chat", "entities": {"amount": null, "invoice_period": null, "ticket_id": null, "device": "application", "address_move": null}, "summary": "User wrote via live chat that the application crashes immediately on launch; requests technical team to investigate.", "status_suggestion": "open"}
...
```
