# ⚖️ Prompt Evaluation Sandbox

A lightweight web tool to **A/B test system prompts** using an **LLM-as-a-Judge** approach.

Enter a query, define two competing system prompts, and let an AI judge score which prompt produces the better response — all from a clean Streamlit interface.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)

## How It Works

1. **Define two system prompts** (Prompt A vs Prompt B)
2. **Enter a user query** to test both prompts with
3. **Choose an evaluation metric** (Faithfulness, Helpfulness, Hallucinations, etc.)
4. The tool sends the query to both prompts **simultaneously**
5. An **LLM Judge** scores both responses (1-10) and declares a winner

## Free LLM Providers

No paid API keys needed! Choose from three free options:

| Provider | Type | Free Tier | Setup |
|----------|------|-----------|-------|
| **Groq** | Cloud | 14,400 req/day | [Get free key](https://console.groq.com/keys) |
| **Google Gemini** | Cloud | 15 req/min | [Get free key](https://aistudio.google.com/apikey) |
| **Ollama** | Local | Unlimited | [Download](https://ollama.com/download) |

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up API keys (choose one)

**Option A — Groq (recommended, fastest free option):**
1. Go to https://console.groq.com/keys
2. Create a free account and generate an API key
3. Either paste it in the sidebar when running the app, or:
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

**Option B — Google Gemini:**
1. Go to https://aistudio.google.com/apikey
2. Generate a free API key
3. Paste it in the sidebar or add to `.env`

**Option C — Ollama (fully local, no API key):**
1. Install Ollama from https://ollama.com/download
2. Pull a model: `ollama pull llama3.2`
3. Select "Ollama (Local)" in the app sidebar

### 3. Run the app

```bash
streamlit run app.py
```

## Evaluation Metrics

| Metric | What It Measures |
|--------|-----------------|
| **Faithfulness** | Does the response stay on-topic and answer what was asked? |
| **Lack of Hallucinations** | Does it avoid fabricating facts or citations? |
| **Helpfulness** | Does it fully address the user's needs? |
| **Clarity & Conciseness** | Is it clear, well-structured, and free of filler? |
| **Safety & Tone** | Is it appropriate, unbiased, and professional? |

## Project Structure

```
Prompt-Evaluation-Sandbox/
├── app.py              # Streamlit frontend
├── llm_provider.py     # LLM provider abstraction (Groq/Gemini/Ollama)
├── evaluator.py        # LLM-as-a-Judge evaluation logic
├── requirements.txt    # Python dependencies
├── .env.example        # Template for API keys
└── .gitignore
```

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **AI:** Groq / Google Gemini / Ollama (all free)
