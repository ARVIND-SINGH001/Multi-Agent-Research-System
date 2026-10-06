from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from langchain.tools import tool
from tavily import TavilyClient
import requests
from rich import print
import os
from bs4 import BeautifulSoup


tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

@tool
def web_search(query : str) ->str:
    """
    Search the web for a given query and return the top & reliable results.
    Args:
        query: A natural-language search query, such as
               "effect of US Iran war on India".
    """

    results = tavily.search(query=query, max_results=2)
    print("Debug: Web search results:", results)  # Debugging line

    out = []
    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:100]}\n"
        )
    return "\n\n".join(out)





@tool
def scrape_url(url: str) -> str:
    """
    Scrape a webpage and return its text content.

    IMPORTANT:
    The `url` argument MUST be a complete webpage URL.
    Example:
    url="https://www.reuters.com/world/..."

    Do not pass keywords, search terms, dates, patterns,
    titles, IDs, or any other value.
    """
    try:
        print(f"Debug: Scraping URL: {url}")  # Debugging line
        resp = requests.get(url,timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]

    except Exception as e:
        return f"Error scraping URL: {str(e)}"    


