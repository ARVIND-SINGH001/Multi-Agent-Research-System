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
- After the search, STOP.
- Do not call web_search again.
- Return the collected search results as is as without any modifications.
    """
    )


def build_reader_agent():
    return create_agent(
        LLM,
        tools=[scrape_url],
        system_prompt= """
You are a research source reader.

You will receive raw search results.

Your job:
1. Select exactly ONE most relevant URL.
2. Call scrape_url exactly ONE time.
3. Return the scraped content to the pipeline.
4. Preserve the source URL.

Rules:
- Only select ONE URL.
- Only make ONE scrape_url call.
- Do not call scrape_url again.
- Do not summarize the content.
- Do not interpret the content.
- Do not add information from your own knowledge.
- Do not make conclusions.
- Do not invent facts.

"""
    )






#  Writer chain

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research writer.

Write a clear, engaging, and well-structured research report
using ONLY the information provided in the research material.


Rules:
- Do not use outside knowledge.
- Do not invent facts, statistics, claims, or sources.
- Explain important findings clearly and provide useful context
  from the research.
- Keep the writing natural and easy to understand.
- Maintain a logical flow between sections.
- Avoid unnecessary repetition and overly technical language.
- Do not use inline citations, footnotes, citation markers,
  or academic-style references.
- Do not use HTML tags such as <br>, <p>, or <div>.
- Use clean Markdown formatting.
-Do not add inline citations, citation markers, line references,
footnotes, or academic-style references. example - 【1†L1-L4】.

Only include the source URLs in the final Sources section.
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
        """
        You are a sharp and constructive research critic. Be honest and specific.

Your job is to review the research report based ONLY on the information provided in the report.

Treat all information contained in the provided report as the source of truth for this review.

Do NOT use your own knowledge, assumptions, memory, or knowledge of current events to fact-check, challenge, or contradict the report.

Do NOT question whether current or recent claims are still true in the real world.

Do NOT say that claims need to be independently verified, fact-checked, or confirmed simply because they concern current or recent events.

Do NOT require the report to contain explicit citations, source-to-claim mappings, methodology sections, or explanations of which source supports each individual claim unless the report itself is internally inconsistent about them.

Evaluate ONLY:
- Whether the report is clear and understandable.
- Whether the report is well-structured and coherent.
- Whether the information presented is internally consistent.
- Whether the report contains contradictions or obvious logical problems within its own content.
- Whether the explanations and conclusions logically follow from the information presented.
- Whether the report is useful and informative for the reader.
- Whether important information presented in the report is confusing, repetitive, irrelevant, or poorly explained.

Accept the claims and information presented in the report as given.

Do NOT penalize the report merely because you personally cannot verify a claim, because a claim concerns a current event, or because the report does not explicitly connect every claim to a source.

Do NOT introduce new facts, corrections, or outside information.

Your review must be about the quality of the report itself, not about independently verifying whether the real-world events described are true.
        """
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
