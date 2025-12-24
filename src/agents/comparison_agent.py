"""
ComparisonAgent - Generates fictional competing product and performs comparisons.
Single Responsibility: Create comparison data between products.
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product
from src.logic_blocks.content_blocks import ContentLogicBlocks


class ComparisonAgent(BaseAgent):
    """
    Generates a fictional competing product and creates detailed comparison.
    
    Input: Product instance (Product A)
    Output: Dict with Product A, Product B, and comparison data
    """
    
    def __init__(self):
        super().__init__(
            agent_id="comparison_agent",
            description="Generates fictional competitor and performs product comparison"
        )
        self.content_blocks = ContentLogicBlocks()
    
    def _generate_fictional_product_b(self, product_a: Product) -> Product:
        """
        Generate a fictional competing product based on Product A.
        
        Args:
            product_a: Original product for reference
            
        Returns:
            Fictional Product B instance
        """
        # Create fictional competing product with different attributes
        product_b_data = {
            "name": "RadiantGlow C+ Serum",
            "concentration": "15% Vitamin C",
            "skin_types": ["Normal", "Dry"],
            "key_ingredients": ["Vitamin C", "Vitamin E", "Ferulic Acid"],
            "benefits": ["Anti-aging", "Brightening", "Firming"],
            "usage_instructions": "Apply 3-4 drops in the evening after cleansing",
            "side_effects": "May cause slight redness initially",
            "price": "₹899"
        }
        
        return Product(**product_b_data)
    
    def _create_comparison_points(self, product_a: Product, product_b: Product) -> list:
        """
        Create detailed comparison points between products.
        
        Args:
            product_a: First product
            product_b: Second product
            
        Returns:
            List of comparison items
        """
        from src.models.outputs import ComparisonItem
        
        comparison_points = []
        
        # Price comparison
        import re
        price_a = int(re.search(r'\d+', product_a.price).group()) if re.search(r'\d+', product_a.price) else 0
        price_b = int(re.search(r'\d+', product_b.price).group()) if re.search(r'\d+', product_b.price) else 0
        
        comparison_points.append(ComparisonItem(
            attribute="Price",
            product_a=product_a.price,
            product_b=product_b.price,
            winner=product_a.name if price_a < price_b else product_b.name
        ))
        
        # Concentration comparison
        concentration_a = int(re.search(r'\d+', product_a.concentration).group()) if re.search(r'\d+', product_a.concentration) else 0
        concentration_b = int(re.search(r'\d+', product_b.concentration).group()) if re.search(r'\d+', product_b.concentration) else 0
        
        comparison_points.append(ComparisonItem(
            attribute="Vitamin C Concentration",
            product_a=product_a.concentration,
            product_b=product_b.concentration,
            winner=product_b.name if concentration_b > concentration_a else product_a.name
        ))
        
        # Ingredients count
        comparison_points.append(ComparisonItem(
            attribute="Number of Key Ingredients",
            product_a=len(product_a.key_ingredients),
            product_b=len(product_b.key_ingredients),
            winner=product_b.name if len(product_b.key_ingredients) > len(product_a.key_ingredients) else product_a.name
        ))
        
        # Skin types
        comparison_points.append(ComparisonItem(
            attribute="Suitable Skin Types",
            product_a=", ".join(product_a.skin_types),
            product_b=", ".join(product_b.skin_types),
            winner="Tie" if len(product_a.skin_types) == len(product_b.skin_types) else (product_a.name if len(product_a.skin_types) > len(product_b.skin_types) else product_b.name)
        ))
        
        # Benefits count
        comparison_points.append(ComparisonItem(
            attribute="Number of Benefits",
            product_a=len(product_a.benefits),
            product_b=len(product_b.benefits),
            winner="Tie" if len(product_a.benefits) == len(product_b.benefits) else (product_b.name if len(product_b.benefits) > len(product_a.benefits) else product_a.name)
        ))
        
        # Ingredients comparison
        ingredients_comp = self.content_blocks.compare_ingredients_block(product_a, product_b)
        comparison_points.append(ComparisonItem(
            attribute="Ingredient Overlap",
            product_a=", ".join(product_a.key_ingredients),
            product_b=", ".join(product_b.key_ingredients),
            winner=f"Common: {', '.join(ingredients_comp['common_ingredients'])}" if ingredients_comp['common_ingredients'] else "No common ingredients"
        ))
        
        # Application timing
        timing_a = "Morning" if "morning" in product_a.usage_instructions.lower() else "Evening"
        timing_b = "Morning" if "morning" in product_b.usage_instructions.lower() else "Evening"
        
        comparison_points.append(ComparisonItem(
            attribute="Recommended Application Time",
            product_a=timing_a,
            product_b=timing_b,
            winner="Flexible" if timing_a != timing_b else "Same"
        ))
        
        return comparison_points
    
    def _create_summary(self, product_a: Product, product_b: Product, comparison_points: list) -> Dict[str, Any]:
        """
        Create comparison summary.
        
        Args:
            product_a: First product
            product_b: Second product
            comparison_points: List of comparison items
            
        Returns:
            Summary dictionary
        """
        # Count wins
        wins_a = sum(1 for item in comparison_points if item.winner == product_a.name)
        wins_b = sum(1 for item in comparison_points if item.winner == product_b.name)
        
        return {
            "total_comparisons": len(comparison_points),
            f"{product_a.name}_wins": wins_a,
            f"{product_b.name}_wins": wins_b,
            "ties": len(comparison_points) - wins_a - wins_b,
            "strengths_a": [
                "More affordable",
                f"Suitable for {' and '.join(product_a.skin_types)} skin",
                "Contains Hyaluronic Acid for hydration"
            ],
            "strengths_b": [
                "Higher Vitamin C concentration",
                "Contains additional antioxidants (Vitamin E, Ferulic Acid)",
                "More comprehensive anti-aging benefits"
            ]
        }
    
    def _create_recommendation(self, product_a: Product, product_b: Product, summary: Dict[str, Any]) -> str:
        """
        Generate recommendation based on comparison.
        
        Args:
            product_a: First product
            product_b: Second product
            summary: Comparison summary
            
        Returns:
            Recommendation text
        """
        wins_a = summary[f"{product_a.name}_wins"]
        wins_b = summary[f"{product_b.name}_wins"]
        
        if wins_a > wins_b:
            return (f"Choose {product_a.name} if you're looking for an affordable, effective vitamin C serum "
                   f"for {' or '.join(product_a.skin_types).lower()} skin with excellent hydration benefits.")
        elif wins_b > wins_a:
            return (f"Choose {product_b.name} if you want higher vitamin C concentration and comprehensive "
                   f"anti-aging benefits with additional antioxidant protection.")
        else:
            return (f"Both products are excellent choices. {product_a.name} offers better value and hydration, "
                   f"while {product_b.name} provides stronger anti-aging and antioxidant benefits. "
                   f"Choose based on your primary concern and budget.")
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate fictional Product B and create comparison.
        
        Args:
            input_data: Contains Product A instance
            
        Returns:
            AgentOutput with comparison data
        """
        try:
            product_a: Product = input_data.data
            
            # Generate fictional Product B
            product_b = self._generate_fictional_product_b(product_a)
            
            # Create comparison points
            comparison_points = self._create_comparison_points(product_a, product_b)
            
            # Generate summary
            summary = self._create_summary(product_a, product_b, comparison_points)
            
            # Generate recommendation
            recommendation = self._create_recommendation(product_a, product_b, summary)
            
            comparison_data = {
                "product_a": product_a,
                "product_b": product_b,
                "comparison_points": comparison_points,
                "summary": summary,
                "recommendation": recommendation
            }
            
            return AgentOutput(
                success=True,
                data=comparison_data,
                metadata={
                    "agent_id": self.agent_id,
                    "comparison_points_count": len(comparison_points),
                    "product_a_wins": summary[f"{product_a.name}_wins"],
                    "product_b_wins": summary[f"{product_b.name}_wins"]
                }
            )
            
        except Exception as e:
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Comparison generation failed: {str(e)}"]
            )
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate that input is a Product instance."""
        return isinstance(input_data.data, Product)
