import streamlit as st
import os
import time
import pandas as pd
import matplotlib.pyplot as plt

from app.assistants.oss_assistant import OSSAssistant
from app.assistants.frontier_assistant import FrontierAssistant

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="AI Assistant Comparison", layout="wide")

# Custom CSS for ChatGPT-like aesthetic
st.markdown("""
<style>
    /* ChatGPT Dark Mode Base */
    .stApp {
        background-color: #343541;
        color: #ececf1;
    }
    
    /* Hide default header */
    header { background-color: transparent !important; }

    /* Assistant messages styling (Darker band) */
    [data-testid="stChatMessage"]:has(svg[title="assistant"]),
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #444654;
        padding: 1.5rem 1rem;
        border-top: 1px solid rgba(32,33,35,0.5);
        border-bottom: 1px solid rgba(32,33,35,0.5);
        margin: 0 -1rem; /* stretch to container bounds */
    }

    /* User messages styling */
    [data-testid="stChatMessage"]:has(svg[title="user"]),
    [data-testid="stChatMessage"]:nth-child(odd) {
        padding: 1.5rem 1rem;
        margin: 0 -1rem;
    }

    /* Input area */
    [data-testid="stChatInput"] {
        background-color: #40414f !important;
        border: 1px solid rgba(32,33,35,0.5) !important;
        border-radius: 0.75rem !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #ececf1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful, concise, factual, and safe AI assistant. Always avoid hallucinating facts. If unsure, clearly say you do not know. Refuse harmful or illegal requests politely."

if "assistants" not in st.session_state:
    st.session_state.assistants = {
        "OSS (Hosted Qwen2.5)": OSSAssistant(system_prompt=st.session_state.system_prompt),
        "Frontier (Gemini 3.1 Flash-Lite)": FrontierAssistant(system_prompt=st.session_state.system_prompt)
    }

if "selected_assistant" not in st.session_state:
    st.session_state.selected_assistant = "Frontier (Gemini 3.1 Flash-Lite)"

if "metrics" not in st.session_state:
    st.session_state.metrics = {"latency": [], "tokens": []}

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Configuration")
    selected = st.selectbox(
        "Select Assistant", 
        ["Frontier (Gemini 3.1 Flash-Lite)", "OSS (Hosted Qwen2.5)"],
        index=0 if st.session_state.selected_assistant == "Frontier (Gemini 3.1 Flash-Lite)" else 1
    )
    
    if selected != st.session_state.selected_assistant:
        st.session_state.selected_assistant = selected
        st.rerun()

    st.divider()
    
    # Dynamic Key Inputs
    if st.session_state.selected_assistant == "Frontier (Gemini 3.1 Flash-Lite)":
        gemini_key = st.text_input("🔑 Gemini API Key", type="password", value=st.session_state.get("gemini_key", ""), help="Get your key from Google AI Studio")
        if gemini_key != st.session_state.get("gemini_key", ""):
            st.session_state.gemini_key = gemini_key
            os.environ["GEMINI_API_KEY"] = gemini_key
            # Re-init assistant to load the new key
            st.session_state.assistants["Frontier (Gemini 3.1 Flash-Lite)"] = FrontierAssistant(system_prompt=st.session_state.system_prompt)
            st.rerun()
    else:
        oss_url = st.text_input("🔗 Hugging Face Space URL", type="default", value=st.session_state.get("oss_url", ""), help="Example: https://huggingface.co/spaces/Ayishik/chat-space")
        if oss_url != st.session_state.get("oss_url", ""):
            st.session_state.oss_url = oss_url
            os.environ["HF_SPACE_URL"] = oss_url
            # Re-init assistant to load the new URL
            st.session_state.assistants["OSS (Hosted Qwen2.5)"] = OSSAssistant(system_prompt=st.session_state.system_prompt)
            st.rerun()

    st.divider()
    
    use_nvidia = st.toggle("🛡️ NVIDIA Semantic Guardrails", value=True, help="Toggle NVIDIA Nemotron-3 content safety API. (Note: Basic Regex safety heuristics will remain active even if this is disabled).")
    
    if use_nvidia:
        nvidia_key = st.text_input("🛡️ NVIDIA API Key", type="password", value=st.session_state.get("nvidia_key", ""), help="Required for semantic guardrails")
        if nvidia_key != st.session_state.get("nvidia_key", ""):
            st.session_state.nvidia_key = nvidia_key
            os.environ["NVIDIA_SAFETY_KEY"] = nvidia_key
            st.rerun()
            
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        for assistant in st.session_state.assistants.values():
            assistant.reset_memory()
        st.session_state.metrics = {"latency": [], "tokens": []}
        st.rerun()
        
    st.divider()
    st.markdown("### Status")
    
    assistant = st.session_state.assistants[st.session_state.selected_assistant]
    
    latencies = st.session_state.metrics["latency"]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    st.metric("Avg Latency", f"{avg_latency:.0f} ms")
    
    tokens = st.session_state.metrics["tokens"]
    total_tokens = sum(tokens) if tokens else 0
    st.metric("Tokens Used", f"{total_tokens}")

# ==========================================
# MAIN LAYOUT
# ==========================================
st.title("🤖 AI Assistant Comparison Platform")

tab1, tab2 = st.tabs(["💬 Chat", "📄 Evaluation Report"])

with tab1:
    st.markdown(f"**Current Assistant:** `{st.session_state.selected_assistant}`")
    
    current_assistant = st.session_state.assistants[st.session_state.selected_assistant]
    
    for msg in current_assistant.memory.history:
        role = msg["role"]
        content = msg["content"]
        avatar = "🧑‍💻" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            
    # Chat Input
    prompt = st.chat_input("Type your message here...")
    
    if prompt:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="🤖"):
            start_time = time.time()
            try:
                content = st.write_stream(current_assistant.process_request_stream(prompt, use_nvidia=use_nvidia))
                latency_ms = (time.time() - start_time) * 1000
                tokens_used = len(content) // 4
                
                st.caption(f"⏱️ {latency_ms:.0f} ms | 🪙 ~{tokens_used} tokens")
                st.session_state.metrics["latency"].append(latency_ms)
                st.session_state.metrics["tokens"].append(tokens_used)
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab2:
    st.header("Executive Evaluation Report")
    report_path = os.path.join(os.path.dirname(__file__), "report", "evaluation_report.md")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    else:
        st.info("Evaluation report not found in `report/evaluation_report.md`.")
