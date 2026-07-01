from typing import Annotated
from pydantic import BaseModel
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
import os

from sys_prompt import system_prompt
from tools import (
    web_search,
    search_anime,
    search_manga,
    get_seasonal_anime,
    get_anime_recommendations
)

class State(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]

def openchat(state: State):
    user_msg = state.messages
    sys_msg = SystemMessage(content=system_prompt)
    full_prompt = [sys_msg] + user_msg
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Gemini API key is missing. Please configure it in your environment or sidebar settings.")
        
    model_name = "gemini-2.5-flash"
    
    client = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key
    )
    
    llm_tool = client.bind_tools([
        web_search,
        search_anime,
        search_manga,
        get_seasonal_anime,
        get_anime_recommendations
    ])
    response = llm_tool.invoke(full_prompt)
    return {"messages": [response]}

def get_compiled_graph():
    tool_node = ToolNode([
        web_search,
        search_anime,
        search_manga,
        get_seasonal_anime,
        get_anime_recommendations
    ])
    
    graph = StateGraph(State)
    graph.add_node("chatbot", openchat)
    graph.add_node("tools", tool_node)
    
    graph.add_edge(START, "chatbot")
    graph.add_conditional_edges("chatbot", tools_condition)
    graph.add_edge("tools", "chatbot")
    
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
