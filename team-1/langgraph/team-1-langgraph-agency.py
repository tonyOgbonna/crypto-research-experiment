# Minimal implementation: Proof of concept. Not exactly according to spec but good enough for testing.
import os
from dotenv import load_dotenv

## 1. Enviromnent Setup
load_dotenv()

## 2. Create Tools
"""Each team will be composed of one or more agents each with one or more tools. 
Below, define all the tools to be used by your different teams.
"""
### 2.1 Research team tools
"""The research team can use a search engine and url scraper to find information on the web. 
Feel free to add additional functionality below to boost the team performance!"""
from typing import Annotated, List, Tuple, Union

import matplotlib.pyplot as plt
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langsmith import trace
from langchain_community.chat_models import ChatOllama
from langchain_experimental.llms.ollama_functions import OllamaFunctions

tavily_tool = TavilySearchResults(max_results=5)

@tool
def scrape_webpages(urls: List[str]) -> str:
    """Use requests and bs4 to scrape the provided web pages for detailed information."""
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
    )

### 2.2 Document writing team tools
"""Next up, we will give some tools for the doc writing team to use.
We define some bare-bones file-access tools below.

Note that this gives the agents access to your file-system, which can be unsafe. 
We also haven't optimized the tool descriptions for performance."""
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional

from langchain_experimental.utilities import PythonREPL
from typing_extensions import TypedDict

script_dir = os.path.dirname(os.path.abspath(__file__))
WORKING_DIRECTORY = os.path.join(script_dir, 'workspace')

@tool
def create_outline(
    points: Annotated[List[str], "List of main points or sections."],
    file_name: Annotated[str, "File path to save the outline."],
) -> Annotated[str, "Path of the saved outline file."]:
    """Create and save an outline."""
    full_path = os.path.join(WORKING_DIRECTORY, file_name)
    with open(full_path, "w") as file:
        for i, point in enumerate(points):
            file.write(f"{i + 1}. {point}\n")
    return f"Outline saved to {file_name}"

@tool
def read_document(
    file_name: Annotated[str, "File path to save the document."],
    start: Annotated[Optional[int], "The start line. Default is 0"] = None,
    end: Annotated[Optional[int], "The end line. Default is None"] = None,
) -> str:
    """Read the specified document."""
    full_path = os.path.join(WORKING_DIRECTORY, file_name)
    with open(full_path, "r") as file:
        lines = file.readlines()
    if start is not None:
        start = 0
    return "\n".join(lines[start:end])

@tool
def write_document(
    content: Annotated[str, "Text content to be written into the document."],
    file_name: Annotated[str, "File path to save the document."],
) -> Annotated[str, "Path of the saved document file."]:
    """Create and save a text document."""
    full_path = os.path.join(WORKING_DIRECTORY, file_name)
    with open(full_path, "w") as file:
        file.write(content)
    return f"Document saved to {file_name}"

@tool
def edit_document(
    file_name: Annotated[str, "Path of the document to be edited."],
    inserts: Annotated[
        Dict[int, str],
        "Dictionary where key is the line number (1-indexed) and value is the text to be inserted at that line.",
    ],
) -> Annotated[str, "Path of the edited document file."]:
    """Edit a document by inserting text at specific line numbers."""
    full_path = os.path.join(WORKING_DIRECTORY, file_name)
    with open(full_path, "r") as file:
        lines = file.readlines()

    sorted_inserts = sorted(inserts.items())

    for line_number, text in sorted_inserts:
        if 1 <= line_number <= len(lines) + 1:
            lines.insert(line_number - 1, text + "\n")
        else:
            return f"Error: Line number {line_number} is out of range."

    with open(full_path, "w") as file:
        file.writelines(lines)

    return f"Document edited and saved to {file_name}"

# Warning: This executes code locally, which can be unsafe when not sandboxed

repl = PythonREPL()

@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."]
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Succesfully executed:\n```python\n{code}\n```\nStdout: {result}"

## 3. Helper Utilites
"""We are going to create a few utility functions to make it more concise when we want to:

1. Create a worker agent.
2. Create a supervisor for the sub-graph.

These will simplify the graph compositional code at the end for us so it's easier to see what's going on."""
from typing import Any, Callable, List, Optional, TypedDict, Union

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from langgraph.graph import END, StateGraph

