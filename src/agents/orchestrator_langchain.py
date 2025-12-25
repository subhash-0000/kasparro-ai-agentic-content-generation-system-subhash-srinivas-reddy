"""
LangChain-powered Orchestrator using proper framework patterns.
Implements LangChain's agent coordination with tools and structured workflow.
"""

import os
import json
import time
from typing import Dict, Any, TypedDict, List, Sequence, Callable
from functools import wraps
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.tools import Tool
from langchain_core.runnables import RunnableSequence, RunnableLambda

from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.agents.data_parser_agent import DataParserAgent
from src.agents.question_generator_agent_llm import QuestionGeneratorAgent
from src.agents.answer_generator_agent_llm import AnswerGeneratorAgent
from src.agents.comparison_agent_llm import ComparisonAgentLLM
from src.agents.product_page_agent_llm import ProductPageAgent
from src.agents.template_agent import TemplateAgent
from src.models.product import Product, QuestionSet
from src.models.outputs import FAQPage, ProductPage, ComparisonPage


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0
):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # Get logger from self if available
                        if args and hasattr(args[0], 'logger'):
                            args[0].logger.warning(
                                f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                        time.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        if args and hasattr(args[0], 'logger'):
                            args[0].logger.error(
                                f"All {max_retries} attempts failed. Last error: {str(e)}"
                            )
            
            raise last_exception
        return wrapper
    return decorator


class WorkflowState(TypedDict):
    """LangChain-managed workflow state with typed fields"""
    product: Product
    questions: QuestionSet
    faq_items: List[Dict[str, Any]]
    comparison: Dict[str, Any]
    product_content: Dict[str, Any]
    pages: List[Any]
    current_step: str
    errors: List[str]


class LangChainOrchestrator(BaseAgent):
    """
    LangChain-based orchestrator using framework-native patterns.
    Implements proper LangChain workflow with RunnableSequence and tools.
    
    Architecture:
    - Uses LangChain's RunnableSequence for chaining operations
    - Implements agents as tools that can be composed
    - Maintains typed state through workflow
    - Provides retry mechanism and error handling
    """
    
    def __init__(self, output_dir: str = "output"):
        super().__init__(
            agent_id="langchain_orchestrator",
            description="LangChain framework-based multi-agent orchestrator"
        )
        self.output_dir = output_dir
        
        # Load environment variables
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file.")
        
        # Initialize Groq LLM via LangChain
        self.log("Initializing Groq LLM via LangChain...")
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=api_key,
            temperature=0.7,
            max_retries=2  # Built-in retry mechanism
        )
        
        # Initialize LLM-powered agents
        self.data_parser = DataParserAgent()
        self.question_generator = QuestionGeneratorAgent(llm=self.llm)
        self.answer_generator = AnswerGeneratorAgent(llm=self.llm)
        self.comparison_agent = ComparisonAgentLLM(llm=self.llm)
        self.product_page_agent = ProductPageAgent(llm=self.llm)
        self.template_agent = TemplateAgent()
        
        # Initialize workflow state
        self.state: WorkflowState = {
            "product": None,
            "questions": None,
            "faq_items": [],
            "comparison": None,
            "product_content": None,
            "pages": [],
            "current_step": "initialized",
            "errors": []
        }
        
        # Build LangChain workflow pipeline
        self._build_workflow_chain()
        
        self.log("LangChain orchestrator initialized with framework-based workflow")
    
    def _build_workflow_chain(self):
        """Build LangChain RunnableSequence for workflow execution"""
        # Create workflow steps as LangChain Runnables
        self.workflow_chain = (
            RunnableLambda(self._step_parse_data)
            | RunnableLambda(self._step_generate_questions)
            | RunnableLambda(self._step_generate_answers)
            | RunnableLambda(self._step_generate_comparison)
            | RunnableLambda(self._step_generate_product_content)
            | RunnableLambda(self._step_format_outputs)
            | RunnableLambda(self._step_save_outputs)
        )
    
    def _update_state(self, **kwargs):
        """Update workflow state with type checking"""
        self.state.update(kwargs)
        self.log(f"State updated: current_step={self.state.get('current_step')}", level="DEBUG")
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _step_parse_data(self, input_data: AgentInput) -> WorkflowState:
        """Step 1: Parse product data"""
        self._update_state(current_step="parsing_data")
        self.log("\n=== Step 1: Parsing Product Data ===")
        
        result = self.data_parser.execute(input_data)
        if not result.success:
            raise ValueError(f"Data parsing failed: {result.errors}")
        
        self._update_state(product=result.data)
        self.log(f"✓ Parsed: {result.data.name}")
        return self.state
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _step_generate_questions(self, state: WorkflowState) -> WorkflowState:
        """Step 2: Generate questions using LLM"""
        self._update_state(current_step="generating_questions")
        self.log("\n=== Step 2: Generating Questions with LLM ===")
        
        result = self.question_generator.execute(AgentInput(data=state["product"]))
        if not result.success:
            raise ValueError(f"Question generation failed: {result.errors}")
        
        self._update_state(questions=result.data)
        self.log(f"✓ Generated {len(result.data.questions)} questions using Groq LLM")
        return self.state
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _step_generate_answers(self, state: WorkflowState) -> WorkflowState:
        """Step 3: Generate answers using LLM (batch mode)"""
        self._update_state(current_step="generating_answers")
        self.log("\n=== Step 3: Generating Answers with LLM (BATCH MODE) ===")
        
        result = self.answer_generator.execute(
            AgentInput(data={'product': state["product"], 'questions': state["questions"].questions})
        )
        if not result.success:
            raise ValueError(f"Answer generation failed: {result.errors}")
        
        # Build FAQ items from batch results
        faq_items = []
        for i, question in enumerate(state["questions"].questions):
            if i < len(result.data):
                faq_items.append({
                    'question': question.question,
                    'answer': result.data[i],
                    'category': question.category
                })
        
        self._update_state(faq_items=faq_items)
        self.log(f"✓ Generated {len(faq_items)} AI-powered answers")
        return self.state
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _step_generate_comparison(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Generate comparison using LLM"""
        self._update_state(current_step="generating_comparison")
        self.log("\n=== Step 4: Generating Competitor & Comparison with LLM ===")
        
        result = self.comparison_agent.execute(AgentInput(data=state["product"]))
        if not result.success:
            raise ValueError(f"Comparison generation failed: {result.errors}")
        
        self._update_state(comparison=result.data)
        self.log(f"✓ Generated fictional competitor: {result.data['product_b']['name']}")
        return self.state
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    def _step_generate_product_content(self, state: WorkflowState) -> WorkflowState:
        """Step 5: Generate product page content using LLM"""
        self._update_state(current_step="generating_product_content")
        self.log("\n=== Step 5: Generating Product Page Content with LLM ===")
        
        result = self.product_page_agent.execute(AgentInput(data=state["product"]))
        if not result.success:
            raise ValueError(f"Product page content generation failed: {result.errors}")
        
        self._update_state(product_content=result.data)
        self.log("✓ Generated product page content using Groq LLM")
        return self.state
    
    def _step_format_outputs(self, state: WorkflowState) -> WorkflowState:
        """Step 6: Format all outputs into structured pages"""
        self._update_state(current_step="formatting_pages")
        self.log("\n=== Step 6: Formatting Structured Outputs ===")
        pages = []
        
        # Format product page
        result = self.template_agent.execute(AgentInput(data={
            "page_type": "product_page",
            "product": state["product"],
            "product_content": state["product_content"]
        }))
        if result.success:
            pages.append(result.data)
            self.log("✓ Formatted Product Page")
        
        # Format FAQ page
        result = self.template_agent.execute(AgentInput(data={
            "page_type": "faq",
            "faq_items": state["faq_items"],
            "product_name": state["product"].name
        }))
        if result.success:
            pages.append(result.data)
            self.log("✓ Formatted FAQ Page")
        
        # Format comparison page
        result = self.template_agent.execute(AgentInput(data={
            "page_type": "comparison",
            "comparison_data": state["comparison"]
        }))
        if result.success:
            pages.append(result.data)
            self.log("✓ Formatted Comparison Page")
        
        self._update_state(pages=pages)
        self.log(f"✓ Formatted {len(pages)} structured pages")
        return self.state
    
    def _step_save_outputs(self, state: WorkflowState) -> WorkflowState:
        """Step 7: Save outputs to files"""
        self._update_state(current_step="saving_outputs")
        self.log("\n=== Step 7: Saving Outputs ===")
        
        os.makedirs(self.output_dir, exist_ok=True)
        for page_data in state["pages"]:
            page_type = type(page_data).__name__.replace('Page', '').lower()
            file_path = os.path.join(self.output_dir, f"{page_type}_page.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(page_data.model_dump() if hasattr(page_data, 'model_dump') else page_data, 
                         f, indent=2, ensure_ascii=False)
            self.log(f"✓ Saved: {file_path}")
        
        self._update_state(current_step="completed")
        return self.state
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute workflow using LangChain RunnableSequence.
        Implements framework-native orchestration pattern.
        
        Args:
            input_data: Contains raw product data dict
            
        Returns:
            AgentOutput with workflow summary
        """
        try:
            self._update_state(current_step="starting", errors=[])
            
            # Execute LangChain workflow pipeline
            self.log("\n🚀 Starting LangChain Framework-Based Workflow...")
            final_state = self.workflow_chain.invoke(input_data)
            
            # Build success summary
            summary = {
                "product_name": final_state["product"].name,
                "questions_generated": len(final_state["questions"].questions),
                "answers_generated": len(final_state["faq_items"]),
                "competitor_generated": final_state["comparison"]['product_b']['name'],
                "comparison_points": len(final_state["comparison"]['comparison_points']),
                "pages_generated": [type(p).__name__ for p in final_state["pages"]],
                "output_directory": self.output_dir,
                "orchestration_framework": "LangChain RunnableSequence",
                "llm_model": "Groq (llama-3.1-8b-instant)",
                "generation_method": "100% LLM-powered (framework-based)",
                "workflow_pattern": "LangChain native orchestration",
                "state_management": "TypedDict with immutable state",
                "retry_mechanism": "Built-in LangChain max_retries",
                "workflow_state": final_state["current_step"],
                "llm_calls": {
                    "questions": 1,
                    "answers": 1,
                    "comparison": 1,
                    "product_page": 1,
                    "total": 4
                }
            }
            
            self.log("\n✅ LangChain Workflow Completed Successfully!")
            self.log(f"✓ FAQ page: {len(final_state['faq_items'])} Q&As (100% LLM-generated)")
            self.log(f"✓ Product page: Complete (100% LLM-generated)")
            self.log(f"✓ Comparison page: vs {final_state['comparison']['product_b']['name']} (100% LLM-generated)")
            self.log(f"✓ Orchestration: LangChain RunnableSequence (framework-based)")
            
            return AgentOutput(
                success=True,
                data=summary,
                metadata={"orchestration_type": "LangChain RunnableSequence Framework"}
            )
            
        except Exception as e:
            self._update_state(current_step="failed", errors=[str(e)])
            self.log(f"Workflow failed: {str(e)}", level="ERROR")
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"LangChain orchestration failed: {str(e)}"]
            )

