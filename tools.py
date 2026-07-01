import os
import urllib.request
import urllib.parse
import json
import time
from langchain.tools import tool
from langchain_tavily import TavilySearch

def _query_jikan(endpoint: str, params: dict = None) -> dict:
    """Helper to query the Jikan API with retry logic for rate limits."""
    url = f"https://api.jikan.moe/v4/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    headers = {
        "User-Agent": "AkiAnimeCompanion/3.0 (Streamlit App)"
    }
    
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limit exceeded (3 requests/sec)
                time.sleep(1.5)
                continue
            return {"error": f"HTTP Error {e.code}: {e.reason}"}
        except Exception as e:
            return {"error": f"Connection error: {str(e)}"}
            
    return {"error": "Jikan API rate limit exceeded. Please try again in a moment."}

@tool
def web_search(query: str) -> str:
    """A web search tool to find information on the web about recent anime, manga, studios, release dates, and pop culture."""
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not tavily_key:
        return "Error: Tavily Search API key is missing. Please configure it in the sidebar settings or environment."
    try:
        os.environ["TAVILY_API_KEY"] = tavily_key
        search = TavilySearch(max_results=3)
        return str(search.invoke(query))
    except Exception as e:
        return f"Error executing web search tool: {str(e)}"

@tool
def search_anime(query: str) -> str:
    """Search the MyAnimeList database for anime details including score, synopsis, genres, studios, and poster image URLs."""
    res = _query_jikan("anime", {"q": query, "limit": 5})
    if "error" in res:
        return f"Error querying database: {res['error']}"
    
    data = res.get("data", [])
    if not data:
        return f"No anime found for query: '{query}'"
        
    output = []
    for item in data:
        title = item.get("title_english") or item.get("title")
        synopsis = item.get("synopsis", "No synopsis available.")
        # Shorten synopsis for the agent if it's too long
        if synopsis and len(synopsis) > 300:
            synopsis = synopsis[:300] + "..."
            
        genres = ", ".join([g.get("name") for g in item.get("genres", []) if g.get("name")])
        studios = ", ".join([s.get("name") for s in item.get("studios", []) if s.get("name")])
        
        # Get poster image URL
        image_url = item.get("images", {}).get("jpg", {}).get("large_image_url") or item.get("images", {}).get("jpg", {}).get("image_url", "")
        
        anime_info = (
            f"- **Title**: {title} (MAL ID: {item.get('mal_id')})\n"
            f"  **Score**: {item.get('score', 'N/A')} | **Type**: {item.get('type', 'N/A')} | **Episodes**: {item.get('episodes', 'N/A')}\n"
            f"  **Status**: {item.get('status', 'N/A')} | **Year**: {item.get('year', 'N/A')}\n"
            f"  **Studios**: {studios or 'N/A'} | **Genres**: {genres or 'N/A'}\n"
            f"  **Poster Image**: {image_url}\n"
            f"  **MAL URL**: {item.get('url', '')}\n"
            f"  **Synopsis**: {synopsis}\n"
        )
        output.append(anime_info)
        
    return "\n".join(output)

@tool
def search_manga(query: str) -> str:
    """Search the MyAnimeList database for manga and light novel details including score, volumes, chapters, genres, authors, and poster image URLs."""
    res = _query_jikan("manga", {"q": query, "limit": 5})
    if "error" in res:
        return f"Error querying database: {res['error']}"
        
    data = res.get("data", [])
    if not data:
        return f"No manga found for query: '{query}'"
        
    output = []
    for item in data:
        title = item.get("title")
        synopsis = item.get("synopsis", "No synopsis available.")
        if synopsis and len(synopsis) > 300:
            synopsis = synopsis[:300] + "..."
            
        genres = ", ".join([g.get("name") for g in item.get("genres", []) if g.get("name")])
        authors = ", ".join([a.get("name") for a in item.get("authors", []) if a.get("name")])
        
        image_url = item.get("images", {}).get("jpg", {}).get("large_image_url") or item.get("images", {}).get("jpg", {}).get("image_url", "")
        
        manga_info = (
            f"- **Title**: {title} (MAL ID: {item.get('mal_id')})\n"
            f"  **Score**: {item.get('score', 'N/A')} | **Type**: {item.get('type', 'N/A')}\n"
            f"  **Chapters**: {item.get('chapters', 'N/A')} | **Volumes**: {item.get('volumes', 'N/A')} | **Status**: {item.get('status', 'N/A')}\n"
            f"  **Authors**: {authors or 'N/A'} | **Genres**: {genres or 'N/A'}\n"
            f"  **Poster Image**: {image_url}\n"
            f"  **MAL URL**: {item.get('url', '')}\n"
            f"  **Synopsis**: {synopsis}\n"
        )
        output.append(manga_info)
        
    return "\n".join(output)

@tool
def get_seasonal_anime() -> str:
    """Retrieve top currently airing seasonal anime from MyAnimeList, sorting them by score."""
    res = _query_jikan("seasons/now", {"limit": 15})
    if "error" in res:
        return f"Error querying database: {res['error']}"
        
    data = res.get("data", [])
    if not data:
        return "No currently airing seasonal anime found."
        
    # Sort by score descending (filter out None scores)
    valid_items = [item for item in data if item.get("score") is not None]
    valid_items.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # Take top 10
    top_10 = valid_items[:10]
    
    output = []
    for item in top_10:
        title = item.get("title_english") or item.get("title")
        genres = ", ".join([g.get("name") for g in item.get("genres", []) if g.get("name")])
        studios = ", ".join([s.get("name") for s in item.get("studios", []) if s.get("name")])
        image_url = item.get("images", {}).get("jpg", {}).get("large_image_url") or item.get("images", {}).get("jpg", {}).get("image_url", "")
        
        anime_info = (
            f"- **Title**: {title} (MAL ID: {item.get('mal_id')})\n"
            f"  **Score**: {item.get('score', 'N/A')} | **Episodes**: {item.get('episodes', 'N/A')} | **Status**: {item.get('status', 'N/A')}\n"
            f"  **Studios**: {studios or 'N/A'} | **Genres**: {genres or 'N/A'}\n"
            f"  **Poster Image**: {image_url}\n"
            f"  **MAL URL**: {item.get('url', '')}\n"
        )
        output.append(anime_info)
        
    return "\n".join(output)

@tool
def get_anime_recommendations(anime_id: int) -> str:
    """Retrieve anime recommendations matching a given MyAnimeList ID. Useful when a user asks for recommendations similar to a specific show."""
    res = _query_jikan(f"anime/{anime_id}/recommendations")
    if "error" in res:
        return f"Error querying database: {res['error']}"
        
    data = res.get("data", [])
    if not data:
        return f"No recommendations found for anime ID: {anime_id}."
        
    # Limit to top 5 recommendations
    recommendations = data[:5]
    
    output = []
    for item in recommendations:
        entry = item.get("entry", {})
        title = entry.get("title")
        mal_id = entry.get("mal_id")
        mal_url = entry.get("url")
        image_url = entry.get("images", {}).get("jpg", {}).get("large_image_url") or entry.get("images", {}).get("jpg", {}).get("image_url", "")
        
        rec_info = (
            f"- **Recommended Title**: {title} (MAL ID: {mal_id})\n"
            f"  **Poster Image**: {image_url}\n"
            f"  **MAL URL**: {mal_url}\n"
        )
        output.append(rec_info)
        
    return "\n".join(output)
