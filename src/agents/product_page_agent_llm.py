"""
LLM-powered ProductPageAgent using LangChain and Groq.
Generates product page content using AI.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product
from typing import Dict, Any


class ProductPageAgent(BaseAgent):
    """
    LLM-powered agent that generates complete product page content using AI.
    
    Input: Product
    Output: AI-generated product page data (tagline, description, features, etc.)
    """
    
    def __init__(self, llm: ChatGroq):
        super().__init__(
            agent_id="product_page_agent",
            description="Generates product page content using LLM"
        )
        self.llm = llm
        
        # Define prompt for product page generation
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional skincare copywriter. Generate compelling product page content based on the product details provided.

Product Information:
Name: {product_name}
Concentration: {concentration}
Skin Types: {skin_types}
Ingredients: {ingredients}
Benefits: {benefits}
Usage: {usage}
Side Effects: {side_effects}
Price: {price}

Generate a JSON response with:
{{
  "tagline": "catchy tagline (max 10 words)",
  "description": "compelling 2-3 sentence product description",
  "key_features": ["feature 1", "feature 2", "feature 3", "feature 4"],
  "ingredient_descriptions": {{"Ingredient Name": "1 sentence description"}},
  "usage_highlights": {{
    "timing": "when to use (morning/evening/both)",
    "application_amount": "how much to use",
    "full_instructions": "{usage}",
    "application_order": "when in routine (before/after other products)",
    "frequency": "how often (daily/twice daily/as needed)",
    "tips": "application tips"
  }},
  "precautions": ["precaution 1", "precaution 2", "precaution 3"],
  "suitable_for_sensitive_skin": "yes/no/with caution + brief explanation"
}}

Guidelines:
- Be persuasive but accurate
- Highlight unique selling points
- Use professional skincare language
- Base all content on provided data only
- Generate realistic precautions based on ingredients and side effects
- Provide practical usage guidance

Return ONLY the JSON, no additional text."""),
            ("human", "Generate product page content for {product_name}")
        ])
        
        self.parser = JsonOutputParser()
        self.chain = self.prompt | self.llm | self.parser
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate product page content using LLM.
        
        Args:
            input_data: Product instance
            
        Returns:
            AgentOutput with AI-generated product page data
        """
        try:
            product: Product = input_data.data
            
            self.log(f"Generating product page content for {product.name} using LLM...")
            
            # Prepare prompt data
            prompt_data = {
                "product_name": product.name,
                "concentration": product.concentration,
                "skin_types": ", ".join(product.skin_types),
                "ingredients": ", ".join(product.key_ingredients),
                "benefits": ", ".join(product.benefits),
                "usage": product.usage_instructions,
                "side_effects": product.side_effects or "None reported",
                "price": product.price
            }
            
            # Generate content using LLM
            response = self.chain.invoke(prompt_data)
            
            self.log(f"✓ Generated product page content using Groq LLM")
            
            # Validate LLM output
            if not self._validate_product_content(response):
                self.log("Product content validation failed, using fallback", level="WARNING")
                return self._fallback_product_content(product)
            
            return AgentOutput(
                success=True,
                data=response,
                metadata={
                    "generation_method": "LLM (Groq via LangChain)",
                    "product_name": product.name,
                    "validation_passed": True
                }
            )
            
        except Exception as e:
            self.log(f"Error generating product page: {str(e)}", level="ERROR")
            self.log("Attempting fallback strategy...", level="WARNING")
            return self._fallback_product_content(product)
    
    def _validate_product_content(self, content: dict) -> bool:
        """Validate product content for required fields and quality."""
        required_keys = ["tagline", "description", "key_features", "precautions"]
        if not all(key in content for key in required_keys):
            self.log("Validation failed: Missing required keys", level="WARNING")
            return False
        
        if not content["tagline"] or len(content["tagline"]) < 10:
            self.log("Validation failed: Tagline too short", level="WARNING")
            return False
        
        if not content["description"] or len(content["description"]) < 50:
            self.log("Validation failed: Description too short", level="WARNING")
            return False
        
        if not content["key_features"] or len(content["key_features"]) < 3:
            self.log("Validation failed: Not enough key features", level="WARNING")
            return False
        
        if not content["precautions"] or len(content["precautions"]) < 2:
            self.log("Validation failed: Need at least 2 precautions", level="WARNING")
            return False
        
        self.log("Product content validation passed", level="DEBUG")
        return True
    
    def _fallback_product_content(self, product: Product) -> AgentOutput:
        """Generate fallback product content when LLM fails."""
        self.log("Using fallback product content generation strategy", level="WARNING")
        
        primary_benefit = product.benefits[0] if product.benefits else "skincare"
        primary_ingredient = product.key_ingredients[0] if product.key_ingredients else "active ingredients"
        
        # Generate realistic precautions based on product data
        precautions = [
            "Perform a patch test before first use",
            "Avoid contact with eyes"
        ]
        
        # Add ingredient-specific precautions
        if any("vitamin c" in ing.lower() or "acid" in ing.lower() for ing in product.key_ingredients):
            precautions.append("Use sunscreen during the day when using this product")
        
        if product.side_effects and "sensitive" in product.side_effects.lower():
            precautions.append("May cause tingling for sensitive skin - discontinue if irritation occurs")
        
        fallback_content = {
            "tagline": f"{primary_benefit.title()} with {primary_ingredient}",
            "description": f"{product.name} is a {product.concentration} serum designed for {' and '.join(product.skin_types)} skin. Formulated with {', '.join(product.key_ingredients)}, it delivers {' and '.join(product.benefits).lower()} benefits. {product.usage_instructions}",
            "key_features": [
                f"{product.concentration} formulation",
                f"Suitable for {' & '.join(product.skin_types)} skin",
                f"Contains {', '.join(product.key_ingredients)}",
                f"Provides {len(product.benefits)} key benefits"
            ],
            "ingredient_descriptions": {ing: f"{ing} - Key active ingredient" for ing in product.key_ingredients},
            "usage_highlights": {
                "timing": "morning" if "morning" in product.usage_instructions.lower() else "as directed",
                "application_amount": "as directed",
                "full_instructions": product.usage_instructions,
                "application_order": "after cleansing, before moisturizer",
                "frequency": "daily",
                "tips": product.usage_instructions
            },
            "precautions": precautions,
            "suitable_for_sensitive_skin": "with caution" if (product.side_effects and "sensitive" in product.side_effects.lower()) else "consult dermatologist"
        }
        
        return AgentOutput(
            success=True,
            data=fallback_content,
            metadata={
                "generation_method": "Fallback (Template-based)",
                "product_name": product.name,
                "fallback_used": True
            }
        )
