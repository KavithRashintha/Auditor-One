# Auditor-One: AI-Native Website Audit Tool

Auditor-One is a lightweight, AI-powered Website Audit Tool built for EIGHT25MEDIA. It combines deterministic data harvesting with advanced LLM reasoning to evaluate webpages and generate structured, actionable recommendations.

## 🚀 Setup Instructions

Follow these steps to run Auditor-One locally:

### 1. Prerequisites

- **Python 3.11+** (Make sure to check "Add Python to PATH" during installation on Windows)
- **Node.js 18+** (with npm)
- An API key for one of the supported LLM providers:
  - OpenAI API Key (`OPENAI_API_KEY`)
  - Anthropic API Key (`ANTHROPIC_API_KEY`)
  - Hugging Face API Token (`HF_API_TOKEN`)

### 2. Clone the Repository

```bash
git clone <repository_url>
cd Auditor-One
```

### 3. Backend Setup

Follow the instructions matching your operating system to set up the backend.

#### 🍏 macOS & Linux

1. **Create and activate the virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Install Playwright Chromium browser:**
   ```bash
   playwright install chromium
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn backend.main:app --reload
   ```

#### 🪟 Windows

1. **Create and activate the virtual environment:**
   
   Using **PowerShell**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   
   Using **Command Prompt**:
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Install Playwright Chromium browser:**
   ```bash
   playwright install chromium
   ```

4. **Configure environment variables:**
   
   Using **PowerShell**:
   ```powershell
   Copy-Item .env.example .env
   ```
   
   Using **Command Prompt**:
   ```cmd
   copy .env.example .env
   ```

5. **Start the FastAPI server:**
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

---

### 4. Configure Environment Variables

Open the newly created `.env` file in the root directory and configure the environment variables:

```ini
# LLM Provider selection: "openai" | "anthropic" | "hf"
LLM_PROVIDER=openai

# Provider Keys (only configure the one you are using)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-your-anthropic-key-optional
HF_API_TOKEN=hf_your-huggingface-token-optional

# Hugging Face Settings (optional)
HF_MODEL=meta-llama/Llama-3.3-70B-Instruct
HF_ENDPOINT=https://router.huggingface.co/v1

# Application URLs & Logging
FRONTEND_URL=http://localhost:5173
LOG_DIR=./logs
```

---

### 5. Frontend Setup

The frontend setup is identical across platforms. Open a new terminal/command prompt window, navigate to the `frontend/` directory, and run the following commands:

```bash
cd frontend
npm install
npm run dev
```

The frontend application will start and run on `http://localhost:5173` (or `http://localhost:5174` if the port is in use). Open the URL in your web browser.

---

## 🏗️ Architecture Overview

The system implements a Backend-For-Frontend (BFF) Gateway pattern using FastAPI and Server-Sent Events (SSE) to stream deterministic data and non-deterministic AI generation to a React SPA.

```mermaid
graph TD
    User([User]) -->|Input URL| React[React SPA Shell]
    React -->|POST /audit| FastAPI[FastAPI SSE Gateway]
    
    subgraph "Layer 1: Security"
        FastAPI --> SSRF[SSRF Guard]
    end
    
    subgraph "Layer 2: Deterministic"
        SSRF --> Harvester[Selectolax Harvester]
        Harvester --> Metrics[Metrics DTO]
        Harvester --> Lexer[DOM Lexer / Token Cap]
    end
    
    subgraph "Layer 3: Heuristics & Orchestration"
        Metrics --> Engine[Heuristics Engine]
        Engine --> Rules[(agency_rules.json)]
        Lexer --> Prompt[Prompt Compiler]
        Engine --> Prompt
    end
    
    subgraph "Layer 4: AI & Logging"
        Prompt --> LLM[LLM Strategy Orchestrator]
        LLM -->|Stream| React
        LLM --> Repo[Local Disk Trace Repository]
        Repo --> Logs[(logs/)]
    end
```

### BFF Gateway Pattern

We use FastAPI as a Backend-For-Frontend (BFF) to encapsulate complex integrations. Instead of the frontend querying scraping APIs or LLM APIs directly, the BFF orchestrates the entire pipeline:

1. **Security**: Verifies URL.
2. **Scraping**: Harvests deterministic metrics quickly.
3. **Reasoning**: Compiles prompts and triggers the LLM.
4. **Streaming**: Multiplexes the execution states (stages, metrics, chunks, JSON, errors) into a single unified SSE stream consumed by the React UI.

