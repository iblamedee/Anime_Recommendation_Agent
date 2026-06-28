from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel
from typing import Annotated
from sys_prompt import system_prompt
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv(override=True)

# Helper functions to resolve API keys from environment or fallbacks
def resolve_gemini_key():
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        key = os.getenv("GOOGLE_API_KEY", "")
    if not key:
        key = "AIzaSyBeAkIolDCEK_XX1LKaoj2F5UHeFeog6Qc"
    return key.strip() if key else ""

def resolve_tavily_key():
    key = os.getenv("TAVILY_API_KEY", "")
    if not key:
        key = "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"
    return key.strip() if key else ""

class State(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]

# Initialize Gemini Model
api_key = resolve_gemini_key()
client = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

@tool
def web_search(query: str):
    """a web search tool to find information on the web about recent anime, manga, and news."""
    tavily_key = resolve_tavily_key()
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
    search = TavilySearch(max_results=3)
    return search.invoke(query)

llm_tool = client.bind_tools([web_search])

sys_prompt = system_prompt

def openchat(state: State):
    user_msg = state.messages
    sys_msg = SystemMessage(content=sys_prompt)
    full_prompt = [sys_msg] + user_msg
    response = llm_tool.invoke(full_prompt)
    return {"messages": [response]}

tool_node = ToolNode([web_search])

graph = StateGraph(State)
graph.add_node("chatbot", openchat)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chatbot")
graph.add_conditional_edges("chatbot", tools_condition)
graph.add_edge("tools", "chatbot")

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

def aki():
    config = {"configurable": {"thread_id": "aki_terminal_session"}}
    print("\n🌸 Aki - The Ultimate Anime Companion (Terminal Mode) 🌸")
    print("Type 'exit', 'quit', or 'q' to end the conversation.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nAki: Sayonara! Matane~ 🌸")
                break
            
            print("Aki: (Thinking...)")
            response = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            # Print response safely unpacking list format if returned
            last_msg = response["messages"][-1].content
            if isinstance(last_msg, list):
                parts = []
                for p in last_msg:
                    if isinstance(p, str):
                        parts.append(p)
                    elif isinstance(p, dict) and "text" in p:
                        parts.append(p["text"])
                last_msg = "".join(parts)
                
            print(f"\nAki: {last_msg}\n")
            
        except KeyboardInterrupt:
            print("\nAki: Sayonara! Matane~ 🌸")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    aki()