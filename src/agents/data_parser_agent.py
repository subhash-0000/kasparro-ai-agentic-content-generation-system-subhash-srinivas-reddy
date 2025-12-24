"""
DataParserAgent - Responsible for parsing raw product data into clean internal models.
Single Responsibility: Data validation and transformation.
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product


class DataParserAgent(BaseAgent):
    """
    Parses raw product data and converts it into validated internal Product model.
    
    Input: Raw product data dictionary
    Output: Validated Product instance
    """
    
    def __init__(self):
        super().__init__(
            agent_id="data_parser_agent",
            description="Parses and validates raw product data into internal model"
        )
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Parse and validate product data.
        
        Args:
            input_data: Contains raw product dictionary
            
        Returns:
            AgentOutput with validated Product instance
        """
        try:
            raw_data = input_data.data
            
            # Transform raw data into Product model format
            product_dict = {
                "name": raw_data.get("product_name"),
                "concentration": raw_data.get("concentration"),
                "skin_types": raw_data.get("skin_type"),  # Will be auto-split
                "key_ingredients": raw_data.get("key_ingredients"),  # Will be auto-split
                "benefits": raw_data.get("benefits"),  # Will be auto-split
                "usage_instructions": raw_data.get("how_to_use"),
                "side_effects": raw_data.get("side_effects"),
                "price": raw_data.get("price")
            }
            
            # Validate using Pydantic model
            product = Product(**product_dict)
            
            return AgentOutput(
                success=True,
                data=product,
                metadata={
                    "agent_id": self.agent_id,
                    "parsed_fields": len(product_dict),
                    "skin_types_count": len(product.skin_types),
                    "ingredients_count": len(product.key_ingredients),
                    "benefits_count": len(product.benefits)
                }
            )
            
        except Exception as e:
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Parsing failed: {str(e)}"]
            )
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate that input contains required product fields."""
        if not isinstance(input_data.data, dict):
            return False
        
        required_fields = ["product_name", "concentration", "skin_type", 
                          "key_ingredients", "benefits", "how_to_use", "price"]
        
        return all(field in input_data.data for field in required_fields)
