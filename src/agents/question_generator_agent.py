"""
QuestionGeneratorAgent - Generates categorized user questions about products.
Single Responsibility: Question generation with automatic categorization.
"""

from typing import List
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product, CategorizedQuestion, QuestionSet


class QuestionGeneratorAgent(BaseAgent):
    """
    Generates diverse categorized questions based on product data.
    
    Input: Product instance
    Output: QuestionSet with 15+ categorized questions
    """
    
    # Question templates by category
    QUESTION_TEMPLATES = {
        "Informational": [
            "What is {product_name}?",
            "What are the key ingredients in {product_name}?",
            "What is the concentration of active ingredients in {product_name}?",
            "What are the main benefits of using {product_name}?",
        ],
        "Usage": [
            "How do I use {product_name}?",
            "When should I apply {product_name}?",
            "How many drops of {product_name} should I use?",
            "Can I use {product_name} with other skincare products?",
        ],
        "Safety": [
            "Are there any side effects of {product_name}?",
            "Is {product_name} safe for sensitive skin?",
            "What should I do if I experience irritation from {product_name}?",
        ],
        "Skin Type": [
            "Is {product_name} suitable for oily skin?",
            "Can people with combination skin use {product_name}?",
            "What skin types is {product_name} best for?",
        ],
        "Purchase": [
            "What is the price of {product_name}?",
            "Where can I buy {product_name}?",
            "Is {product_name} worth the price?",
        ],
        "Comparison": [
            "How does {product_name} compare to other vitamin C serums?",
            "What makes {product_name} different from other serums?",
        ],
        "Results": [
            "How long does it take to see results from {product_name}?",
            "What results can I expect from {product_name}?",
        ],
        "Ingredients": [
            "What does Hyaluronic Acid do in {product_name}?",
            "Why is Vitamin C important in {product_name}?",
        ]
    }
    
    def __init__(self):
        super().__init__(
            agent_id="question_generator_agent",
            description="Generates categorized user questions about products"
        )
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate categorized questions based on product data.
        
        Args:
            input_data: Contains Product instance
            
        Returns:
            AgentOutput with QuestionSet containing 15+ questions
        """
        try:
            product: Product = input_data.data
            questions: List[CategorizedQuestion] = []
            
            # Generate questions for each category
            for category, templates in self.QUESTION_TEMPLATES.items():
                for priority, template in enumerate(templates, start=1):
                    question_text = template.format(product_name=product.name)
                    
                    questions.append(CategorizedQuestion(
                        category=category,
                        question=question_text,
                        priority=priority
                    ))
            
            # Create question set
            question_set = QuestionSet(
                questions=questions,
                categories=list(self.QUESTION_TEMPLATES.keys())
            )
            
            return AgentOutput(
                success=True,
                data=question_set,
                metadata={
                    "agent_id": self.agent_id,
                    "total_questions": len(questions),
                    "categories_count": len(question_set.categories),
                    "categories": question_set.categories
                }
            )
            
        except Exception as e:
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Question generation failed: {str(e)}"]
            )
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate that input is a Product instance."""
        return isinstance(input_data.data, Product)
