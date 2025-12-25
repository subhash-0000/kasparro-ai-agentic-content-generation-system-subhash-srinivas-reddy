"""
Robustness tests for error handling, retry mechanisms, validation, and fallback strategies.
Tests the new comprehensive error handling and resilience features.
"""

import pytest
import os
from src.agents.question_generator_agent_llm import QuestionGeneratorAgent
from src.agents.answer_generator_agent_llm import AnswerGeneratorAgent
from src.agents.comparison_agent_llm import ComparisonAgentLLM
from src.agents.product_page_agent_llm import ProductPageAgent
from src.agents.base_agent import AgentInput
from src.models.product import Product, CategorizedQuestion
from langchain_groq import ChatGroq
from unittest.mock import Mock, patch


def test_logging_infrastructure():
    """Test that logging infrastructure is properly initialized"""
    from src.agents.data_parser_agent import DataParserAgent
    
    agent = DataParserAgent()
    
    # Check logger exists
    assert hasattr(agent, 'logger')
    assert agent.logger is not None
    
    # Check log directory created
    assert os.path.exists('logs')
    
    # Check log file created
    log_file = os.path.join('logs', f'{agent.agent_id}.log')
    assert os.path.exists(log_file)
    
    # Test logging
    agent.log("Test log message", level="INFO")
    agent.log("Test warning", level="WARNING")
    agent.log("Test error", level="ERROR")


def test_question_validation():
    """Test question validation rejects invalid LLM outputs"""
    mock_llm = Mock(spec=ChatGroq)
    agent = QuestionGeneratorAgent(llm=mock_llm)
    
    # Test: Too few questions
    invalid_questions_few = [
        CategorizedQuestion(category="Informational", question="What is it?", priority=1),
        CategorizedQuestion(category="Usage", question="How to use?", priority=1),
    ]
    assert agent._validate_questions(invalid_questions_few) == False
    
    # Test: Missing required category
    invalid_questions_category = [
        CategorizedQuestion(category="Purchase", question=f"Question {i}?", priority=1)
        for i in range(15)
    ]
    assert agent._validate_questions(invalid_questions_category) == False
    
    # Test: Invalid question format (no question mark)
    invalid_questions_format = [
        CategorizedQuestion(category="Informational", question="What is it", priority=1),
    ] + [
        CategorizedQuestion(category="Usage", question=f"Question {i}?", priority=1)
        for i in range(14)
    ]
    assert agent._validate_questions(invalid_questions_format) == False
    
    # Test: Valid questions
    valid_questions = [
        CategorizedQuestion(category="Informational", question="What is the product?", priority=1),
        CategorizedQuestion(category="Informational", question="What are the ingredients?", priority=1),
        CategorizedQuestion(category="Informational", question="What are the benefits?", priority=1),
        CategorizedQuestion(category="Informational", question="What is the concentration?", priority=1),
        CategorizedQuestion(category="Usage", question="How to use it?", priority=1),
        CategorizedQuestion(category="Usage", question="When to apply?", priority=1),
        CategorizedQuestion(category="Usage", question="How much to use?", priority=1),
        CategorizedQuestion(category="Safety", question="Any side effects?", priority=1),
        CategorizedQuestion(category="Safety", question="Is it safe?", priority=1),
        CategorizedQuestion(category="Safety", question="What precautions?", priority=1),
    ] + [
        CategorizedQuestion(category="Results", question=f"Question {i}?", priority=1)
        for i in range(5)
    ]
    assert agent._validate_questions(valid_questions) == True


