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
            self.log(f"Generating questions for {product.name} using Gemini...")
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
            
            return AgentOutput(
                success=True,
                data=question_set,
                metadata={
                    "total_questions": len(questions),
                    "categories": list(categories),
                    "generation_method": "LLM (Groq via LangChain)"
                }
            )
            
        except Exception as e:
            self.log(f"Error generating questions: {str(e)}", level="ERROR")
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Question generation failed: {str(e)}"]
            )