---

## 🧠 AI Design Decisions & Prompting Strategy

### Token Economy Decisions

- **Why Selectolax over BeautifulSoup4?** We chose the `selectolax` C-parser because it routinely parses large DOM trees in under 10ms, whereas BS4 can take over 100ms. In an AI-native application, we want the LLM to spend token generation time, not scraping wait time.
- **Why the 12,800 Character Token Cap?** Instead of feeding massive raw HTML dumps to the LLM, the `DOMLexer` intelligently strips out semantic noise (scripts, styles, SVGs) and converts the tree to Markdown. The output is hard-capped at 12,800 characters (~3,200 tokens). This ensures predictable costs, avoids exceeding context windows, and forces the LLM to focus on the most important structural messaging of the page.

### Grounding & Agency Rules

We strictly separate the deterministic layer from the non-deterministic layer. Factual metrics (e.g., total images, links, H1 counts) are scraped first and locked into a `ScrapedMetricsDTO`.
These metrics are passed through a deterministic **Heuristics Engine** which checks them against `agency_rules.json` (e.g., "Missing H1", "Too few CTAs").
The LLM is prompted strictly using these verified metrics and rules, preventing it from hallucinating non-existent webpage elements.

### The Stream Splitter

To deliver an excellent UX, the AI output is streamed progressively to the frontend.
The LLM is instructed to generate Markdown insights first, followed by a strict delimiter `---REC_SPLIT---`, followed by a JSON array of actionable recommendations. The backend parses this stream in real-time, yielding markdown chunks to the UI immediately, while accumulating and verifying the JSON array before the final payload.

---

## ⚙️ Technical Trade-offs

### In-Memory vs. Disk Logging

For **Prompt Logs & Reasoning Traces**, we opted for a `LocalDiskTraceRepository`. The system writes the complete, untruncated system prompt, user prompt, deterministic state, and raw LLM output to the `logs/` directory asynchronously.

- *Trade-off*: We avoided setting up an external database (PostgreSQL/MongoDB) or dedicated observability tool (Langfuse) to keep setup simple and local. Writing to disk asynchronously avoids blocking the SSE stream, providing the required auditability without the infrastructure overhead.

### SSRF Defense Rationale

A tool that makes HTTP requests on behalf of a user is highly susceptible to Server-Side Request Forgery (SSRF).
We implemented a strict security layer that resolves target domains to IP addresses and rejects private, loopback, link-local, and AWS metadata IPs (`169.254.169.254`).

- *Trade-off*: Validating IPs manually is safe but slightly increases the TTFB (Time to First Byte). However, it is an absolutely necessary defense for cloud-deployed web scrapers.

### Strategy Pattern for LLMs

The architecture uses the **Strategy Pattern** for the `LLMOrchestrator` (`BaseLLMOrchestrator`, `OpenAIOrchestrator`, `AnthropicOrchestrator`, `HFLLMOrchestrator`).

- *Trade-off*: By abstracting the provider, we accept a slightly more complex backend structure instead of tightly coupling to the OpenAI SDK. This allows easy swapping of models via the `.env` file (e.g., `LLM_PROVIDER=hf` or `LLM_PROVIDER=anthropic`).

---

## 🔍 Deliverables Checklist

- [x] **GitHub Repository**: Complete solution included.
- [x] **Setup Instructions**: Available above.
- [x] **README**: Architecture, decisions, and trade-offs documented.
- [x] **Prompt Logs**: Reasoning traces are generated automatically and saved to the `/logs` directory during every execution.

---

## 🔮 Known Limitations & Future Improvements

If given more time, we would implement the following improvements:

1. **Playwright/Puppeteer Support**: The current HTTP request harvester (`httpx`) cannot execute JavaScript. Sites heavily reliant on React/Vue client-side rendering may return incomplete DOM trees. Adding an optional Playwright headful/headless layer would fix this.
2. **Streaming JSON Parsing**: Currently, the JSON recommendation array is accumulated in memory and parsed at the end. We would implement a streaming JSON parser (like `ijson`) to yield recommendation cards to the UI one by one as they are generated.
3. **Persisted History & Database**: We would replace the local disk logging with a PostgreSQL database, allowing users to revisit past audits and compare metrics over time.
4. **Enhanced Markdown Rendering**: Add customized Tailwind typography plugins to the frontend to render the LLM's markdown tables and code blocks more beautifully.
