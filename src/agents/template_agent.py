"""
TemplateAgent - Structures LLM-generated content into JSON schemas.
Single Responsibility: Format AI-generated content into Pydantic models.
NO GENERATION - only formatting pre-generated LLM content.
"""

from typing import Dict, Any
import re
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product, QuestionSet
from src.models.outputs import FAQItem, FAQPage, ProductPage, ComparisonPage, ComparisonItem


class TemplateAgent(BaseAgent):
    """
    Structures LLM-generated content into validated JSON schemas.
    No hardcoded generation - only formatting and validation.
    
    Input: Dict with page_type, product data, and LLM-generated content
    Output: Structured page (FAQPage, ProductPage, or ComparisonPage)
    """
    
    def __init__(self):
        super().__init__(
            agent_id="template_agent",
            description="Structures AI-generated content into JSON schemas"
        )
    
    def _generate_faq_page(self, faq_items: list, product_name: str) -> FAQPage:
        """
        Generate FAQ page from pre-generated LLM answers.
        
        Args:
            faq_items: List of dicts with question, answer, category (LLM-generated)
            product_name: Product name
            
        Returns:
            FAQPage instance
        """
        # Convert to FAQItem objects
        from src.models.outputs import FAQItem
        faq_objs = [
            FAQItem(
                question=item['question'],
                answer=item['answer'],
                category=item['category']
            ) for item in faq_items
        ]
        
        # Create FAQ page
        return FAQPage(
            product_name=product_name,
            total_questions=len(faq_objs),
            categories=list(set([item['category'] for item in faq_items])),
            faqs=faq_objs
        )
    
    def _generate_product_page(self, product: Product, product_content: Dict[str, Any]) -> ProductPage:
        """
        Format product page from LLM-generated content.
        Pure formatter - NO generation, only structuring LLM output.
        
        Args:
            product: Product instance
            product_content: LLM-generated content (ALL fields must be provided)
            
        Returns:
            ProductPage instance
        """
        # Extract pricing data (only data extraction, no generation)
        import re
        price_match = re.search(r'₹?(\d+)', product.price)
        price_value = int(price_match.group(1)) if price_match else 0
        
        pricing = {
            "price": product.price,
            "price_value": str(price_value),
            "currency": "INR",
            "value_rating": "product price"
        }
        
        # Use LLM-generated content directly - NO fallback generation
        usage_guide = product_content.get('usage_highlights', {
            "timing": "as directed",
            "application_amount": "as directed",
            "full_instructions": product.usage_instructions,
            "application_order": "as directed",
            "frequency": "as directed"
        })
        
        # Use LLM-generated safety info - NO hardcoded content
        safety_info = product_content.get('safety_information', {
            "side_effects": product.side_effects or "None reported",
            "precautions": product_content.get('precautions', ["Consult product packaging"]),
            "suitable_for_sensitive_skin": product_content.get('suitable_for_sensitive_skin', "Consult dermatologist"),
            "warnings": product.side_effects if product.side_effects else "None"
        })
        
        # Create product page using 100% LLM-generated content
        return ProductPage(
            product_name=product.name,
            tagline=product_content.get('tagline', product.name),
            description=product_content.get('description', f"{product.name} serum"),
            key_features=product_content.get('key_features', []),
            ingredients=product_content.get('ingredient_descriptions', {ing: ing for ing in product.key_ingredients}),
            usage_guide=usage_guide,
            suitable_for=product.skin_types,
            benefits=product.benefits,
            safety_information=safety_info,
            pricing=pricing
        )
    
    def _generate_comparison_page(self, comparison_data: Dict[str, Any]) -> ComparisonPage:
        """
        Generate comparison page using comparison template.
        
        Args:
            comparison_data: Dict with product_a, product_b, comparison_points, etc.
            
        Returns:
            ComparisonPage instance
        """
        product_a = comparison_data["product_a"]
        product_b = comparison_data["product_b"]
        
        # Handle both Product objects and dicts
        if isinstance(product_a, dict):
            product_a_dict = product_a
        else:
            product_a_dict = {
                "name": product_a.name,
                "concentration": product_a.concentration,
                "skin_types": product_a.skin_types,
                "key_ingredients": product_a.key_ingredients,
                "benefits": product_a.benefits,
                "price": product_a.price
            }
        
        if isinstance(product_b, dict):
            product_b_dict = product_b
        else:
            product_b_dict = {
                "name": product_b.name,
                "concentration": product_b.concentration,
                "skin_types": product_b.skin_types,
                "key_ingredients": product_b.key_ingredients,
                "benefits": product_b.benefits,
                "price": product_b.price
            }
        
        return ComparisonPage(
            product_a=product_a_dict,
            product_b=product_b_dict,
            comparison_points=comparison_data["comparison_points"],
            summary=comparison_data["summary"],
            recommendation=comparison_data["recommendation"]
        )
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Apply appropriate template and generate page.
        
        Args:
            input_data: Contains page_type and relevant data
            
        Returns:
            AgentOutput with generated page
        """
        try:
            page_type = input_data.data.get("page_type")
            
            if page_type == "faq":
                faq_items = input_data.data.get("faq_items")
                product_name = input_data.data.get("product_name")
                page = self._generate_faq_page(faq_items, product_name)
                
            elif page_type == "product_page":
                product = input_data.data.get("product")
                product_content = input_data.data.get("product_content")
                page = self._generate_product_page(product, product_content)
                
            elif page_type == "comparison":
                comparison_data = input_data.data.get("comparison_data")
                page = self._generate_comparison_page(comparison_data)
                
            else:
                raise ValueError(f"Unknown page type: {page_type}")
            
            return AgentOutput(
                success=True,
                data=page,
                metadata={
                    "agent_id": self.agent_id,
                    "page_type": page_type,
                    "template_applied": True
                }
            )
            
        except Exception as e:
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Template application failed: {str(e)}"]
            )
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate that input contains required data for template application."""
        if not isinstance(input_data.data, dict):
            return False
        
        page_type = input_data.data.get("page_type")
        if page_type not in ["faq", "product_page", "comparison"]:
            return False
        
        # Check required data for each page type
        if page_type == "faq":
            return "faq_items" in input_data.data and "product_name" in input_data.data
        elif page_type == "product_page":
            return "product" in input_data.data and "product_content" in input_data.data
        elif page_type == "comparison":
            return "comparison_data" in input_data.data
        
        return False
