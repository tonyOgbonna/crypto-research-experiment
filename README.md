# crypto-research-experiment
Crypto Research: A learning experiment on AI Agent Swarm implementation and AI frameworks evaluation.

Under the hood this is an organised **experimentation, learning and mastery journey** into the worlds of AI development, AI autonomy, AI agent swarm, AI application development frameworks, Python programming, among other things.

Hence there is not a certain destination to this project: the journey is the goal. The choice of Crypto Research here is arbitrary. Cryptocurrency just happens to be one of my many fields of curiosity and interest. And I just decided 'why not?'. Crypto Research is just the 'vehicle' with which I choose to embark on this journey with. Any other 'vehicle' would have served all the same.

So whether anything concrete comes out of this project is of secondary importance: the journey is the goal.

**Note:** I am not an expert in any of this. This is just a crucial part of my journey from beginner towards expertise in all of it.
## Experiment Design
1 Goal. 3 Teams (agencies). 4 Frameworks. 12 Implementations
### Goal
Cryptocurrency Intelligence (Daily) Reporting: A Cryptocurrency research, analysis and report creation agency powered by autonomous AI agent swarm.
### Teams
There are three independent (AI) agencies (agent swarm teams), each tasked with the same goal. The difference is that each agency is defined and designed using three different popular LLM Models: Google's Gemini Chatbot, OpenAI's GPT-4 Chatbot and ChatGPT 3.5.

Apart from the common goal and using exactly the same prompts with the different Models, the teams compositions, specifications and dynamics where defined and designed differently by their respective LLM Models.

Each team's overlord LLM was tasked with the following through direct prompting:
1. **Daily Practices - Skills, Workflows & Resources:** As a crypto expert, actively involved in cryptocurrency trading, investing and staying ahead of your game, describe your daily practices in terms of skills, workflows & resources.
2. **Report Template:** Assume that you run an agency that creates daily crypto reports for clients, what will your reporting template look like.
3. **Key Questions for Customised Insights:** What key questions would you ask each of your client to enable you effectively research, analyze and create a customized report for each client?
4. **Roles and Responsibilities:** Assume that your agency is composed of a team, what are the necessary roles and responsibilities for handling the different sections of the standard reporting template you use across each client?
5. **Role's Resources, Tools and Workflows:** Define and describe each of the role's resources, tools and workflows necessary to execute on their tasks.
6. **Team Workflow and dynamics:** Define and describe the overall team workflow and dynamics towards the ultimate goal of creating an excellent report for a client.

From the responses to the above queries by each LLM, a distinct team to be tasked with the ultimate goal of this experiment will be created, comprising, but not limited to, the team's compositions, specifications and dynamics.

From this LLM Chatbots prompting exercise, it was interesting to note that each LLM model approached the goal differently. I can't wait to compare and contract the intermediate and end results of each models unique approach.

See the README file in each of the team folders for specific details on each team specifications.
#### Team 1: Gemini
Defined and designed using Google's Gemini Chatbot.
#### Team 2: GPT-4
Defined and designed using OpenAI's GPT-4 Chatbot.
#### Team 3: GPT-3.5
Defined and designed using OpenAI's ChatGPT 3.5.
### Frameworks
Each team's agent swarm is implemented using four different open-source LLM applications development frameworks of interest that has agentic functionality, making a total of 12 implementations.

Each implementation is completely isolated and is used independently. 

Along the way and, perhaps, in the end I intend to observe, evaluate and compare the strengths and shortcomings of each of the frameworks.
#### Agent Swarm
##### Introduction
An opensource agent orchestration framework built on top of the latest OpenAI Assistants API.

Agency Swarm started as a desire and effort of Arsenii Shatokhin (aka VRSEN) to fully automate his AI Agency with AI. By building this framework, we aim to simplify the agent creation process and enable anyone to create collaborative swarm of agents (Agencies), each with distinct roles and capabilities. By thinking about automation in terms of real world entities, such as agencies and specialized agent roles, we make it a lot more intuitive for both the agents and the users.
- https://vrsen.github.io/agency-swarm/
- https://github.com/VRSEN/agency-swarm
#### AutoGen
##### Introduction
**Multi-Agent Conversation Framework**
AutoGen is a framework that enables development of LLM applications using multiple agents that can converse with each other to solve tasks. AutoGen agents are customizable, conversable, and seamlessly allow human participation. They can operate in various modes that employ combinations of LLMs, human inputs, and tools.
- https://microsoft.github.io/autogen/
- https://github.com/microsoft/autogen
#### CrewAI
##### Introduction
 Framework for orchestrating role-playing, autonomous AI agents. By fostering collaborative intelligence, CrewAI empowers agents to work together seamlessly, tackling complex tasks.
- https://www.crewai.io/
- https://github.com/joaomdmoura/crewai
#### LangChain / LangGraph
##### Introduction
LangGraph is a library for building stateful, multi-actor applications with LLMs, built on top of (and intended to be used with) LangChain. It extends the LangChain Expression Language with the ability to coordinate multiple chains (or actors) across multiple steps of computation in a cyclic manner.

The main use is for adding cycles to your LLM application. Crucially, LangGraph is NOT optimized for only DAG workflows. If you want to build a DAG, you should just use LangChain Expression Language.

Cycles are important for agent-like behaviors, where you call an LLM in a loop, asking it what action to take next.
- https://python.langchain.com/docs/langgraph
- https://blog.langchain.dev/langgraph/
- https://blog.langchain.dev/langgraph-multi-agent-workflows/
- https://github.com/langchain-ai/langgraph/tree/main?ref=blog.langchain.dev
### Implementations
#### Team 1: Gemini
- 1. Agent Swarm
- 2. AutoGen
- 3. CrewAI
- 4. LangGraph
#### Team 2: GPT-4
- 5. Agent Swarm
- 6. AutoGen
- 7. CrewAI
- 8. LangGraph
#### Team 3: GPT-3.5
- 9. Agent Swarm
- 10. AutoGen
- 11. CrewAI
- 12. LangGraph
