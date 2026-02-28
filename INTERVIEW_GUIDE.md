# Prompt Evaluation Sandbox — Interview Guide

## The Setup (Initiative & Hustle)

> "When we scheduled this interview, I took a closer look at the job description, specifically the requirements around **A/B testing and output evaluation**. Since my day-to-day as a cloud systems engineer is heavily focused on backend architecture, I wanted to spend this weekend building a practical bridge between my systems background and prompt engineering. So, I built a lightweight **Prompt Evaluation Sandbox**."

### Why This Project Maps to the Role

| Job Requirement | What This Project Demonstrates |
|---|---|
| Run A/B tests, output evaluations, and few-shot benchmarking | The entire app is an A/B testing framework for prompts |
| Design and implement high-performing prompt systems | The Judge prompt is a production-grade system prompt with strict JSON output constraints |
| Programming experience building prompt pipelines | Python backend with provider abstraction, concurrent execution, structured evaluation |
| Strong analytical mindset — data-driven experimentation | Scores, metrics, structured verdicts, evaluation history |
| Deep technical understanding of LLMs and their constraints | Multi-provider support (Groq, Gemini, Ollama), model selection, temperature tuning |
| Develop structured, modular prompt templates | Two competing prompt architectures evaluated side-by-side |

---

## "I did this..." (Architecture & Execution)

> "I built a **Python/Streamlit application** that allows a developer to run A/B tests on system prompts. You input a test case, and the app routes it to two different prompt architectures **simultaneously**. But instead of manually reading the outputs to see which is better, I implemented an **'LLM-as-a-Judge' flow**. I configured a strictly formatted evaluation prompt that grades Prompt A and Prompt B on accuracy and outputs the winner in a **structured JSON format**."

### Architecture Walkthrough (for screen-sharing)

```
User Query
    │
    ├──► System Prompt A ──► LLM ──► Response A ──┐
    │                                              ├──► Judge Prompt ──► LLM ──► Structured Verdict
    └──► System Prompt B ──► LLM ──► Response B ──┘          │
                                                             ▼
                                                    { score_a: 8,
                                                      score_b: 9,
                                                      winner: "Prompt B",
                                                      explanation: "..." }
```

### Key Technical Decisions to Mention

1. **Parallel execution** — Both prompts run concurrently via `ThreadPoolExecutor`, so the user isn't waiting for sequential API calls. This mirrors how you'd handle scale in production.

2. **Provider abstraction layer** — I built an abstract base class (`LLMProvider`) so the same evaluation logic works across Groq, Gemini, or Ollama without changing a single line of evaluation code. This is the kind of modularity you need when maintaining prompt libraries across multiple models.

3. **The Judge prompt** — This was the hardest part. The system prompt for the Judge is tightly constrained:
   - It must output **only valid JSON** (no markdown, no extra text)
   - It scores on a **1–10 scale** with a specific metric definition
   - It must provide a brief **explanation** justifying its scores
   - It must declare a **winner** from exactly three options

4. **Five evaluation metrics** — Not just one generic "which is better" — the tool lets you evaluate on Faithfulness, Hallucinations, Helpfulness, Clarity, and Safety. Each metric has a precise definition fed to the Judge.

### Files to Walk Through

| File | What to show | Key talking point |
|---|---|---|
| `app.py` | The Streamlit UI | "The frontend is intentionally simple — the value is in the evaluation logic, not the UI" |
| `evaluator.py` | The Judge prompt + scoring logic | "This is where the real prompt engineering lives — constraining the Judge's output format" |
| `llm_provider.py` | Provider abstraction | "I designed this so you can swap models without touching evaluation logic — important for benchmarking across providers" |

---

## "Here is how I used AI to build it..." (Efficiency)

> "To get this shipped over the weekend, I heavily utilized LLMs as my **pair-programmer**. I used them to rapidly generate the Streamlit boilerplate and handle the asynchronous API calls so the UI wouldn't block while waiting for the models. It allowed me to focus purely on the **architecture and the logic of the evaluation prompts**, rather than getting bogged down in UI syntax."

### What AI Helped With vs. What I Designed

| AI Helped With (Scaffolding) | I Designed (Architecture) |
|---|---|
| Streamlit layout and widget syntax | The evaluation pipeline flow |
| API client boilerplate for each provider | The Judge prompt and its constraints |
| CSS styling for the score cards | The metric definitions and scoring criteria |
| File structure and imports | The provider abstraction pattern |
| Error handling patterns | The decision to run prompts in parallel |

**The key insight to communicate:** AI is a force multiplier. I used it for the parts that don't require creative judgment, so I could invest my time in the parts that do — prompt design, system architecture, and evaluation logic.

---

## "I learned this..." (The "Aha" Moment)

> "Building this reinforced my understanding from my academic coursework in Artificial Intelligence — specifically that while we **can't evaluate LLMs using traditional deterministic unit tests**, we absolutely must have structured, programmatic ways to measure their performance. I learned that designing the **'Judge' prompt is actually harder than designing the operational prompt**, because you have to constrain its grading criteria incredibly tightly to prevent it from giving inconsistent scores. It really highlighted why this role requires a **systematic, engineering mindset**, not just a linguistic one."

### Specific Lessons to Elaborate On If Asked

1. **JSON output enforcement is fragile** — The Judge sometimes wraps its response in markdown code fences even when told not to. I had to add regex parsing (`re.search(r"\{.*\}", raw, re.DOTALL)`) as a fallback. In production, you'd want structured output modes or function calling.

2. **Metric definitions matter enormously** — A vague metric like "quality" gives inconsistent results. I learned to write metric descriptions that are specific and measurable (e.g., *"Does the response avoid fabricating facts, citations, or details that are not grounded in the query or common knowledge?"*).

3. **The same model judging itself has bias** — When the same LLM generates responses AND judges them, there's inherent bias. In a production system, you'd want the judge to be a different (ideally stronger) model than the one generating responses.

4. **Temperature matters for judges** — The generation prompts use `temperature=0.7` for creativity, but ideally the judge should use `temperature=0` for consistency. This is a real production consideration.

---

## If Caleb Asks Follow-Up Questions

**"How would you scale this?"**
> "I'd add batch evaluation — upload a CSV of test cases and run all of them against both prompts, then aggregate the scores into a report. I'd also separate the judge model from the response model, and add Elo-style ranking if you're comparing more than two prompts."

**"What would you change?"**
> "Three things: (1) Use a stronger model as the judge than the one generating responses, (2) Add few-shot examples to the judge prompt to calibrate its scoring, and (3) Store evaluation history in a database instead of session state so you can track prompt performance over time."

**"How does this relate to your cloud engineering work?"**
> "The architecture is the same pattern I use daily — abstraction layers, concurrent execution, provider-agnostic interfaces. The difference is the domain: instead of orchestrating cloud services, I'm orchestrating LLM calls. The engineering principles are identical."
