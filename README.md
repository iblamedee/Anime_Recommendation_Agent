# 🌸 Aki: The Ultimate Anime Companion

Aki is a high-energy, passionate, and fast AI anime companion powered by **LangGraph**, **LangChain**, **Google Gemini**, and **Tavily Search**. Aki is designed to provide instant watch orders, recommendation cards, spoiler-shielded answers, and search-driven seasonal updates with genuine otaku energy—but with zero unnecessary fluff.

---

## 🛠️ Tech Stack

- **Core Framework**: Python 3.14+
- **Agent Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **Model Integration**: [LangChain Google GenAI](https://github.com/langchain-ai/langchain-google) (using `gemini-2.5-flash`)
- **Web UI Interface**: [Streamlit](https://streamlit.io/)
- **Search Tooling**: [Tavily Search API](https://tavily.com/)
- **State Management**: LangGraph `MemorySaver` (short-term session memory persistence)

---

## 📂 Project Structure

The project has been refactored into a clean, modular structure following a strict separation of concerns:

```
├── .env                  # Process environment keys (local-only, gitignored)
├── .env.example          # Sample environment template
├── requirements.txt      # Project library dependencies
├── pyproject.toml        # Metadata configuration
├── sys_prompt.py         # System prompt defining Aki's constraints & personality
├── tools.py              # Shared LangChain tools (e.g. web search)
├── agent.py              # Core LangGraph agent state, nodes, and compiled graph
├── streamlit_app.py      # Entry point: Streamlit Web Dashboard & UI
└── main.py               # Entry point: Interactive Terminal interface
```

### 🧩 Module Details

1. **[sys_prompt.py](file:///x:/project/random/sys_prompt.py)**: Houses the ultimate otaku system prompt. Defines rules for:
   - **Speed Mode**: Cap on words (max 200) and strict formatting limits.
   - **Instant Link Protocol**: Automatically generates MAL, AniList, and Watch/Read links for all mentioned titles.
   - **Spoiler Shield**: Protects plot twists and character deaths.
2. **[tools.py](file:///x:/project/random/tools.py)**: Contains the LangChain `@tool` definitions. Holds the general `web_search` tool linked to the Tavily API as well as custom Jikan API database tools (`search_anime`, `search_manga`, `get_seasonal_anime`, `get_anime_recommendations`) for querying the MyAnimeList database directly.
3. **[agent.py](file:///x:/project/random/agent.py)**: Defines the Graph `State`, creates the nodes (`chatbot` and `tools`), compiles the graph with standard checkpointing memory (`MemorySaver`), and exports the compiled agent.
4. **[streamlit_app.py](file:///x:/project/random/streamlit_app.py)**: Renders a premium, glassmorphism-inspired dark UI with custom CSS. Manages key input overrides, renders conversation history, displays search progress indicators, and streams responses with typewriter animations.
5. **[main.py](file:///x:/project/random/main.py)**: An interactive CLI version of Aki that allows quick testing and full conversation loops in the terminal.

---

## 🚀 Getting Started

### 1. Installation

First, clone the workspace and install the required dependencies using a virtual environment manager:

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using standard pip
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory and add your API credentials:

```ini
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

*Note: In the Streamlit Web interface, you can also override and save these keys dynamically using the configuration sidebar.*

### 3. Running the Interfaces

#### Run the Terminal CLI
```bash
python main.py
```

#### Run the Streamlit Web Application
```bash
streamlit run streamlit_app.py
```
