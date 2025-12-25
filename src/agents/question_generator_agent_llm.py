"""
LLM-powered QuestionGeneratorAgent using LangChain and Groq.
Generates 15+ categorized questions using AI instead of templates.
"""

from typing import List
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product, CategorizedQuestion, QuestionSet


class QuestionGeneratorAgent(BaseAgent):
    """
    LLM-powered agent that generates diverse categorized questions.
    
    Input: Product instance
    Output: QuestionSet with 15+ AI-generated categorized questions
    """
    
    def __init__(self, llm: ChatGroq):
        super().__init__(
            agent_id="question_generator_agent",
            description="Generates categorized user questions using LLM"
        )
        self.llm = llm
        
        # Define prompt for question generation
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating realistic user questions about skincare products.
            
Generate exactly 20 diverse questions across these categories:
- Informational (4 questions): What is it, what does it do, key features
- Usage (3 questions): How to use, when to apply, application tips
- Safety (3 questions): Side effects, precautions, skin sensitivity
- Skin Type (3 questions): Suitability for different skin types
- Purchase (3 questions): Price, where to buy, value assessment
- Comparison (2 questions): How it compares to competitors
- Results (2 questions): Expected outcomes, timeline

Generate natural, conversational questions a real user would ask.

Return ONLY a JSON array with this exact structure:
[
  {{"category": "Informational", "question": "What is the product?", "priority": 1}},
  {{"category": "Usage", "question": "How do I use it?", "priority": 1}}
]

Product Details:
Name: {product_name}
Concentration: {concentration}
Skin Types: {skin_types}
Ingredients: {ingredients}
Benefits: {benefits}
Usage: {usage}
Side Effects: {side_effects}
Price: {price}"""),
            ("human", "Generate 20 diverse questions. Return ONLY the JSON array, no other text.")
        ])
        
        self.chain = self.prompt | self.llm | JsonOutputParser()
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate questions using LLM.
        
        Args:
            input_data: Contains Product instance
            
        Returns:
            AgentOutput with QuestionSet containing 20+ AI-generated questions
        """
        try:
            product: Product = input_data.data
            
            # Prepare product data for prompt
            prompt_data = {
                "product_name": product.name,
                "concentration": product.concentration,
                "skin_types": ", ".join(product.skin_types),
                "ingredients": ", ".join(product.key_ingredients),
                "benefits": ", ".join(product.benefits),
                "usage": product.usage_instructions,
                "side_effects": product.side_effects,
                "price": product.price
            }
            
            # Generate questions using LLM
            self.log(f"Generating questions for {product.name} using Groq...")
            questions_raw = self.chain.invoke(prompt_data)
            
            # Convert to CategorizedQuestion objects
            questions: List[CategorizedQuestion] = []
            categories = set()
            
            for q_data in questions_raw:
                question = CategorizedQuestion(
                    category=q_data["category"],
                    question=q_data["question"],
                    priority=q_data.get("priority", 1)
                )
                questions.append(question)
                categories.add(q_data["category"])
            
            # Create question set
            question_set = QuestionSet(
                questions=questions,
                categories=list(categories)
            )
            
            self.log(f"Generated {len(questions)} questions across {len(categories)} categories")
            
            # Validate LLM output
            if not self._validate_questions(questions):
                self.log("LLM output validation failed, using fallback", level="WARNING")
                return self._fallback_questions(product)
            
            return AgentOutput(
                success=True,
                data=question_set,
                metadata={
                    "total_questions": len(questions),
                    "categories": list(categories),
                    "generation_method": "LLM (Groq via LangChain)",
                    "validation_passed": True
                }
            )
            
        except Exception as e:
            self.log(f"Error generating questions: {str(e)}", level="ERROR")
            self.log("Attempting fallback strategy...", level="WARNING")
            return self._fallback_questions(product)
    
    def _validate_questions(self, questions: list) -> bool:
        """Validate LLM-generated questions for quality and completeness."""
        if not questions or len(questions) < 15:
            self.log(f"Validation failed: Only {len(questions)} questions generated (minimum 15)", level="WARNING")
            return False
        
        required_categories = {"Informational", "Usage", "Safety"}
        found_categories = {q.category for q in questions}
        
        if not required_categories.issubset(found_categories):
            self.log(f"Validation failed: Missing required categories", level="WARNING")
            return False
        
        # Check question quality
        for q in questions:
            if not q.question or len(q.question) < 10:
                self.log(f"Validation failed: Invalid question format", level="WARNING")
                return False
            if not q.question.strip().endswith('?'):
                self.log(f"Validation failed: Questions must end with '?'", level="WARNING")
                return False
        
        self.log("LLM output validation passed", level="DEBUG")
        return True
    
    def _fallback_questions(self, product: Product) -> AgentOutput:
        """Generate fallback questions when LLM fails."""
        self.log("Using fallback question generation strategy", level="WARNING")
        
        fallback_questions = [
            CategorizedQuestion(category="Informational", question=f"What is {product.name}?", priority=1),
            CategorizedQuestion(category="Informational", question=f"What are the key ingredients in {product.name}?", priority=1),
            CategorizedQuestion(category="Informational", question=f"What benefits does {product.name} provide?", priority=1),
            CategorizedQuestion(category="Informational", question=f"What is the concentration of {product.name}?", priority=2),
            CategorizedQuestion(category="Usage", question=f"How do I use {product.name}?", priority=1),
            CategorizedQuestion(category="Usage", question=f"When should I apply {product.name}?", priority=1),
            CategorizedQuestion(category="Usage", question=f"How much {product.name} should I use?", priority=2),
            CategorizedQuestion(category="Safety", question=f"Are there any side effects of {product.name}?", priority=1),
            CategorizedQuestion(category="Safety", question=f"Is {product.name} safe for sensitive skin?", priority=1),
            CategorizedQuestion(category="Safety", question=f"What precautions should I take with {product.name}?", priority=2),
            CategorizedQuestion(category="Skin Type", question=f"What skin types is {product.name} suitable for?", priority=1),
            CategorizedQuestion(category="Skin Type", question=f"Can I use {product.name} on oily skin?", priority=2),
            CategorizedQuestion(category="Skin Type", question=f"Can I use {product.name} on dry skin?", priority=2),
            CategorizedQuestion(category="Purchase", question=f"What is the price of {product.name}?", priority=1),
            CategorizedQuestion(category="Purchase", question=f"Where can I buy {product.name}?", priority=2),
            CategorizedQuestion(category="Comparison", question=f"How does {product.name} compare to similar products?", priority=2),
            CategorizedQuestion(category="Results", question=f"When will I see results from {product.name}?", priority=1),
            CategorizedQuestion(category="Results", question=f"What results can I expect from {product.name}?", priority=1),
        ]
        
        question_set = QuestionSet(
            questions=fallback_questions,
            categories=["Informational", "Usage", "Safety", "Skin Type", "Purchase", "Comparison", "Results"]
        )
        
        return AgentOutput(
            success=True,
            data=question_set,
            metadata={
                "total_questions": len(fallback_questions),
                "categories": question_set.categories,
                "generation_method": "Fallback (Template-based)",
                "fallback_used": True
            }
        )
