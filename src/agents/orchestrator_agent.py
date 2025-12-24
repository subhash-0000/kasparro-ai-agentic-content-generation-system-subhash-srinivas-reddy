"""
OrchestratorAgent - Coordinates the entire multi-agent workflow.
Single Responsibility: Agent orchestration and state management.
"""

import json
from typing import Dict, Any
from pathlib import Path
from src.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from src.agents.data_parser_agent import DataParserAgent
from src.agents.question_generator_agent import QuestionGeneratorAgent
from src.agents.comparison_agent import ComparisonAgent
from src.agents.template_agent import TemplateAgent
from src.models.product import Product, QuestionSet
from src.models.outputs import FAQPage, ProductPage, ComparisonPage


class OrchestratorAgent(BaseAgent):
    """
    Orchestrates the entire multi-agent workflow.
    
    Workflow:
    1. DataParserAgent: Parse raw product data
    2. QuestionGeneratorAgent: Generate categorized questions
    3. ComparisonAgent: Create fictional Product B and comparison
    4. TemplateAgent: Generate all three pages (FAQ, Product, Comparison)
    5. Output: Save JSON files
    """
    
    def __init__(self, output_dir: str = "output"):
        super().__init__(
            agent_id="orchestrator_agent",
            description="Coordinates multi-agent workflow and manages state"
        )
        
        # Initialize all agents
        self.data_parser = DataParserAgent()
        self.question_generator = QuestionGeneratorAgent()
        self.comparison_agent = ComparisonAgent()
        self.template_agent = TemplateAgent()
        
        # Output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Workflow state
        self.workflow_state = {
            "product": None,
            "question_set": None,
            "comparison_data": None,
            "pages": {}
        }
    
    def _step_1_parse_data(self, raw_data: Dict[str, Any]) -> AgentOutput:
        """
        Step 1: Parse raw product data.
        
        Args:
            raw_data: Raw product dictionary
            
        Returns:
            AgentOutput with Product instance
        """
        print("\n[STEP 1] Parsing product data...")
        input_data = AgentInput(data=raw_data)
        output = self.data_parser(input_data)
        
        if output.success:
            self.workflow_state["product"] = output.data
            print(f"✓ Product parsed: {output.data.name}")
        else:
            print(f"✗ Parsing failed: {output.errors}")
        
        return output
    
    def _step_2_generate_questions(self) -> AgentOutput:
        """
        Step 2: Generate categorized questions.
        
        Returns:
            AgentOutput with QuestionSet
        """
        print("\n[STEP 2] Generating categorized questions...")
        input_data = AgentInput(data=self.workflow_state["product"])
        output = self.question_generator(input_data)
        
        if output.success:
            self.workflow_state["question_set"] = output.data
            print(f"✓ Generated {output.metadata['total_questions']} questions")
            print(f"  Categories: {', '.join(output.metadata['categories'])}")
        else:
            print(f"✗ Question generation failed: {output.errors}")
        
        return output
    
    def _step_3_generate_comparison(self) -> AgentOutput:
        """
        Step 3: Generate fictional Product B and comparison.
        
        Returns:
            AgentOutput with comparison data
        """
        print("\n[STEP 3] Generating product comparison...")
        input_data = AgentInput(data=self.workflow_state["product"])
        output = self.comparison_agent(input_data)
        
        if output.success:
            self.workflow_state["comparison_data"] = output.data
            print(f"✓ Comparison generated with {output.metadata['comparison_points_count']} points")
        else:
            print(f"✗ Comparison generation failed: {output.errors}")
        
        return output
    
    def _step_4_generate_faq_page(self) -> AgentOutput:
        """
        Step 4a: Generate FAQ page.
        
        Returns:
            AgentOutput with FAQPage
        """
        print("\n[STEP 4a] Generating FAQ page...")
        input_data = AgentInput(data={
            "page_type": "faq",
            "product": self.workflow_state["product"],
            "question_set": self.workflow_state["question_set"]
        })
        output = self.template_agent(input_data)
        
        if output.success:
            self.workflow_state["pages"]["faq"] = output.data
            print(f"✓ FAQ page generated with {output.data.total_questions} Q&As")
        else:
            print(f"✗ FAQ page generation failed: {output.errors}")
        
        return output
    
    def _step_5_generate_product_page(self) -> AgentOutput:
        """
        Step 4b: Generate product description page.
        
        Returns:
            AgentOutput with ProductPage
        """
        print("\n[STEP 4b] Generating product page...")
        input_data = AgentInput(data={
            "page_type": "product_page",
            "product": self.workflow_state["product"]
        })
        output = self.template_agent(input_data)
        
        if output.success:
            self.workflow_state["pages"]["product"] = output.data
            print(f"✓ Product page generated: {output.data.product_name}")
        else:
            print(f"✗ Product page generation failed: {output.errors}")
        
        return output
    
    def _step_6_generate_comparison_page(self) -> AgentOutput:
        """
        Step 4c: Generate comparison page.
        
        Returns:
            AgentOutput with ComparisonPage
        """
        print("\n[STEP 4c] Generating comparison page...")
        input_data = AgentInput(data={
            "page_type": "comparison",
            "comparison_data": self.workflow_state["comparison_data"]
        })
        output = self.template_agent(input_data)
        
        if output.success:
            self.workflow_state["pages"]["comparison"] = output.data
            print(f"✓ Comparison page generated")
        else:
            print(f"✗ Comparison page generation failed: {output.errors}")
        
        return output
    
    def _step_7_save_outputs(self) -> bool:
        """
        Step 5: Save all generated pages as JSON files.
        
        Returns:
            bool: Success status
        """
        print("\n[STEP 5] Saving JSON outputs...")
        
        try:
            # Save FAQ page
            faq_path = self.output_dir / "faq.json"
            with open(faq_path, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_state["pages"]["faq"].dict(), f, indent=2, ensure_ascii=False)
            print(f"✓ Saved: {faq_path}")
            
            # Save Product page
            product_path = self.output_dir / "product_page.json"
            with open(product_path, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_state["pages"]["product"].dict(), f, indent=2, ensure_ascii=False)
            print(f"✓ Saved: {product_path}")
            
            # Save Comparison page
            comparison_path = self.output_dir / "comparison_page.json"
            with open(comparison_path, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_state["pages"]["comparison"].dict(), f, indent=2, ensure_ascii=False)
            print(f"✓ Saved: {comparison_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to save outputs: {str(e)}")
            return False
    
    def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute the complete multi-agent workflow.
        
        Args:
            input_data: Contains raw product data
            
        Returns:
            AgentOutput with workflow summary
        """
        print("="*60)
        print("MULTI-AGENT CONTENT GENERATION SYSTEM")
        print("="*60)
        
        try:
            raw_data = input_data.data
            
            # Execute workflow steps
            step1_output = self._step_1_parse_data(raw_data)
            if not step1_output.success:
                return step1_output
            
            step2_output = self._step_2_generate_questions()
            if not step2_output.success:
                return step2_output
            
            step3_output = self._step_3_generate_comparison()
            if not step3_output.success:
                return step3_output
            
            step4_output = self._step_4_generate_faq_page()
            if not step4_output.success:
                return step4_output
            
            step5_output = self._step_5_generate_product_page()
            if not step5_output.success:
                return step5_output
            
            step6_output = self._step_6_generate_comparison_page()
            if not step6_output.success:
                return step6_output
            
            save_success = self._step_7_save_outputs()
            
            if not save_success:
                return AgentOutput(
                    success=False,
                    data=None,
                    errors=["Failed to save output files"]
                )
            
            print("\n" + "="*60)
            print("WORKFLOW COMPLETED SUCCESSFULLY")
            print("="*60)
            
            return AgentOutput(
                success=True,
                data={
                    "product_name": self.workflow_state["product"].name,
                    "questions_generated": len(self.workflow_state["question_set"].questions),
                    "pages_generated": list(self.workflow_state["pages"].keys()),
                    "output_directory": str(self.output_dir)
                },
                metadata={
                    "agent_id": self.agent_id,
                    "workflow_steps": 7,
                    "agents_used": 4
                }
            )
            
        except Exception as e:
            print(f"\n✗ Workflow failed: {str(e)}")
            return AgentOutput(
                success=False,
                data=None,
                errors=[f"Workflow execution failed: {str(e)}"]
            )
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate that input contains raw product data."""
        return isinstance(input_data.data, dict) and "product_name" in input_data.data
