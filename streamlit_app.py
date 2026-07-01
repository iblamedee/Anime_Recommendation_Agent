import streamlit as st
import os
import uuid
import time
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from agent import get_compiled_graph as compile_agent_graph

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

/* Card wrapper styling */
.ani-card {
    display: flex;
    flex-direction: row;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(236, 72, 153, 0.15);
    border-radius: 12px;
    padding: 12px;
    margin: 12px 0;
    gap: 16px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.ani-card-poster {
    width: 90px !important;
    height: 130px !important;
    object-fit: cover !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4) !important;
    flex-shrink: 0 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}

.ani-card-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.ani-card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ec4899;
    margin: 0 0 4px 0;
}

.ani-card-meta {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-bottom: 6px;
    line-height: 1.4;
}

.ani-card-hook {
    font-size: 0.95rem;
    font-style: italic;
    color: #f1f5f9;
    margin-bottom: 8px;
    line-height: 1.4;
}

.ani-card-links {
    font-size: 0.85rem;
    margin-top: 4px;
}

.ani-card-link {
    color: #ec4899 !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    padding: 3px 8px !important;
    background: rgba(236, 72, 153, 0.1) !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
    margin-right: 8px !important;
    border: 1px solid rgba(236, 72, 153, 0.2) !important;
    display: inline-block !important;
}

.ani-card-link:hover {
    background: rgba(236, 72, 153, 0.2) !important;
    border-color: rgba(236, 72, 153, 0.4) !important;
    box-shadow: 0 0 8px rgba(236, 72, 153, 0.3) !important;
}

/* General fallback for any inline image inside Aki bubbles */
.chat-bubble-aki img:not(.ani-card-poster) {
    max-width: 90px !important;
    max-height: 130px !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    margin: 5px !important;
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
    # Check streamlit secrets (used in Streamlit Cloud)
    try:
        if "TAVILY_API_KEY" in st.secrets:
            return st.secrets["TAVILY_API_KEY"].strip()
    except Exception:
        pass
    key = os.getenv("TAVILY_API_KEY", "")
    return key.strip() if key else ""

def sync_env_keys():
    gemini_key = resolve_gemini_key()
    tavily_key = resolve_tavily_key()
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key


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

# Sync the keys to os.environ so that the agent modules can access them
sync_env_keys()

# Verify that the keys are configured in environment or secrets
gemini_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
if not gemini_key.strip():
    st.sidebar.warning("⚠️ Gemini API Key is missing in environment (.env or secrets). Please configure it to activate Aki.")
else:
    st.sidebar.success("🌸 Aki is online and ready!")

st.sidebar.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)

# Conversation reset
if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.thread_id = f"aki_session_{uuid.uuid4().hex[:8]}"
    st.toast("Chat history has been reset!", icon="🌸")
    time.sleep(0.5)
    st.rerun()

# ----------------------------------------------------
# 4. LangGraph Agent Logic Integration
# ----------------------------------------------------
@st.cache_resource
def get_cached_graph():
    return compile_agent_graph()

app = get_cached_graph()


# ----------------------------------------------------
# 5. Header Section
# ----------------------------------------------------
st.markdown('<h1 class="header-container">🌸 Aki: Anime Companion</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-container">Your passionate, high-energy anime expert companion! Driven by LangGraph & Tavily Search.</p>', unsafe_allow_html=True)


# ----------------------------------------------------
# 5.5. Recommendation Card Parser Helpers
# ----------------------------------------------------
def parse_and_format_cards(text: str) -> str:
    """Parses standard markdown recommendation cards and converts them into visual flexbox HTML cards."""
    lines = text.split("\n")
    output_lines = []
    
    in_card = False
    card_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("🎌"):
            # If we were already in a card, process and close it first
            if in_card:
                output_lines.append(_render_card_html(card_lines))
                card_lines = []
            in_card = True
            card_lines.append(line)
        elif in_card:
            # Close card if we hit lists, block headers, or dividers
            if stripped == "" or stripped.startswith("-") or stripped.startswith("1."):
                output_lines.append(_render_card_html(card_lines))
                card_lines = []
                in_card = False
                output_lines.append(line)
            else:
                card_lines.append(line)
        else:
            output_lines.append(line)
            
    # Process final card if still open
    if in_card:
        output_lines.append(_render_card_html(card_lines))
        
    return "\n".join(output_lines)

