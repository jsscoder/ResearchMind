import streamlit as st
import time
from app.agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

STEPS = ["search", "reader", "writer", "critic"]
STEP_META = {
    "search": ("Search Agent", "Gathers recent web information"),
    "reader": ("Reader Agent", "Scrapes & extracts deep content"),
    "writer": ("Writer Chain", "Drafts the full research report"),
    "critic": ("Critic Chain", "Reviews & scores the report"),
}

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #050814;
    --bg-card: rgba(13, 19, 40, 0.55);
    --border-subtle: rgba(0, 240, 255, 0.15);

    --neon-cyan: #00f0ff;
    --neon-indigo: #7b2cbf;
    --electric-blue: #0077ff;
    --error-red: #f43f5e;

    --text-main: #f8fafc;
    --text-muted: #94a3b8;

    --font-sans: 'Inter', sans-serif;
    --font-display: 'Space Grotesk', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

html, body, [class*="css"] { font-family: var(--font-sans); color: var(--text-main); }

.stApp {
    background: var(--bg-main);
    background-image:
        radial-gradient(circle at 15% 50%, rgba(0, 240, 255, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 85% 30%, rgba(123, 44, 191, 0.08) 0%, transparent 50%),
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(180deg, #050814 0%, #03050c 100%);
    background-size: auto, auto, 42px 42px, 42px 42px, auto;
    background-attachment: fixed;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 2rem 5rem; max-width: 1200px; }

/* ── Hero ── */
.hero { text-align: center; padding: 4rem 0 3rem; }
.hero-eyebrow {
    font-family: var(--font-mono); font-size: 0.75rem; font-weight: 500;
    letter-spacing: 0.3em; text-transform: uppercase; color: var(--neon-cyan);
    margin-bottom: 1.2rem; text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
}
.hero h1 {
    font-family: var(--font-display); font-size: clamp(3rem, 7vw, 5.5rem);
    font-weight: 700; line-height: 1.1; letter-spacing: -0.04em; color: #fff; margin: 0 0 1.2rem;
}
.hero h1 span {
    background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--electric-blue) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: 0 0 30px rgba(0, 240, 255, 0.2);
}
.hero-sub { font-size: 1.15rem; font-weight: 300; color: var(--text-muted); max-width: 580px; margin: 0 auto; line-height: 1.7; }

.divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border-subtle), transparent); margin: 3rem 0; }

/* ── Input card ── */
.input-card {
    background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 16px;
    padding: 2rem; margin-bottom: 1.5rem; backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.stTextInput > div > div > input {
    background: rgba(0, 0, 0, 0.2) !important; border: 1px solid rgba(0, 240, 255, 0.2) !important;
    border-radius: 12px !important; color: #fff !important; font-family: var(--font-sans) !important;
    font-size: 1.05rem !important; padding: 1rem 1.2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--neon-cyan) !important;
    box-shadow: 0 0 0 1px var(--neon-cyan), 0 0 20px rgba(0, 240, 255, 0.15) !important;
}
.stTextInput > div > div > input:disabled { opacity: 0.45 !important; }
.stTextInput > label {
    font-family: var(--font-display) !important; font-size: 0.85rem !important; letter-spacing: 0.05em !important;
    color: var(--text-muted) !important; font-weight: 500 !important; margin-bottom: 0.5rem !important;
}

/* ── Primary button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--electric-blue) 100%) !important;
    color: #000 !important; font-family: var(--font-display) !important; font-weight: 700 !important;
    font-size: 1rem !important; letter-spacing: 0.02em !important; border: none !important;
    border-radius: 12px !important; padding: 0.8rem 2.2rem !important; cursor: pointer !important;
    transition: all 0.2s ease !important; box-shadow: 0 4px 15px rgba(0, 240, 255, 0.3) !important; width: 100%;
}
.stButton > button:hover:not(:disabled) {
    transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(0, 240, 255, 0.5) !important;
    background: linear-gradient(135deg, #2cf5ff 0%, #1a85ff 100%) !important;
}
.stButton > button:active:not(:disabled) { transform: translateY(0) !important; }
.stButton > button:disabled {
    opacity: 0.35 !important; cursor: not-allowed !important; transform: none !important; box-shadow: none !important;
}

/* ── Suggestion chip buttons ── */
.st-key-chip_row .stButton > button {
    background: rgba(0, 240, 255, 0.04) !important; color: var(--text-muted) !important;
    border: 1px solid rgba(0, 240, 255, 0.15) !important; font-family: var(--font-sans) !important;
    font-weight: 400 !important; font-size: 0.82rem !important; letter-spacing: 0 !important;
    border-radius: 999px !important; padding: 0.4rem 1rem !important; box-shadow: none !important; width: auto;
}
.st-key-chip_row .stButton > button:hover:not(:disabled) {
    border-color: var(--neon-cyan) !important; color: var(--neon-cyan) !important;
    background: rgba(0, 240, 255, 0.08) !important; transform: none !important; box-shadow: none !important;
}
.chip-label {
    font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-muted);
    letter-spacing: 0.1em; margin-bottom: 0.6rem; display: block;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--neon-cyan), var(--electric-blue)) !important;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.5);
}
.stProgress > div > div { background: rgba(255,255,255,0.06) !important; }

