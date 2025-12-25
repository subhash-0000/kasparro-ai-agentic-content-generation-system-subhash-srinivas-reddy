"""
Reusable content logic blocks for transforming product data into structured content.
Each block is a pure function with a single responsibility.
"""

from typing import Dict, Any, List
from src.models.product import Product, CategorizedQuestion


class ContentLogicBlocks:
    """
    Collection of reusable content transformation blocks.
    Each method represents a discrete content generation logic.
    """
    
    @staticmethod
    def generate_benefits_block(product: Product) -> Dict[str, Any]:
        """
        Extract product benefits into structured format.
        
        Args:
            product: Product instance
            
        Returns:
            Dict with formatted benefits
        """
        benefits_detail = []
        
        for benefit in product.benefits:
            benefits_detail.append({
                "benefit": benefit,
                "description": benefit
            })
        
        return {
            "benefits": benefits_detail,
            "primary_benefit": product.benefits[0] if product.benefits else None
        }
    
    @staticmethod
    def extract_usage_block(product: Product) -> Dict[str, Any]:
        """
        Extract and structure usage instructions.
        
        Args:
            product: Product instance
            
        Returns:
            Structured usage guide
        """
        usage_text = product.usage_instructions
        
        # Parse usage instructions
        timing = "morning" if "morning" in usage_text.lower() else "evening" if "evening" in usage_text.lower() else "as directed"
        
        # Extract application amount
        amount = None
        if "drops" in usage_text.lower():
            import re
            match = re.search(r'(\d+)[-–]?(\d+)?\s*drops', usage_text)
            if match:
                amount = f"{match.group(1)}-{match.group(2)} drops" if match.group(2) else f"{match.group(1)} drops"
        
        return {
            "timing": timing,
            "application_amount": amount or "as directed",
            "full_instructions": usage_text,
            "application_order": "see instructions",
            "frequency": "as directed"
        }
    
    @staticmethod
    def compare_ingredients_block(product_a: Product, product_b: Product) -> Dict[str, Any]:
        """
        Compare ingredients between two products.
        
        Args:
            product_a: First product
            product_b: Second product
            
        Returns:
            Ingredient comparison data
        """
        ingredients_a = set(product_a.key_ingredients)
        ingredients_b = set(product_b.key_ingredients)
        
        common = ingredients_a.intersection(ingredients_b)
        unique_a = ingredients_a.difference(ingredients_b)
        unique_b = ingredients_b.difference(ingredients_a)
        
        return {
            "common_ingredients": list(common),
            f"{product_a.name}_unique": list(unique_a),
            f"{product_b.name}_unique": list(unique_b),
            "similarity_score": len(common) / max(len(ingredients_a), len(ingredients_b)) if ingredients_a or ingredients_b else 0
        }
    
    @staticmethod
    def safety_info_block(product: Product) -> Dict[str, Any]:
        """
        Extract safety information from product data.
        
        Args:
            product: Product instance
            
        Returns:
            Safety information structure
        """
        return {
            "side_effects": product.side_effects or "None reported",
            "precautions": [],
            "suitable_for_sensitive_skin": "check product details",
            "warnings": product.side_effects if product.side_effects else "None"
        }
    
    @staticmethod
    def pricing_info_block(product: Product) -> Dict[str, Any]:
        """
        Structure pricing information.
        
        Args:
            product: Product instance
            
        Returns:
            Pricing details
        """
        import re
        price_match = re.search(r'₹?(\d+)', product.price)
        price_value = int(price_match.group(1)) if price_match else 0
        
        return {
            "price": product.price,
            "price_value": str(price_value),
            "currency": "INR",
            "value_rating": "product price"
        }
    
    @staticmethod
    def product_summary_block(product: Product) -> Dict[str, Any]:
        """
        Generate product summary from product data.
        
        Args:
            product: Product instance
            
        Returns:
            Summary content
        """
        # Simple concatenation of product data, no synthetic generation
        primary_benefit = product.benefits[0] if product.benefits else "skincare"
        primary_ingredient = product.key_ingredients[0] if product.key_ingredients else "active ingredients"
        
        tagline = f"{primary_benefit} with {primary_ingredient}"
        
        description = (
            f"{product.name} is a {product.concentration} serum designed for "
            f"{' and '.join(product.skin_types)} skin. "
            f"Formulated with {', '.join(product.key_ingredients)}, "
            f"it delivers {' and '.join(product.benefits).lower()} benefits. "
            f"{product.usage_instructions}."
        )
        
        return {
            "tagline": tagline,
            "description": description,
            "key_features": [
                f"{product.concentration}",
                f"For {' & '.join(product.skin_types)} skin",
                f"Contains {', '.join(product.key_ingredients)}",
                f"{len(product.benefits)} benefits"
            ]
        }
    