def create_agent(
    # llm: ChatOpenAI,
    llm: OllamaFunctions(model="mistral"),
    tools: list,
    system_prompt: str,
) -> str:
    """Create a function-calling agent and add it to the graph."""
    system_prompt += "\nWork autonomously according to your specialty, using the tools available to you."
    " Do not ask for clarification."
    " Your other team members (and other teams) will collaborate with you with their own specialties."
    " You are chosen for a reason! You are one of the following team members: {team_members}."
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}

def create_team_supervisor(llm: ChatOpenAI, system_prompt, members) -> str:
    """An LLM-based router."""
    options = ["FINISH"] + members
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                },
            },
            "required": ["next"],
        },
    }
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), team_members=", ".join(members))
    return (
        prompt
        | llm.bind_functions(functions=[function_def], function_call="route")
        | JsonOutputFunctionsParser()
    )

## 4. Define Agent Teams
"""Now we can get to define our hierachical teams. "Choose your player!"
"""
### 4.1 Research Team
"""The research team will have a search agent and a web scraping "research_agent" as the two worker nodes. 
Let's create those, as well as the team supervisor."""
import functools
import operator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai.chat_models import ChatOpenAI
import functools

# Research team graph state
class ResearchTeamState(TypedDict):
    # A message is added after each team member finishes
    messages: Annotated[List[BaseMessage], operator.add]
    # The team members are tracked so they are aware of
    # the others' skill-sets
    team_members: List[str]
    # Used to route work. The supervisor calls a function
    # that will update this every time it makes a decision
    next: str


# llm = ChatOpenAI(model="gpt-4-1106-preview")
llm = ChatOpenAI(model="gpt-4-0125-preview")
# llm = ChatOllama(model="llama2")
# llm = OllamaFunctions(model="mistral")

search_agent = create_agent(
    llm,
    [tavily_tool],
    "You are a research assistant who can search for up-to-date info using the tavily search engine.",
)
search_node = functools.partial(agent_node, agent=search_agent, name="Search")

research_agent = create_agent(
    llm,
    [scrape_webpages],
    "You are a research assistant who can scrape specified urls for more detailed information using the scrape_webpages function.",
)
research_node = functools.partial(agent_node, agent=research_agent, name="WebScraper")

supervisor_agent = create_team_supervisor(
    llm,
    "You are a supervisor tasked with managing a conversation between the"
    " following workers:  Search, WebScraper. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH.",
    ["Search", "WebScraper"],
)
#### 4.1.1
"""Now that we've created the necessary components, defining their interactions is easy. 
Add the nodes to the team graph, and define the edges, which determine the transition criteria."""
research_graph = StateGraph(ResearchTeamState)
research_graph.add_node("Search", search_node)
research_graph.add_node("WebScraper", research_node)
research_graph.add_node("supervisor", supervisor_agent)

# Define the control flow
research_graph.add_edge("Search", "supervisor")
research_graph.add_edge("WebScraper", "supervisor")
research_graph.add_conditional_edges(
    "supervisor",
    lambda x: x["next"],
    {"Search": "Search", "WebScraper": "WebScraper", "FINISH": END},
)

research_graph.set_entry_point("supervisor")
chain = research_graph.compile()

# The following functions interoperate between the top level graph state
# and the state of the research sub-graph
# this makes it so that the states of each graph don't get intermixed
def enter_chain(message: str):
    results = {
        "messages": [HumanMessage(content=message)],
    }
    return results

research_chain = enter_chain | chain
"""We can give this team work directly. Try it out below."""
"""for s in research_chain.stream(
    "when is Taylor Swift's next tour?", {"recursion_limit": 100}
):
    if "__end__" not in s:
        print(s)
        print("---")
"""
### 4.2 Document Writing Team
"""Create the document writing team below using a similar approach. 
This time, we will give each agent access to different file-writing tools.

Note that we are giving file-system access to our agent here, which is not safe in all cases."""
import operator
from pathlib import Path

# Document writing team graph state
class DocWritingState(TypedDict):
    # This tracks the team's conversation internally
    messages: Annotated[List[BaseMessage], operator.add]
    # This provides each worker with context on the others' skill sets
    team_members: str
    # This is how the supervisor tells langgraph who to work next
    next: str
    # This tracks the shared directory state
    current_files: str

