"""
LLM-powered AnswerGeneratorAgent using LangChain and Groq.
Generates intelligent answers for questions using AI.
OPTIMIZED: Batch processing to reduce API calls from 20 to 1.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.models.product import Product, CategorizedQuestion
from typing import List


class AnswerGeneratorAgent(BaseAgent):
    """
    LLM-powered agent that generates contextual answers to product questions.
    OPTIMIZED: Batches all questions into 1 API call instead of 20 separate calls.
    
    Input: Product + List of Questions
    Output: AI-generated answers for all questions
    """
    
    def __init__(self, llm: ChatGroq):
        super().__init__(
            agent_id="answer_generator_agent",
            description="Generates intelligent answers using LLM (Batch Mode)"
        )
        self.llm = llm
        
        # Define BATCH prompt for answer generation (all questions at once)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a knowledgeable skincare expert providing helpful, accurate answers about products.

Generate answers for ALL questions below based ONLY on the provided product information.

Product Details:
Name: {product_name}
Concentration: {concentration}
Skin Types: {skin_types}
Ingredients: {ingredients}
Benefits: {benefits}
Usage Instructions: {usage}
Side Effects: {side_effects}
Price: {price}

Guidelines:
- Each answer should be 2-3 sentences max
- Be conversational but professional
- Answer directly without fluff
- Use specific product details from above

Return JSON array with this structure:
[
  {{"question": "question text 1", "answer": "answer text 1"}},
  {{"question": "question text 2", "answer": "answer text 2"}}
]

IMPORTANT: Return ONLY the JSON array, no additional text."""),
            ("human", "Generate answers for these questions:\n\n{questions_list}")
        ])
        
        self.parser = JsonOutputParser()
        self.chain = self.prompt | self.llm | self.parser
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate answers for ALL questions using LLM in ONE API call.
        
        Args:
            input_data: Dict with 'product' (Product) and 'questions' (List[CategorizedQuestion])
            
        Returns:
            AgentOutput with list of generated answers
        """
        try:
            data = input_data.data
            product: Product = data['product']
            questions: List[CategorizedQuestion] = data['questions']
            
            self.log(f"Generating answers for {len(questions)} questions in BATCH mode...")
            
            # Format questions for batch processing
            questions_text = "\n".join([
                f"{i+1}. [{q.category}] {q.question}" 
                for i, q in enumerate(questions)
            ])
            
            # Prepare prompt data
            prompt_data = {
                "product_name": product.name,
                "concentration": product.concentration,
                "skin_types": ", ".join(product.skin_types),
                "ingredients": ", ".join(product.key_ingredients),
                "benefits": ", ".join(product.benefits),
                "usage": product.usage_instructions,
                "side_effects": product.side_effects,
                "price": product.price,
                "questions_list": questions_text
            }
            
            # Generate ALL answers in ONE API call
            response = self.chain.invoke(prompt_data)
            
            # Match answers with questions
            answers = []
            for item in response:
                answers.append(item.get('answer', 'Answer not available'))
            
            self.log(f"✓ Generated {len(answers)} answers in 1 API call")
            
            # Validate LLM output
            if not self._validate_answers(answers, questions):
                self.log("Answer validation failed, using fallback", level="WARNING")
                return self._fallback_answers(product, questions)
            
            return AgentOutput(
                success=True,
                data=answers,
                metadata={
                    "total_questions": len(questions),
                    "api_calls_saved": len(questions) - 1,
                    "generation_method": "LLM Batch (Groq via LangChain)",
                    "validation_passed": True
                }
            )
            
        except Exception as e:
            self.log(f"Error generating answers: {str(e)}", level="ERROR")
            self.log("Attempting fallback strategy...", level="WARNING")
            return self._fallback_answers(product, questions)
    
    def _validate_answers(self, answers: list, questions: list) -> bool:
        """Validate LLM-generated answers for quality."""
        if not answers or len(answers) != len(questions):
            self.log(f"Validation failed: Answer count ({len(answers)}) != question count ({len(questions)})", level="WARNING")
            return False
        
        for i, answer in enumerate(answers):
            if not answer or len(answer.strip()) < 20:
                self.log(f"Validation failed: Answer {i+1} too short or empty", level="WARNING")
                return False
        
        self.log("Answer validation passed", level="DEBUG")
        return True
    
    def _fallback_answers(self, product: Product, questions: List[CategorizedQuestion]) -> AgentOutput:
        """Generate fallback answers when LLM fails."""
        self.log("Using fallback answer generation strategy", level="WARNING")
        
        fallback_answers = []
        for question in questions:
            # Generate basic answers from product data
            if "what is" in question.question.lower():
                answer = f"{product.name} is a {product.concentration} serum formulated for {', '.join(product.skin_types)} skin types."
            elif "ingredient" in question.question.lower():
                answer = f"{product.name} contains {', '.join(product.key_ingredients)} as key active ingredients."
            elif "benefit" in question.question.lower():
                answer = f"{product.name} provides {', '.join(product.benefits).lower()} benefits."
            elif "how to use" in question.question.lower() or "how do i use" in question.question.lower():
                answer = product.usage_instructions
            elif "side effect" in question.question.lower():
                answer = product.side_effects if (product.side_effects and len(product.side_effects) > 20) else "No significant side effects have been reported for this product. However, it's always recommended to perform a patch test before first use."
            elif "price" in question.question.lower():
                answer = f"{product.name} is priced at {product.price}."
            elif "skin type" in question.question.lower():
                answer = f"{product.name} is suitable for {', '.join(product.skin_types)} skin types."
            else:
                answer = f"For detailed information about {question.question.lower().replace('?', '')}, please refer to the product documentation or consult with a skincare professional."
            
            fallback_answers.append(answer)
        
        return AgentOutput(
            success=True,
            data=fallback_answers,
            metadata={
                "total_questions": len(questions),
                "generation_method": "Fallback (Template-based)",
                "fallback_used": True
            }
        )
