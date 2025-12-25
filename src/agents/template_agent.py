"""
TemplateAgent - Applies templates to generate structured page content.
Single Responsibility: Template application and page generation.
"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product, QuestionSet
from src.models.outputs import FAQItem, FAQPage, ProductPage, ComparisonPage, ComparisonItem
from src.template_engine.engine import TemplateEngine
from src.logic_blocks.content_blocks import ContentLogicBlocks


class TemplateAgent(BaseAgent):
    """
    Applies templates to generate structured pages using content logic blocks.
    
    Input: Dict with page_type, product data, and additional context
    Output: Structured page (FAQPage, ProductPage, or ComparisonPage)
    """
    
    def __init__(self):
        super().__init__(
            agent_id="template_agent",
            description="Applies templates and generates structured page content"
        )
        self.template_engine = TemplateEngine()
        self.content_blocks = ContentLogicBlocks()
    
    def _generate_faq_page(self, product: Product, question_set: QuestionSet) -> FAQPage:
        """
        Generate FAQ page using FAQ template.
        
        Args:
            product: Product instance
            question_set: Set of categorized questions
            
        Returns:
            FAQPage instance
        """
        # Select top questions for FAQ (20 questions to strongly exceed minimum requirement)
        selected_questions = []
        questions_per_category = {}
        
        # Group questions by category
        for q in question_set.questions:
            if q.category not in questions_per_category:
                questions_per_category[q.category] = []
            questions_per_category[q.category].append(q)
        
        # Select questions from each category to reach 20 questions
        # With 8 categories and 23 total questions, we can take 2-3 per category
        for category in question_set.categories:
            if category in questions_per_category:
                # Take up to 3 questions per category to reach 20
                questions_to_add = min(3, len(questions_per_category[category]))
                for i in range(questions_to_add):
                    if len(selected_questions) < 20:
                        selected_questions.append(questions_per_category[category][i])
            if len(selected_questions) >= 20:
                break
        
        # Generate FAQ items with answers
        faq_items = []
        for question in selected_questions:
            answer = self.content_blocks.answer_generator_block(product, question)
            faq_items.append(FAQItem(
                question=question.question,
                answer=answer,
                category=question.category
            ))
        
        # Create FAQ page
        return FAQPage(
            product_name=product.name,
            total_questions=len(faq_items),
            categories=[q.category for q in selected_questions],
            faqs=faq_items
        )
    
    def _generate_product_page(self, product: Product) -> ProductPage:
        """
        Generate product description page using product template.
        
        Args:
            product: Product instance
            
        Returns:
            ProductPage instance
        """
        # Use content blocks to generate sections
        summary = self.content_blocks.product_summary_block(product)
        benefits = self.content_blocks.generate_benefits_block(product)
        usage = self.content_blocks.extract_usage_block(product)
        safety = self.content_blocks.safety_info_block(product)
        pricing = self.content_blocks.pricing_info_block(product)
        
        # Create ingredient details
        ingredient_descriptions = {
            "Vitamin C": "A powerful antioxidant that brightens skin tone and reduces signs of aging",
            "Hyaluronic Acid": "A moisture-binding ingredient that hydrates and plumps the skin",
            "Vitamin E": "An antioxidant that protects skin from environmental damage",
            "Ferulic Acid": "Enhances the stability and effectiveness of other antioxidants"
        }
        
        ingredients_dict = {
            ingredient: ingredient_descriptions.get(ingredient, "Key active ingredient")
            for ingredient in product.key_ingredients
        }
        
        # Create product page
        return ProductPage(
            product_name=product.name,
            tagline=summary["tagline"],
            description=summary["description"],
            key_features=summary["key_features"],
            ingredients=ingredients_dict,
            usage_guide=usage,
            suitable_for=product.skin_types,
            benefits=[b["benefit"] for b in benefits["benefits"]],
            safety_information=safety,
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
                product = input_data.data.get("product")
                question_set = input_data.data.get("question_set")
                page = self._generate_faq_page(product, question_set)
                
            elif page_type == "product_page":
                product = input_data.data.get("product")
                page = self._generate_product_page(product)
                
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
            return "product" in input_data.data and "question_set" in input_data.data
        elif page_type == "product_page":
            return "product" in input_data.data
        elif page_type == "comparison":
            return "comparison_data" in input_data.data
        
        return False
