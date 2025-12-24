"""
Main entry point for the multi-agent content generation system.
"""

from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.base_agent import AgentInput


def main():
    """
    Main execution function.
    Runs the complete multi-agent workflow.
    """
    
    # Raw product data (as specified in assignment)
    raw_product_data = {
        "product_name": "GlowBoost Vitamin C Serum",
        "concentration": "10% Vitamin C",
        "skin_type": "Oily, Combination",
        "key_ingredients": "Vitamin C, Hyaluronic Acid",
        "benefits": "Brightening, Fades dark spots",
        "how_to_use": "Apply 2–3 drops in the morning before sunscreen",
        "side_effects": "Mild tingling for sensitive skin",
        "price": "₹699"
    }
    
    # Create orchestrator
    orchestrator = OrchestratorAgent(output_dir="output")
    
    # Execute workflow
    input_data = AgentInput(data=raw_product_data)
    result = orchestrator(input_data)
    
    # Print final summary
    if result.success:
        print("\n✅ SUCCESS!")
        print(f"\nGenerated content for: {result.data['product_name']}")
        print(f"Questions generated: {result.data['questions_generated']}")
        print(f"Pages created: {', '.join(result.data['pages_generated'])}")
        print(f"\nOutput files saved in: {result.data['output_directory']}/")
    else:
        print("\n❌ FAILED!")
        print(f"Errors: {', '.join(result.errors)}")


if __name__ == "__main__":
    main()
