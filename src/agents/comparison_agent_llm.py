"""
LLM-powered ComparisonAgent using LangChain and Groq.
Generates fictional competitor and performs intelligent comparison.
"""

import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product


class ComparisonAgentLLM(BaseAgent):
    """
    LLM-powered agent that creates fictional competitors and performs comparisons.
    
    Input: Product instance
    Output: Fictional competitor + comparison analysis
    """
    
    def __init__(self, llm: ChatGroq):
        super().__init__(
            agent_id="comparison_agent_llm",
            description="Generates competitor product and comparison using LLM"
        )
        self.llm = llm
        
        # Single combined prompt for competitor + comparison (1 API call instead of 2)
        self.combined_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert skincare product analyst with deep knowledge of cosmetic formulations, market positioning, and consumer needs.

Your task: Generate a realistic fictional competing product AND a comprehensive comparison analysis in ONE response.

COMPETITOR REQUIREMENTS:
- Create a believable competitor in the same category (Vitamin C serums)
- Different but professional brand name (not too similar to original)
- Comparable but distinct formulation (different concentration, additional actives)
- Realistic price point (₹500-₹1200 range for skincare serums)
- 2-4 overlapping skin types but potentially broader/narrower target
- 3-5 key ingredients (must include active ingredient, can add complementary actives)
- 2-4 realistic benefits (overlapping but with unique angles)

COMPARISON REQUIREMENTS:
Generate exactly 7 detailed comparison points covering:
1. **Price & Value** - Compare pricing and value proposition
2. **Active Ingredient Concentration** - Compare % strength and efficacy potential
3. **Ingredient Complexity** - Number and variety of key ingredients
4. **Targeted Skin Types** - Breadth of skin type compatibility
5. **Claimed Benefits** - Range and specificity of benefits
6. **Usage Convenience** - Based on application method and frequency
7. **Overall Market Positioning** - Premium vs affordable, clinical vs natural, etc.

For each comparison point:
- Provide specific values for both products
- Declare a clear winner (or "Tie" if truly equal)
- Base winner on objective criteria (more benefits = winner, lower price = winner, etc.)

SUMMARY REQUIREMENTS:
- Identify overall winner based on majority of comparison points
- Provide 1-2 sentence summary of key differentiators

RECOMMENDATION:
- Give practical one-sentence recommendation for which product to choose
- Base it on use case (e.g., "Choose A for budget", "Choose B for potency")

Return ONLY this exact JSON structure (no markdown, no extra text):
{{
  "competitor": {{
    "name": "Competitor product name",
    "concentration": "X% Active Ingredient Name",
    "skin_types": ["Type1", "Type2"],
    "key_ingredients": ["Ingredient1", "Ingredient2", "Ingredient3"],
    "benefits": ["Benefit1", "Benefit2", "Benefit3"],
    "price": "₹XXX"
  }},
  "comparison_points": [
    {{"attribute": "Price & Value", "product_a": "value", "product_b": "value", "winner": "Product Name"}},
    {{"attribute": "Active Ingredient Concentration", "product_a": "value", "product_b": "value", "winner": "Product Name"}},
    {{"attribute": "Ingredient Complexity", "product_a": "value", "product_b": "value", "winner": "Product Name"}},
    {{"attribute": "Targeted Skin Types", "product_a": "value", "product_b": "value", "winner": "Product Name"}},
    {{"attribute": "Claimed Benefits", "product_a": "value", "product_b": "value", "winner": "Product Name"}},
    {{"attribute": "Usage Convenience", "product_a": "value", "product_b": "value", "winner": "Product Name"}},
    {{"attribute": "Overall Market Positioning", "product_a": "value", "product_b": "value", "winner": "Product Name"}}
  ],
  "summary": {{
    "winner": "Product Name that wins most comparison points",
    "key_differences": "1-2 sentence summary of main differentiators between the products"
  }},
  "recommendation": "One clear sentence recommending which product to choose and for what use case or consumer profile"
}}

Original Product to Compare Against:
Name: {product_name}
Concentration: {concentration}
Price: {price}
Skin Types: {skin_types}
Key Ingredients: {ingredients}
Benefits: {benefits}"""),
            ("human", "Generate a realistic competitor and comprehensive 7-point comparison. Return pure JSON only.")
        ])
        
        self.combined_chain = self.combined_prompt | self.llm | JsonOutputParser()
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate fictional competitor and comparison using LLM.
        
        Args:
            input_data: Contains Product instance
            
        Returns:
            AgentOutput with competitor data and comparison points
        """
        try:
            product_a: Product = input_data.data
            
            # Single API call: Generate competitor + comparison together
            self.log(f"Generating competitor + comparison for {product_a.name}...")
            combined_data = {
                "product_name": product_a.name,
                "concentration": product_a.concentration,
                "price": product_a.price,
                "skin_types": ", ".join(product_a.skin_types),
                "ingredients": ", ".join(product_a.key_ingredients),
                "benefits": ", ".join(product_a.benefits)
            }
            
            # Single API call for both competitor and comparison
            response = self.combined_chain.invoke(combined_data)
            product_b_raw = response["competitor"]
            
            # Build result
            result = {
                "product_a": {
                    "name": product_a.name,
                    "concentration": product_a.concentration,
                    "skin_types": product_a.skin_types,
                    "key_ingredients": product_a.key_ingredients,
                    "benefits": product_a.benefits,
                    "price": product_a.price
                },
                "product_b": product_b_raw,
                "comparison_points": response["comparison_points"],
                "summary": response["summary"],
                "recommendation": response["recommendation"]
            }
            
            self.log(f"✓ Generated competitor: {product_b_raw['name']}")
            self.log(f"✓ Generated {len(response['comparison_points'])} comparison points in 1 API call")
            
            return AgentOutput(
                success=True,
                data=result,
                metadata={
                    "competitor_name": product_b_raw["name"],
                    "comparison_dimensions": len(response["comparison_points"]),
                    "generation_method": "LLM (OpenAI via LangChain)",
                    "api_calls": 1
                }
            )
            
        except Exception as e:
            self.log(f"Error in comparison generation: {str(e)}", level="ERROR")
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Comparison generation failed: {str(e)}"]
            )
