from agency_swarm.tools import BaseTool
from pydantic import Field
import os


class DataReadyNotifier(BaseTool):
    """
    A tool to notify the DataCruncher agent that the data collected and processed by MarketScanner is ready for analysis. This tool simulates the SendMessage functionality for direct communication within the Agency Swarm framework. 
    """

    data_cruncher_agent: str = Field(
        ..., description="The identifier of the DataCruncher agent to notify."
    )
    message: str = Field(
        ..., description="The message to be sent, indicating data readiness."
    )

    def run(self):
        # In a real implementation, this method would use the SendMessage tool
        # For simulation, this just returns the message that would be sent
        return f"Notifying {self.data_cruncher_agent} agent: {self.message}"
