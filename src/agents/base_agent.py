"""
Base agent class defining the contract for all agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging
import os
from datetime import datetime
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
        
        # Setup structured logging
        self._setup_logging()
    
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
    
    def _setup_logging(self):
        """Setup structured logging with file and console handlers."""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger for this agent
        self.logger = logging.getLogger(self.agent_id)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # File handler with rotation support
            log_file = os.path.join(log_dir, f"{self.agent_id}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Structured format with timestamp
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
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
        self.logger.info(f"Execution #{self.execution_count}")
        self.logger.info(f"  Success: {output.success}")
        if output.errors:
            self.logger.error(f"  Errors: {output.errors}")
    
    def log(self, message: str, level: str = "INFO"):
        """
        Log a message with agent context.
        
        Args:
            message: Message to log
            level: Log level (INFO, ERROR, WARNING, DEBUG)
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
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
