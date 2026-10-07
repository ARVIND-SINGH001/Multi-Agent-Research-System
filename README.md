
# Multi-Agent Research System

An **agentic AI research system** that automatically searches the web, gathers relevant information, generates a structured research report, and evaluates the final output.

---

## Overview

This project uses multiple specialized AI components to perform a complete research workflow instead of relying on a single LLM call.

**Research Flow:**

**User Topic → Search Agent → Reader Agent → Writer → Critic → Final Report**

Each component has a specific responsibility, making the overall workflow more structured, grounded, and easier to validate.

---

## How It Works

### 1. Search Agent

The **Search Agent** uses the **Tavily API** to search the web for recent and relevant information.

It identifies useful sources and returns:

- Source titles
- URLs
- Search snippets

The search results are then passed to the Reader Agent for deeper research.

---

### 2. Reader Agent

The **Reader Agent** analyzes the search results and selects the most relevant source.

It uses a **BeautifulSoup-based web scraper** to retrieve the actual content from the selected webpage.

The scraped content is passed forward as **raw research evidence**, allowing the Writer to perform the analysis and synthesis.

---

### 3. Writer

The **Writer** uses the collected research to generate a clear, structured, and user-readable report.

The report contains:

- **Introduction**
- **Key Findings**
- **Conclusion**
- **Sources**

The Writer is instructed to remain grounded in the collected research and avoid introducing unsupported information.

---

### 4. Critic

The **Critic** evaluates the generated report before it is treated as the final output.

It checks areas such as:

- **Factual grounding**
- **Research quality**
- **Unsupported claims**
- **Missing information**
- **Overall report quality**

This creates a separate validation stage rather than assuming the first generated report is correct.

---

## Architecture

```text
                         User Topic
                             |
                             v
                    +----------------+
                    |  Search Agent  |
                    |     Tavily     |
                    +-------+--------+
                            |
                     Search Results
                            |
                            v
                    +----------------+
                    |  Reader Agent  |
                    |  Web Scraper  |
                    +-------+--------+
                            |
                      Raw Research
                            |
                            v
                    +----------------+
                    |     Writer     |
                    +-------+--------+
                            |
                     Research Report
                            |
                            v
                    +----------------+
                    |     Critic     |
                    +-------+--------+
                            |
                            v
                      Final Report
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core application |
| **LangChain** | Agent and LLM orchestration |
| **Groq** | LLM inference |
| **Tavily API** | Web search and source discovery |
| **BeautifulSoup** | Webpage content extraction |
| **Requests** | HTTP requests |
| **python-dotenv** | Environment variable management |

---

## Challenges & Solutions

Building the system exposed several practical challenges with **LLM agents and tool calling**.

### Invalid Tool Calls

Agents sometimes generated incorrect arguments when calling tools.

**Solution:** Used clearer tool schemas, descriptions, and stricter agent instructions to constrain tool usage.

### Repeated URL Scraping

The Reader Agent could sometimes call the scraper multiple times for the same URL.

**Solution:** Added **deterministic duplicate-URL protection** at the tool level instead of relying only on the LLM prompt.

### Unsupported Information

The Writer could sometimes introduce information that was not present in the collected research.

**Solution:** Strengthened grounding instructions and explicitly restricted the Writer to the provided research material.

### Large Model Requests

Passing large amounts of scraped webpage content could exceed the model's token limits.

**Solution:** Cleaned webpage content and limited the amount of information passed between stages.

### API Rate Limits

Repeated agent and tool calls could result in API rate-limit errors.

**Solution:** Reduced unnecessary calls and added stronger controls around agent behavior.

---

## Key Learning

The main focus of this project was not just building an agentic workflow, but understanding the **reliability challenges of agentic systems**.

LLMs can reason about which tools to use, but their behavior is not always deterministic. This project demonstrated the importance of combining **LLM-based reasoning with deterministic safeguards**, especially when agents interact with external APIs and web resources.

The result is a research workflow that combines:

**Agentic Reasoning + Web Retrieval + Tool Use + Report Generation + Validation**

---

## Future Improvements

- Add a **revision loop** where the Writer improves the report when the Critic gives a low score.
- Allow the Reader Agent to gather evidence from **multiple high-quality sources**.
- Improve **source quality and reliability scoring**.
- Add better handling for webpages that block automated scraping.
- Add a more interactive research interface.

