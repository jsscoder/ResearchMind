import os
from dotenv import load_dotenv

# 1. Force environment loading BEFORE importing or initializing the SDK
load_dotenv()

import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from google import genai
from google.genai import types

# 2. Pass the API key explicitly as a fallback argument
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --------------------
# Custom Tools (Plain Functions with explicit Docstrings)
# --------------------

def web_search(query: str) -> str:
    """Search the web for recent and reliable information. Returns Titles, URLs, and summaries.

    Args:
        query: The search engine query string.
    """
    try:
        results = tavily.search(query=query, max_results=4)
        out = []
        for r in results.get('results', []):
            out.append(f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nSummary: {r.get('content', '')}\n")
        return "\n----\n".join(out)
    except Exception as e:
        return f"Search initialization failed: {str(e)}"

def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading.

    Args:
        url: The exact HTTP or HTTPS web link to extract text from.
    """
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "form"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:4000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

# --------------------
# Mock Message Object for Frontend
# --------------------
class AIMessage:
    """Mimics LangChain's AIMessage object so the frontend can call .content"""
    def __init__(self, content: str):
        self.content = content

# --------------------
# Agent Classes (Using Gemini Tool Calling)
# --------------------

class SearchAgent:
    def invoke(self, inputs: dict) -> dict:
        # Extract the prompt from the frontend's message list: [("user", "prompt text")]
        user_prompt = inputs.get("messages", [])[-1][1]

        config = types.GenerateContentConfig(
            tools=[web_search],
            temperature=0.2,
            system_instruction="You are a search agent. Use the web_search tool to find the most recent and accurate information based on the user's query. Return a detailed summary of your findings."
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt,
            config=config
        )

        # Return in the exact format the frontend expects: sr["messages"][-1].content
        return {"messages": [AIMessage(response.text)]}

class ReaderAgent:
    def invoke(self, inputs: dict) -> dict:
        user_prompt = inputs.get("messages", [])[-1][1]

        config = types.GenerateContentConfig(
            tools=[scrape_url],
            temperature=0.2,
            system_instruction="You are a data-extraction agent. Identify the single most relevant URL from the user's prompt, use the scrape_url tool to read it, and return the deep content you found."
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt,
            config=config
        )

        return {"messages": [AIMessage(response.text)]}

# --------------------
# Tool Providers (Factory Endpoints matching App Architecture)
# --------------------

def build_search_agent():
    """Returns the SearchAgent instance for the Streamlit UI loop execution."""
    return SearchAgent()

def build_reader_agent():
    """Returns the ReaderAgent instance for the Streamlit UI loop execution."""
    return ReaderAgent()

# --------------------
# Writer Chain Component
# --------------------

class WriterChain:
    def __init__(self):
        self.system_instruction = "You are an expert research writer. Write clear, structured and insightful reports."

    def invoke(self, inputs: dict) -> str:
        """Mimics the LangChain .invoke() interface for a seamless frontend match."""
        topic = inputs.get("topic", "")
        research = inputs.get("research", "")

        prompt = f"""
Write a detailed research report on the topic below.

Topic:
{topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional. Use clean Markdown styling.
"""
        config = types.GenerateContentConfig(
            temperature=0.2,
            system_instruction=self.system_instruction
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )
        # Frontend expects a raw string back from the writer chain
        return response.text

writer_chain = WriterChain()

# --------------------
# Critic Chain Component
# --------------------

class CriticChain:
    def __init__(self):
        self.system_instruction = "You are a sharp and constructive research critic. Be honest and specific."

    def invoke(self, inputs: dict) -> str:
        """Mimics the LangChain .invoke() interface for a seamless frontend match."""
        report = inputs.get("report", "")

        prompt = f"""
Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

**Score:** X/10

**Strengths:**
- ...

**Areas to Improve:**
- ...

**One line verdict:** ...
"""
        config = types.GenerateContentConfig(
            temperature=0.2,
            system_instruction=self.system_instruction
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config
        )
        # Frontend expects a raw string back from the critic chain
        return response.text

critic_chain = CriticChain()
