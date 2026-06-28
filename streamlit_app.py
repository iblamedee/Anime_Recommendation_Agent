import streamlit as st
import os
import uuid
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel
from typing import Annotated
from sys_prompt import system_prompt

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

# ----------------------------------------------------
# 1. Page Configuration & Styling
# ----------------------------------------------------
st.set_page_config(
    page_title="Aki - Ultimate Anime Companion",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Fira+Code:wght@400;500&display=swap');

/* Main layouts and fonts */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif;
    background-color: #0d0b18;
    color: #e2e8f0;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(18, 15, 36, 0.95) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(236, 72, 153, 0.15);
}

/* Custom premium buttons */
.stButton > button {
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.35);
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(236, 72, 153, 0.5) !important;
    border: none !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Header layout styling */
.header-container {
    background: linear-gradient(135deg, #ec4899 0%, #a855f7 50%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.8rem;
    margin-bottom: 0px;
    letter-spacing: -0.5px;
    animation: glow-pulse 4s infinite alternate;
}

.subtitle-container {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

/* Message bubbles styling */
.chat-bubble-user {
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 18px 18px 4px 18px;
    padding: 14px 20px;
    color: #f1f5f9;
    margin-bottom: 8px;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.05);
    line-height: 1.6;
}

.chat-bubble-aki {
    background: rgba(236, 72, 153, 0.08);
    border: 1px solid rgba(236, 72, 153, 0.2);
    border-radius: 18px 18px 18px 4px;
    padding: 14px 20px;
    color: #f8fafc;
    margin-bottom: 8px;
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.03);
    line-height: 1.6;
}

/* Status message override */
div[data-testid="stNotification"] {
    background-color: rgba(18, 15, 36, 0.8) !important;
    border: 1px solid rgba(168, 85, 247, 0.3) !important;
    border-radius: 12px !important;
}

/* Expanders styling */
div[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
}

/* Input boxes customization */
div[data-testid="stChatInput"] {
    border-radius: 16px !important;
    border: 1px solid rgba(236, 72, 153, 0.2) !important;
    background-color: rgba(18, 15, 36, 0.8) !important;
}

@keyframes glow-pulse {
    0% { filter: drop-shadow(0 0 2px rgba(236, 72, 153, 0.2)); }
    100% { filter: drop-shadow(0 0 8px rgba(168, 85, 247, 0.5)); }
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# 2. Session State Initialization
# ----------------------------------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"aki_session_{uuid.uuid4().hex[:8]}"

# Determine if avatar file exists
avatar_path = "aki_avatar.png" if os.path.exists("aki_avatar.png") else "🌸"


# Helper functions to resolve API keys from environment
def resolve_gemini_key():
    if "gemini_key_override" in st.session_state and st.session_state.gemini_key_override.strip():
        return st.session_state.gemini_key_override.strip()
    # Check streamlit secrets (used in Streamlit Cloud)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"].strip()
    except Exception:
        pass
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        key = os.getenv("GOOGLE_API_KEY", "")
    return key.strip() if key else ""

def resolve_tavily_key():
    if "tavily_key_override" in st.session_state and st.session_state.tavily_key_override.strip():
        return st.session_state.tavily_key_override.strip()
    # Check streamlit secrets (used in Streamlit Cloud)
    try:
        if "TAVILY_API_KEY" in st.secrets:
            return st.secrets["TAVILY_API_KEY"].strip()
    except Exception:
        pass
    key = os.getenv("TAVILY_API_KEY", "")
    return key.strip() if key else ""


def extract_text_content(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        return "".join(text_parts)
    elif isinstance(content, dict) and "text" in content:
        return content["text"]
    return str(content)


# ----------------------------------------------------
# 3. Sidebar UI (Settings & Configuration)
# ----------------------------------------------------
st.sidebar.markdown('<div style="text-align: center; margin-top: 1rem;"><h2 style="color: #ec4899; margin-bottom: 0px; font-weight: 800; font-size: 1.8rem;">🌸 Aki Config</h2><p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0px;">Configure your anime companion</p></div>', unsafe_allow_html=True)

if os.path.exists("aki_avatar.png"):
    st.sidebar.image("aki_avatar.png", use_container_width=True)

st.sidebar.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)

st.sidebar.markdown("### 🔑 API Authentication")

# Get initial values from environment or secrets
env_gemini = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        env_gemini = st.secrets["GEMINI_API_KEY"]
    elif "GOOGLE_API_KEY" in st.secrets:
        env_gemini = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

if not env_gemini:
    env_gemini = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
env_gemini = env_gemini.strip() if env_gemini else ""

env_tavily = ""
try:
    if "TAVILY_API_KEY" in st.secrets:
        env_tavily = st.secrets["TAVILY_API_KEY"]
except Exception:
    pass

if not env_tavily:
    env_tavily = os.getenv("TAVILY_API_KEY", "")
env_tavily = env_tavily.strip() if env_tavily else ""

# Input fields
gemini_input = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    value=st.session_state.get("gemini_key_override", env_gemini),
    help="Enter your Gemini API key (from Google AI Studio)"
)
st.session_state.gemini_key_override = gemini_input

