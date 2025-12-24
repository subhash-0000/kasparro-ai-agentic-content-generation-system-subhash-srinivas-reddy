"""
Core data models for the product content generation system.
Defines clean internal representations with validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class Product(BaseModel):
    """Internal representation of a product with validated fields."""
    
    name: str = Field(..., description="Product name")
    concentration: str = Field(..., description="Active ingredient concentration")
    skin_types: List[str] = Field(..., description="Compatible skin types")
    key_ingredients: List[str] = Field(..., description="Main ingredients")
    benefits: List[str] = Field(..., description="Product benefits")
    usage_instructions: str = Field(..., description="How to use the product")
    side_effects: Optional[str] = Field(None, description="Potential side effects")
    price: str = Field(..., description="Product price")
    
    @validator('skin_types', 'key_ingredients', 'benefits', pre=True)
    def split_comma_separated(cls, v):
        """Convert comma-separated strings to lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',')]
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "GlowBoost Vitamin C Serum",
                "concentration": "10% Vitamin C",
                "skin_types": ["Oily", "Combination"],
                "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
                "benefits": ["Brightening", "Fades dark spots"],
                "usage_instructions": "Apply 2–3 drops in the morning before sunscreen",
                "side_effects": "Mild tingling for sensitive skin",
                "price": "₹699"
            }
        }


class CategorizedQuestion(BaseModel):
    """Represents a user question with its category."""
    
    category: str = Field(..., description="Question category")
    question: str = Field(..., description="The actual question")
    priority: int = Field(default=1, description="Priority level for ordering")
    
    class Config:
        schema_extra = {
            "example": {
                "category": "Usage",
                "question": "How often should I use GlowBoost Vitamin C Serum?",
                "priority": 1
            }
        }


class QuestionSet(BaseModel):
    """Collection of categorized questions."""
    
    questions: List[CategorizedQuestion] = Field(..., description="All generated questions")
    categories: List[str] = Field(..., description="List of unique categories")
    
    @validator('categories', always=True)
    def extract_categories(cls, v, values):
        """Auto-extract unique categories from questions."""
        if 'questions' in values:
            return list(set(q.category for q in values['questions']))
        return v


class ContentBlock(BaseModel):
    """Represents a reusable content logic block output."""
    
    block_type: str = Field(..., description="Type of content block")
    content: dict = Field(..., description="Generated content data")
    dependencies: List[str] = Field(default_factory=list, description="Required input fields")
    
    class Config:
        schema_extra = {
            "example": {
                "block_type": "benefits_block",
                "content": {"benefits": ["Brightens skin", "Reduces dark spots"]},
                "dependencies": ["product.benefits"]
            }
        }
