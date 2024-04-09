from agency_swarm.agents import Agent
from agency_swarm.tools import CodeInterpreter

class DataCruncher(Agent):
    def __init__(self):
        super().__init__(
            name="DataCruncher",
            description="Analyzing the data collected by the MarketScanner for CryptoSphereResearch. Performs technical and market trend analyses, focusing on volume changes, price movements, and sentiment analysis.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[CodeInterpreter],
            tools_folder="./tools"
        )