/* ── Pipeline step cards ── */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 10px rgba(0, 240, 255, 0.2); }
    50% { box-shadow: 0 0 25px rgba(0, 240, 255, 0.4); border-color: var(--neon-cyan); }
    100% { box-shadow: 0 0 10px rgba(0, 240, 255, 0.2); }
}
@keyframes cardIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.step-card-wrap { position: relative; animation: cardIn 0.4s ease both; }
.step-card-wrap:not(:last-child)::after {
    content: ''; position: absolute; left: 22px; top: 100%; width: 1px; height: 1rem;
    background: linear-gradient(180deg, rgba(255,255,255,0.15), transparent);
}
.step-card {
    background: var(--bg-card); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px;
    padding: 1.4rem 1.6rem; margin-bottom: 1rem; position: relative; overflow: hidden;
    backdrop-filter: blur(12px); transition: all 0.3s ease;
}
.step-card.active { background: rgba(0, 240, 255, 0.05); border-color: var(--neon-cyan); animation: pulseGlow 2s infinite; }
.step-card.done { background: rgba(123, 44, 191, 0.05); border-color: rgba(123, 44, 191, 0.4); }
.step-card.error { background: rgba(244, 63, 94, 0.06); border-color: rgba(244, 63, 94, 0.5); }
.step-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; border-radius: 14px 0 0 14px;
    background: rgba(255, 255, 255, 0.1); transition: background 0.3s, box-shadow 0.3s;
}
.step-card.active::before { background: var(--neon-cyan); box-shadow: 0 0 10px var(--neon-cyan); }
.step-card.done::before { background: var(--neon-indigo); box-shadow: 0 0 10px var(--neon-indigo); }
.step-card.error::before { background: var(--error-red); box-shadow: 0 0 10px var(--error-red); }

