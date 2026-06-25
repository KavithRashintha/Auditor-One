# Auditor-One: `.env` Environment Setup & Hugging Face Troubleshooting Guide

This guide details the active `.env` configuration of the application and provides recovery instructions if you encounter Hugging Face credit limit or token errors.

---

## 🔑 Active `.env` Configuration

Below is the current content of the `.env` file in the root of the project:

```ini
LLM_PROVIDER=hf
HF_API_TOKEN=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
HF_MODEL=meta-llama/Llama-3.3-70B-Instruct
HF_ENDPOINT=https://router.huggingface.co/v1
FRONTEND_URL=http://localhost:5174
LOG_DIR=./logs
```

---

## 🚨 Hugging Face Credit / Rate Limit Recovery

If the Hugging Face (HF) API is not responding or returns errors such as:
*   `Exceeded credit limit`
*   `Rate limit reached`
*   `Unauthorized / Invalid Token`

Follow these steps to recover:

### Step 1: Generate a New Read Token
1. Go to your Hugging Face Account Settings: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2. Click **Create new token**.
3. Set the **Token type** to **Read**.
4. Give it a name (e.g., `Auditor-One-Local`) and click **Generate**.
5. Copy the newly generated token (starts with `hf_`).

### Step 2: Update the `.env` File
Open the `.env` file in the root directory and replace the `HF_API_TOKEN` value with your new token:

```ini
HF_API_TOKEN=hf_yourNewTokenHere
```

### Step 3: Reload the Backend
For changes in the `.env` file to take effect, the FastAPI backend server must be restarted/reloaded:

*   **If running natively (Terminal/CMD/PowerShell)**:
    1. Stop the running server by pressing `Ctrl + C` in the backend terminal.
    2. Restart the backend:
       ```bash
       uvicorn backend.main:app --reload
       ```

*   **If running with Docker**:
    1. Stop and down the containers:
       ```bash
       docker compose down
       ```
    2. Start the services again (Docker will reload the new environment variables):
       ```bash
       docker compose up --build
       ```
