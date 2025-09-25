# Running the script

Prerequisites
- Python 3.9+ and pip
- (Optional) Docker Desktop if running Qdrant locally
- (Optional) Make (macOS/Linux) or just use the raw commands below

Setup
- Windows (PowerShell):
    ```
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```
- macOS/Linux:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

- Run the streamlit :
    ```
    python -m streamlit run ./main.py
    ```