tavily_input = st.sidebar.text_input(
    "Tavily API Key",
    type="password",
    value=st.session_state.get("tavily_key_override", env_tavily),
    help="Enter your Tavily API key for web search"
)
st.session_state.tavily_key_override = tavily_input

if not gemini_input.strip():
    st.sidebar.warning("⚠️ Gemini API Key is missing. Enter a key above to activate Aki.")

if st.sidebar.button("💾 Save Keys to .env", use_container_width=True):
    try:
        with open(dotenv_path, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY = {gemini_input.strip()}\n")
            f.write(f"TAVILY_API_KEY = {tavily_input.strip()}\n")
        
        # Keep environment variable updated in current process memory too
        os.environ["GEMINI_API_KEY"] = gemini_input.strip()
        os.environ["TAVILY_API_KEY"] = tavily_input.strip()
        
        st.toast("Keys saved to `.env`!", icon="✅")
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error saving to `.env`: {e}")

st.sidebar.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

# Conversation reset
if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.thread_id = f"aki_session_{uuid.uuid4().hex[:8]}"
    st.toast("Chat history has been reset!", icon="🌸")
    time.sleep(0.5)
    st.rerun()

# ----------------------------------------------------
# 4. LangGraph Agent Logic Definition
# ----------------------------------------------------
class State(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]

# Interactive tool definition
@tool
def web_search(query: str):
    """a web search tool to find information on the web about recent anime, manga, studios, release dates, and pop culture."""
    tavily_key = resolve_tavily_key()
    if not tavily_key:
        return "Error: Tavily Search API key is missing. Please configure it in the sidebar settings."
    try:
        os.environ["TAVILY_API_KEY"] = tavily_key
        search = TavilySearch(max_results=3)
        return search.invoke(query)
    except Exception as e:
        return f"Error executing web search tool: {str(e)}"

# Chatbot node
def openchat(state: State):
    user_msg = state.messages
    sys_msg = SystemMessage(content=system_prompt)
    full_prompt = [sys_msg] + user_msg
    
    api_key = resolve_gemini_key()
    if not api_key:
        raise ValueError("Gemini API key is missing. Please configure it in the sidebar settings on the left.")
        
    model_name = "gemini-2.5-flash"
    
    client = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key
    )
    
    llm_tool = client.bind_tools([web_search])
    response = llm_tool.invoke(full_prompt)
    return {"messages": [response]}

# Compile LangGraph graph
@st.cache_resource
def get_compiled_graph():
    tool_node = ToolNode([web_search])
    
    graph = StateGraph(State)
    graph.add_node("chatbot", openchat)
    graph.add_node("tools", tool_node)
    
    graph.add_edge(START, "chatbot")
    graph.add_conditional_edges("chatbot", tools_condition)
    graph.add_edge("tools", "chatbot")
    
    memory = MemorySaver = None # we'll instantiate MemorySaver here
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)

app = get_compiled_graph()


# ----------------------------------------------------
# 5. Header Section
# ----------------------------------------------------
st.markdown('<h1 class="header-container">🌸 Aki: Anime Companion</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-container">Your passionate, high-energy anime expert companion! Driven by LangGraph & Tavily Search.</p>', unsafe_allow_html=True)