.step-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.4rem; }
.step-num { font-family: var(--font-mono); font-size: 0.75rem; font-weight: 500; color: var(--text-muted); }
.step-card.active .step-num { color: var(--neon-cyan); }
.step-card.done .step-num { color: var(--neon-indigo); }
.step-card.error .step-num { color: var(--error-red); }
.step-title { font-family: var(--font-display); font-size: 1rem; font-weight: 500; color: var(--text-main); }
.step-status { margin-left: auto; font-family: var(--font-mono); font-size: 0.7rem; letter-spacing: 0.05em; border-radius: 4px; padding: 0.2rem 0.5rem; }
.status-waiting { color: #64748b; background: rgba(100, 116, 139, 0.1); }
.status-running { color: var(--neon-cyan); background: rgba(0, 240, 255, 0.1); }
.status-done { color: #d8b4fe; background: rgba(123, 44, 191, 0.2); }
.status-error { color: var(--error-red); background: rgba(244, 63, 94, 0.15); }

/* ── Result panels (containers, not the broken split-div trick) ── */
.result-panel {
    background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 16px;
    padding: 2rem; margin-top: 1rem; margin-bottom: 1.5rem; backdrop-filter: blur(12px);
}
.result-panel-title {
    font-family: var(--font-mono); font-size: 0.75rem; font-weight: 500; letter-spacing: 0.1em;
    text-transform: uppercase; color: var(--neon-cyan); margin-bottom: 1.5rem; padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(0, 240, 255, 0.15);
}
.result-content { font-size: 0.95rem; line-height: 1.7; color: var(--text-muted); white-space: pre-wrap; font-family: var(--font-sans); }

.st-key-report_panel {
    background: rgba(13, 19, 40, 0.8) !important; border: 1px solid rgba(0, 240, 255, 0.25) !important;
    border-radius: 16px !important; padding: 2.5rem !important; margin-top: 2rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}
.st-key-feedback_panel {
    background: rgba(20, 10, 35, 0.8) !important; border: 1px solid rgba(123, 44, 191, 0.3) !important;
    border-radius: 16px !important; padding: 2.5rem !important; margin-top: 1.5rem;
}
.panel-label {
    font-family: var(--font-display); font-size: 1.1rem; font-weight: 500; letter-spacing: 0.05em;
    margin-bottom: 1.5rem; padding-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;
}
.panel-label.cyan { color: var(--neon-cyan); border-bottom: 1px solid rgba(0, 240, 255, 0.15); }
.panel-label.indigo { color: #d8b4fe; border-bottom: 1px solid rgba(123, 44, 191, 0.2); }

.stSpinner > div > div { border-color: var(--neon-cyan) transparent transparent transparent !important; }
.stSpinner > div { color: var(--neon-cyan) !important; font-family: var(--font-mono) !important; font-size: 0.9rem !important; }

.streamlit-expanderHeader {
    font-family: var(--font-mono) !important; font-size: 0.85rem !important; color: var(--text-main) !important;
    background: rgba(255,255,255,0.02) !important; border-radius: 8px !important;
}

.section-heading { font-family: var(--font-display); font-size: 1.4rem; font-weight: 600; color: #fff; margin: 1.5rem 0 1.2rem; letter-spacing: -0.02em; }

.notice { font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); text-align: center; margin-top: 4rem; letter-spacing: 0.05em; opacity: 0.6; }

.st-key-report_panel h1, .st-key-report_panel h2, .st-key-report_panel h3 { font-family: var(--font-display); color: #fff; margin-top: 1.5rem; }
.st-key-report_panel p, .st-key-report_panel li { color: #cbd5e1; }

.error-banner {
    font-family: var(--font-mono); font-size: 0.85rem; color: var(--error-red);
    background: rgba(244, 63, 94, 0.08); border: 1px solid rgba(244, 63, 94, 0.3);
    border-radius: 10px; padding: 1rem 1.2rem; margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, step_key: str, state: str):
    title, desc = STEP_META[step_key]
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done": ("✓ DONE", "status-done"),
        "error": ("✕ FAILED", "status-error"),
    }
    label, status_cls = status_map[state]
    card_cls = {"running": "active", "done": "done", "error": "error"}.get(state, "")
    st.markdown(f"""
    <div class="step-card-wrap">
        <div class="step-card {card_cls}">
            <div class="step-header">
                <span class="step-num">{num}</span>
                <span class="step-title">{title}</span>
                <span class="step-status {status_cls}">{label}</span>
            </div>
            <div style="font-size:0.85rem;color:var(--text-muted);margin-top:0.4rem;line-height:1.4;">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def step_status(step_key: str) -> str:
    if st.session_state.error and st.session_state.error["step"] == step_key:
        return "error"
    if step_key in st.session_state.results:
        return "done"
    if st.session_state.running:
        next_step = next((s for s in STEPS if s not in st.session_state.results), None)
        if next_step == step_key:
            return "running"
    return "waiting"


def start_pipeline(topic_value: str):
    st.session_state.results = {}
    st.session_state.running = True
    st.session_state.done = False
    st.session_state.error = None
    st.session_state.topic = topic_value
    st.rerun()


def reset_pipeline():
    st.session_state.results = {}
    st.session_state.running = False
    st.session_state.done = False
    st.session_state.error = None
    st.rerun()


def run_step(step_key: str, topic_value: str, results: dict):
    """Executes exactly one pipeline step and returns its output."""
    if step_key == "search":
        agent = build_search_agent()
        out = agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_value}")]
        })
        return out["messages"][-1].content

    if step_key == "reader":
        agent = build_reader_agent()
        out = agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_value}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        return out["messages"][-1].content

    if step_key == "writer":
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        return writer_chain.invoke({"topic": topic_value, "research": research_combined})

    if step_key == "critic":
        return critic_chain.invoke({"report": results["writer"]})

    raise ValueError(f"Unknown step: {step_key}")


# ── Session state init ────────────────────────────────────────────────────────
for key, default in [("results", {}), ("running", False), ("done", False), ("topic", ""), ("error", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# A chip click needs to set the text_input's value on the *next* run, before that
# widget is instantiated again — doing it after instantiation raises an error.
if "pending_topic" in st.session_state:
    st.session_state["topic_input"] = st.session_state.pop("pending_topic")


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI Platform</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub center">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        disabled=st.session_state.running,
    )
    run_btn = st.button(
        "Initialize Research Pipeline",
        use_container_width=True,
        disabled=st.session_state.running,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<span class="chip-label">SUGGESTIONS</span>', unsafe_allow_html=True)
    with st.container(key="chip_row"):
        examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
        chip_cols = st.columns(len(examples))
        for i, ex in enumerate(examples):
            if chip_cols[i].button(ex, key=f"chip_{i}", disabled=st.session_state.running):
                st.session_state["pending_topic"] = ex
                start_pipeline(ex)

with col_pipeline:
    st.markdown('<div class="section-heading">Agent Pipeline</div>', unsafe_allow_html=True)

    completed = len(st.session_state.results)
    st.progress(completed / len(STEPS) if not st.session_state.error else completed / len(STEPS))

    for i, step_key in enumerate(STEPS, start=1):
        step_card(f"0{i}", step_key, step_status(step_key))

    if st.session_state.error:
        st.markdown(
            f'<div class="error-banner">Pipeline stopped at <b>{st.session_state.error["step"]}</b>: '
            f'{st.session_state.error["message"]}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Retry from failed step", use_container_width=True):
            st.session_state.error = None
            st.session_state.running = True
            st.rerun()


# ── Kick off a run ────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        start_pipeline(topic)

# ── Execute exactly one step per script run, then rerun ──────────────────────
# This is what actually makes the pipeline cards above update live — running all
# four agent calls in a single blocking pass (the previous version) never gives
# Streamlit a chance to re-render in between, so "running" never visibly shows.
if st.session_state.running and not st.session_state.done and not st.session_state.error:
    next_step = next((s for s in STEPS if s not in st.session_state.results), None)
    if next_step is None:
        st.session_state.running = False
        st.session_state.done = True
        st.rerun()
    else:
        spinner_text = {
            "search": "Search Agent is querying external sources...",
            "reader": "Reader Agent is parsing deep content...",
            "writer": "Writer is synthesizing the final report...",
            "critic": "Critic is validating and scoring...",
        }[next_step]
        try:
            with st.spinner(spinner_text):
                output = run_step(next_step, st.session_state.topic, st.session_state.results)
            st.session_state.results[next_step] = output
        except Exception as e:
            st.session_state.error = {"step": next_step, "message": str(e)}
            st.session_state.running = False
        st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider" style="margin-top: 4rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Execution Artifacts</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("Show Search Agent Telemetry", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Raw Search Context</div>'
                f'<div class="result-content">{r["search"]}</div></div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("Show Reader Agent Telemetry", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Extracted Document Data</div>'
                f'<div class="result-content">{r["reader"]}</div></div>',
                unsafe_allow_html=True,
            )

    # Final report — st.container(key=...) gives a real DOM element to style,
    # unlike opening a <div> in one st.markdown call and closing it in another
    # (each st.markdown call is its own isolated HTML fragment, so the browser
    # auto-closes the unclosed div and the "card" never actually wraps the content).
    if "writer" in r:
        with st.container(key="report_panel"):
            st.markdown("""
            <div class="panel-label cyan">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Final Research Synthesis
            </div>
            """, unsafe_allow_html=True)
            st.markdown(r["writer"])

        col_dl, col_reset = st.columns([3, 1])
        with col_dl:
            st.download_button(
                label="Download Markdown Report",
                data=r["writer"],
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_reset:
            if st.button("New Research", use_container_width=True):
                reset_pipeline()

    if "critic" in r:
        with st.container(key="feedback_panel"):
            st.markdown("""
            <div class="panel-label indigo">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                Critic Chain Evaluation
            </div>
            """, unsafe_allow_html=True)
            st.markdown(r["critic"])


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind Enterprise AI System · Multi-Agent Architecture · Powered by Streamlit
</div>
""", unsafe_allow_html=True)
