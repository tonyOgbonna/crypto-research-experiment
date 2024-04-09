from agency_swarm.agents import Agent
from agency_swarm.tools import CodeInterpreter

class ReportAssembler(Agent):
    def __init__(self):
        super().__init__(
            name="ReportAssembler",
            description="Assembles the analyzed data into structured reports in the prescribed format focusing on clarity and comprehensive coverage for CryptoSphereResearch.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[CodeInterpreter],
            tools_folder="./tools"
        )
