"""
LangChain-powered Orchestrator for multi-agent content generation workflow.
Uses LangChain's composition to coordinate agents.
"""

import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.agents.data_parser_agent import DataParserAgent
from src.agents.question_generator_agent_llm import QuestionGeneratorAgent
from src.agents.answer_generator_agent_llm import AnswerGeneratorAgent
from src.agents.comparison_agent_llm import ComparisonAgentLLM
from src.agents.template_agent import TemplateAgent
from src.models.product import Product, QuestionSet
from src.models.outputs import FAQPage, ProductPage, ComparisonPage


class LangChainOrchestrator(BaseAgent):
    """
    LangChain-based orchestrator that coordinates the multi-agent workflow.
    
    Workflow:
    1. Parse raw data -> Product model
    2. Generate questions using LLM -> QuestionSet
    3. Generate answers using LLM -> FAQ items
    4. Generate competitor + comparison using LLM -> Comparison data
    5. Apply templates -> Structured JSON outputs
    6. Save outputs to files
    """
    
    def __init__(self, output_dir: str = "output"):
        super().__init__(
            agent_id="langchain_orchestrator",
            description="LangChain-powered multi-agent workflow coordinator"
        )
        self.output_dir = output_dir
        
        # Load environment variables
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file.")
        
        # Initialize Groq LLM
        self.log("Initializing Groq LLM via LangChain...")
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=api_key,
            temperature=0.7
        )
        
        # Initialize agents with LLM
        self.data_parser = DataParserAgent()
        self.question_generator = QuestionGeneratorAgent(llm=self.llm)
        self.answer_generator = AnswerGeneratorAgent(llm=self.llm)
        self.comparison_agent = ComparisonAgentLLM(llm=self.llm)
        self.template_agent = TemplateAgent()
        
        self.log("LangChain orchestrator initialized with Groq-powered agents")
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute the complete LangChain-powered workflow.
        
        Args:
            input_data: Contains raw product data dict
            
        Returns:
            AgentOutput with workflow summary
        """
        try:
            workflow_state: Dict[str, Any] = {}
            
            # Step 1: Parse product data
            self.log("\n=== Step 1: Parsing Product Data ===")
            parser_result = self.data_parser.execute(input_data)
            if not parser_result.success:
                return self._handle_failure("Data parsing", parser_result.errors)
            
            product: Product = parser_result.data
            workflow_state['product'] = product
            self.log(f"✓ Parsed: {product.name}")
            
            # Step 2: Generate questions using LLM
            self.log("\n=== Step 2: Generating Questions with LLM ===")
            question_result = self.question_generator.execute(
                AgentInput(data=product)
            )
            if not question_result.success:
                return self._handle_failure("Question generation", question_result.errors)
            
            question_set: QuestionSet = question_result.data
            workflow_state['questions'] = question_set
            self.log(f"✓ Generated {len(question_set.questions)} questions using Groq LLM")
            
            # Step 3: Generate ALL answers in BATCH (1 API call instead of 20)
            self.log("\n=== Step 3: Generating Answers with LLM (BATCH MODE) ===")
            answer_result = self.answer_generator.execute(
                AgentInput(data={'product': product, 'questions': question_set.questions})
            )
            if not answer_result.success:
                return self._handle_failure("Answer generation", answer_result.errors)
            
            # Build FAQ items from batch results
            faq_items = []
            for i, question in enumerate(question_set.questions):
                if i < len(answer_result.data):
                    faq_items.append({
                        'question': question.question,
                        'answer': answer_result.data[i],
                        'category': question.category
                    })
            
            workflow_state['faq_items'] = faq_items
            self.log(f"✓ Generated {len(faq_items)} AI-powered answers (API calls saved: {answer_result.metadata.get('api_calls_saved', 0)})")
            
            # Step 4: Generate comparison using LLM
            self.log("\n=== Step 4: Generating Competitor & Comparison with LLM ===")
            comparison_result = self.comparison_agent.execute(
                AgentInput(data=product)
            )
            if not comparison_result.success:
                return self._handle_failure("Comparison generation", comparison_result.errors)
            
            workflow_state['comparison'] = comparison_result.data
            self.log(f"✓ Generated fictional competitor: {comparison_result.data['product_b']['name']}")
            
            # Step 5: Generate all structured output pages
            self.log("\n=== Step 5: Generating Structured Outputs ===")
            pages = []
            
            # Generate FAQ page (using LLM-generated questions and answers)
            from src.models.product import QuestionSet
            question_set_for_template = QuestionSet(
                product_name=product.name,
                questions=question_set.questions,
                total_questions=len(question_set.questions),
                categories=list(set([q.category for q in question_set.questions]))
            )
            
            # Generate product page
            product_page_result = self.template_agent.execute(
                AgentInput(data={
                    "page_type": "product_page",
                    "product": product
                })
            )
            if product_page_result.success:
                pages.append(product_page_result.data)
                self.log("✓ Generated Product Page")
            
            # Generate FAQ page with LLM-generated content
            from src.models.outputs import FAQItem, FAQPage
            faq_items_objs = [
                FAQItem(
                    question=item['question'],
                    answer=item['answer'],
                    category=item['category']
                ) for item in faq_items
            ]
            faq_page = FAQPage(
                product_name=product.name,
                total_questions=len(faq_items),
                categories=list(set([item['category'] for item in faq_items])),
                faqs=faq_items_objs
            )
            pages.append(faq_page)
            self.log("✓ Generated FAQ Page")
            
            # Generate comparison page
            comparison_page_result = self.template_agent.execute(
                AgentInput(data={
                    "page_type": "comparison",
                    "comparison_data": comparison_result.data
                })
            )
            if comparison_page_result.success:
                pages.append(comparison_page_result.data)
                self.log("✓ Generated Comparison Page")
            else:
                self.log(f"⚠ Comparison page failed: {comparison_page_result.errors}", level="WARN")
            
            self.log(f"✓ Generated {len(pages)} structured pages")
            
            # Step 6: Save outputs
            self.log("\n=== Step 6: Saving Outputs ===")
            self._save_outputs(pages)
            
            # Final summary
            summary = {
                "product_name": product.name,
                "questions_generated": len(question_set.questions),
                "answers_generated": len(faq_items),
                "competitor_generated": comparison_result.data['product_b']['name'],
                "comparison_points": len(comparison_result.data['comparison_points']),
                "pages_generated": [type(p).__name__ for p in pages],
                "output_directory": self.output_dir,
                "llm_framework": "LangChain",
                "llm_model": "Groq (llama-3.1-8b-instant)",
                "generation_method": "AI-powered (not rule-based)"
            }
            
            self.log("\n✅ Workflow completed successfully!")
            self.log(f"✓ FAQ page: {len(faq_items)} Q&As (AI-generated)")
            self.log(f"✓ Product page: Complete")
            self.log(f"✓ Comparison page: vs {comparison_result.data['product_b']['name']}")
            
            return AgentOutput(
                success=True,
                data=summary,
                metadata={"workflow_type": "LangChain Multi-Agent System"}
            )
            
        except Exception as e:
            self.log(f"Workflow failed: {str(e)}", level="ERROR")
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Orchestration failed: {str(e)}"]
            )
    
    def _save_outputs(self, pages: list):
        """Save generated pages to JSON files."""
        os.makedirs(self.output_dir, exist_ok=True)
        
        for i, page_data in enumerate(pages):
            page_type = type(page_data).__name__.replace('Page', '').lower()
            file_path = os.path.join(self.output_dir, f"{page_type}_page.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(page_data.model_dump() if hasattr(page_data, 'model_dump') else page_data, 
                         f, indent=2, ensure_ascii=False)
            self.log(f"✓ Saved: {file_path}")
    
    def _handle_failure(self, step_name: str, errors: list) -> AgentOutput:
        """Handle workflow step failure."""
        self.log(f"✗ Failed at: {step_name}", level="ERROR")
        for error in errors:
            self.log(f"  - {error}", level="ERROR")
        return AgentOutput(
            success=False,
            data=None,
            errors=[f"{step_name} failed"] + errors
        )