def test_answer_validation():
    """Test answer validation rejects invalid LLM outputs"""
    mock_llm = Mock(spec=ChatGroq)
    agent = AnswerGeneratorAgent(llm=mock_llm)
    
    questions = [
        CategorizedQuestion(category="Informational", question="What is it?", priority=1),
        CategorizedQuestion(category="Usage", question="How to use?", priority=1),
        CategorizedQuestion(category="Safety", question="Is it safe?", priority=1),
    ]
    
    # Test: Answer count mismatch
    invalid_answers_count = ["Answer 1", "Answer 2"]
    assert agent._validate_answers(invalid_answers_count, questions) == False
    
    # Test: Empty answers
    invalid_answers_empty = ["", "Answer 2", "Answer 3"]
    assert agent._validate_answers(invalid_answers_empty, questions) == False
    
    # Test: Too short answers
    invalid_answers_short = ["Short", "Also short", "Too short"]
    assert agent._validate_answers(invalid_answers_short, questions) == False
    
    # Test: Valid answers
    valid_answers = [
        "This is a comprehensive answer to the first question with sufficient detail.",
        "This is another detailed answer that provides useful information to users.",
        "This answer also meets the minimum length requirement for validation."
    ]
    assert agent._validate_answers(valid_answers, questions) == True


def test_comparison_validation():
    """Test comparison validation rejects invalid LLM outputs"""
    mock_llm = Mock(spec=ChatGroq)
    agent = ComparisonAgentLLM(llm=mock_llm)
    
    # Test: Missing required keys
    invalid_comparison_keys = {
        "product_a": {},
        "product_b": {},
        "comparison_points": []
    }
    assert agent._validate_comparison(invalid_comparison_keys) == False
    
    # Test: Too few comparison points
    invalid_comparison_points = {
        "product_a": {"name": "Product A"},
        "product_b": {"name": "Product B"},
        "comparison_points": [{"attribute": "Price", "winner": "A"}],
        "summary": "Summary",
        "recommendation": "Recommendation"
    }
    assert agent._validate_comparison(invalid_comparison_points) == False
    
    # Test: Missing competitor name
    invalid_comparison_name = {
        "product_a": {"name": "Product A"},
        "product_b": {},
        "comparison_points": [{"attr": f"Point {i}"} for i in range(6)],
        "summary": "Summary",
        "recommendation": "Recommendation"
    }
    assert agent._validate_comparison(invalid_comparison_name) == False
    
    # Test: Valid comparison
    valid_comparison = {
        "product_a": {"name": "Product A"},
        "product_b": {"name": "Product B"},
        "comparison_points": [{"attribute": f"Point {i}", "winner": "A"} for i in range(7)],
        "summary": {"winner": "A", "key_differences": "Differences"},
        "recommendation": "Choose A"
    }
    assert agent._validate_comparison(valid_comparison) == True


def test_product_content_validation():
    """Test product content validation rejects invalid LLM outputs"""
    mock_llm = Mock(spec=ChatGroq)
    agent = ProductPageAgent(llm=mock_llm)
    
    # Test: Missing required keys
    invalid_content_keys = {
        "tagline": "Tagline only"
    }
    assert agent._validate_product_content(invalid_content_keys) == False
    
    # Test: Tagline too short
    invalid_content_tagline = {
        "tagline": "Short",
        "description": "This is a longer description with sufficient content for validation.",
        "key_features": ["Feature 1", "Feature 2", "Feature 3"],
        "precautions": ["Precaution 1", "Precaution 2"]
    }
    assert agent._validate_product_content(invalid_content_tagline) == False
    
    # Test: Description too short
    invalid_content_description = {
        "tagline": "This is a proper tagline",
        "description": "Too short",
        "key_features": ["Feature 1", "Feature 2", "Feature 3"],
        "precautions": ["Precaution 1", "Precaution 2"]
    }
    assert agent._validate_product_content(invalid_content_description) == False
    
    # Test: Too few features
    invalid_content_features = {
        "tagline": "This is a proper tagline",
        "description": "This is a longer description with sufficient content for validation.",
        "key_features": ["Feature 1"],
        "precautions": ["Precaution 1", "Precaution 2"]
    }
    assert agent._validate_product_content(invalid_content_features) == False
    
    # Test: Too few precautions
    invalid_content_precautions = {
        "tagline": "This is a proper tagline",
        "description": "This is a longer description with sufficient content for validation.",
        "key_features": ["Feature 1", "Feature 2", "Feature 3"],
        "precautions": ["Only one"]
    }
    assert agent._validate_product_content(invalid_content_precautions) == False
    
    # Test: Valid content
    valid_content = {
        "tagline": "Amazing skincare solution",
        "description": "This is a comprehensive product description with detailed information about the product benefits and usage.",
        "key_features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
        "precautions": ["Precaution 1", "Precaution 2", "Precaution 3"]
    }
    assert agent._validate_product_content(valid_content) == True


