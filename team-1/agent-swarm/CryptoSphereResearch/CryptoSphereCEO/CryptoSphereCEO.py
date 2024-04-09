from agency_swarm.agents import Agent


class CryptoSphereCEO(Agent):
    def __init__(self):
        super().__init__(
            name="CryptoSphereCEO",
            description="Managing client relations, overseeing operational dynamics, and coordinating between agents for CryptoSphereResearch.",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools"
        )
