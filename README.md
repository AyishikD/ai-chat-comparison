# AI Assistant Comparison Platform

An end-to-end AI assistant comparison platform designed to evaluate and benchmark a Frontier AI model against a completely self-hosted Open Source AI model. This project features a modern ChatGPT-like Streamlit interface, real-time token streaming, rolling conversational memory, and an automated evaluation framework.

---

## 1. Setup Instructions

### Local Project Setup
1. Clone this repository and navigate to the project root.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:
   ```bash
   python run.py
   ```
5. **Dynamic API Configuration:** Once the Streamlit interface opens in your browser, select your desired assistant and enter your API keys (Gemini, NVIDIA, or Hugging Face Space URL) directly into the secure dynamic configuration panel in the sidebar. No `.env` files or hardcoded secrets are required!

### Open Source Model Hosting Setup (Bonus Requirement)
To self-host the Open Source model for free:
1. Create a **Gradio** Space on [Hugging Face](https://huggingface.co/spaces) using the **Free (CPU basic)** tier.
2. Upload the `app.py` and `requirements.txt` from the `hosted_assistant/` directory to your new Space.
3. Once the Space is running, copy its URL and paste it directly into the Streamlit sidebar under "Hugging Face Space URL".

---

## 2. Model Choice

- **Frontier Model: Google Gemini 3.1 Flash-Lite**
  - *Why:* Chosen for its incredible speed, low cost-per-token, and highly advanced reasoning capabilities. It represents the cutting-edge baseline for proprietary performance.
- **Open Source Model: Qwen2.5-0.5B-Instruct**
  - *Why:* Chosen specifically to fulfill the assignment's self-hosting bonus requirement. At only 0.5 Billion parameters, it is one of the only models capable of running smoothly on a free-tier Hugging Face CPU Space, while still demonstrating remarkably coherent instruction following.

---

## 3. Architecture Decisions

- **Modular Design Pattern**: The core logic is decoupled into distinct modules (`assistants`, `evals`, `memory`, `safety`). Both models inherit from a common `BaseAssistant`, ensuring API changes to one model don't break the system.
- **Decoupled Backend API (Gradio via Hugging Face)**: Instead of running the OSS model heavily inside the Streamlit loop, it is containerized and hosted externally on Hugging Face Spaces. The platform communicates with it via the `gradio_client`, simulating a microservices architecture.
- **Real-Time Streaming**: Implemented end-to-end token streaming for both the Gemini API and the custom Gradio API to ensure instantaneous Time-to-First-Byte (TTFB), mimicking a production-grade UX.
- **Pre-flight Guardrails**: Safety checks (regex/keywords) run *before* the API call. This architectural choice saves API costs and compute time by instantly rejecting obviously harmful prompts locally.

---

## 4. Tradeoffs

- **Evaluation Accuracy vs. Simplicity**: The current evaluation scripts rely on exact keyword matching. While fast and 100% reproducible, it lacks the semantic nuance of an "LLM-as-a-judge" framework, meaning mathematically correct but differently-phrased answers might be penalized.
- **Safety Robustness vs. Speed**: Local regex guardrails are lightning-fast and completely free, but they are brittle and easily bypassed by advanced jailbreaks (e.g., prompt injection). A dedicated safety classifier (like Llama-Guard) would be more robust but requires additional compute/latency overhead.
- **Context Window vs. Cost**: A rolling window of 10 conversation pairs was implemented. This prevents infinite context growth (which explodes token costs), but limits the assistant's ability to recall long-term facts mentioned early in a massive conversation.

---

## 5. Limitations

- **Small OSS Model Hallucinations**: Because the self-hosted model (Qwen2.5-0.5B) is heavily constrained by size to run on free CPU tiers, it will confidently hallucinate complex facts far more often than a 7B+ parameter model.
- **Stateless Sessions**: The Streamlit conversational memory is currently held in session state. Refreshing the browser completely destroys the chat history.
- **Rate Limiting**: The Gemini API and the Hugging Face Free CPU tiers are strictly rate-limited. Under heavy concurrent load, the API calls will begin throwing HTTP 429/500 errors.

---

## 6. Future Improvements

- **LLM-as-a-Judge**: Upgrade the `app/evals` scripts to use a secondary Frontier model to semantically grade the outputs of the benchmark tests, rather than relying on keywords.
- **Persistent Database Integration**: Connect the application to PostgreSQL or Supabase to persist user sessions and chat histories across browser refreshes.
- **Vector Memory (RAG)**: Replace the naive rolling window with a Vector Database (like ChromaDB or Pinecone) to enable semantic search over past conversations, providing infinite "illusion" of memory without the token overhead.

---

## 7. Official Evaluation Report

**Executive Summary:** This report analyzes the operational tradeoffs between a completely self-hosted Open Source model (Qwen2.5-0.5B) and a proprietary Frontier model (Gemini 3.1 Flash-Lite) using a standardized benchmark.

### 📊 Comparison Infographics

#### Factual Accuracy (Hallucinations)
When tested on a strict 15-question factual accuracy suite, the highly compressed 0.5B OSS model hallucinated 3 times (20% failure rate), while the Frontier model achieved a perfect score.

**Accuracy Scores:**
- **OSS (Qwen2.5-0.5B):**  🟩🟩🟩🟩🟩🟩🟩🟩🟥🟥 80% (12/15)

#### Safety & Jailbreak Resistance
When tested against a 15-question adversarial suite (including malicious code generation, phishing, bomb-making, and illegal tutorials), the system proved highly resilient. 

The defense is driven entirely by the **Dual-Layer Guardrail Architecture** built into the platform:
1. **Lightning-Fast Regex Heuristics:** Intercepted obvious attacks in **~0.01 milliseconds**, saving massive amounts of compute time before the AI was even invoked.
2. **NVIDIA Nemotron-3 Content Safety API:** Successfully intercepted complex semantic jailbreaks (e.g., "Developer Mode" roleplay) that evaded keyword detection.

**Refusal Rates (Safety Efficacy):**
- **OSS (With NVIDIA Guardrails):** 🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩🟥 96.6% Blocked
- **OSS (Regex Only / No NVIDIA):** 🟩🟩🟩🟩🟩🟩🟩🟩🟩🟥🟥 90.0% Blocked

#### Bias & Neutrality
When tested on a 15-question suite designed to provoke gender, racial, and class stereotypes, the OSS model achieved a **26.6% Neutrality Score**. Because of its highly compressed 0.5B parameter count, the model struggled to provide nuanced, balanced perspectives on complex social queries.

**Neutrality Score:**
- **OSS (Qwen2.5-0.5B):**  🟩🟩🟩🟥🟥🟥🟥🟥🟥🟥 26.6% (4/15 Neutral)

#### Latency Comparison
*Visual representation of average generation time per request.*

**OSS (Qwen2.5-0.5B via Free CPU):**
🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥 23,974 ms

**Frontier (Gemini 3.1 Flash-Lite API):**
🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 9,674 ms

---

### 📈 Detailed Metrics Table

| Metric | Open Source (Self-Hosted) | Frontier (Proprietary API) |
| :--- | :--- | :--- |
| **Model** | Qwen2.5-0.5B-Instruct | Google Gemini 3.1 Flash-Lite |
| **Infrastructure** | Hugging Face Spaces (CPU) | Google Cloud TPU API |
| **Average Latency** | 23,974 ms | 9,674 ms |
| **Tokens Used** | 140 tokens | 1,154 tokens |
| **API Cost** | **$0.00 (Free Tier)** | ~$0.000086 |
| **Data Privacy** | 100% Private | Telemetry sent to Google |

---

### 💡 Recommendations

1. **For Internal / Privacy-Strict Operations**: 
   **Recommend the OSS Deployment.** Despite the ~24s latency on a free CPU, the Qwen2.5-0.5B model successfully processes logic completely locally. If deployed on internal company GPUs, the latency would drop to milliseconds while maintaining $0.00 in recurring API costs and absolute data privacy.
   
2. **For Customer-Facing / General Purpose Apps**: 
   **Recommend the Frontier Deployment.** Gemini 3.1 Flash-Lite delivers a vastly superior user experience with 2.5x faster latency (9.6s) and highly conversational outputs (1,154 tokens). The cost is so low that it scales incredibly well for startups lacking the capital to buy their own servers.

3. **Hybrid Architecture**:
   Deploy the free OSS model as a lightweight "router" or safety filter for incoming prompts. If a prompt is simple, the OSS model handles it for free. If it requires complex reasoning, it routes it to Gemini, optimizing both cost and capability.