# This will be run before each worker agent begins work
# It makes it so they are more aware of the current state
# of the working directory.
def prelude(state):
    written_files = []
    if not os.path.exists(WORKING_DIRECTORY):
        os.mkdir(WORKING_DIRECTORY)
    try:
        written_files = [
            f for f in Path(WORKING_DIRECTORY).rglob("*")
        ]
    except:
        pass
    if not written_files:
        return {**state, "current_files": "No files written."}
    return {
        **state,
        "current_files": "\nBelow are files your team has written to the directory:\n"
        + "\n".join([f" - {f}" for f in written_files]),
    }

llm = ChatOpenAI(model="gpt-4-0125-preview")
# llm = ChatOllama(model="llama2")
# llm = OllamaFunctions(model="mistral")

doc_writer_agent = create_agent(
    llm,
    [write_document, edit_document, read_document],
    "You are an expert writing a research document.\n"
    # The {current_files} value is populated automatically by the graph state
    "Below are files currently in your directory:\n{current_files}",
)
# Injects current directory working state before each call
context_aware_doc_writer_agent = prelude | doc_writer_agent
doc_writing_node = functools.partial(
    agent_node, agent=context_aware_doc_writer_agent, name="DocWriter"
)

note_taking_agent = create_agent(
    llm,
    [create_outline, read_document],
    "You are an expert senior researcher tasked with writing a paper outline and"
    " taking notes to craft a perfect paper.{current_files}",
)
context_aware_note_taking_agent = prelude | note_taking_agent
note_taking_node = functools.partial(
    agent_node, agent=context_aware_note_taking_agent, name="NoteTaker"
)

chart_generating_agent = create_agent(
    llm,
    [read_document, python_repl],
    "You are a data viz expert tasked with generating charts for a research project."
    "{current_files}",
)
context_aware_chart_generating_agent = prelude | chart_generating_agent
chart_generating_node = functools.partial(
    agent_node, agent=context_aware_note_taking_agent, name="ChartGenerator"
)

doc_writing_supervisor = create_team_supervisor(
    llm,
    "You are a supervisor tasked with managing a conversation between the"
    " following workers:  {team_members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH.",
    ["DocWriter", "NoteTaker", "ChartGenerator"],
)

"""With the objects themselves created, we can form the graph."""
# Create the graph here:
# Note that we have unrolled the loop for the sake of this doc
authoring_graph = StateGraph(DocWritingState)
authoring_graph.add_node("DocWriter", doc_writing_node)
authoring_graph.add_node("NoteTaker", note_taking_node)
authoring_graph.add_node("ChartGenerator", chart_generating_node)
authoring_graph.add_node("supervisor", doc_writing_supervisor)

# Add the edges that always occur
authoring_graph.add_edge("DocWriter", "supervisor")
authoring_graph.add_edge("NoteTaker", "supervisor")
authoring_graph.add_edge("ChartGenerator", "supervisor")

# Add the edges where routing applies
authoring_graph.add_conditional_edges(
    "supervisor",
    lambda x: x["next"],
    {
        "DocWriter": "DocWriter",
        "NoteTaker": "NoteTaker",
        "ChartGenerator": "ChartGenerator",
        "FINISH": END,
    },
)

authoring_graph.set_entry_point("supervisor")
chain = research_graph.compile()

# The following functions interoperate between the top level graph state
# and the state of the research sub-graph
# this makes it so that the states of each graph don't get intermixed
def enter_chain(message: str, members: List[str]):
    results = {
        "messages": [HumanMessage(content=message)],
        "team_members": ", ".join(members),
    }
    return results

# We re-use the enter/exit functions to wrap the graph
authoring_chain = (
    functools.partial(enter_chain, members=authoring_graph.nodes)
    | authoring_graph.compile()
)
"""Intermediate testing the graph"""
"""for s in authoring_chain.stream(
    "Write an outline for poem and then write the poem to disk.",
    {"recursion_limit": 100},
):
    if "__end__" not in s:
        print(s)
        print("---")
"""

