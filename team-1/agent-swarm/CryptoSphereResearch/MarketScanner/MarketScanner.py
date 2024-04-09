from agency_swarm.agents import Agent
from agency_swarm.tools import CodeInterpreter

class MarketScanner(Agent):
    def __init__(self):
        super().__init__(
            name="MarketScanner",
            description="Dedicated to gathering real-time data and news on cryptocurrency market activities for CryptoSphereResearch.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[CodeInterpreter],
            tools_folder="./tools"
        )
