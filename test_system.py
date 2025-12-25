"""
Basic tests for the multi-agent content generation system.
Tests agent initialization, workflow execution, and output validation.
"""

import pytest
import os
import json
from src.agents.data_parser_agent import DataParserAgent
from src.agents.base_agent import AgentInput, AgentOutput
from src.models.product import Product
from src.models.outputs import FAQPage, FAQItem
from pydantic import ValidationError


def test_data_parser_agent():
    """Test DataParserAgent successfully parses valid product data"""
    agent = DataParserAgent()
    
    raw_data = {
        "product_name": "Test Serum",
        "concentration": "10% Vitamin C",
        "skin_type": "Oily, Combination",
        "key_ingredients": "Vitamin C, Hyaluronic Acid",
        "benefits": "Brightening, Hydrating",
        "how_to_use": "Apply 2-3 drops in the morning",
        "side_effects": "None reported",
        "price": "₹899"
    }
    
    result = agent.execute(AgentInput(data=raw_data))
    
    assert result.success == True
    assert isinstance(result.data, Product)
    assert result.data.name == "Test Serum"
    assert len(result.data.skin_types) == 2
    assert len(result.data.key_ingredients) == 2


def test_data_parser_validation():
    """Test DataParserAgent validates input correctly"""
    agent = DataParserAgent()
    
    # Missing required fields
    invalid_data = {
        "product_name": "Test Serum"
    }
    
    is_valid = agent.validate_input(AgentInput(data=invalid_data))
    assert is_valid == False


def test_pydantic_schema_enforcement():
    """Test Pydantic models enforce schema validation"""
    # Test valid FAQ page
    valid_faq = {
        "product_name": "Test Product",
        "total_questions": 3,
        "categories": ["General"],
        "faqs": [
            {"question": "Q1?", "answer": "A1", "category": "General"},
            {"question": "Q2?", "answer": "A2", "category": "General"},
            {"question": "Q3?", "answer": "A3", "category": "General"}
        ]
    }
    
    faq_page = FAQPage(**valid_faq)
    assert faq_page.total_questions == 3
    assert len(faq_page.faqs) == 3
    
    # Test invalid FAQ page (missing required fields)
    invalid_faq = {
        "product_name": "Test Product"
        # Missing total_questions, categories, faqs
    }
    
    with pytest.raises(ValidationError):
        FAQPage(**invalid_faq)


def test_faq_count_deterministic():
    """Test FAQ count is deterministically set to match actual FAQ list length"""
    faqs = [
        FAQItem(question=f"Question {i}?", answer=f"Answer {i}", category="General")
        for i in range(20)
    ]
    
    faq_page = FAQPage(
        product_name="Test Product",
        total_questions=len(faqs),  # Deterministically set
        categories=["General"],
        faqs=faqs
    )
    
    assert faq_page.total_questions == len(faq_page.faqs)
    assert faq_page.total_questions == 20


def test_output_files_generated():
    """Test that output files are created in correct format"""
    output_dir = "output"
    
    # Check if output files exist
    assert os.path.exists(output_dir)
    
    files = ["faq_page.json", "product_page.json", "comparison_page.json"]
    for file in files:
        file_path = os.path.join(output_dir, file)
        if os.path.exists(file_path):
            # Validate JSON structure
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert isinstance(data, dict)
                assert "page_type" in data or "product_name" in data


def test_faq_output_structure():
    """Test FAQ output has correct structure and meets requirements"""
    faq_file = os.path.join("output", "faq_page.json")
    
    if os.path.exists(faq_file):
        with open(faq_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Check required fields
            assert "product_name" in data
            assert "total_questions" in data
            assert "faqs" in data
            
            # Check FAQ count meets minimum requirement (≥15)
            assert data["total_questions"] >= 15
            assert len(data["faqs"]) >= 15
            
            # Verify total_questions matches actual FAQ count (deterministic)
            assert data["total_questions"] == len(data["faqs"])
            
            # Check FAQ item structure
            for faq in data["faqs"]:
                assert "question" in faq
                assert "answer" in faq
                assert "category" in faq
                assert len(faq["answer"]) > 0  # Ensure answers are not empty
                assert len(faq["question"]) > 0  # Ensure questions are not empty
            
            # Validate Pydantic can parse the JSON
            faq_page = FAQPage(**data)
            assert faq_page.total_questions >= 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
