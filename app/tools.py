import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Tavily Client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query: str) -> str:
    """Search the web for recent and reliable information about a given topic.
    Returns Titles, URLs, and summaries of the top results.

    Args:
        query: The search query string.
    """
    try:
        results = tavily.search(query=query, max_results=4)
        out = []
        for r in results.get('results', []):
            out.append(f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nSummary: {r.get('content', '')}\n")
        return "\n----\n".join(out)
    except Exception as e:
        return f"Search execution failed: {str(e)}"


def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading.

    Args:
        url: The absolute HTTP/HTTPS URL string to parse.
    """
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "form"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"