def test_fallback_question_generation():
    """Test fallback question generation works when LLM fails"""
    mock_llm = Mock(spec=ChatGroq)
    agent = QuestionGeneratorAgent(llm=mock_llm)
    
    product = Product(
        name="Test Serum",
        concentration="10% Vitamin C",
        skin_types=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid"],
        benefits=["Brightening", "Hydration"],
        usage_instructions="Apply 2-3 drops",
        side_effects="None",
        price="₹899"
    )
    
    result = agent._fallback_questions(product)
    
    assert result.success == True
    assert result.data is not None
    assert len(result.data.questions) >= 15
    assert result.metadata.get("fallback_used") == True
    assert result.metadata.get("generation_method") == "Fallback (Template-based)"


def test_fallback_answer_generation():
    """Test fallback answer generation works when LLM fails"""
    mock_llm = Mock(spec=ChatGroq)
    agent = AnswerGeneratorAgent(llm=mock_llm)
    
    product = Product(
        name="Test Serum",
        concentration="10% Vitamin C",
        skin_types=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid"],
        benefits=["Brightening", "Hydration"],
        usage_instructions="Apply 2-3 drops in the morning",
        side_effects="None reported",
        price="₹899"
    )
    
    questions = [
        CategorizedQuestion(category="Informational", question="What is Test Serum?", priority=1),
        CategorizedQuestion(category="Usage", question="How do I use Test Serum?", priority=1),
        CategorizedQuestion(category="Safety", question="Are there any side effects?", priority=1),
    ]
    
    result = agent._fallback_answers(product, questions)
    
    assert result.success == True
    assert len(result.data) == len(questions)
    assert result.metadata.get("fallback_used") == True
    # Check answers have content
    for answer in result.data:
        assert len(answer) > 20


def test_fallback_comparison_generation():
    """Test fallback comparison generation works when LLM fails"""
    mock_llm = Mock(spec=ChatGroq)
    agent = ComparisonAgentLLM(llm=mock_llm)
    
    product = Product(
        name="Test Serum",
        concentration="10% Vitamin C",
        skin_types=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid"],
        benefits=["Brightening", "Hydration"],
        usage_instructions="Apply 2-3 drops",
        side_effects="None",
        price="₹899"
    )
    
    result = agent._fallback_comparison(product)
    
    assert result.success == True
    assert result.data["product_b"]["name"] is not None
    assert len(result.data["comparison_points"]) >= 5
    assert result.metadata.get("fallback_used") == True


def test_fallback_product_content_generation():
    """Test fallback product content generation works when LLM fails"""
    mock_llm = Mock(spec=ChatGroq)
    agent = ProductPageAgent(llm=mock_llm)
    
    product = Product(
        name="Test Serum",
        concentration="10% Vitamin C",
        skin_types=["Oily", "Combination"],
        key_ingredients=["Vitamin C", "Hyaluronic Acid"],
        benefits=["Brightening", "Hydration"],
        usage_instructions="Apply 2-3 drops in the morning",
        side_effects="None reported",
        price="₹899"
    )
    
    result = agent._fallback_product_content(product)
    
    assert result.success == True
    assert "tagline" in result.data
    assert "description" in result.data
    assert len(result.data["key_features"]) >= 3
    assert result.metadata.get("fallback_used") == True


def test_retry_mechanism_exists():
    """Test that retry decorator is applied to workflow steps"""
    from src.agents.orchestrator_langchain import retry_with_exponential_backoff
    
    # Test decorator exists
    assert callable(retry_with_exponential_backoff)
    
    # Test decorated function
    call_count = 0
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=0.1)
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Simulated failure")
        return "Success"
    
    result = failing_function()
    assert result == "Success"
    assert call_count == 3  # Failed twice, succeeded on third attempt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