def _render_card_html(lines: list[str]) -> str:
    title = ""
    image_url = ""
    meta = ""
    hook = ""
    links = ""
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("🎌"):
            title = stripped.replace("🎌", "", 1).strip().replace("**", "")
        elif stripped.startswith("![Poster]"):
            # Extract URL from markdown format ![Poster](url)
            start = stripped.find("(")
            end = stripped.find(")")
            if start != -1 and end != -1:
                image_url = stripped[start+1:end].strip()
        elif stripped.startswith("🎭"):
            meta = stripped.replace("🎭", "", 1).strip().replace("**", "")
        elif stripped.startswith("⚡"):
            hook = stripped.replace("⚡", "", 1).strip().replace("**", "")
        elif stripped.startswith("🔗"):
            links = stripped.replace("🔗", "", 1).strip()
            
    # Format poster image column
    img_html = ""
    if image_url:
        img_html = f'<img class="ani-card-poster" src="{image_url}" alt="Poster" />'
        
    # Convert markdown links or raw URLs in the link line to premium HTML badges
    links_html = ""
    if links:
        import re
        parts = links.split("|")
        linkified_parts = []
        for p in parts:
            part_str = p.strip()
            if not part_str:
                continue
                
            # 1. Check for markdown link [label](url)
            md_match = re.search(r"\[(.*?)\]\((.*?)\)", part_str)
            if md_match:
                label = md_match.group(1).strip()
                url = md_match.group(2).strip()
                prefix = part_str[:md_match.start()].strip().rstrip(":").strip()
                link_text = f"{prefix}: {label}" if prefix else label
                linkified_parts.append(f'<a href="{url}" target="_blank" class="ani-card-link">{link_text}</a>')
                continue
                
            # 2. Check for raw HTTP/HTTPS URL
            url_match = re.search(r"(https?://[^\s|]+)", part_str)
            if url_match:
                url = url_match.group(1).strip()
                prefix = part_str[:url_match.start()].strip().rstrip(":").strip()
                link_text = prefix if prefix else "Link"
                linkified_parts.append(f'<a href="{url}" target="_blank" class="ani-card-link">{link_text}</a>')
                continue
                
            # 3. Fallback to plain text if no link matches
            linkified_parts.append(part_str)
            
        links_html = " ".join(linkified_parts)
    
    card_html = f'<div class="ani-card">{img_html}<div class="ani-card-content"><div class="ani-card-title">🎌 {title}</div><div class="ani-card-meta">🎭 {meta}</div>'
    if hook:
        card_html += f'<div class="ani-card-hook">⚡ {hook}</div>'
    if links_html:
        card_html += f'<div class="ani-card-links">🔗 {links_html}</div>'
    card_html += '</div></div>'
    return card_html


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
                        formatted_text = parse_and_format_cards(content_text)
                        st.markdown(f'<div class="chat-bubble-aki">{formatted_text}</div>', unsafe_allow_html=True)
            
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
                # During typing, render normally inside the bubble
                response_placeholder.markdown(f'<div class="chat-bubble-aki">{typed_text}</div>', unsafe_allow_html=True)
                time.sleep(0.003)
            
            # Once typing is complete, convert standard text to custom premium cards
            formatted_answer = parse_and_format_cards(final_answer)
            response_placeholder.markdown(f'<div class="chat-bubble-aki">{formatted_answer}</div>', unsafe_allow_html=True)
            
            # Make sure the UI updates completely
            st.rerun()
