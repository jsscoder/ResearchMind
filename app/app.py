import streamlit as st
import time
import re
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
from dotenv import load_dotenv

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_dotenv()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

/* ── Reset & base Synthwave Styles ── */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    color: #ffb7df;
}

.stApp {
    background: #06050c;
    background-image:
        linear-gradient(rgba(255, 46, 126, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 46, 126, 0.05) 1px, transparent 1px),
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(255, 0, 127, 0.2) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 20% 90%, rgba(0, 240, 255, 0.1) 0%, transparent 60%);
    background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100%;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #00f0ff;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2.8rem, 6vw, 4.8rem);
    font-weight: 900;
    line-height: 1.1;
    letter-spacing: -0.01em;
    color: #ffffff;
    text-shadow: 0 0 20px rgba(255, 0, 127, 0.8), 0 0 40px rgba(255, 0, 127, 0.4);
    margin: 0 0 1rem;
    text-transform: uppercase;
}
.hero h1 span {
    color: #ff2e7e;
    text-shadow: 0 0 20px rgba(255, 46, 126, 0.9), 0 0 40px rgba(255, 46, 126, 0.5);
}
.hero-sub {
    font-size: 1.15rem;
    font-weight: 500;
    color: #da97c2;
    max-width: 580px;
    margin: 0 auto;
    line-height: 1.6;
    letter-spacing: 0.05em;
}

/* ── Synthwave Neon Grid Divider ── */
.divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #ff007f, #00f0ff, #ff007f, transparent);
    box-shadow: 0 0 12px #ff007f;
    margin: 2.5rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(13, 10, 25, 0.75);
    border: 2px solid #ff2e7e;
    box-shadow: 0 0 20px rgba(255, 46, 126, 0.3), inset 0 0 15px rgba(255, 46, 126, 0.1);
    border-radius: 12px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(20, 15, 35, 0.9) !important;
    border: 1px solid #00f0ff !important;
    border-radius: 6px !important;
    color: #ffffff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.1rem !important;
    padding: 0.85rem 1rem !important;
    letter-spacing: 0.05em;
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.2) !important;
    transition: all 0.25s ease-in-out !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff2e7e !important;
    box-shadow: 0 0 18px rgba(255, 46, 126, 0.6) !important;
}
.stTextInput > label {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #00f0ff !important;
    text-shadow: 0 0 5px rgba(0, 240, 255, 0.5);
    font-weight: 700 !important;
    margin-bottom: 0.6rem !important;
}

