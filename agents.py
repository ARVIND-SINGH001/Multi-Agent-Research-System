from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url




LLM = ChatGroq(model="openai/gpt-oss-120b",temperature=0)

# agents

def build_search_agent():
    return create_agent(
        LLM,
        tools=[web_search],
        system_prompt="""
    You are a research search agent.

Your task is to find reliable information about the user's research topic.

Use the web_search tool to search for relevant information.

IMPORTANT:
- Perform at only 1 web search for each topic.
- After the searche, STOP.
- Do not call web_search again.
- Return the collected search results, including titles, URLs and relevant content.
    """
    )


def build_reader_agent():
    return create_agent(
        LLM,
        tools=[scrape_url],
        system_prompt="""
You are a research source reader.

You will receive raw search results.

Your job:

1. Select the 2 most relevant sources, only scrape 2 urls.
2. Call scrape_url once for each selected URL.
3. Extract factual information from those pages.
4. Preserve the source URL with every source.
5. Do not add information from your own knowledge.
6. Do not make conclusions.
7. Do not invent facts.
"""
    )






#  Writer chain

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a research writer.

Use ONLY the verified scraped sources provided to you.

Rules:
- Do not use your pretrained knowledge.
- Do not invent facts.
- Do not infer unsupported statistics.
- Every factual claim must be supported by a provided source.
- Clearly distinguish forecasts from established facts.
- If evidence is insufficient, explicitly say so.
- If sources disagree, report the disagreement.
        """
    ),
    (
        "human",
        """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""
    )
])


writer_chain = writer_prompt | LLM | StrOutputParser()






# Critic chain-------

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. Be honest and specific."
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""
    )
])



critic_chain = critic_prompt | LLM | StrOutputParser()