## 5. Add Layers
"""In this design, we are enforcing a top-down planning policy. 
We've created two graphs already, but we have to decide how to route work between the two.

We'll create a _third_ graph to orchestrate the previous two, and add some connectors 
to define how this top-level state is shared between the different graphs."""
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4-0125-preview")
# llm = ChatOllama(model="llama2")
# llm = OllamaFunctions(model="mistral")

supervisor_node = create_team_supervisor(
    llm,
    "You are a supervisor tasked with managing a conversation between the"
    " following teams: {team_members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH.",
    ["Research team", "Paper writing team"],
)

# Top-level graph state
class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: str

def get_last_message(state: State) -> str:
    return state["messages"][-1].content

def join_graph(response: dict):
    return {"messages": [response["messages"][-1]]}

# Define the graph.
super_graph = StateGraph(State)
# First add the nodes, which will do the work
super_graph.add_node("Research team", get_last_message | research_chain | join_graph)
super_graph.add_node(
    "Paper writing team", get_last_message | authoring_chain | join_graph
)
super_graph.add_node("supervisor", supervisor_node)

# Define the graph connections, which controls how the logic
# propagates through the program
super_graph.add_edge("Research team", "supervisor")
super_graph.add_edge("Paper writing team", "supervisor")
super_graph.add_conditional_edges(
    "supervisor",
    lambda x: x["next"],
    {
        "Paper writing team": "Paper writing team",
        "Research team": "Research team",
        "FINISH": END,
    },
)
super_graph.set_entry_point("supervisor")
super_graph = super_graph.compile()

## 6. Invoke the Graph
"""We can now invoke the graph!"""

crypto_report_template = """# Crypto Market Activity Report - [Date]

**Prepared by:** [Your Name]
## I. Market Overview
- **Total Market Cap:** [Current Total Market Cap] (USD) - [Change from Yesterday]
- **Top Gainers:** List top 3 gainers with % change and brief explanation (e.g., news, project development)
- **Top Losers:** List top 3 losers with % change and brief explanation (e.g., technical correction, negative news)
- **Trading Volume:** Overall 24-hour trading volume compared to yesterday.
## II. Technical Analysis
- **Bitcoin (BTC):** Briefly discuss current price action, dominant trend (upward/downward), key support/resistance levels, and any relevant indicators (e.g., RSI, MACD).
- **Etherium (ETH):** Briefly discuss current price action, dominant trend (upward/downward), key support/resistance levels, and any relevant indicators (e.g., RSI, MACD).
- **Solana (SOL):** Briefly discuss current price action, dominant trend (upward/downward), key support/resistance levels, and any relevant indicators (e.g., RSI, MACD).
## III. Fundamental Analysis
- **Top News & Events:** Summarize 2-3 major news stories impacting the market (regulations, project updates, etc.).
## IV. Investment Opportunities
- **Emerging Projects:** Briefly highlight 1-2 promising new projects with strong fundamentals and potential for growth.
- **Staking & DeFi:** If relevant, discuss potential staking opportunities or DeFi protocols offering passive income.
## V. Risk Management
- **Market Volatility:** Assess current market volatility and potential risks based on technical and fundamental factors.
## VI. Social Media Sentiment
- **Trending Topics:** Highlight key trending topics within the crypto community (e.g., on Twitter) that might impact the market.
- **Community Sentiment:** Summarize the overall sentiment (bullish/bearish) within the crypto community.
## VII. Actionable Insights
- **Trading Ideas:** Based on your analysis, provide 1-2 actionable trading ideas (e.g., potential entry/exit points for specific crypto of current interest).
- **Investment Recommendations:** Offer 1-2 long-term investment recommendations based on fundamental analysis and potential for growth.
## VIII. Disclaimer
- Include a disclaimer stating that this report is for informational purposes only and does not constitute financial advice.
## IX. Conclusion
- Provide a brief conclusion of the report.
## X. References
- Include any relevant references or sources of the information or data used in the report.
"""
for s in super_graph.stream(
    {
        "messages": [
            HumanMessage(
                content=f"Do a brief daily up-to-date (April 09, 2024) Cryptocurrency analysis research, and write a report according to the following template: {crypto_report_template}. Include relevant charts. It is important that you do not make stuff up. Use only factual information, for the date given.",
            )
        ],
    },
    {"recursion_limit": 250},
):
    if "__end__" not in s:
        print(s)
        print("---")
