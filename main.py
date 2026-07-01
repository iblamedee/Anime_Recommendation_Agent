from dotenv import load_dotenv
import os
import sys
from langchain_core.messages import HumanMessage
from agent import get_compiled_graph

# Load environment variables
load_dotenv(override=True)

# Ensure Gemini API key is set before running CLI agent
api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
if not api_key:
    print("\n❌ Error: Gemini API key is missing! Please configure GEMINI_API_KEY in your .env file or environment.\n")
    sys.exit(1)

app = get_compiled_graph()

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