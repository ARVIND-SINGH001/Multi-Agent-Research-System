from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain




def run_research_pipeline(topic : str) -> dict:
    state = {}

    print("\n"+"-"*50)
    print(f"Research Pipeline Initiated for Topic: {topic}")
    print("-"*50+"\n")
    
    #step 1: Search Agent
    search_agent = build_search_agent()
    search_result = search_agent.invoke(
        {
            "messages" :[("user" , f"Find recent, reliable and detailed information about {topic}")]
        }
    )

    state["search_results"] = search_result["messages"][-1].content
    print("Search Results:\n", state["search_results"] )

    # step 2: Reader Agent
    print("-"*50)
    print("Reader agent scraping the most relevant URLs...\n")

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
    "messages": [
        (
            "user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results']}"
        )
    ]
})

    state["scraped_content"] = reader_result["messages"][-1].content
    print("Scraped Content:\n", state["scraped_content"], "...\n")

    # step 3: Writer chain

    print("-"*50)
    print("Writer chain generating a detailed research report...\n")

    research_combined = (
    f"Search Results:\n{state['search_results']}\n\n"
    f"Detailed Scraped Content:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke(
    {
        "topic": topic,
        "research": research_combined
    }
    )

    print("Research Report Generated:\n", state["report"])

    #critique the report
    print("-"*50)
    print("Critic chain evaluating the research report...\n")

    state["feedback"] = critic_chain.invoke(
    {
        "report": state["report"]
    }
    )

    print("Critique Feedback:\n", state["feedback"])

    return state






if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    run_research_pipeline(topic)


