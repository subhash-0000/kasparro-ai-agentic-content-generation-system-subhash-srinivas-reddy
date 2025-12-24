"""
Base agent class defining the contract for all agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class AgentInput(BaseModel):
    """Standard input wrapper for agents."""
    data: Any
    context: Dict[str, Any] = {}


class AgentOutput(BaseModel):
    """Standard output wrapper for agents."""
    success: bool
    data: Any
    metadata: Dict[str, Any] = {}
    errors: list = []


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Each agent has a single responsibility and defined I/O contract.
    """
    
    def __init__(self, agent_id: str, description: str):
        """
        Initialize agent with identity.
        
        Args:
            agent_id: Unique identifier for this agent
            description: What this agent does
        """
        self.agent_id = agent_id
        self.description = description
        self.execution_count = 0
    
    @abstractmethod
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Main execution method. Must be implemented by all agents.
        
        Args:
            input_data: Standardized input wrapper
            
        Returns:
            AgentOutput: Standardized output wrapper
        """
        pass
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """
        Validate input before execution.
        
        Args:
            input_data: Input to validate
            
        Returns:
            bool: Whether input is valid
        """
        return True
    
    def log_execution(self, input_data: AgentInput, output: AgentOutput):
        """
        Log execution details for debugging and monitoring.
        
        Args:
            input_data: Input that was processed
            output: Output that was generated
        """
        self.execution_count += 1
        print(f"[{self.agent_id}] Execution #{self.execution_count}")
        print(f"  Success: {output.success}")
        if output.errors:
            print(f"  Errors: {output.errors}")
    
    def __call__(self, input_data: AgentInput) -> AgentOutput:
        """
        Allow agent to be called as a function.
        Handles validation and logging automatically.
        
        Args:
            input_data: Input to process
            
        Returns:
            AgentOutput: Processing result
        """
        if not self.validate_input(input_data):
            return AgentOutput(
                success=False,
                data=None,
                errors=["Input validation failed"]
            )
        
        output = self.execute(input_data)
        self.log_execution(input_data, output)
        return output