/* ── Action Button ── */
.stButton > button {
    background: linear-gradient(135deg, #ff007f 0%, #7900ff 100%) !important;
    color: #ffffff !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border: 1px solid #ffb7df !important;
    border-radius: 6px !important;
    padding: 0.9rem 2.2rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(255, 0, 127, 0.5) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 35px rgba(255, 0, 127, 0.85), 0 0 10px rgba(0, 240, 255, 0.5) !important;
    color: #00f0ff !important;
}
.stButton > button:active {
    transform: translateY(1px) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(15, 10, 28, 0.7);
    border: 1px solid rgba(255, 46, 126, 0.2);
    border-radius: 10px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(5px);
    transition: all 0.3s;
}
.step-card.active {
    border-color: #00f0ff;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.4), inset 0 0 10px rgba(0, 240, 255, 0.1);
    background: rgba(0, 240, 255, 0.03);
}
.step-card.done {
    border-color: #ff2e7e;
    box-shadow: 0 0 15px rgba(255, 46, 126, 0.3), inset 0 0 10px rgba(255, 46, 126, 0.1);
    background: rgba(255, 46, 126, 0.03);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: rgba(255, 255, 255, 0.05);
    transition: background 0.3s;
}
.step-card.active::before { background: #00f0ff; box-shadow: 0 0 10px #00f0ff; }
.step-card.done::before   { background: #ff2e7e; box-shadow: 0 0 10px #ff2e7e; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: #ff2e7e;
}
.step-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: #ffffff;
}
.step-status {
    margin-left: auto;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
}
.status-waiting  { color: #4e3f5d; }
.status-running  { color: #00f0ff; text-shadow: 0 0 8px #00f0ff; }
.status-done     { color: #ff2e7e; text-shadow: 0 0 8px #ff2e7e; }

/* ── Result panels ── */
.result-panel {
    background: rgba(10, 6, 20, 0.8);
    border: 1px solid rgba(0, 240, 255, 0.3);
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
    border-radius: 10px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.result-panel-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #00f0ff;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(0, 240, 255, 0.2);
}
.result-content {
    font-size: 1rem;
    line-height: 1.7;
    color: #e2c9dc;
    white-space: pre-wrap;
    font-family: 'Rajdhani', sans-serif;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(12, 5, 22, 0.85);
    border: 2px solid #ff2e7e;
    box-shadow: 0 0 25px rgba(255, 46, 126, 0.4);
    border-radius: 12px;
    padding: 2.5rem;
    margin-top: 1rem;
}
.feedback-panel {
    background: rgba(8, 12, 24, 0.85);
    border: 2px solid #00f0ff;
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.3);
    border-radius: 12px;
    padding: 2.5rem;
    margin-top: 1.5rem;
}
.panel-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    padding-bottom: 0.8rem;
}
.panel-label.orange {
    color: #ff2e7e;
    text-shadow: 0 0 10px rgba(255, 46, 126, 0.5);
    border-bottom: 1px solid rgba(255, 46, 126, 0.3);
}
.panel-label.green {
    color: #00f0ff;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
    border-bottom: 1px solid rgba(0, 240, 255, 0.3);
}

/* Markdown Rendering Color Customizations */
.report-panel h1, .report-panel h2, .report-panel h3 { color: #ffffff !important; font-family: 'Orbitron', sans-serif; }
.report-panel strong { color: #00f0ff !important; }
.feedback-panel strong { color: #ff2e7e !important; }

/* ── Progress & Spinners ── */
.stSpinner > div { color: #ff2e7e !important; }

/* ── Expander ── */
details {
    background: rgba(15, 8, 25, 0.5) !important;
    border: 1px solid rgba(255, 46, 126, 0.15) !important;
    margin-bottom: 0.5rem !important;
    border-radius: 6px;
}
details summary {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
    color: #da97c2 !important;
    letter-spacing: 0.15em !important;
    cursor: pointer;
    padding: 0.5rem;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #ffffff;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    margin: 2rem 0 1.2rem;
}

/* ── Download Button Styling Overrides ── */
.stDownloadButton > button {
    background: transparent !important;
    color: #00f0ff !important;
    border: 1px solid #00f0ff !important;
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.2) !important;
    margin-top: 1rem;
    border-radius: 6px !important;
}
.stDownloadButton > button:hover {
    background: rgba(0, 240, 255, 0.1) !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.5) !important;
}

/* ── Toast-style notice / Footer ── */
.notice {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #5c4b75;
    text-align: center;
    margin-top: 4rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("OFFLINE", "status-waiting"),
        "running": ("▲ PROCESSING", "status-running"),
        "done":    ("■ COMPLETE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.85rem;color:#a385a7;margin-top:0.3rem;letter-spacing:0.05em;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">// NEURAL NETWORK MULTI-AGENT SUB-SYSTEM</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized cyberpunk AI entities collaborate — harvesting, decoding,
        structuring, and auditing — to craft synthesized knowledge intelligence matrix.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Enter Target Objective / Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2026",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡ EXECUTE CORE PIPELINE", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1.5rem;align-items:center;">
        <span style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:#7900ff;letter-spacing:0.1em;font-weight:bold;">LOAD_PRESET //</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2026", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f"""
        <span style="
            background:rgba(255,46,126,0.06);
            border:1px solid rgba(255,46,126,0.3);
            border-radius:4px;
            padding:0.3rem 0.8rem;
            font-size:0.8rem;
            color:#ffb7df;
            font-family:'Share Tech Mono',monospace;
            cursor:default;
            box-shadow: 0 0 5px rgba(255,46,126,0.1);
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">System Core Monitor</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]

        if step in r:
            return "done"

        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("SYSTEM_01", "Search Matrix Agent",  s("search"), "Queries globally synchronized web indices")
    step_card("SYSTEM_02", "Deep Content Scraper",  s("reader"), "Decodes raw deep-web structural content nodes")
    step_card("SYSTEM_03", "Synthesis Writing Chain",  s("writer"), "Compiles intelligence matrix into a report block")
    step_card("SYSTEM_04", "Critic Quality Audit",  s("critic"), "Evaluates coherence, precision, and logical telemetry")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Matrix target parameter missing. Input research query.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.wm_topic = topic.strip()
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = st.session_state.results
    topic_val = st.session_state.get("wm_topic", st.session_state.topic_input)

    # ── Step 1: Search ──
    if "search" not in results:
        with st.spinner("🔮 Initiating Search Datastream..."):
            search_agent = build_search_agent()
            query_str = f"Find recent, reliable and detailed information about: {topic_val}"

            try:
                sr = search_agent.invoke(query_str)
            except Exception:
                try:
                    sr = search_agent.invoke({"query": query_str})
                except Exception as final_err:
                    sr = f"Search fallback failure. Telemetry context: {str(final_err)}"

            if hasattr(sr, "content"):
                results["search"] = sr.content
            elif isinstance(sr, dict) and "messages" in sr:
                results["search"] = sr["messages"][-1].content
            elif isinstance(sr, list):
                results["search"] = "\n\n".join([
                    f"URL: {res.get('url', 'N/A')}\nSnippet: {res.get('content', res.get('snippet', ''))}"
                    for res in sr if isinstance(res, dict)
                ])
            else:
                results["search"] = str(sr)

            st.session_state.results = results
            st.rerun()

    # ── Step 2: Reader ──
    if "reader" not in results:
        with st.spinner("🔮 Scraping deep content vectors..."):
            reader_tool = build_reader_agent()
            urls = re.findall(r"https?://[^\s)]+", results["search"])

            if urls:
                try:
                    rr = reader_tool.invoke({"url": urls[0]})
                    if hasattr(rr, "content"):
                        rr = rr.content
                except Exception as e:
                    rr = f"Failed to breach content nodes at {urls[0]}. Error: {str(e)}"
            else:
                rr = "No peripheral link targets matched inside space indices."

            results["reader"] = str(rr)
            st.session_state.results = results
            st.rerun()

    # ── Step 3: Writer ──
    if "writer" not in results:
        with st.spinner("🔮 Compiling data block report units..."):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            rw = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            results["writer"] = rw.content if hasattr(rw, "content") else str(rw)
            st.session_state.results = results
            st.rerun()

    # ── Step 4: Critic ──
    if "critic" not in results:
        with st.spinner("🔮 Auditing telemetry architecture structural integrity..."):
            rc = critic_chain.invoke({
                "report": results["writer"]
            })
            results["critic"] = rc.content if hasattr(rc, "content") else str(rc)
            st.session_state.results = results

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Decrypted Output Matrices</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("// RAW MATRIX TELEMETRY: SEARCH DATABASES", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Logs</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("// RAW MATRIX TELEMETRY: SCRAPED DATABLOCKS", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Extraction Units</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">🔮 Synthesized Intelligence Core Document</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="⭳ EXTRACT CORE REPORT MATRIX (.md)",
            data=r["writer"],
            file_name=f"synth_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🔮 Quality Audit Vector Telemetry</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind v2.86 // Powered by LangChain multi-agent framework // Streamlit Interface Overhaul Successful
</div>
""", unsafe_allow_html=True)