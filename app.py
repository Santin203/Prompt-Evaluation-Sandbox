"""
Prompt Evaluation Sandbox — Streamlit App
A lightweight tool to A/B test system prompts using an LLM-as-a-Judge.
"""

import streamlit as st
from llm_provider import PROVIDERS, GroqProvider, GeminiProvider, OllamaProvider, get_provider
from evaluator import METRICS, run_prompts_parallel, judge


# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Prompt Evaluation Sandbox",
    page_icon="PE",
    layout="wide",
    menu_items={},
)

# Inject theme-aware CSS for cards
st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stStatusWidget"] {display: none;}

.eval-card {
    padding: 15px;
    border-radius: 10px;
    background-color: var(--background-secondary, #f0f2f6);
    color: var(--text-color, inherit);
}
.score-card {
    text-align: center;
    padding: 20px;
    border-radius: 10px;
    background-color: var(--background-secondary, #f0f2f6);
    color: var(--text-color, inherit);
}
@media (prefers-color-scheme: dark) {
    .eval-card, .score-card {
        background-color: #1a1a2e;
    }
}
[data-testid="stAppViewContainer"][data-theme="dark"] .eval-card,
[data-testid="stAppViewContainer"][data-theme="dark"] .score-card {
    background-color: #1a1a2e;
}

/* Pointer cursor on dropdowns, buttons, and interactive widgets */
[data-testid="stSelectbox"],
[data-testid="stSelectbox"] * ,
[data-testid="stMultiSelect"],
[data-testid="stMultiSelect"] *,
div[data-baseweb="select"],
div[data-baseweb="select"] * {
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Prompt Evaluation Sandbox")
st.caption("A/B test two system prompts and let an LLM judge which one wins.")

# ── Sidebar: Provider & Model Selection ─────────────────────────────────────

with st.sidebar:
    st.header("Configuration")

    provider_name = st.selectbox("LLM Provider", list(PROVIDERS.keys()))

    # Model selection based on provider
    if provider_name == "Groq (Free Cloud)":
        model_options = GroqProvider.MODELS
    elif provider_name == "Google Gemini (Free Cloud)":
        model_options = GeminiProvider.MODELS
    else:
        model_options = OllamaProvider.MODELS

    selected_model = st.selectbox("Model", model_options)

    # API key input (not needed for Ollama)
    api_key = None
    if "Groq" in provider_name:
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value=st.session_state.get("groq_key", ""),
        )
        st.session_state["groq_key"] = api_key
    elif "Gemini" in provider_name:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get("gemini_key", ""),
        )
        st.session_state["gemini_key"] = api_key

    st.divider()

    metric = st.selectbox("Evaluation Metric", list(METRICS.keys()))
    st.info(f"**{metric}:** {METRICS[metric]}")



# ── Main: Prompt Inputs ─────────────────────────────────────────────────────

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Prompt A")
    prompt_a = st.text_area(
        "System Prompt A",
        height=150,
        placeholder="You are a helpful assistant that answers concisely...",
        value=st.session_state.get("prompt_a", "You are a helpful and empathetic customer support assistant for Dialogue Labs. Do your best to resolve the user's issue and make sure they leave happy."),
    )

with col_b:
    st.subheader("Prompt B")
    prompt_b = st.text_area(
        "System Prompt B",
        height=150,
        placeholder="You are a detailed expert who provides thorough answers...",
        value=st.session_state.get("prompt_b", """You are a customer support assistant for Dialogue Labs. You must strictly adhere to the following company policy: 'Refunds are only issued if requested within 14 days of the INITIAL purchase. Subscription renewals are strictly non-refundable. '

Constraints:

Do not grant refunds for renewals under any circumstances.

Do not invent links, phone numbers, or escalation paths that are not provided in this prompt.

If a request falls outside the policy, politely decline and state the exact policy rule."""),
    )

st.divider()

user_query = st.text_area(
    "User Query",
    height=100,
    placeholder="Enter the query to test both prompts with...",
    value=st.session_state.get("user_query", ""),
)

# ── Run Evaluation ──────────────────────────────────────────────────────────

run_disabled = not user_query.strip() or not prompt_a.strip() or not prompt_b.strip()

if st.button("Run Evaluation", type="primary", use_container_width=True, disabled=run_disabled):
    # Validate API key
    if "Ollama" not in provider_name and not api_key:
        st.error("Please enter your API key in the sidebar.")
        st.stop()

    try:
        # Build provider
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        provider = get_provider(provider_name, model=selected_model, **kwargs)

        # Step 1: Run both prompts
        with st.status("Sending query to both prompts...", expanded=True) as status:
            st.write(f"Provider: **{provider.name()}**")
            st.write(f"Metric: **{metric}**")

            result_a, result_b = run_prompts_parallel(provider, prompt_a, prompt_b, user_query)
            status.update(label="Responses received.", state="complete")

        # Display responses side by side
        st.subheader("Responses")
        resp_col_a, resp_col_b = st.columns(2)

        with resp_col_a:
            st.markdown("**Response A**")
            st.markdown(
                f'<div class="eval-card" style="border-left:4px solid #3b82f6;">'
                f'{result_a.response}</div>',
                unsafe_allow_html=True,
            )

        with resp_col_b:
            st.markdown("**Response B**")
            st.markdown(
                f'<div class="eval-card" style="border-left:4px solid #f59e0b;">'
                f'{result_b.response}</div>',
                unsafe_allow_html=True,
            )

        # Step 2: Judge
        with st.status("Judge is evaluating responses...", expanded=True) as status:
            verdict = judge(provider, result_a, result_b, user_query, metric)
            status.update(label="Judgement complete.", state="complete")

        # Display results
        st.divider()
        st.subheader(f"Judgement — {metric}")

        score_col_a, score_winner, score_col_b = st.columns([1, 1, 1])

        with score_col_a:
            color_a = "#22c55e" if verdict.winner == "Prompt A" else "#6b7280"
            st.markdown(
                f'<div class="score-card" style="border:2px solid {color_a};">'
                f'<h2 style="color:{color_a};">{verdict.score_a}/10</h2>'
                f'<p>Prompt A</p></div>',
                unsafe_allow_html=True,
            )

        with score_winner:
            if verdict.winner == "Tie":
                label, color = "TIE", "#f59e0b"
            elif verdict.winner == "Prompt A":
                label, color = "WINNER", "#3b82f6"
            else:
                label, color = "WINNER", "#f59e0b"

            st.markdown(
                f'<div class="score-card" style="border:2px solid {color};">' 
                f'<h2 style="color:{color};">{label}</h2>'
                f'<h3 style="color:{color};">{verdict.winner}</h3></div>',
                unsafe_allow_html=True,
            )

        with score_col_b:
            color_b = "#22c55e" if verdict.winner == "Prompt B" else "#6b7280"
            st.markdown(
                f'<div class="score-card" style="border:2px solid {color_b};">'
                f'<h2 style="color:{color_b};">{verdict.score_b}/10</h2>'
                f'<p>Prompt B</p></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown(f"**Judge's Explanation:** {verdict.explanation}")

        # Save to history
        if "history" not in st.session_state:
            st.session_state["history"] = []
        st.session_state["history"].append({
            "query": user_query,
            "metric": metric,
            "score_a": verdict.score_a,
            "score_b": verdict.score_b,
            "winner": verdict.winner,
            "explanation": verdict.explanation,
        })

    except Exception as e:
        st.error(f"Error: {e}")

# ── History ─────────────────────────────────────────────────────────────────

if st.session_state.get("history"):
    st.divider()
    st.subheader("Evaluation History")
    for i, h in enumerate(reversed(st.session_state["history"]), 1):
        with st.expander(f"Run {len(st.session_state['history']) - i + 1}: {h['query'][:60]}..."):
            st.write(f"**Metric:** {h['metric']}")
            st.write(f"**Scores:** A={h['score_a']}/10 | B={h['score_b']}/10")
            st.write(f"**Winner:** {h['winner']}")
            st.write(f"**Explanation:** {h['explanation']}")
