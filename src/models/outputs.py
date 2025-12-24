"""
Output models for generated pages.
Defines the structure of final JSON outputs.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FAQItem(BaseModel):
    """Single FAQ entry."""
    
    question: str = Field(..., description="User question")
    answer: str = Field(..., description="Detailed answer")
    category: str = Field(..., description="Question category")


class FAQPage(BaseModel):
    """FAQ page output structure."""
    
    page_type: str = Field(default="faq", description="Page type identifier")
    product_name: str = Field(..., description="Product name")
    total_questions: int = Field(..., description="Total number of FAQs")
    categories: List[str] = Field(..., description="All question categories")
    faqs: List[FAQItem] = Field(..., description="List of FAQ items")
    generated_by: str = Field(default="Multi-Agent System", description="System identifier")


class ProductPage(BaseModel):
    """Product description page output structure."""
    
    page_type: str = Field(default="product_page", description="Page type identifier")
    product_name: str = Field(..., description="Product name")
    tagline: str = Field(..., description="Product tagline")
    description: str = Field(..., description="Full product description")
    key_features: List[str] = Field(..., description="Key product features")
    ingredients: Dict[str, str] = Field(..., description="Ingredients with descriptions")
    usage_guide: Dict[str, Any] = Field(..., description="How to use the product")
    suitable_for: List[str] = Field(..., description="Skin types")
    benefits: List[str] = Field(..., description="Product benefits")
    safety_information: Dict[str, Any] = Field(..., description="Safety and side effects")
    pricing: Dict[str, str] = Field(..., description="Price information")
    generated_by: str = Field(default="Multi-Agent System", description="System identifier")


class ComparisonItem(BaseModel):
    """Single comparison point."""
    
    attribute: str = Field(..., description="Attribute being compared")
    product_a: Any = Field(..., description="Product A value")
    product_b: Any = Field(..., description="Product B value")
    winner: Optional[str] = Field(None, description="Which product is better for this attribute")


class ComparisonPage(BaseModel):
    """Comparison page output structure."""
    
    page_type: str = Field(default="comparison", description="Page type identifier")
    product_a: Dict[str, Any] = Field(..., description="First product details")
    product_b: Dict[str, Any] = Field(..., description="Second product details")
    comparison_points: List[ComparisonItem] = Field(..., description="Detailed comparisons")
    summary: Dict[str, Any] = Field(..., description="Comparison summary")
    recommendation: str = Field(..., description="Recommendation based on comparison")
    generated_by: str = Field(default="Multi-Agent System", description="System identifier")
