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
        Transform product benefits into detailed benefit descriptions.
        
        Args:
            product: Product instance
            
        Returns:
            Dict with formatted benefits
        """
        benefits_detail = []
        benefit_descriptions = {
            "Brightening": "Illuminates and evens out skin tone for a radiant complexion",
            "Fades dark spots": "Reduces hyperpigmentation and dark spots over time",
            "Anti-aging": "Reduces fine lines and wrinkles",
            "Hydrating": "Provides deep moisture to the skin",
            "Firming": "Improves skin elasticity and firmness"
        }
        
        for benefit in product.benefits:
            benefits_detail.append({
                "benefit": benefit,
                "description": benefit_descriptions.get(benefit, f"Provides {benefit.lower()} effects")
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
        timing = "morning" if "morning" in usage_text.lower() else "evening"
        
        # Extract application amount
        amount = None
        if "drops" in usage_text.lower():
            import re
            match = re.search(r'(\d+)[-–]?(\d+)?\s*drops', usage_text)
            if match:
                amount = f"{match.group(1)}-{match.group(2)} drops" if match.group(2) else f"{match.group(1)} drops"
        
        return {
            "timing": timing,
            "application_amount": amount or "As directed",
            "full_instructions": usage_text,
            "application_order": "before sunscreen" if "sunscreen" in usage_text.lower() else "as part of routine",
            "frequency": "daily"
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
        Generate safety and side effect information.
        
        Args:
            product: Product instance
            
        Returns:
            Safety information structure
        """
        return {
            "side_effects": product.side_effects or "None reported",
            "precautions": [
                "Perform patch test before first use",
                "Avoid contact with eyes",
                "Discontinue use if irritation occurs"
            ],
            "suitable_for_sensitive_skin": "caution" if product.side_effects and "sensitive" in product.side_effects.lower() else "yes",
            "warnings": "May cause mild tingling" if product.side_effects else "None"
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
            "price_value": str(price_value),  # Convert to string for schema compliance
            "currency": "INR",
            "value_rating": "affordable" if price_value < 1000 else "premium" if price_value < 2000 else "luxury"
        }
    
    @staticmethod
    def product_summary_block(product: Product) -> Dict[str, Any]:
        """
        Generate product summary and tagline.
        
        Args:
            product: Product instance
            
        Returns:
            Summary content
        """
        # Generate tagline based on primary benefit and ingredient
        primary_benefit = product.benefits[0] if product.benefits else "skincare"
        primary_ingredient = product.key_ingredients[0] if product.key_ingredients else "active ingredients"
        
        tagline = f"{primary_benefit} power with {primary_ingredient}"
        
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
                f"Suitable for {' & '.join(product.skin_types)} skin",
                f"Contains {', '.join(product.key_ingredients)}",
                f"{len(product.benefits)} key benefits"
            ]
        }
    
    @staticmethod
    def answer_generator_block(product: Product, question: CategorizedQuestion) -> str:
        """
        Generate answer for a given question based on product data.
        
        Args:
            product: Product instance
            question: Question to answer
            
        Returns:
            Generated answer string
        """
        q_lower = question.question.lower()
        
        # Answer generation logic based on question content
        if "what is" in q_lower and product.name.lower() in q_lower:
            return f"{product.name} is a {product.concentration} serum containing {', '.join(product.key_ingredients)}. It's designed for {' and '.join(product.skin_types)} skin types."
        
        elif "key ingredients" in q_lower:
            return f"The key ingredients in {product.name} are: {', '.join(product.key_ingredients)}. These work together to provide {' and '.join(product.benefits).lower()} benefits."
        
        elif "concentration" in q_lower:
            return f"{product.name} contains {product.concentration} of active ingredients, providing effective results while being gentle on the skin."
        
        elif "benefits" in q_lower or "main benefits" in q_lower:
            return f"The main benefits of {product.name} include: {', '.join(product.benefits)}. Regular use can help improve overall skin health and appearance."
        
        elif "how do i use" in q_lower or "how to use" in q_lower:
            return f"To use {product.name}: {product.usage_instructions}. For best results, use consistently as part of your daily skincare routine."
        
        elif "when should i apply" in q_lower:
            timing = "morning" if "morning" in product.usage_instructions.lower() else "evening"
            return f"Apply {product.name} in the {timing}. {product.usage_instructions}"
        
        elif "how many drops" in q_lower:
            return f"{product.usage_instructions}. This amount is optimal for facial coverage without product waste."
        
        elif "side effects" in q_lower:
            return f"{product.side_effects or 'No significant side effects reported.'}. Always perform a patch test before first use."
        
        elif "sensitive skin" in q_lower:
            if product.side_effects and "sensitive" in product.side_effects.lower():
                return f"{product.side_effects}. If you have very sensitive skin, consult with a dermatologist before use."
            return f"{product.name} is generally well-tolerated, but always patch test if you have sensitive skin."
        
        elif "irritation" in q_lower:
            return "If you experience irritation, discontinue use immediately and rinse with water. Consult a dermatologist if irritation persists."
        
        elif "oily skin" in q_lower or "combination skin" in q_lower:
            skin_type = "oily" if "oily" in q_lower else "combination"
            if skin_type.title() in product.skin_types:
                return f"Yes, {product.name} is specifically formulated for {' and '.join(product.skin_types)} skin types."
            return f"{product.name} is best suited for {' and '.join(product.skin_types)} skin."
        
        elif "skin types" in q_lower or "best for" in q_lower:
            return f"{product.name} is best suited for {' and '.join(product.skin_types)} skin types."
        
        elif "price" in q_lower:
            return f"{product.name} is priced at {product.price}, offering professional-grade skincare at an accessible price point."
        
        elif "where can i buy" in q_lower:
            return f"{product.name} is available online and at select skincare retailers. Check the official website for authorized sellers."
        
        elif "worth the price" in q_lower:
            return f"At {product.price}, {product.name} offers excellent value with {product.concentration} and quality ingredients like {', '.join(product.key_ingredients)}."
        
        elif "compare" in q_lower or "different from" in q_lower:
            return f"{product.name} stands out with its {product.concentration} formulation and combination of {', '.join(product.key_ingredients)}, offering {' and '.join(product.benefits).lower()} benefits."
        
        elif "results" in q_lower:
            return f"With consistent use, you can expect to see {product.benefits[0].lower()} results within 2-4 weeks, with continued improvement over 8-12 weeks."
        
        elif "hyaluronic acid" in q_lower:
            return "Hyaluronic Acid in this formula provides deep hydration and helps the skin retain moisture, creating a plump and smooth appearance."
        
        elif "vitamin c" in q_lower:
            return "Vitamin C is a powerful antioxidant that brightens skin, fades dark spots, and protects against environmental damage while promoting collagen production."
        
        elif "other products" in q_lower:
            return f"Yes, {product.name} can be incorporated into your existing routine. Apply it before heavier creams and oils, and always follow with sunscreen in the morning."
        
        else:
            # Generic answer for unmatched questions
            return f"For detailed information about {product.name}, please refer to the product description or consult with a skincare professional."
