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
            
            # Validate LLM output
            if not self._validate_comparison(result):
                self.log("Comparison validation failed, using fallback", level="WARNING")
                return self._fallback_comparison(product_a)
            
            return AgentOutput(
                success=True,
                data=result,
                metadata={
                    "competitor_name": product_b_raw["name"],
                    "comparison_dimensions": len(response["comparison_points"]),
                    "generation_method": "LLM (Groq via LangChain)",
                    "api_calls": 1,
                    "validation_passed": True
                }
            )
            
        except Exception as e:
            self.log(f"Error in comparison generation: {str(e)}", level="ERROR")
            self.log("Attempting fallback strategy...", level="WARNING")
            return self._fallback_comparison(product_a)
    
    def _validate_comparison(self, result: dict) -> bool:
        """Validate comparison output for completeness."""
        required_keys = ["product_a", "product_b", "comparison_points", "summary", "recommendation"]
        if not all(key in result for key in required_keys):
            self.log("Validation failed: Missing required keys", level="WARNING")
            return False
        
        if not result["comparison_points"] or len(result["comparison_points"]) < 5:
            self.log(f"Validation failed: Only {len(result.get('comparison_points', []))} comparison points (minimum 5)", level="WARNING")
            return False
        
        if not result["product_b"].get("name"):
            self.log("Validation failed: Missing competitor name", level="WARNING")
            return False
        
        self.log("Comparison validation passed", level="DEBUG")
        return True
    
    def _fallback_comparison(self, product_a: Product) -> AgentOutput:
        """Generate fallback comparison when LLM fails."""
        self.log("Using fallback comparison generation strategy", level="WARNING")
        
        # Generate fictional competitor
        product_b = {
            "name": f"Alternative {product_a.name.split()[0]} Serum",
            "concentration": f"{float(product_a.concentration.split('%')[0]) * 1.2 if '%' in product_a.concentration else '15'}% Active",
            "skin_types": ["All Skin Types"],
            "key_ingredients": ["Vitamin E", "Hyaluronic Acid", "Peptides"],
            "benefits": ["Hydration", "Anti-aging", "Brightening"],
            "price": "₹999"
        }
        
        result = {
            "product_a": {
                "name": product_a.name,
                "concentration": product_a.concentration,
                "skin_types": product_a.skin_types,
                "key_ingredients": product_a.key_ingredients,
                "benefits": product_a.benefits,
                "price": product_a.price
            },
            "product_b": product_b,
            "comparison_points": [
                {"attribute": "Price", "product_a": product_a.price, "product_b": product_b["price"], "winner": product_a.name},
                {"attribute": "Concentration", "product_a": product_a.concentration, "product_b": product_b["concentration"], "winner": "Comparable"},
                {"attribute": "Ingredients", "product_a": f"{len(product_a.key_ingredients)} actives", "product_b": f"{len(product_b['key_ingredients'])} actives", "winner": "Comparable"},
                {"attribute": "Skin Types", "product_a": ", ".join(product_a.skin_types), "product_b": ", ".join(product_b["skin_types"]), "winner": product_b["name"]},
                {"attribute": "Benefits", "product_a": f"{len(product_a.benefits)} benefits", "product_b": f"{len(product_b['benefits'])} benefits", "winner": "Comparable"},
            ],
            "summary": {
                "winner": product_a.name,
                "key_differences": f"{product_a.name} offers targeted formulation while {product_b['name']} provides broader compatibility."
            },
            "recommendation": f"Choose {product_a.name} for specialized skincare needs, or {product_b['name']} for versatile daily use."
        }
        
        return AgentOutput(
            success=True,
            data=result,
            metadata={
                "competitor_name": product_b["name"],
                "comparison_dimensions": len(result["comparison_points"]),
                "generation_method": "Fallback (Template-based)",
                "fallback_used": True
            }
        )