# ----------------------------------------------------
# 6. Past Message Rendering Logic
# ----------------------------------------------------
def render_past_messages():
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    state = app.get_state(config)
    messages = state.values.get("messages", [])
    
    idx = 0
    while idx < len(messages):
        msg = messages[idx]
        if isinstance(msg, SystemMessage):
            idx += 1
            continue
        elif isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(f'<div class="chat-bubble-user">{msg.content}</div>', unsafe_allow_html=True)
            idx += 1
        elif isinstance(msg, AIMessage):
            tool_calls = msg.tool_calls
            tool_outputs = []
            
            # Find any successive ToolMessages to associate them with this assistant response
            next_idx = idx + 1
            while next_idx < len(messages) and isinstance(messages[next_idx], ToolMessage):
                tool_outputs.append(messages[next_idx])
                next_idx += 1
            
            with st.chat_message("assistant", avatar=avatar_path):
                # Render tool calls inside expander
                if tool_calls:
                    for tc in tool_calls:
                        tool_name = tc.get("name", "web_search")
                        tool_args = tc.get("args", {})
                        
                        # Match tool output
                        matching_output = ""
                        for to in tool_outputs:
                            if to.tool_call_id == tc.get("id"):
                                matching_output = to.content
                                break
                        if not matching_output and tool_outputs:
                            matching_output = tool_outputs[0].content
                        
                        st.info(f"🔮 **Aki searched the web** for: `{tool_args.get('query', '')}`")
                        with st.expander("Show web search results", expanded=False):
                            st.write(matching_output)
                
                # Render final reply
                if msg.content:
                    content_text = extract_text_content(msg.content)
                    if content_text:
                        st.markdown(f'<div class="chat-bubble-aki">{content_text}</div>', unsafe_allow_html=True)
            
            idx = next_idx

# Render chat history
render_past_messages()


# ----------------------------------------------------
# 7. Preset Prompt Chips
# ----------------------------------------------------
st.markdown("##### Spark a Conversation:")
col1, col2, col3 = st.columns(3)
preset_prompt = None

with col1:
    if st.button("🌸 Cozy Slice-of-Life recommendations", key="chip_sol", use_container_width=True):
        preset_prompt = "Can you recommend a cozy slice-of-life anime and explain why I'll love it?"
with col2:
    if st.button("⚔️ Fate Watch Order guide", key="chip_fate", use_container_width=True):
        preset_prompt = "What is the simplest and best watch order for the Fate series?"
with col3:
    if st.button("🔥 Latest Anime News & Trends", key="chip_news", use_container_width=True):
        preset_prompt = "Search the web for the latest major anime news and upcoming seasonal highlights!"


# ----------------------------------------------------
# 8. User Input & Agent Run Execution Loop
# ----------------------------------------------------
user_input = st.chat_input("Ask Aki about anime, characters, watch orders...")

if preset_prompt:
    user_input = preset_prompt

if user_input:
    # Display User Message
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-bubble-user">{user_input}</div>', unsafe_allow_html=True)
    
    # Display Assistant Message and execute Agent graph
    with st.chat_message("assistant", avatar=avatar_path):
        status_container = st.container()
        response_placeholder = st.empty()
        
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        final_answer = ""
        
        with st.spinner("Aki is focusing..."):
            try:
                events = app.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config,
                    stream_mode="updates"
                )
                
                for event in events:
                    # Log/Draw Agent Steps
                    if "chatbot" in event:
                        node_output = event["chatbot"]
                        messages = node_output.get("messages", [])
                        for msg in messages:
                            if isinstance(msg, AIMessage):
                                if msg.tool_calls:
                                    for tc in msg.tool_calls:
                                        tool_args = tc.get("args", {})
                                        with status_container:
                                            st.info(f"🔮 **Aki is searching the web** for info on `{tool_args.get('query', '')}`...")
                                if msg.content:
                                    final_answer = extract_text_content(msg.content)
                                    
                    elif "tools" in event:
                        node_output = event["tools"]
                        messages = node_output.get("messages", [])
                        for msg in messages:
                            if isinstance(msg, ToolMessage):
                                with status_container:
                                    st.success(f"✅ **Search Completed!**")
                                    with st.expander("Show raw web search results", expanded=False):
                                        st.write(msg.content)
                                        
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")
                final_answer = "Sorry! I encountered an error running my LLM or tool nodes. Please check your API keys and try again."
        
        # Render final answer with custom typewriter animation
        if final_answer:
            typed_text = ""
            for char in final_answer:
                typed_text += char
                response_placeholder.markdown(f'<div class="chat-bubble-aki">{typed_text}</div>', unsafe_allow_html=True)
                time.sleep(0.003)
            
            # Make sure the UI updates completely
            st.rerun()
